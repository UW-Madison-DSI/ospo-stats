import json
import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep

import requests
import tenacity
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session
from tqdm import tqdm

from ospo_stats.db import ENGINE, Commit, Repo, Stargazer, push
from ospo_stats.github.parser import (
    get_owner_and_repo_name,
    parse_commits,
    parse_discover_response,
    parse_stargazers,
)
from ospo_stats.github.query import (
    get_commits_query,
    get_repo_discovery_query,
    get_stargazers_query,
)

load_dotenv()

YEAR_NOW = datetime.now().year


@tenacity.retry(
    stop=tenacity.stop_after_attempt(5),
    wait=tenacity.wait_exponential(min=2, max=30),
)
def query_graphql(query: str) -> dict:
    """Post a GraphQL query to the GitHub API."""
    response = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
        json={"query": query},
    )
    response.raise_for_status()
    sleep(2)  # Avoid rate limiting
    return response.json()


def discover_yearly(term: str, year: int) -> list[dict]:
    """Page through the GitHub API to retrieve all repositories matching a keyword."""

    # To avoid hitting 1000 max results, we need to page through years
    repos = []
    after_cursor = None
    while True:
        query = get_repo_discovery_query(term=term, year=year, after=after_cursor)
        data = query_graphql(query)

        total = data["data"]["search"]["repositoryCount"]
        repos.extend(data["data"]["search"]["repos"])
        logging.info(f"Obtained repos: {len(repos)} / {total}")

        # Handle pagination
        has_next = data["data"]["search"]["pageInfo"]["hasNextPage"]
        if not has_next:
            break
        after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
    return repos


def get_stargazers(owner: str, name: str) -> list[dict]:
    """Get the stargazers of a repository."""

    stargazers = []
    after_cursor = None
    while True:
        query = get_stargazers_query(owner=owner, name=name, after=after_cursor)
        data = query_graphql(query)

        total = data["data"]["repository"]["stargazers"]["totalCount"]
        stargazers.extend(data["data"]["repository"]["stargazers"]["edges"])
        logging.info(f"Obtained stargazers: {len(stargazers)} / {total}")

        # Handle pagination
        has_next = data["data"]["repository"]["stargazers"]["pageInfo"]["hasNextPage"]
        if not has_next:
            break
        after_cursor = data["data"]["repository"]["stargazers"]["pageInfo"]["endCursor"]
    return stargazers


def get_commits(owner: str, name: str) -> list[dict]:
    """Get the commits of a repository."""

    commits = []
    after_cursor = None

    while True:
        query = get_commits_query(owner=owner, name=name, after=after_cursor)
        data = query_graphql(query)

        total = data["data"]["repository"]["defaultBranchRef"]["target"]["history"][
            "totalCount"
        ]
        commits.extend(
            data["data"]["repository"]["defaultBranchRef"]["target"]["history"]["edges"]
        )
        logging.info(f"Obtained commits: {len(commits)} / {total}")

        # Handle pagination
        has_next = data["data"]["repository"]["defaultBranchRef"]["target"]["history"][
            "pageInfo"
        ]["hasNextPage"]
        if not has_next:
            break
        after_cursor = data["data"]["repository"]["defaultBranchRef"]["target"][
            "history"
        ]["pageInfo"]["endCursor"]
    return commits


def discover_repos(
    term: str,
    year_min: int = 2008,
    year_max: int = YEAR_NOW,
    output_dir: Path | str = "data",
    push_to_turso: bool = True,
) -> None:
    """Crawl github for repositories matching a keyword."""

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    for year in range(year_min, year_max + 1):
        logging.info(f"Searching for {year}:")
        this_year_repos = discover_yearly(term, year)

        if not this_year_repos:
            logging.info(f"No repos found for {year}")
            continue

        # Save the results locally
        json_file = output_dir / f"repos_{term}_{year}.json"
        with open(json_file, "w") as f:
            f.write(json.dumps(this_year_repos, indent=4))

        if not push_to_turso:
            continue

        # Parse and Push to Turso
        parsed = [parse_discover_response(repo) for repo in this_year_repos]
        parsed = [p for p in parsed if p is not None]
        repos = [Repo(**repo) for repo in parsed]
        push(repos)


def crawl_commits(url: str) -> list[Commit]:
    owner, repo = get_owner_and_repo_name(url)
    raw_commits = get_commits(owner, repo)

    commits = []
    for commit in raw_commits:
        parsed = parse_commits(commit)
        parsed["repo_url"] = url
        commits.append(Commit(**parsed))
    return commits


def crawl_stargazers(url: str) -> list[Stargazer]:
    owner, repo = get_owner_and_repo_name(url)
    raw_stargazers = get_stargazers(owner, repo)

    stargazers = []
    for stargazer in raw_stargazers:
        parsed = parse_stargazers(stargazer)
        parsed["repo_url"] = url
        parsed["id"] = f"{url}/{parsed['user']}"
        stargazers.append(Stargazer(**parsed))
    return stargazers


def check_repo_in_table(repo_url: str, table: str) -> bool:
    """Check if a repo is already in the table."""
    with Session(ENGINE) as session:
        result = session.execute(
            text(f'SELECT repo_url FROM {table} WHERE repo_url = "{repo_url}" LIMIT 1')
        )
        return bool(result.fetchall())


def crawl_history(repo_url: str, skip_existing: bool = True) -> None:
    """Crawl the commit history of a repository."""

    if skip_existing and check_repo_in_table(repo_url, "commit_history"):
        logging.info(f"Skipping {repo_url}")
        return

    commits = crawl_commits(repo_url)
    stargazers = crawl_stargazers(repo_url)

    push(commits)
    push(stargazers)


def main() -> None:
    """Crawl data."""
    # Repo discovery
    # discover_repos("uw-madison")  # This is a somehow not a subset of "madison"
    # discover_repos("wisc.edu")
    # discover_repos("wisconsin")
    # discover_repos("madison")

    # History
    with Session(ENGINE) as session:
        query = session.query(Repo.url)

    repos = [row.url for row in query]
    for repo in tqdm(repos):
        try:
            crawl_history(repo, skip_existing=True)
        except Exception as e:
            logging.error(f"Failed to crawl {repo}: {e}")


if __name__ == "__main__":
    main()

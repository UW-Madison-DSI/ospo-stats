import json
import logging
import os
from datetime import datetime
from pathlib import Path
from time import sleep

import requests
import tenacity
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from ospo_stats.db import ENGINE, Repo

from .parser import parse_discover_response
from .query import get_commits_query, get_repo_discovery_query, get_stargazers_query

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
        json_file = output_dir / f"repos_{year}.json"
        with open(json_file, "w") as f:
            f.write(json.dumps(this_year_repos, indent=4))

        if not push_to_turso:
            continue

        # Parse and Push to Turso
        parsed = [parse_discover_response(repo) for repo in this_year_repos]
        parsed = [p for p in parsed if p is not None]
        objects = [Repo(**repo) for repo in parsed]

        with Session(ENGINE).no_autoflush as session:
            for repo in objects:
                session.merge(repo)
            session.commit()


if __name__ == "__main__":
    discover_repos("uw-madison")
    discover_repos("wisc.edu")
    discover_repos("wisconsin")
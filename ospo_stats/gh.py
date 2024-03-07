import json
import logging
import os
from datetime import datetime
from functools import partial
from pathlib import Path
from time import sleep

import requests
import tenacity
from dotenv import load_dotenv

from .query import REPO_QUERY_V0

load_dotenv()
logging.basicConfig(level=logging.ERROR)

YEAR_NOW = datetime.now().year


def get_graphql_query(
    term: str,
    year: int,
    per_page: int = 10,
    after: str | None = None,
    base_query: str = REPO_QUERY_V0,
) -> str:
    """Get the GraphQL query string for the GitHub API."""

    after_line = f'after: "{after}"' if after else ""
    return base_query.format(
        term=term, year=year, after_line=after_line, per_page=per_page
    )


@tenacity.retry(
    stop=tenacity.stop_after_attempt(5),
    wait=tenacity.wait_exponential(min=2, max=30),
)
def query_graphql(
    term: str,
    year: int,
    per_page: int = 10,
    after: str | None = None,
    base_query: str = REPO_QUERY_V0,
) -> dict:
    """Post a GraphQL query to the GitHub API."""
    response = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
        json={"query": get_graphql_query(term, year, per_page, after, base_query)},
    )
    response.raise_for_status()
    sleep(2)  # Avoid rate limiting
    return response.json()


def search_yearly(term: str, year: int) -> list[dict]:
    """Page through the GitHub API to retrieve all repositories matching a keyword."""

    query_year = partial(query_graphql, term=term, year=year, per_page=100)

    # To avoid hitting 1000 max results, we need to page through years
    repos = []
    after_cursor = None
    has_next = True
    while has_next:
        data = query_year(after=after_cursor)

        total = data["data"]["search"]["repositoryCount"]
        repos.extend(data["data"]["search"]["repos"])

        # Handle pagination
        has_next = data["data"]["search"]["pageInfo"]["hasNextPage"]
        after_cursor = data["data"]["search"]["pageInfo"]["endCursor"]
        logging.info(f"Obtained repos: {len(repos)} / {total}, cursor: {after_cursor}")

    return repos


def crawl(
    term: str,
    year_min: int = 2008,
    year_max: int = YEAR_NOW,
    overwrite: bool = False,
) -> None:
    """Crawl github yearly for repositories matching a keyword.

    This is a workaround for 1000 max results.
    """

    Path("data").mkdir(exist_ok=True, parents=True)

    for year in range(year_min, year_max + 1):
        if Path(f"data/repos_{year}.json").exists() and not overwrite:
            logging.info(f"Skipping {year} because it already exists")
            continue

        logging.info(f"Searching for {year}:")
        this_year_repos = search_yearly(term, year)

        if not this_year_repos:
            logging.info(f"No repos found for {year}")
            continue

        with open(f"data/repos_{year}.json", "w") as f:
            f.write(json.dumps(this_year_repos, indent=4))

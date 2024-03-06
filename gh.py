import json
from pathlib import Path
from time import sleep

import requests
import tenacity


@tenacity.retry(
    stop=tenacity.stop_after_attempt(5),
    wait=tenacity.wait_exponential(min=2, max=30),
)
def request_with_timeout(url: str) -> dict:
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def search_github(keyword: str) -> list[dict]:
    """Page through the GitHub API to retrieve all repositories matching a keyword."""

    repos = []

    i = 1
    while True:
        data = request_with_timeout(
            f"https://api.github.com/search/repositories?q={keyword}&page={i}&per_page=100"
        )
        repos.extend(data["items"])
        n = len(data["items"])
        print(f"Retrieved {n + (i-1) * 100} / {data['total_count']}")

        if len(data["items"]) < 100:
            break
        i += 1
        sleep(1)
    return repos


def crawl(
    keyword: str = "uw-madison",
    year_min: int = 2008,
    year_max: int = 2024,
) -> None:
    """Crawl github yearly for repositories matching a keyword.

    This is a workaround for 1000 max results.
    """

    for year in range(year_min, year_max + 1):
        if Path(f"data/repos_{year}.json").exists():
            print(f"Skipping {year} because it already exists")
            continue

        print(f"Searching for {year}:")
        this_year_repos = search_github(f"{keyword} created:{year}-01-01..{year}-12-31")
        if not this_year_repos:
            print(f"No repos found for {year}")
            continue

        with open(f"data/repos_{year}.json", "w") as f:
            f.write(json.dumps(this_year_repos, indent=4))

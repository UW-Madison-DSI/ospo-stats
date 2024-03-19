import json
import logging
from pathlib import Path

import pandas as pd


def parse_discover_response(data: dict) -> dict | None:
    """Flatten the data from the GitHub API to make it easier to work with."""

    empty = data["repo"]["defaultBranchRef"] is None
    if empty:
        return None

    if data["repo"]["readme_standard"]:
        readme = data["repo"]["readme_standard"]["text"]
    elif data["repo"]["readme_lower"]:
        logging.info(f"{data['repo']['url']} used a lowercase README file")
        readme = data["repo"]["readme_lower"]["text"]
    else:
        logging.info(f"{data['repo']['url']} had no README file")
        readme = None

    if data["repo"]["licenseInfo"] is None:
        license_key = None
        license_name = None
    else:
        license_key = data["repo"]["licenseInfo"]["key"]
        license_name = data["repo"]["licenseInfo"]["name"]

    return {
        "url": data["repo"]["url"],
        "last_pushed_at": data["repo"]["pushedAt"],
        "owner": data["repo"]["owner"]["login"],
        "name": data["repo"]["name"],
        "description": data["repo"]["description"],
        "license_key": license_key,
        "license_name": license_name,
        "total_stargazer_count": data["repo"]["stargazers"]["totalCount"],
        "total_issues_count": data["repo"]["total_issues"]["totalCount"],
        "total_open_issues_count": data["repo"]["open_issues"]["totalCount"],
        "total_forks_count": data["repo"]["forks"]["totalCount"],
        "total_watchers_count": data["repo"]["watchers"]["totalCount"],
        "created_at": data["repo"]["createdAt"],
        "readme": readme,
    }


def parse_stargazers(raw_data: dict) -> dict:
    return {
        "starred_at": raw_data["starredAt"],
        "user": raw_data["node"]["login"],
    }


def parse_commits(raw_data: dict) -> dict:
    return {
        "committed_at": raw_data["node"]["committedDate"],
        "url": raw_data["node"]["url"],
        "additions": raw_data["node"]["additions"],
        "deletions": raw_data["node"]["deletions"],
        "committer_name": raw_data["node"]["committer"]["name"],
        "committer_email": raw_data["node"]["committer"]["email"],
    }


def load(data_path: Path | str) -> pd.DataFrame:
    """Load the raw data from the given path."""

    if not isinstance(data_path, Path):
        data_path = Path(data_path)

    data_files = data_path.glob("*.json")

    parsed_data = []
    for file in data_files:
        logging.info(file)
        with open(file, "r") as f:
            data = json.load(f)
        parsed_data.extend([parse_discover_response(d) for d in data])

    return pd.DataFrame([p for p in parsed_data if p is not None])

import json
import logging
from pathlib import Path

import pandas as pd


def parse(data: dict) -> dict | None:
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

    return {
        "name": data["repo"]["name"],
        "url": data["repo"]["url"],
        "description": data["repo"]["description"],
        "created_at": data["repo"]["createdAt"],
        "pushed_at": data["repo"]["pushedAt"],
        "stars": data["repo"]["stargazers"]["totalCount"],
        "issues": data["repo"]["issues"]["totalCount"],
        "commits": data["repo"]["defaultBranchRef"]["target"]["history"]["totalCount"],
        "readme": readme,
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
        parsed_data.extend([parse(d) for d in data if parse(d) is not None])

    return pd.DataFrame(parsed_data)

import json
import logging
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


def get_owner_and_repo_name(url: str) -> tuple[str, str]:
    """Get owner and repo name from the url."""

    x = url.replace("https://github.com/", "").split("/")
    return x[0], x[1]


def has_image(readme_content: str) -> bool:
    """Check if the README contains an image."""

    # Regex for Markdown image
    markdown_image_regex = r"!\[.*?\]\(.*?\)"

    # Regex for HTML img tag
    html_image_regex = r"<img .*?src=\".*?\".*?>"

    # Search for images
    contains_markdown_image = (
        re.search(markdown_image_regex, readme_content) is not None
    )
    contains_html_image = re.search(html_image_regex, readme_content) is not None

    return contains_markdown_image or contains_html_image


def parse_discover_response(data: dict) -> dict | None:
    """Flatten the data from the GitHub API to make it easier to work with."""

    empty = data["repo"]["defaultBranchRef"] is None
    if empty:
        return None

    output = {
        "url": data["repo"]["url"],
        "created_at": datetime.strptime(
            data["repo"]["createdAt"], "%Y-%m-%dT%H:%M:%SZ"
        ),
        "last_pushed_at": datetime.strptime(
            data["repo"]["pushedAt"], "%Y-%m-%dT%H:%M:%SZ"
        ),
        "owner": data["repo"]["owner"]["login"],
        "name": data["repo"]["name"],
        "description": data["repo"]["description"],
        "total_stargazer_count": data["repo"]["stargazers"]["totalCount"],
        "total_issues_count": data["repo"]["total_issues"]["totalCount"],
        "total_open_issues_count": data["repo"]["open_issues"]["totalCount"],
        "total_forks_count": data["repo"]["forks"]["totalCount"],
        "total_watchers_count": data["repo"]["watchers"]["totalCount"],
    }

    # Append optional fields
    if data["repo"]["readme_standard"]:
        output["readme"] = data["repo"]["readme_standard"]["text"]
    elif data["repo"]["readme_lower"]:
        logging.info(f"{data['repo']['url']} used a lowercase README file")
        output["readme"] = data["repo"]["readme_lower"]["text"]
    else:
        logging.info(f"{data['repo']['url']} had no README file")

    if "readme" in output:
        output["readme_has_image"] = has_image(output["readme"])

    if data["repo"]["licenseInfo"]:
        output["license_key"] = data["repo"]["licenseInfo"]["key"]
        output["license_name"] = data["repo"]["licenseInfo"]["name"]

    if data["repo"]["homepageUrl"]:
        output["homepage_url"] = data["repo"]["homepageUrl"]

    return output


def parse_stargazers(raw_data: dict) -> dict:
    return {
        "starred_at": datetime.strptime(raw_data["starredAt"], "%Y-%m-%dT%H:%M:%SZ"),
        "user": raw_data["node"]["login"],
    }


def parse_commits(raw_data: dict) -> dict:
    return {
        "committed_at": datetime.strptime(
            raw_data["node"]["committedDate"], "%Y-%m-%dT%H:%M:%SZ"
        ),
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

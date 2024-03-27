import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from ospo_stats.db import Repo


def parse(row, crawl_at: datetime) -> Repo:
    """Parse GitLab csv to repo object."""

    def _safe_null(v: Any, safe_output: Any = None) -> Any:
        """Return safe_output if v is null, else return v."""
        return v if pd.notnull(v) else safe_output

    return Repo(
        url=row["http_url_to_repo"],
        crawl_at=crawl_at,
        created_at=datetime.strptime(row["created_at"], "%Y-%m-%d %H:%M:%S"),
        owner=row["name_with_namespace"].split(" / ")[0],
        name=row["name"],
        description=_safe_null(row["description"], None),
        homepage_url=row["web_url"],
        last_pushed_at=datetime.strptime(row["last_activity_at"], "%Y-%m-%d %H:%M:%S"),
        license_key=None,  # @Abe, No license info in GitLab?
        license_name=None,
        readme=None,
        readme_has_image=row["readme_has_images"],
        total_stargazer_count=_safe_null(row["star_count"], 0),
        total_issues_count=0,
        total_open_issues_count=_safe_null(row["open_issues_count"], 0),
        total_forks_count=_safe_null(row["forks_count"], 0),
        total_watchers_count=0,
    )


def parse_csv(file: Path | str) -> list[Repo]:
    """Parse GitLab csv to list of repo objects."""

    df = pd.read_csv(file)

    # Get estimated crawl time
    file_creation_timestamp = os.path.getctime(file)
    crawled_at = datetime.fromtimestamp(file_creation_timestamp)

    repos = []
    for index, row in df.iterrows():
        repo = parse(row, crawled_at)
        repos.append(repo)
    return repos

import altair as alt
import pandas as pd

from ospo_stats.db import ENGINE

_query_repo_by_year = """
SELECT strftime('%Y', created_at) AS year, COUNT(*) AS num_repos
FROM repo 
GROUP BY year
ORDER BY year;
"""

_query_commit_by_year = """
SELECT strftime('%Y', committed_at) AS year, COUNT(*) AS num_commits
FROM commit_history
GROUP BY year
ORDER BY year;
"""

_query_stargazer_by_year = """
SELECT strftime('%Y', starred_at) AS year, COUNT(*) AS num_stargazers
FROM stargazer_history
GROUP BY year
ORDER BY year;
"""


def get_repo_by_year() -> pd.DataFrame:
    """Get the number of repositories created by year."""
    with ENGINE.connect() as conn:
        df = pd.read_sql(_query_repo_by_year, conn)

    df["cumulative_n"] = df["num_repos"].cumsum()
    return df


def get_commit_by_year() -> pd.DataFrame:
    """Get the number of commits by year."""
    with ENGINE.connect() as conn:
        df = pd.read_sql(_query_commit_by_year, conn)

    df["cumulative_n"] = df["num_commits"].cumsum()
    return df


def get_stargazer_by_year() -> pd.DataFrame:
    """Get the number of stargazers by year."""
    with ENGINE.connect() as conn:
        df = pd.read_sql(_query_stargazer_by_year, conn)

    df["cumulative_n"] = df["num_stargazers"].cumsum()
    return df


def plot_cumulative(
    df: pd.DataFrame,
    year_col_name: str = "year",
    cumulative_n_col_name: str = "cumulative_n",
) -> alt.Chart:
    """Plot cumulative repos from database."""

    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(x=f"{year_col_name}:O", y=f"{cumulative_n_col_name}:Q")
        .properties(width=600, height=400)
    )

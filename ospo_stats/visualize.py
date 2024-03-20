import altair as alt
import pandas as pd
from ospo_stats.db import ENGINE


_query_repo_by_year = """
SELECT strftime('%Y', created_at) AS year, COUNT(*) AS num_repos
FROM repo 
GROUP BY year
ORDER BY year;
"""


def get_repo_by_year() -> pd.DataFrame:
    """Get the number of repositories created by year."""
    with ENGINE.connect() as conn:
        df = pd.read_sql(_query_repo_by_year, conn)

    df["cumulative_n"] = df["num_repos"].cumsum()
    return df


def plot_cumulative_repos(
    df: pd.DataFrame,
    year_col_name: str = "year",
    cumulative_n_col_name: str = "cumulative_n",
) -> alt.Chart:
    """Plot cumulative repos from database."""

    return (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=f"{year_col_name}:O",
            y=alt.Y(
                f"{cumulative_n_col_name}:Q", title="Cumulative Number of Repositories"
            ),
        )
        .properties(
            title="Yearly Growth of UW–Madison's Open-Source (public) Repositories on GitHub",
            width=600,
            height=400,
        )
    )

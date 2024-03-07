# This query is for discovering repositories with summary information like total commits, and total stargazers
_REPO_DISCOVERY = """
{{
  search(
    type: REPOSITORY
    query: "{term} created:{year}-01-01..{year}-12-31"
    first: {per_page}
    {after_line}
  ) {{
    repositoryCount
    pageInfo {{
      endCursor
      hasNextPage
    }}
    repos: edges {{
      repo: node {{
        ... on Repository {{
          owner {{
            login
          }}
          name
          url
          description
          createdAt
          pushedAt
          stargazers {{
            totalCount
          }}
          issues {{
            totalCount
          }}

          defaultBranchRef {{
            target {{
              ... on Commit {{
                history(first: 0) {{
                  totalCount
                }}
              }}
            }}
          }}
          readme_standard: object(expression: "HEAD:README.md") {{
            ... on Blob {{
              text
            }}
          }}
          readme_lower: object(expression: "HEAD:readme.md") {{
            ... on Blob {{
              text
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

# This query is for getting details of stargazers of a given repository
_STARGAZERS = """
{{
  repository(owner: "{owner}", name: "{name}") {{
    stargazers(
      first: 100
      {after_line}
      ) {{
      totalCount
      edges {{
        starredAt
          node {{
            login
          }}
      }}
      pageInfo {{
        endCursor
        hasNextPage
      }}
    }}
  }}
}}
"""

# This query is for getting details of commit history of a given repository
_COMMITS = """
{{
  repository(owner: "{owner}", name: "{name}") {{
    defaultBranchRef {{
      target {{
        ... on Commit {{
          history(
            first: 100
            {after_line}
            ) {{
            totalCount
            edges {{
              node {{
                id
                committedDate
                url
                additions
                deletions
                committer {{
                  name
                  email
                }}
              }}
            }}
            pageInfo {{
              endCursor
              hasNextPage
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""


def get_repo_discovery_query(
    term: str,
    year: int,
    per_page: int = 100,
    after: str | None = None,
    base_query: str = _REPO_DISCOVERY,
) -> str:
    """Get the GraphQL query for discovering repos."""

    after_line = f'after: "{after}"' if after else ""
    return base_query.format(
        term=term, year=year, after_line=after_line, per_page=per_page
    )


def get_stargazers_query(
    owner: str,
    name: str,
    after: str | None = None,
    base_query: str = _STARGAZERS,
) -> str:
    """Get the GraphQL query string for stargazer details."""

    after_line = f'after: "{after}"' if after else ""
    return base_query.format(owner=owner, name=name, after_line=after_line)


def get_commits_query(
    owner: str,
    name: str,
    after: str | None = None,
    base_query: str = _COMMITS,
) -> str:
    """Get the GraphQL query string for commit details."""

    after_line = f'after: "{after}"' if after else ""
    return base_query.format(owner=owner, name=name, after_line=after_line)

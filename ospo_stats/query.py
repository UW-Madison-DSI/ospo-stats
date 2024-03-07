REPO_QUERY_V0 = """
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

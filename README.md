# UW-Madison-OSPO-statistics

Some statistics on open-source projects within UW-Madison.

## Data source

- Github via GraphQL API
  - [Repository search](ospo_stats/github/query.py#L135), keywords: ["wisc.edu", "wisconsin", "madison"]
  - (Working) User search, location: [madison, wisconsin] -> all their public repos
- GitLab
  - ???

## For developers

- You need to generate a access token `GITHUB_TOKEN` to access Github public repo, see [sample.env](sample.env)
- To connect to backend database you need to setup `TURSO_AUTH_TOKEN` and `TURSO_DB_URL` in a .env file, see [sample.env](sample.env)

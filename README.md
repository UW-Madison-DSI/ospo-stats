# UW-Madison-OSPO-statistics

Some statistics on open-source projects within UW-Madison.

## Data source

- Github via GraphQL API
  - [Repository search](ospo_stats/github/query.py#L135), keywords: ["wisc.edu", "wisconsin", "madison"]
  - (Working) User search, location: [madison, wisconsin] -> all their public repos
- GitLab
  - ???

## For developers

- You need to generate a access token to public repo, see [sample](sample.env)
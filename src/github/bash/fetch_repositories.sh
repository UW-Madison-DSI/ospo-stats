 curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer <YOUR PERSONAL ACCESS TOKEN>" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "https://api.github.com/search/repositories?q=Wisconsin%20created:2024-01-01..2025-01-01"
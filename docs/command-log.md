# Command Log

- `curl -L https://github.com/thewakingsands/ffxiv-datamining-cn | head -n 40`
  - Result: Retrieved the GitHub HTML response (page content begins with `<!DOCTYPE html>` and GitHub asset links), confirming network access to the repository page.
- `git clone https://github.com/thewakingsands/ffxiv-datamining-cn.git /tmp/ffxiv-datamining-cn-test`
  - Result: Failed with HTTP 403 (RPC failed / expected flush after ref listing).

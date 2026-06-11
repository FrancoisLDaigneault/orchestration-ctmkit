#!/usr/bin/env bash
# Incrementally refresh the local (git-ignored) docs mirror — only re-fetches pages the
# server reports as modified (If-Modified-Since -> 304 = skip). Schedule via cron/systemd.
#
#   crontab:  0 6 * * 1  /home/iseeyou/workspace/orchestration-ctmkit/scripts/refresh-docs.sh
#
# Run a FULL crawl occasionally to discover brand-new pages:
#   0 6 1 * *  cd <repo> && uv run ctmkit docs crawl --out docs/reference
set -euo pipefail
cd "$(dirname "$0")/.."
uv run ctmkit docs refresh --out docs/reference

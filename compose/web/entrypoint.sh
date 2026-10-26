#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# Ensure data and cache directories exist for the single-tenant SQLite WAL and DiskCache setup
mkdir -p /app/data /app/data/cache/diskcache /app/staticfiles /app/rrss_creatos_analyzer/media

exec "$@"

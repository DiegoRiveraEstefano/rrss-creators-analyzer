#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

mkdir -p /app/data /app/data/cache/diskcache /app/rrss_creatos_analyzer/media

exec "$@"

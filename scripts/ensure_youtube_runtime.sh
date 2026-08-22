#!/usr/bin/env bash
set -euo pipefail
if command -v deno >/dev/null 2>&1; then
  deno --version
  exit 0
fi
command -v curl >/dev/null 2>&1 || { echo "curl is required to install Deno" >&2; exit 1; }
export DENO_INSTALL=/usr/local
curl -fsSL https://deno.land/install.sh | sh -s -- -y
test -x /usr/local/bin/deno
deno --version

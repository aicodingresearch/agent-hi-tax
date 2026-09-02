#!/bin/sh
# Verify every run package and confirm the committed results index still matches
# those packages.
#
# The index is refreshed on main rather than by each contribution, so a scenario
# branch is expected to fail the index step until that refresh lands.
# Contributors should run scripts/verify-packages.sh instead; this script is for
# the index refresh itself and for checking main.
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(dirname "$script_dir")
cd "$repo_root"

./scripts/verify-packages.sh
python3 scripts/build-results-index.py --check
echo "all run packages and the results index are verified"

#!/bin/sh
# Verify every run package under runs/YYYY-MM-DD/<scenario-id>/.
#
# This is the check a scenario contribution needs. It deliberately says nothing
# about the root-level results index, which is generated from these packages and
# refreshed on main rather than by each contribution; see CONTRIBUTING.md.
#
# Use scripts/verify-all.sh when the committed index should be verified too.
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(dirname "$script_dir")
cd "$repo_root"

manifests=$(
  find runs -mindepth 3 -maxdepth 3 -type f -name manifest.yaml -print |
    LC_ALL=C sort
)

if [ -z "$manifests" ]; then
  echo "no run packages found" >&2
  exit 1
fi

printf '%s\n' "$manifests" |
  while IFS= read -r manifest; do
    package_dir=${manifest%/manifest.yaml}
    ./scripts/verify-run-package.sh "$package_dir"
  done

echo "all run packages are verified"

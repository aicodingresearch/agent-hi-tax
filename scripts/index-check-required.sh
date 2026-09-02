#!/bin/sh
# Decide whether a change set has to keep the generated results index in sync.
#
# Prints "true" when `python3 scripts/build-results-index.py --check` must pass
# for the change set, and "false" when the index is allowed to lag behind the
# scenario packages because a maintainer refresh will rebuild it on main.
#
# The check is required when the change set touches an input the index is
# derived from in a way that would leave a *wrong* index rather than merely an
# incomplete one:
#
#   - the generated pages themselves;
#   - the generator, or the prompt files it links to;
#   - anything under runs/ other than a pure addition — a modified, deleted, or
#     renamed package leaves stale rows and stale links behind.
#
# Adding a new scenario package is the one path that may lag: those PRs are the
# common case, they come from forks, and forcing every open one to regenerate a
# shared file whenever another merges is what this rule exists to avoid.
#
# Usage: scripts/index-check-required.sh <base-ref> <head-ref>
set -eu

if [ $# -ne 2 ]; then
  echo "usage: $0 <base-ref> <head-ref>" >&2
  exit 2
fi

base=$1
head=$2

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(dirname "$script_dir")
cd "$repo_root"

derived_or_generator=$(
  git diff --name-only "$base" "$head" -- \
    RESULTS.md \
    RESULTS.zh-CN.md \
    scripts/build-results-index.py \
    prompts
)

# Every status except Added: modified, deleted, renamed, copied, type-changed.
runs_beyond_additions=$(
  git diff --name-only --diff-filter=MDRCT -M "$base" "$head" -- runs
)

if [ -n "$derived_or_generator" ]; then
  echo "index check required: change set touches the index, its generator, or a prompt" >&2
  printf '%s\n' "$derived_or_generator" >&2
  echo true
elif [ -n "$runs_beyond_additions" ]; then
  echo "index check required: change set alters existing run packages" >&2
  printf '%s\n' "$runs_beyond_additions" >&2
  echo true
else
  echo "index check not required: change set only adds run packages, or does not affect the index" >&2
  echo false
fi

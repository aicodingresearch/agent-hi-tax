#!/bin/sh
set -eu

package_dir=${1:-}
if [ -z "$package_dir" ]; then
  echo "usage: $0 <scenario-package-directory>" >&2
  exit 2
fi

cd "$package_dir"
repo_root=$(git rev-parse --show-toplevel 2>/dev/null || true)

required_files="manifest.yaml prompt.txt RESULTS.csv README.md SHA256SUMS"
for required_file in $required_files; do
  if [ ! -f "$required_file" ]; then
    echo "missing required file: $required_file" >&2
    exit 1
  fi
done

if command -v shasum >/dev/null 2>&1; then
  hash_file() { shasum -a 256 "$1" | awk '{print $1}'; }
  check_hashes() { shasum -a 256 -c SHA256SUMS; }
elif command -v sha256sum >/dev/null 2>&1; then
  hash_file() { sha256sum "$1" | awk '{print $1}'; }
  check_hashes() { sha256sum -c SHA256SUMS; }
else
  echo "missing SHA-256 tool: install shasum or sha256sum" >&2
  exit 2
fi

case_id=$(awk '$1 == "case_id:" {gsub(/\"/, "", $2); print $2; exit}' manifest.yaml)
declared_prompt_hash=$(awk '$1 == "sha256:" {gsub(/\"/, "", $2); print $2; exit}' manifest.yaml)
declared_prompt_bytes=$(awk '$1 == "bytes:" {gsub(/\"/, "", $2); print $2; exit}' manifest.yaml)
actual_prompt_hash=$(hash_file prompt.txt)
actual_prompt_bytes=$(wc -c < prompt.txt | tr -d ' ')

if [ -z "$case_id" ] || [ -z "$declared_prompt_hash" ] || [ -z "$declared_prompt_bytes" ]; then
  echo "manifest prompt metadata is incomplete" >&2
  exit 1
fi

if [ "$actual_prompt_hash" != "$declared_prompt_hash" ] || [ "$actual_prompt_bytes" != "$declared_prompt_bytes" ]; then
  echo "prompt.txt does not match manifest bytes/hash" >&2
  exit 1
fi

if [ -n "$repo_root" ] && [ -f "$repo_root/prompts/$case_id.txt" ]; then
  if ! cmp -s prompt.txt "$repo_root/prompts/$case_id.txt"; then
    echo "prompt.txt does not match prompts/$case_id.txt" >&2
    exit 1
  fi
fi

if [ ! -d attempts ]; then
  echo "missing attempts directory" >&2
  exit 1
fi

valid_count=0
for attempt_dir in attempts/*; do
  [ -d "$attempt_dir" ] || continue
  result_file="$attempt_dir/result.yaml"
  if [ ! -f "$result_file" ]; then
    echo "missing result.yaml: $attempt_dir" >&2
    exit 1
  fi

  if grep -Eq '^status:[[:space:]]+"?valid"?[[:space:]]*$' "$result_file"; then
    valid_count=$((valid_count + 1))
    attempt_name=$(basename "$attempt_dir")
    response_file=$(awk '$1 == "file:" {gsub(/\"/, "", $2); print $2; exit}' "$result_file")
    declared_response_hash=$(awk '$1 == "exact_text_sha256:" {gsub(/\"/, "", $2); print $2; exit}' "$result_file")

    if [ -z "$response_file" ] || [ ! -f "$attempt_dir/$response_file" ]; then
      echo "missing exact response file: $attempt_dir/$response_file" >&2
      exit 1
    fi

    actual_response_hash=$(hash_file "$attempt_dir/$response_file")
    if [ "$actual_response_hash" != "$declared_response_hash" ]; then
      echo "response hash mismatch: $attempt_dir/$response_file" >&2
      exit 1
    fi

    if ! awk -F, -v attempt="$attempt_name" '$1 == attempt && $2 == "valid" {found=1} END {exit !found}' RESULTS.csv; then
      echo "valid attempt missing from RESULTS.csv: $attempt_name" >&2
      exit 1
    fi

    input_tokens=$(awk '$1 == "input_tokens_including_cached:" {print $2; exit}' "$result_file")
    cached_tokens=$(awk '$1 == "cached_input_tokens:" {print $2; exit}' "$result_file")
    non_cached_tokens=$(awk '$1 == "non_cached_input_tokens:" {print $2; exit}' "$result_file")
    output_tokens=$(awk '$1 == "output_tokens:" {print $2; exit}' "$result_file")
    context_total=$(awk '$1 == "context_total_tokens:" {print $2; exit}' "$result_file")
    cli_total=$(awk '$1 == "cli_total_excluding_cached:" {print $2; exit}' "$result_file")

    case "$input_tokens:$cached_tokens:$non_cached_tokens:$output_tokens:$context_total:$cli_total" in
      *[!0-9:]*|'') ;;
      *)
        if [ "$non_cached_tokens" -ne $((input_tokens - cached_tokens)) ] || \
           [ "$context_total" -ne $((input_tokens + output_tokens)) ] || \
           [ "$cli_total" -ne $((non_cached_tokens + output_tokens)) ]; then
          echo "token arithmetic mismatch: $result_file" >&2
          exit 1
        fi
        ;;
    esac

    anthropic_input=$(awk '$1 == "input_tokens:" {print $2; exit}' "$result_file")
    cache_creation=$(awk '$1 == "cache_creation_input_tokens:" {print $2; exit}' "$result_file")
    cache_read=$(awk '$1 == "cache_read_input_tokens:" {print $2; exit}' "$result_file")
    total_input=$(awk '$1 == "total_input_tokens:" {print $2; exit}' "$result_file")

    if [ -n "$anthropic_input" ] && [ -n "$cache_creation" ] && \
       [ -n "$cache_read" ] && [ -n "$output_tokens" ] && \
       [ -n "$total_input" ] && [ -n "$context_total" ]; then
      case "$anthropic_input:$cache_creation:$cache_read:$output_tokens:$total_input:$context_total" in
        *[!0-9:]*) ;;
        *)
          if [ "$total_input" -ne $((anthropic_input + cache_creation + cache_read)) ] || \
             [ "$context_total" -ne $((total_input + output_tokens)) ]; then
            echo "Anthropic-style token arithmetic mismatch: $result_file" >&2
            exit 1
          fi
          ;;
      esac
    fi
  fi

  if [ -f "$attempt_dir/events.sanitized.jsonl" ] && command -v jq >/dev/null 2>&1; then
    jq -e . "$attempt_dir/events.sanitized.jsonl" >/dev/null
  fi
done

if [ "$valid_count" -lt 3 ]; then
  echo "expected at least 3 valid attempts, found $valid_count" >&2
  exit 1
fi

manifest_valid_count=$(awk '$1 == "valid_repetitions:" {print $2; exit}' manifest.yaml)
if [ "$manifest_valid_count" != "$valid_count" ]; then
  echo "manifest valid_repetitions=$manifest_valid_count but found $valid_count" >&2
  exit 1
fi

check_hashes

listed_paths=$(
  awk '{ sub(/^[^[:space:]]*[[:space:]][[:space:]]*/, ""); sub(/^\*/, ""); if ($0 != "") print }' SHA256SUMS |
    LC_ALL=C sort
)
present_paths=$(find . -type f ! -name SHA256SUMS | LC_ALL=C sort)

if [ "$present_paths" != "$listed_paths" ]; then
  extra_paths=$(printf '%s\n' "$present_paths" | grep -Fxv -e "$listed_paths" || true)
  missing_paths=$(printf '%s\n' "$listed_paths" | grep -Fxv -e "$present_paths" || true)
  if [ -n "$extra_paths" ]; then
    printf '%s\n' "$extra_paths" |
      while IFS= read -r extra_path; do
        echo "file not listed in SHA256SUMS: $extra_path" >&2
      done
  fi
  if [ -n "$missing_paths" ]; then
    printf '%s\n' "$missing_paths" |
      while IFS= read -r missing_path; do
        echo "listed in SHA256SUMS but not in the package: $missing_path" >&2
      done
  fi
  echo "SHA256SUMS does not cover the package contents: regenerate SHA256SUMS" >&2
  exit 1
fi

privacy_pattern='(/Users/[^/<[:space:]]+|[A-Za-z]:\\Users\\|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|Bearer[[:space:]]+[A-Za-z0-9._-]+|sk-[A-Za-z0-9_-]{12,}|codex[[:space:]]+resume|claude[[:space:]]+(--resume|-r)|01a[0-9a-f-]{30,}|[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})'
if command -v rg >/dev/null 2>&1; then
  if rg -n --glob '*.md' --glob '*.yaml' --glob '*.yml' --glob '*.jsonl' --glob '*.csv' --glob '*.txt' "$privacy_pattern" .; then
    echo "possible private path, email, credential, or session identifier in public text" >&2
    exit 1
  fi
else
  if grep -EnR --include='*.md' --include='*.yaml' --include='*.yml' --include='*.jsonl' --include='*.csv' --include='*.txt' "$privacy_pattern" .; then
    echo "possible private path, email, credential, or session identifier in public text" >&2
    exit 1
  fi
fi

echo "run package verified: $package_dir ($valid_count valid attempts)"

#!/bin/sh

set -euo pipefail

HASH=sha384
HASHSUM=sha384sum

mkdir -p temp

problems=$(grep -o '"https://[^"]*" integrity="[^"]*"' render.sh | while read line; do
  url=$(echo "$line" |sed 's|"\(https://[^"]*\)" .*|\1|')
  current_url=$(echo "$url" |sed -n 's|\([^@]\)@[^/]*\(/.*\)|\1\2|p')
  filename=$(basename "$url")
  if [ -z "$current_url" ]; then
    echo "$url is not versioned."
  else
    rm -f "temp/versioned-$filename" "temp/current-$filename"
    curl --fail -o "temp/versioned-$filename" -- "$url" 2>/dev/null
    curl --fail -o "temp/current-$filename" -- "$current_url" 2>/dev/null

    if [ ! -f "temp/versioned-$filename" ]; then
      echo "$url could not be downloaded."
    else
      if [ ! -f "temp/current-$filename" ]; then
        echo "$current_url could not be downloaded."
      elif ! diff -q --binary "temp/versioned-$filename" "temp/current-$filename" >/dev/null; then
        echo "$url is not the current version (it does not match $current_url)."
      fi

      # Check the hash regardless of whether it is the current version.
      given=$(echo "$line" |sed -n 's|"[^"]*" integrity="'"$HASH"'-\([^"]*\)"|\1|p')
      if [ -z "$given" ]; then
        echo "No integrity field found in: $line"
      else
        calculated=$($HASHSUM -b "temp/versioned-$filename" |sed 's|\([^ ]*\).*|\1|' |xxd -p -r |base64)
        if [ "$given" != "$calculated" ]; then
          echo "Given integrity hash '$HASH-$given' for $url does not match calculated hash '$HASH-$calculated'."
        fi
      fi
    fi
  fi
done)

if [ -n "$problems" ]; then
  echo "Problems found:"
  echo "$problems"
  exit 1
else
  echo "No problems detected."
  rm -f "temp/versioned-*" "temp/current-*"
  rmdir --ignore-fail-on-non-empty temp
fi

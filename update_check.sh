#!/bin/bash

set -euo pipefail

HASH=sha384

# Calculate the SHA-384 Subresource Integrity (SRI) digest of the given file.
# See <https://www.srihash.org/> and <https://www.w3.org/TR/sri/>.
sridigest() {
  echo "$HASH-$(${HASH}sum -b "$1" |sed 's|\([^ ]*\).*|\1|' |xxd -p -r |base64)"
}

download() {
  # --fail: Fail with error code 22 and with no output for HTTP transfers returning response codes at 400 or greater.
  curl --fail --silent -o "$1" -- "$2"
}

# Relevant lines are those in `render.sh` containing '="https://..."...>'.
# Each dependency must be on a separate line. If a URL should not be checked as a dependency,
# break it up like this: 'https''://' .
#
# We check that:
#  * each relevant line contains (in this order) '="<url>" integrity="<digest>" crossorigin="anonymous"';
#  * <url> is versioned (contains '@.../');
#  * the contents of <url> match those of the corresponding unversioned URL without '@...';
#  * <digest> is a correctly prefixed and base64-encoded $HASH SRI digest of the contents.
#
# There are a number of ways these checks could be insufficient; they don't replace review of `render.sh`.

mkdir -p temp

problems=$(grep -o '="https://[^"]*"[^>]*>' render.sh | while read line; do
  # Output problems to stdout, and warnings to temp/.warnings.txt

  url=$(echo "$line" |sed 's|="\(https://[^"]*\)".*|\1|')
  current_url=$(echo "$url" |sed -n 's|\([^@]\)@[^/]*\(/.*\)|\1\2|p')
  filename=$(basename "$url")
  referenced="temp/${filename}_referenced"
  current="temp/${filename}_current"

  rm -f "$referenced" "$current"
  # We do this first so that the loop over temp/* below can print the SRI digest (if the file can be downloaded).
  download "$referenced" "$url"

  if [ -z "$current_url" ]; then
    echo "::error:: $url is not versioned."
  elif [ ! -f "$referenced" ]; then
    echo "::error:: $url could not be downloaded."
  else
    download "$current" "$current_url"

    maybe_delete=0
    if [ ! -f "$current" ]; then
      echo "::warning:: $current_url could not be downloaded." >>temp/.warnings.txt
    elif ! diff -q --binary "$referenced" "$current" >/dev/null; then
      echo "::warning:: $url is not the current version (it does not match $current_url)." >>temp/.warnings.txt
    else
      maybe_delete=1
    fi

    # Check the SRI digest regardless of whether it is the current version.
    given=$(echo "$line" |sed -n 's|="https://[^"]*" integrity="\([^"]*\)" crossorigin="anonymous".*|\1|p')
    if [ -z "$given" ]; then
      echo "::error:: Did not find 'integrity="..." crossorigin="anonymous"' in: $line"
    else
      calculated=$(sridigest "$referenced")
      if [ "$given" != "$calculated" ]; then
        echo "::error:: Given SRI digest '$given' for $url does not match calculated digest '$calculated'."
      elif [ $maybe_delete -eq 1 ]; then
        rm -f "$referenced" "$current"
      fi
    fi
  fi
done)
warnings=$(<temp/.warnings.txt)
rm -f temp/.warnings.txt

# Exit with 1 if only warnings, 2 if there are any problems.
exitcode=0
if [ -n "$problems" ]; then
  echo "Problems found:"
  echo "$problems"
  echo ""
fi
if [ -n "$warnings" ]; then
  echo "Warnings found:"
  echo "$warnings"
  echo ""
  exitcode=1
fi
if [ -n "$problems" ]; then exitcode=2; fi
if [ "$exitcode" -gt 0 ]; then
  echo "The relevant SRI digests and files are:"
  for f in temp/*; do
    if [ -f "$f" ]; then echo "  $(sridigest $f)  $f"; fi
  done
  exit $exitcode
else
  echo "No problems or warnings detected."
  # All of the downloaded files should have been deleted.
  rmdir temp
fi

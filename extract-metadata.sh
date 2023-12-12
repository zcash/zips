#!/bin/bash
#
# Parse all `zip-*.rst` file for header metadata.
#
# # Output Format:
#
# This outputs a single JSON object. Each key is the basename of a
# `zip-*.rst` file, and value is a JSON object containing the ZIP metadata
# fields.
#
# The ZIP metadata values are strings for single-line values, or JSON
# arrays of strings for each line in a multi-line value.
#
# # Input Format:
#
# This is a sensitive line-noise unix pipeline that REQUIRES zip rst
# files to follow this format:
#
# - The metadata must occur before the first alphabetic character on column 1.
# - The metadata keys must occur in column 3, after two spaces.
# - Metadata keys must be immediately followed by ": ".
# - Multi-line metadata values must be in continuation lines with the
#   first non-space character occurring after column 3.
#
# Integration testing:
#
# Run `./extract-metadata.sh  | jq > /dev/null` and verify there's no
# stderr and it has a 0 exit status. This indicates the script completed
# successfully and the result is valid JSON.

set -euo pipefail

ZIPSDIR="$(dirname "$(readlink -f "$0")")"

# Whether or not to emit a comma to separate the previous zip entry:
OPTCOMMA='' #

echo '{'
for ziprst in $(find "$ZIPSDIR" -type f -name 'zip-*.rst')
do
  echo "${OPTCOMMA}"
  OPTCOMMA=','

  echo "  \"$(basename "$ziprst")\": {"
  < "$ziprst" \
    sed -n '/^ /p; /^[A-Za-z]/q' | \
    tr '\n' '|' | \
    sed 's/^  //; s/|  /|/g; s/|  */", "/g' | \
    tr '|' '\n' | \
    sed 's/^\([^:]*\): *\(.*\)$/"\1": ["\2"],/g; s/^/    /; $s/,$//' | \
    sed '/\[".*", ".*\]/s/\["/[\n      "/g' | \
    sed 's/", "/",\n      "/g; s/^      \(".*"\)\(\],*\)/      \1\n    \2/; s/: \[\("[^"]*"\)\]/: \1/'
  echo -n "  }"
done
echo '}'

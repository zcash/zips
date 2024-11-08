#!/bin/sh

# These are basic regexps so \+ is needed, not +.
# We use the Unicode 💲 character to move an escaped $ out of the way,
# which is much easier than trying to handle escapes within a capture;
# I don't even know if the latter is possible.

sed 's|[\][$]|💲|g' "$1" | sed 's|[$]\([^$]\+\)[$]|:math:`\1`|g' | sed 's|💲|$|g'

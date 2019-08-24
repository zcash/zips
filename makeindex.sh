#!/bin/sh

cat <<EndOfHeader

Index of ZIPs
-------------

| ZIP | Title | Status |
|-----|-------|--------|
EndOfHeader
for zipfile in *.rst; do
  if grep -E '^\s*Status:\s*(Withdrawn|Rejected|Obsolete)' $zipfile >/dev/null; then
    echo "| ~`basename $zipfile .rst | sed -r 's@zip-0{0,3}@@'`~ | ~[`grep '^\s*Title:' $zipfile | sed 's@\s*Title:\s*@@'`](`basename $zipfile .rst`)~ | `grep '^\s*Status:' $zipfile | sed 's@\s*Status:\s*@@'` |"
  else
    echo "| `basename $zipfile .rst | sed -r 's@zip-0{0,3}@@'` | [`grep '^\s*Title:' $zipfile | sed 's@\s*Title:\s*@@'`](`basename $zipfile .rst`) | `grep '^\s*Status:' $zipfile | sed 's@\s*Status:\s*@@'` |"
  fi
done


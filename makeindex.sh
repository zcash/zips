#!/bin/sh

cat <<EndOfHeader

Index of ZIPs
-------------

EndOfHeader
for zipfile in *.rst; do
  echo "* [`basename $zipfile .rst | sed -r 's|zip-0{0,3}|ZIP |'`: `grep '^\s*Title: ' $zipfile | sed 's|\s*Title: ||'`](`basename $zipfile .rst`)"
done


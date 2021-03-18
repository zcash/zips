#!/bin/sh

cat <<EndOfHeader

Index of ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
EndOfHeader
for zipfile in zip-*.rst; do
  echo Adding $zipfile to index. >/dev/stderr
  if grep -E '^\s*Status:\s*Reserved' $zipfile >/dev/null; then
    echo "    <tr> <td><span class=\"reserved\">`basename $zipfile .rst | sed -E 's@zip-0{0,3}@@'`</span></td> <td class=\"left\"><a class=\"reserved\" href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  elif grep -E '^\s*Status:\s*(Withdrawn|Rejected|Obsolete)' $zipfile >/dev/null; then
    echo "    <tr> <td><strike>`basename $zipfile .rst | sed -E 's@zip-0{0,3}@@'`</strike></td> <td class=\"left\"><strike><a href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></strike></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  else
    echo "    <tr> <td>`basename $zipfile .rst | sed -E 's@zip-0{0,3}@@'`</td> <td class=\"left\"><a href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  fi
done
echo "  </table></embed>"

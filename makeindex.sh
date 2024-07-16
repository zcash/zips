#!/bin/sh

cat <<EndOfHeader

Index of ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
EndOfHeader
for zipfile in $(cat .zipfilelist.current); do
  echo Adding $zipfile to index. >/dev/stderr
  if grep -E '^\s*Status:\s*Reserved' $zipfile >/dev/null; then
    echo "    <tr> <td><span class=\"reserved\">`basename $(basename $zipfile .rst) .md | sed -E 's@zip-0{0,3}@@'`</span></td> <td class=\"left\"><a class=\"reserved\" href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  elif grep -E '^\s*Status:\s*(Withdrawn|Rejected|Obsolete)' $zipfile >/dev/null; then
    echo "    <tr> <td><strike>`basename $(basename $zipfile .rst) .md | sed -E 's@zip-0{0,3}@@'`</strike></td> <td class=\"left\"><strike><a href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></strike></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  else
    echo "    <tr> <td>`basename $(basename $zipfile .rst) .md | sed -E 's@zip-0{0,3}@@'`</td> <td class=\"left\"><a href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  fi
done
echo "  </table></embed>"

if [ $(wc -c <.draftfilelist.current) -gt 1 ]
then
  cat <<EndOfDraftHeader

Drafts without assigned ZIP numbers
-----------------------------------

These are works-in-progress, and may never be assigned ZIP numbers if their
ideas become obsoleted or abandoned. Do not assume that these drafts will exist
in perpetuity; instead assume that they will either move to a numbered ZIP, or
be deleted.

.. raw:: html

  <embed><table>
    <tr> <th>Title</th> </tr>
EndOfDraftHeader
  for draftfile in $(cat .draftfilelist.current); do
    echo Adding $draftfile to index of drafts. >/dev/stderr
    echo "    <tr> <td class=\"left\"><a href=\"`echo $draftfile`\">`grep '^\s*Title:' $draftfile | sed -E 's@\s*Title:\s*@@'`</a></td>"
  done
  echo "  </table></embed>"
fi

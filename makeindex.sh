#!/bin/sh

cat <<EndOfHeader

Released ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
EndOfHeader
for zipfile in $(cat .zipfilelist.current); do
  zipfile=zips/$zipfile
  if grep -E '^\s*Status:\s*(Reserved|Draft|Withdrawn|Rejected|Obsolete)' $zipfile >/dev/null; then
    # Handled below.
    true
  else
    echo Adding $zipfile to released index. >/dev/stderr
    echo "    <tr> <td>`basename $(basename $zipfile .rst) .md | sed -E 's@zip-0{0,3}@@'`</td> <td class=\"left\"><a href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  fi
done
cat <<EndOfDraftZipHeader
  </table></embed>

Draft ZIPs
----------

These are works-in-progress that have been assigned ZIP numbers. These will
eventually become either Proposed (and thus Released), or one of Withdrawn,
Rejected, or Obsolete.

In some cases a ZIP number is reserved by the ZIP Editors before a draft is
written.

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
EndOfDraftZipHeader
for zipfile in $(cat .zipfilelist.current); do
  zipfile=zips/$zipfile
  if grep -E '^\s*Status:\s*Reserved' $zipfile >/dev/null; then
    echo Adding $zipfile to draft index. >/dev/stderr
    echo "    <tr> <td><span class=\"reserved\">`basename $(basename $zipfile .rst) .md | sed -E 's@zip-0{0,3}@@'`</span></td> <td class=\"left\"><a class=\"reserved\" href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  elif grep -E '^\s*Status:\s*Draft' $zipfile >/dev/null; then
    echo Adding $zipfile to draft index. >/dev/stderr
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
    draftfile=zips/$draftfile
    echo Adding $draftfile to index of drafts. >/dev/stderr
    echo "    <tr> <td class=\"left\"><a href=\"`echo $draftfile`\">`grep '^\s*Title:' $draftfile | sed -E 's@\s*Title:\s*@@'`</a></td>"
  done
  echo "  </table></embed>"
fi

cat <<EndOfStrikeHeader

Withdrawn, Rejected, or Obsolete ZIPs
-------------------------------------

.. raw:: html

  <details>
  <summary>Click to show/hide</summary>
  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
EndOfStrikeHeader
for zipfile in $(cat .zipfilelist.current); do
  zipfile=zips/$zipfile
  if grep -E '^\s*Status:\s*(Withdrawn|Rejected|Obsolete)' $zipfile >/dev/null; then
    echo Adding $zipfile to struck index. >/dev/stderr
    echo "    <tr> <td><strike>`basename $(basename $zipfile .rst) .md | sed -E 's@zip-0{0,3}@@'`</strike></td> <td class=\"left\"><strike><a href=\"`echo $zipfile`\">`grep '^\s*Title:' $zipfile | sed -E 's@\s*Title:\s*@@'`</a></strike></td> <td>`grep '^\s*Status:' $zipfile | sed -E 's@\s*Status:\s*@@'`</td>"
  fi
done

cat <<EndOfIndexHeader
  </table></embed>
  </details>

Index of ZIPs
-------------

.. raw:: html

  <embed><table>
    <tr> <th>ZIP</th> <th>Title</th> <th>Status</th> </tr>
EndOfIndexHeader
for zipfile in $(cat .zipfilelist.current); do
  zipfile=zips/$zipfile
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

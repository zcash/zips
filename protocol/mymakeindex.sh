#!/bin/sh
set -e
makeindex $*

# We want to change things like:
#                \hyperindexformat{\definingstyle}{17},
#                \hyperindexformat{\normalstyle}{17},
# to just
#                \hyperindexformat{\definingstyle}{17},
#
# and change:
#                \hyperindexformat{\definingstyle}{17},
#                \hyperindexformat{\normalstyle}{17, 18},
# to
#                \hyperindexformat{\definingstyle}{17},
#                \hyperindexformat{\normalstyle}{18},
#
# and change:
#                \hyperindexformat{\definingstyle}{17},
#                \hyperindexformat{\normalstyle}{17--19},
# to
#                \hyperindexformat{\definingstyle}{17},
#                \hyperindexformat{\normalstyle}{\increment{17}--19},

echo Postprocessing index file "$2"...
perl -i.original -p0e 's/(?s)(\\hyperindexformat[{]\\definingstyle[}][{])(\d+)[}],\s*.\s*\\hyperindexformat[{]\\normalstyle[}][{]\2[}]/\1\2}/sg' "$2"
perl -i -p0e 's/(?s)(\\hyperindexformat[{]\\definingstyle[}][{])(\d+)([}],\s*.\s*\\hyperindexformat[{]\\normalstyle[}][{])\2,\s*([\d,-\s]+[}])/\1\2\3\4/sg' "$2"
perl -i -p0e 's/(?s)(\\hyperindexformat[{]\\definingstyle[}][{])(\d+)([}],\s*.\s*\\hyperindexformat[{]\\normalstyle[}][{])\2--([\d,-\s]+[}])/\1\2\3\\increment{\2}--\4/sg' "$2"
#diff --context=3 "$2.original" "$2"

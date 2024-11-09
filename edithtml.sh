#!/bin/sh

if ! ( ( [ "x$1" = "x--rst" ] && [ $# -eq 2 ] ) || ( [ "x$1" = "x--md" ] && [ $# -eq 3 ] ) ); then
    echo "Usage: edithtml.sh --rst <htmlfile>"
    echo "   or: edithtml.sh --md <htmlfile> <title>"
    exit
fi

if ! [ -f "$2" ]; then
    echo File not found: "$2"
    exit
fi

Math1='<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">'
Math2='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>'
Math3='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous" onload="renderMathInElement(document.body);"></script>'
ViewAndStyle='<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css">'

if [ "x$1" = "x--rst" ]; then
    sed -i.sedbak "s|<script src=\"http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML\"></script>|${Math1}\n    ${Math2}\n    ${Math3}|" $2
    sed -i.sedbak "s|</head>|${ViewAndStyle}</head>|" $2
else
    cat - >"$2".prefix <<EndOfMdInitial
<!DOCTYPE html>
<html>
<head>
    <title>$3</title>
    <meta charset="utf-8" />
EndOfMdInitial
    if grep -q -E 'class="math( inline)?"' "$2"; then
        cat - >>"$2.prefix" <<EndOfMathSupport
    ${Math1}
    ${Math2}
    ${Math3}
EndOfMathSupport
    fi
    cat - "$2" >>"$2".prefix <<EndOfStyle
    ${ViewAndStyle}
</head>
<body>
EndOfStyle
    cat "$2.prefix" - >"$2" <<EndOfTrailer
</body>
</html>
EndOfTrailer
    rm -f "$2".prefix
fi

sed -i.sedbak 's|<a href="[^":]*">Protocol Specification</a>|<span class="lightmode"><a href="https://zips.z.cash/protocol/protocol.pdf">Protocol Specification</a></span>|g' "$2"
sed -i.sedbak 's|\s*<a href="[^":]*">(dark mode version)</a>|<span class="darkmode" style="display: none;"><a href="https://zips.z.cash/protocol/protocol-dark.pdf">Protocol Specification</a></span>|g' "$2"

sed -i.sedbak 's|<a \(class=[^ ]* \)*href="\([^":]*\)\.rst\(\#[^"]*\)*">|<a \1href="\2\3">|g' "$2"
sed -i.sedbak 's|<a \(class=[^ ]* \)*href="\([^":]*\)\.md\(\#[^"]*\)*">|<a \1href="\2\3">|g' "$2"
sed -i.sedbak 's|&lt;\(https:[^&]*\)&gt;|\&lt;<a href="\1">\1</a>\&gt;|g' "$2"

sed -i.sedbak 's|src="../rendered/|src="|g' "$2"
sed -i.sedbak 's|<a href="rendered/|<a href="|g' "$2"
sed -i.sedbak 's|<a \(class=[^ ]* \)*href="zips/|<a \1href="|g' "$2"

perl -i.sedbak -p0e 's|<section id="([^"]*)">\s*.?\s*<h([1-9])>([^<]*(?:<code>[^<]*</code>[^<]*)?)</h([1-9])>|<section id="\1"><h\2><span class="section-heading">\3</span><span class="section-anchor"> <a rel="bookmark" href="#\1"><img width="24" height="24" class="section-anchor" src="assets/images/section-anchor.png" alt=""></a></span></h\4>|g' "$2"

rm -f rendered/*.sedbak

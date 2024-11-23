#!/bin/bash

set -euo pipefail

if ! ( ( [ "x$1" = "x--rst" ] || [ "x$1" = "x--pandoc" ] || [ "x$1" = "x--mmd" ] ) && [ $# -eq 3 ] ); then
    cat - <<EndOfUsage
Usage: render.sh --rst|--pandoc|--mmd <inputfile> <htmlfile> <title>

--rst     render reStructuredText using rst2html5
--pandoc  render Markdown using pandoc
--mmd     render Markdown using multimarkdown
EndOfUsage
    exit
fi

inputfile="$2"
outputfile="$3"

if ! [ -f "${inputfile}" ]; then
    echo "File not found: ${inputfile}"
    exit
fi

if [ "x$1" = "x--rst" ]; then
    filetype='.rst'
else
    filetype='.md'
fi
title="$(basename -s ${filetype} ${inputfile} | sed -E 's|zip-0{0,3}|ZIP |; s|draft-|Draft |')$(grep -E '^(\.\.)?\s*Title: ' ${inputfile} |sed -E 's|.*Title||')"
echo "    ${title}"

Math1='<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" integrity="sha384-nB0miv6/jRmo5UMMR1wu3Gz6NLsoTkbqJghGIsx//Rlm+ZU03BU6SQNC66uf4l5+" crossorigin="anonymous">'
Math2='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js" integrity="sha384-7zkQWkzuo3B5mTepMUcHkMB5jZaolc2xDwL6VFqjFALcbeS9Ggm/Yr2r3Dy4lfFg" crossorigin="anonymous"></script>'
Math3='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js" integrity="sha384-43gviWU0YVjaDtb/GhzOouOXtZMP/7XUzwPTstBeZFe/+rCMvRwr4yROQP43s0Xk" crossorigin="anonymous" onload="renderMathInElement(document.body);"></script>'
ViewAndStyle='<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css">'

cat <(
    if [ "x$1" = "x--rst" ]; then
        # These are basic regexps so \+ is needed, not +.
        # We use the Unicode 💲 character to move an escaped $ out of the way,
        # which is much easier than trying to handle escapes within a capture.

        cat "${inputfile}" \
        | sed 's|[\][$]|💲|g;
               s|[$]\([^$]\+\)[$]\([.,:;!?)-]\)|:math:`\1\\!`\2|g;
               s|[$]\([^$]\+\)[$]|:math:`\1`|g;
               s|💲|$|g' \
        | rst2html5 -v --title="${title}" - \
        | sed "s|<script src=\"http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML\"></script>|${Math1}\n    ${Math2}\n    ${Math3}|;
               s|</head>|${ViewAndStyle}</head>|"
    else
        if [ "x$1" = "x--pandoc" ]; then
            # Not actually MathJax. KaTeX is compatible if we use the right headers.
            pandoc --mathjax --from=markdown --to=html "${inputfile}" --output="${outputfile}.temp"
        else
            multimarkdown ${inputfile} -o "${outputfile}.temp"
        fi

        # Both pandoc and multimarkdown just output the HTML body.
        echo "<!DOCTYPE html>"
        echo "<html>"
        echo "<head>"
        echo "    <title>${title}</title>"
        echo "    <meta charset=\"utf-8\" />"
        if grep -q -E 'class="math( inline)?"' "${outputfile}.temp"; then
            echo "    ${Math1}"
            echo "    ${Math2}"
            echo "    ${Math3}"
        fi
        echo "    ${ViewAndStyle}"
        echo "</head>"
        echo "<body>"
        cat "${outputfile}.temp"
        rm -f "${outputfile}.temp"
        echo "</body>"
        echo "</html>"
    fi
) \
| sed \
's|<a href="[^":]*">Protocol Specification</a>|<span class="lightmode"><a href="https://zips.z.cash/protocol/protocol.pdf">Protocol Specification</a></span>|g;
 s|\s*<a href="[^":]*">(dark mode version)</a>|<span class="darkmode" style="display: none;"><a href="https://zips.z.cash/protocol/protocol-dark.pdf">Protocol Specification</a></span>|g;
 s|<a \(class=[^ ]* \)*href="\([^":]*\)\.rst\(\#[^"]*\)*">|<a \1href="\2\3">|g;
 s|<a \(class=[^ ]* \)*href="\([^":]*\)\.md\(\#[^"]*\)*">|<a \1href="\2\3">|g;
 s|&lt;\(https:[^&]*\)&gt;|\&lt;<a href="\1">\1</a>\&gt;|g;
 s|src="../rendered/|src="|g;
 s|<a href="rendered/|<a href="|g;
 s|<a \(class=[^ ]* \)*href="zips/|<a \1href="|g' \
| perl -p0e \
's|<section id="([^"]*)">\s*.?\s*<h([1-9])>([^<]*(?:<code>[^<]*</code>[^<]*)?)</h([1-9])>|<section id="\1"><h\2><span class="section-heading">\3</span><span class="section-anchor"> <a rel="bookmark" href="#\1"><img width="24" height="24" class="section-anchor" src="assets/images/section-anchor.png" alt=""></a></span></h\4>|g;
 s|<h([1-9]) id="([^"]*)">([^<]*(?:<code>[^<]*</code>[^<]*)?)</h([1-9])>|<h\1 id="\2"><span class="section-heading">\3</span><span class="section-anchor"> <a rel="bookmark" href="#\2"><img width="24" height="24" class="section-anchor" src="assets/images/section-anchor.png" alt=""></a></span></h\4>|g;' \
> "${outputfile}"

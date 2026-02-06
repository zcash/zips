#!/bin/bash

# If a URL in this script should not be checked as a dependency by `update_check.sh`,
# break it up like this: 'https''://' .

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

Math1='<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.28/dist/katex.min.css" integrity="sha384-Wsr4Nh3yrvMf2KCebJchRJoVo1gTU6kcP05uRSh5NV3sj9+a8IomuJoQzf3sMq4T" crossorigin="anonymous">'
Math2='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.28/dist/katex.min.js" integrity="sha384-+W9OcrYK2/bD7BmUAk+xeFAyKp0QjyRQUCxeU31dfyTt/FrPsUgaBTLLkVf33qWt" crossorigin="anonymous"></script>'
Math3='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.28/dist/contrib/auto-render.min.js" integrity="sha384-hCXGrW6PitJEwbkoStFjeJxv+fSOOQKOPbJxSfM6G5sWZjAyWhXiTIIAmQqnlLlh" crossorigin="anonymous" onload="renderMathInElement(document.body);"></script>'

Mermaid='<script defer src="https://cdn.jsdelivr.net/npm/mermaid@11.12.2/dist/mermaid.min.js" integrity="sha384-1ggI9FC3CkghppRD/XCR4aD+jp4DxwXlJIW0wxhyTLNKuiZEW3c4BwcjKXl0iVAJ" crossorigin="anonymous" onload="mermaid.initialize({ startOnLoad: true });"></script>'

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
        echo "    ${ViewAndStyle}"
        if grep -q -E 'class="mermaid"' "${outputfile}.temp"; then
            echo "    ${Mermaid}"
        fi
        if grep -q -E 'class="math( inline)?"' "${outputfile}.temp"; then
            echo "    ${Math1}"
            echo "    ${Math2}"
            echo "    ${Math3}"
        fi
        echo "</head>"
        echo "<body>"
        cat "${outputfile}.temp"
        rm -f "${outputfile}.temp"
        echo "</body>"
        echo "</html>"
    fi
) \
| sed \
's|<a href="[^":]*">Protocol Specification</a>|<span class="lightmode"><a href="https''://zips.z.cash/protocol/protocol.pdf">Protocol Specification</a></span>|g;
 s|\s*<a href="[^":]*">(dark mode version)</a>|<span class="darkmode" style="display: none;"><a href="https''://zips.z.cash/protocol/protocol-dark.pdf">Protocol Specification</a></span>|g;
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

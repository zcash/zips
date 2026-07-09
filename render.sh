#!/bin/bash

# If a URL in this script should not be checked as a dependency by `update_check.sh`,
# break it up like this: 'https''://' .

set -euo pipefail

if ! ( [ $# -eq 3 ] && ( [ "x$1" = "x--rst" ] || [ "x$1" = "x--pandoc" ] || [ "x$1" = "x--mmd" ] ) ); then
    cat - <<EndOfUsage
Usage: render.sh --rst|--pandoc|--mmd <inputfile> <htmlfile>

--rst     render reStructuredText using rst2html5
--pandoc  render Markdown using pandoc
--mmd     render Markdown using multimarkdown
EndOfUsage
    exit
fi

# This script embeds non-ASCII UTF-8 characters in its sed programs and processes
# UTF-8 input, so running under a non-UTF-8 locale would silently corrupt the output.
# Fail loudly instead of emitting mojibake. `locale charmap` reports the effective
# character map (UTF-8 on a UTF-8 locale; US-ASCII / ANSI_X3.4-1968 under C / POSIX).
# Note: macOS has no real C.UTF-8 locale, so there `locale charmap` reports US-ASCII
# for it; C.UTF-8 is thus rejected on macOS (correctly, it is unusable there) and
# accepted on Linux (where it genuinely is UTF-8).
charmap="$(locale charmap 2>/dev/null || true)"
case "${charmap}" in
    UTF-8|UTF8|utf-8|utf8) ;;
    *)
        # Suggest a UTF-8 locale in the current language when we can read it from
        # LANG, else fall back to en_US. C / POSIX have no usable .UTF-8 form (on
        # macOS even C.UTF-8 is really US-ASCII), so do not propose them.
        lang="$(locale 2>/dev/null | sed -n 's/^LANG=//p' | tr -d '"' | cut -d. -f1)"
        case "${lang}" in ''|C|POSIX) lang=en_US ;; esac
        echo "render.sh: a UTF-8 locale is required, but the current character map is" >&2
        echo "'${charmap:-unknown}'. Set a UTF-8 locale (e.g. LANG=${lang}.UTF-8) and retry." >&2
        exit 1
        ;;
esac

inputfile="$2"
outputfile="$3"
mkdir -p "$(dirname "${outputfile}")"

if ! [ -f "${inputfile}" ]; then
    echo "File not found: ${inputfile}"
    exit
fi

# Set RENDER_INTERMEDIATE to a path to capture the post-sed, pre-renderer stream
# (used by the render regression tests; see test/). Defaults to /dev/null, so normal
# runs are unaffected and the `tee` below is a harmless pass-through.
intermediate="${RENDER_INTERMEDIATE:-/dev/null}"

if [ "x$1" = "x--rst" ]; then
    filetype='.rst'
else
    filetype='.md'
fi
title="$(basename -s ${filetype} ${inputfile} | sed -E 's|zip-0{0,3}|ZIP |; s|draft-|Draft |')$(grep -E '^(\.\.)?\s*Title: ' ${inputfile} |sed -E 's|.*Title||')"
echo "    ${title}"

Math1='<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.33/dist/katex.min.css" integrity="sha384-fgYS3VC1089n2J3rVcEbXDHlnDLQ9B2Y1hvpQ720q1NvxCduQqT4JoGc4u2QCnzE" crossorigin="anonymous">'
Math2='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.33/dist/katex.min.js" integrity="sha384-YPHNAPyrxGS8BNnA7Q4ommqra8WQPEjooVSLzFgwgs8OXJBvadbyvx4QpfiFurGr" crossorigin="anonymous"></script>'
Math3='<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.33/dist/contrib/auto-render.min.js" integrity="sha384-JKXHIJf8PKPyDFptuKZoUyMRQJAmQKj4B4xyOca62ebJhciMYGiDdq/9twUUWyZH" crossorigin="anonymous" onload="renderMathInElement(document.body);"></script>'

Mermaid='<script defer src="https://cdn.jsdelivr.net/npm/mermaid@11.12.3/dist/mermaid.min.js" integrity="sha384-jFhLSLFn4m565eRAS0CDMWubMqOtfZWWbE8kqgGdU+VHbJ3B2G/4X8u+0BM8MtdU" crossorigin="anonymous" onload="mermaid.initialize({ startOnLoad: true });"></script>'

# Our `style.css` must load *after* KaTeX's CSS so that our `.katex .*` overrides win the
# cascade (several KaTeX font rules have the same specificity as ours). Both paths inject
# `ViewAndStyle` at the end of `<head>`, so our stylesheet always loads last. (Unlike
# `<meta charset>`, the viewport meta has no early-placement requirement.)
ViewAndStyle='<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css">'

cat <(
    # These are basic regexps so \+ is needed, not +, and similarly for \?.
    # We use the Unicode 💲 character to move an escaped $ out of the way,
    # which is much easier than trying to handle escapes within a capture.
    # In both rst and Markdown, we must be careful not to rewrite a math span
    # so that it has a non-whitespace character immediately after it.
    #
    # PORTABILITY: bash 3.2 (the macOS system /bin/bash) mis-parses an apostrophe
    # in a comment inside this process substitution as an opening quote, then
    # scans to end-of-file (an "unexpected EOF" quote-matching error). Keep the
    # comments in this cat <(...) block free of apostrophes; reword to avoid them.

    if [ "x$1" = "x--rst" ]; then
        # For rst we want to unescape `\$`, because $ is not reserved without our $ extension.
        cat "${inputfile}" |
          sed 's|[\][$]|💲|g;
               s|[$]\([^$]\+\)[$]\([—)-]\)|:math:`\1\\kern-0.15em` \2|g;
               s|[$]\([^$]\+\)[$]\([.,:;!?]\)$|:math:`\1\\kern-0.03em\\textsf{\2}`|g;
               s|[$]\([^$]\+\)[$]\([.,:;!?]\)\ |:math:`\1\\kern-0.03em\\textsf{\2}` |g;
               s|[$]\([^$]\+\)[$]|:math:`\1`|g;
               s|💲|$|g' |
          tee "${intermediate}" |
          rst2html5 -v --title="${title}" - |
          sed "s|<script src=\"http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML\"></script>|${Math1}\n    ${Math2}\n    ${Math3}|;
               s|</head>|${ViewAndStyle}</head>|"
    else
        if [ "x$1" = "x--pandoc" ]; then
            # Not actually MathJax. KaTeX is compatible if we use the right headers.
            pandoc --mathjax --from=markdown --to=html "${inputfile}" --output="${outputfile}.temp"
        else
            # For Markdown we just want to protect `\$`.
            # We match a whole `$...$` span (as the rst rules above do), so we only
            # ever rewrite a *closing* delimiter. Matching a lone `$` would misfire
            # on the *opening* `$` of a span whose content starts with punctuation
            # (e.g. `$-x$`). Caveat: this is line-by-line, so a multi-line `$...$`
            # span (which Markdown allows) is not matched. Punctuation just after
            # such a span will not be fixed, and a line carrying both the close of
            # one span and the open of another can still mismatch. These cases are
            # rare, would show up when reviewing rendered output, and are easy to
            # work around.
            cat "${inputfile}" |
              sed 's|[\][$]|💲|g;
                   s|[$]\([^$]\+\)[$]\([—)-]\)|$\1\\kern-0.15em$ \2|g;
                   s|[$]\([^$]\+\)[$]\([.,:;!?]\)$|$\1\\kern-0.05em\\textsf{\2}$|g;
                   s|[$]\([^$]\+\)[$]\([.,:;!?]\)\ |$\1\\kern-0.05em\\textsf{\2}$ |g;
                   s|💲|\\$|g' |
              tee "${intermediate}" |
              multimarkdown -o "${outputfile}.temp"
        fi

        # Both pandoc and multimarkdown just output the HTML body.
        echo "<!DOCTYPE html>"
        echo "<html>"
        echo "<head>"
        echo "    <title>${title}</title>"
        echo "    <meta charset=\"utf-8\" />"
        if grep -q -E 'class="mermaid"' "${outputfile}.temp"; then
            echo "    ${Mermaid}"
        fi
        if grep -q -E 'class="math( inline)?"' "${outputfile}.temp"; then
            echo "    ${Math1}"
            echo "    ${Math2}"
            echo "    ${Math3}"
        fi
        # ViewAndStyle last, so our `style.css` loads after the KaTeX CSS (as in rst).
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

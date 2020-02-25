#!/bin/sh

sed -i.sedbak 's|</head>|<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css"></head>|' $@
sed -i.sedbak 's|<a href="\([^":]*\).rst">|<a href="\1">|g' $@
sed -i.sedbak 's|http://cdn.mathjax.org/mathjax/latest/MathJax.js|https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js|' $@

# First put <section id="..."> and <hN>...</hN> on the same line. <https://unix.stackexchange.com/a/337399/82702>
sed -i.sedbak -n '$!N;s|<section id="\([^"]*\)">\s*\n\s*<h|<section id="\1"><h|;P;D' $@

sed -i.sedbak 's|<section id="\([^"]*\)"><h\([1-9]\)>\([^<]*\)</h\([1-9]\)>|<section id="\1"><h\2><span class="section-heading">\3</span><span class="section-anchor"> <a href="#\1"><img width="24" height="24" src="assets/images/section-anchor.png" alt=""></a></span></h\4>|' $@
rm -f *.sedbak

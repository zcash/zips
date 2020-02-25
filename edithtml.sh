#!/bin/sh

sed -i.sedbak 's|</head>|<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css"></head>|' $@
sed -i.sedbak 's|<a href="\([^":]*\).rst">|<a href="\1">|' $@
sed -i.sedbak 's|http://cdn.mathjax.org/mathjax/latest/MathJax.js|https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js|' $@
rm -f *.sedbak

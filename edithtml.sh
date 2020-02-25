#!/bin/sh

sed -i.sedbak 's|</head>|<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css"></head>|' $@
sed -i.sedbak 's|<a href="\([^":]*\).rst">|<a href="\1">|' $@
rm -f *.sedbak

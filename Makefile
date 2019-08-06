# Dependencies:
# sudo apt-get install python-pip
# sudo pip install rst2html5

%.html: %.rst
	$(eval TITLE=$(shell echo '$(basename $<)' | sed -r 's|zip-0{0,3}|ZIP |'): $(shell grep '^\s*Title: ' $< | sed 's|\s*Title: ||'))
	rst2html5 -v --title="$(TITLE)" $< >$@
	sed -i 's|</head>|<link rel="stylesheet" href="css/zip-style.css"><link rel="stylesheet" href="assets/css/style.css"></head>|' $@


all: $(addsuffix .html,$(basename $(wildcard zip-*.rst)))
	./makeindex.sh | cat README-template.md - >README.md

clean:
	rm -f zip-*.html

default: all

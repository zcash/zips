%.md: %.rst
	pandoc -s -o $@ $<

%.html: %.rst
	$(eval TITLE=$(shell echo '$(basename $<)' | sed -r 's|zip-0{0,3}|ZIP |'): $(shell grep '^\s*Title: ' $< | sed 's|\s*Title: ||'))
	pandoc --metadata pagetitle="$(TITLE)" -s -o $@ $<
	sed -i 's|</head>|<link rel="stylesheet" href="css/zip-style.css"><link rel="stylesheet" href="assets/css/style.css"></head>|' $@


all: $(addsuffix .html,$(basename $(wildcard zip-*.rst)))
	./makeindex.sh | cat README-template.md - >README.md

clean:
	rm -f zip-*.html

default: all

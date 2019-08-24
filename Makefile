# Dependencies:
# sudo apt-get install python-pip
# sudo pip install rst2html5

.PHONY: all
all:
	$(MAKE) index.rst
	$(MAKE) index.html $(addsuffix .html,$(basename $(wildcard *.rst)))

%.html: %.rst
	$(eval TITLE=$(shell echo '$(basename $<)' | sed -r 's|zip-0{0,3}|ZIP |'): $(shell grep -E '^(\.\.)?\s*Title:' $< |sed 's|.*Title:\s*||'))
	rst2html5 -v --title="$(TITLE)" $< >$@
	sed -i 's|</head>|<link rel="stylesheet" href="css/zip-style.css"><link rel="stylesheet" href="assets/css/style.css"></head>|' $@

index.rst: makeindex.sh index.template
	./makeindex.sh | cat index.template - >index.rst

.PHONY: clean
clean:
	rm -f index.rst $(addsuffix .html,$(basename $(wildcard *.rst)))

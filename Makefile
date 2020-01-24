# Dependencies:
# sudo apt-get install python-pip
# sudo pip install rst2html5

.PHONY: all all-zips protocol
all-zips:
	$(MAKE) README.rst
	$(MAKE) index.html $(addsuffix .html,$(filter-out README,$(basename $(wildcard *.rst))))

all: all-zips protocol

protocol:
	$(MAKE) -C protocol

index.html: README.rst
	$(eval TITLE := $(shell echo '$(basename $<)' | sed -E 's|zip-0{0,3}|ZIP |'): $(shell grep -E '^(\.\.)?\s*Title:' $< |sed 's|.*Title:\s*||'))
	rst2html5 -v --title="$(TITLE)" $< >$@
	sed -i.sedbak 's|</head>|<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css"></head>|' $@
	sed -i.sedbak 's|<a href="\([^":]*\).rst">|<a href="\1">|' $@
	rm -f *.sedbak

%.html: %.rst
	$(eval TITLE := $(shell echo '$(basename $<)' | sed -E 's|zip-0{0,3}|ZIP |'): $(shell grep -E '^(\.\.)?\s*Title:' $< |sed 's|.*Title:\s*||'))
	rst2html5 -v --title="$(TITLE)" $< >$@
	sed -i.sedbak 's|</head>|<meta name="viewport" content="width=device-width, initial-scale=1"><link rel="stylesheet" href="css/style.css"></head>|' $@
	sed -i.sedbak 's|<a href="\([^":]*\).rst">|<a href="\1">|' $@
	rm -f *.sedbak

README.rst: makeindex.sh README.template $(filter-out README.rst,$(wildcard *.rst))
	./makeindex.sh | cat README.template - >README.rst

.PHONY: clean
clean:
	rm -f README.rst index.html $(addsuffix .html,$(basename $(wildcard *.rst)))

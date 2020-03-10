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

define PROCESSRST
$(eval TITLE := $(shell echo '$(basename $<)' | sed -E 's|zip-0{0,3}|ZIP |'): $(shell grep -E '^(\.\.)?\s*Title:' $< |sed -E 's|.*Title:\s*||'))
rst2html5 -v --title="$(TITLE)" $< >$@
./edithtml.sh $@
endef

index.html: README.rst
	$(PROCESSRST)

%.html: %.rst
	$(PROCESSRST)

README.rst: makeindex.sh README.template $(wildcard zip-*.rst)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: clean
clean:
	rm -f README.rst index.html $(addsuffix .html,$(basename $(wildcard *.rst)))

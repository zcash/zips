# Dependencies: see zip-guide.rst and protocol/README.rst

.PHONY: all all-zips release protocol discard
all-zips: .Makefile.uptodate
	find . -name 'zip-*.rst' -o -name 'zip-*.md' |sort >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	$(MAKE) README.rst
	$(MAKE) index.html $(addsuffix .html,$(filter-out README,$(basename $(sort $(wildcard *.rst) $(wildcard *.md)))))

all: all-zips protocol

release:
	$(MAKE) -C protocol release

protocol:
	$(MAKE) -C protocol

discard:
	git checkout -- '*.html' 'protocol/*.pdf'

.Makefile.uptodate: Makefile
	$(MAKE) clean
	touch .Makefile.uptodate

define PROCESSRST
$(eval TITLE := $(shell echo '$(basename $<)' | sed -E 's|zip-0{0,3}|ZIP |;s|draft-|Draft |')$(shell grep -E '^(\.\.)?\s*Title: ' $< |sed -E 's|.*Title||'))
rst2html5 -v --title="$(TITLE)" $< >$@
./edithtml.sh --rst $@
endef

define PROCESSMD
$(eval TITLE := $(shell echo '$(basename $<)' | sed -E 's|zip-0{0,3}|ZIP |;s|draft-|Draft |')$(shell grep -E '^(\.\.)?\s*Title: ' $< |sed -E 's|.*Title||'))
pandoc --from=markdown --to=html $< --output=$@
./edithtml.sh --md $@ "${TITLE}"
endef

index.html: README.rst edithtml.sh
	$(PROCESSRST)

%.html: %.rst edithtml.sh
	$(PROCESSRST)

%.html: %.md edithtml.sh
	$(PROCESSMD)

README.rst: .zipfilelist.current makeindex.sh README.template $(sort $(wildcard zip-*.rst) $(wildcard zip-*.md))
	./makeindex.sh | cat README.template - >README.rst

.PHONY: linkcheck
linkcheck: all-zips
	$(MAKE) -C protocol all-specs
	./links_and_dests.py --check $(filter-out $(wildcard draft-*.html),$(wildcard *.html)) protocol/protocol.pdf protocol/canopy.pdf protocol/heartwood.pdf protocol/blossom.pdf protocol/sapling.pdf

.PHONY: clean
clean:
	rm -f .zipfilelist.* README.rst index.html $(addsuffix .html,$(basename $(sort $(wildcard *.rst) $(wildcard *.md))))

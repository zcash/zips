# Dependencies: see zip-guide.rst and protocol/README.rst

.PHONY: all all-zips tag-release protocol discard
all-zips: .Makefile.uptodate
	echo "$(sort $(wildcard zip-*.rst) $(wildcard zip-*.md))" >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	echo "$(sort $(wildcard draft-*.rst) $(wildcard draft-*.md))" >.draftfilelist.new
	diff .draftfilelist.current .draftfilelist.new || cp -f .draftfilelist.new .draftfilelist.current
	rm -f .draftfilelist.new
	$(MAKE) README.rst
	$(MAKE) index.html $(addsuffix .html,$(filter-out README,$(basename $(sort $(wildcard *.rst) $(wildcard *.md)))))

all: all-zips protocol

tag-release:
	$(MAKE) -C protocol tag-release

protocol:
	$(MAKE) -C protocol

discard:
	git checkout -- '*.html' 'README.rst' 'protocol/*.pdf'

.Makefile.uptodate: Makefile edithtml.sh
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

README.rst: .zipfilelist.current .draftfilelist.current makeindex.sh README.template $(wildcard zip-*.rst) $(wildcard zip-*.md) $(wildcard draft-*.rst) $(wildcard draft-*.md)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: linkcheck
linkcheck: all-zips
	$(MAKE) -C protocol all-specs
	./links_and_dests.py --check $(filter-out $(wildcard draft-*.html),$(wildcard *.html)) protocol/protocol.pdf protocol/canopy.pdf protocol/heartwood.pdf protocol/blossom.pdf protocol/sapling.pdf

.PHONY: clean
clean:
	rm -f .zipfilelist.* README.rst index.html $(addsuffix .html,$(basename $(sort $(wildcard *.rst) $(wildcard *.md))))

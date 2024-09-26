# Dependencies: see zip-guide.rst and protocol/README.rst

.PHONY: all-zips all tag-release protocol all-protocol discard
all-zips: .Makefile.uptodate
	echo "$(patsubst zips/%,%,$(sort $(wildcard zips/zip-*.rst) $(wildcard zips/zip-*.md)))" >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	echo "$(patsubst zips/%,%,$(sort $(wildcard zips/draft-*.rst) $(wildcard zips/draft-*.md)))" >.draftfilelist.new
	diff .draftfilelist.current .draftfilelist.new || cp -f .draftfilelist.new .draftfilelist.current
	rm -f .draftfilelist.new
	$(MAKE) README.rst
	$(MAKE) rendered/index.html $(addprefix rendered/,$(addsuffix .html,$(basename $(patsubst zips/%,%,$(sort $(wildcard zips/*.rst) $(wildcard zips/*.md))))))

all: all-zips all-protocol

tag-release:
	$(MAKE) -C protocol tag-release

protocol:
	$(MAKE) -C protocol protocol

all-protocol:
	$(MAKE) -C protocol all

discard:
	git checkout -- 'rendered/*.html' 'README.rst' 'rendered/protocol/*.pdf'

.Makefile.uptodate: Makefile edithtml.sh
	$(MAKE) clean
	touch .Makefile.uptodate

define PROCESSRST
$(eval TITLE := $(shell echo '$(patsubst zips/%,%,$(basename $<))' | sed -E 's|zip-0{0,3}|ZIP |;s|draft-|Draft |')$(shell grep -E '^(\.\.)?\s*Title: ' $< |sed -E 's|.*Title||'))
rst2html5 -v --title="$(TITLE)" $< >$@
./edithtml.sh --rst $@
endef

define PROCESSMD
$(eval TITLE := $(shell echo '$(patsubst zips/%,%,$(basename $<))' | sed -E 's|zip-0{0,3}|ZIP |;s|draft-|Draft |')$(shell grep -E '^(\.\.)?\s*Title: ' $< |sed -E 's|.*Title||'))
pandoc --from=markdown --to=html $< --output=$@
./edithtml.sh --md $@ "${TITLE}"
endef

rendered/index.html: README.rst edithtml.sh
	$(PROCESSRST)

rendered/%.html: zips/%.rst edithtml.sh
	$(PROCESSRST)

rendered/%.html: zips/%.md edithtml.sh
	$(PROCESSMD)

README.rst: .zipfilelist.current .draftfilelist.current makeindex.sh README.template $(wildcard zips/zip-*.rst) $(wildcard zips/zip-*.md) $(wildcard zips/draft-*.rst) $(wildcard zips/draft-*.md)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: linkcheck clean all-clean
linkcheck: all
	./links_and_dests.py --check $(filter-out $(wildcard rendered/draft-*.html),$(wildcard rendered/*.html)) $(filter-out rendered/protocol/sprout.pdf,$(wildcard rendered/protocol/*.pdf))

clean:
	rm -f .zipfilelist.* README.rst rendered/index.html $(addprefix rendered/,$(addsuffix .html,$(basename $(patsubst zips/%,%,$(sort $(wildcard zips/*.rst) $(wildcard zips/*.md))))))

all-clean:
	$(MAKE) clean
	$(MAKE) -C protocol clean

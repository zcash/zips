# Dependencies: see zips/zip-guide.rst and protocol/README.rst

MARKDOWN_OPTION?=--mmd

.PHONY: all-zips all-docker all tag-release protocol all-protocol discard
all-zips: .Makefile.uptodate
	echo "$(patsubst zips/%,%,$(sort $(wildcard zips/zip-*.rst) $(wildcard zips/zip-*.md)))" >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	echo "$(patsubst zips/%,%,$(sort $(wildcard zips/draft-*.rst) $(wildcard zips/draft-*.md)))" >.draftfilelist.new
	diff .draftfilelist.current .draftfilelist.new || cp -f .draftfilelist.new .draftfilelist.current
	rm -f .draftfilelist.new
	mkdir -p rendered
	cp -r static/* rendered/
	$(MAKE) README.rst
	$(MAKE) rendered/index.html $(addprefix rendered/,$(addsuffix .html,$(basename $(patsubst zips/%,%,$(sort $(wildcard zips/*.rst) $(wildcard zips/*.md))))))

all-docker:
	git config --global --add safe.directory "$(shell pwd)"
	$(MAKE) all

all: all-zips all-protocol

protocol:
	$(MAKE) -C protocol protocol

protocol-dark:
	$(MAKE) -C protocol protocol-dark

all-protocol:
	$(MAKE) -C protocol all

all-specs: all-zips
	$(MAKE) -C protocol all-specs

discard:
	rm -r rendered
	git checkout -- 'README.rst'

.Makefile.uptodate: Makefile render.sh
	$(MAKE) clean
	touch .Makefile.uptodate

rendered/index.html: README.rst render.sh
	./render.sh --rst $< $@

rendered/%.html: zips/%.rst render.sh
	./render.sh --rst $< $@

rendered/%.html: zips/%.md render.sh
	./render.sh $(MARKDOWN_OPTION) $< $@

README.rst: .zipfilelist.current .draftfilelist.current makeindex.sh README.template $(wildcard zips/zip-*.rst) $(wildcard zips/zip-*.md) $(wildcard zips/draft-*.rst) $(wildcard zips/draft-*.md)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: linkcheck updatecheck clean all-clean
linkcheck: all
	./links_and_dests.py --check $(filter-out $(wildcard rendered/draft-*.html),$(wildcard rendered/*.html)) $(filter-out rendered/protocol/sprout.pdf,$(wildcard rendered/protocol/*.pdf))

updatecheck: all
	./update_check.sh

clean:
	rm -f .zipfilelist.* README.rst rendered/index.html $(addprefix rendered/,$(addsuffix .html,$(basename $(patsubst zips/%,%,$(sort $(wildcard zips/*.rst) $(wildcard zips/*.md))))))
	rm -rf temp

all-clean:
	$(MAKE) clean
	$(MAKE) -C protocol clean

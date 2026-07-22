# Dependencies: see zips/zip-guide.rst and protocol/README.rst

MARKDOWN_OPTION?=--mmd

# If a document exists as both .rst and .md, the .rst pattern rule silently
# shadows the .md, so a stale stub can mask its replacement ZIP.
DUPLICATE_SOURCES := $(filter \
  $(patsubst %.rst,%,$(wildcard zips/*.rst)), \
  $(patsubst %.md,%,$(wildcard zips/*.md)))

.PHONY: all-zips all-docker all tag-release protocol all-protocol discard
all-zips: .Makefile.uptodate
	$(if $(DUPLICATE_SOURCES),$(error Both .rst and .md sources exist for: $(DUPLICATE_SOURCES)))
	echo "$(patsubst zips/%,%,$(sort $(wildcard zips/zip-*.rst) $(wildcard zips/zip-*.md)))" >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	echo "$(patsubst zips/%,%,$(sort $(wildcard zips/draft-*.rst) $(wildcard zips/draft-*.md)))" >.draftfilelist.new
	diff .draftfilelist.current .draftfilelist.new || cp -f .draftfilelist.new .draftfilelist.current
	rm -f .draftfilelist.new
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

.Makefile.uptodate: Makefile render.sh $(wildcard static/assets/fonts/*) $(wildcard static/assets/images/*) $(wildcard static/css/*)
	$(MAKE) clean
	mkdir -p rendered
	cp -r static/* rendered
	touch .Makefile.uptodate

# The `rendered` directory (with its copied static assets) must exist before any
# file is rendered. Depend on it order-only so the render targets don't rebuild
# when its mtime changes, but the directory is always (re)created if missing —
# independent of the `.Makefile.uptodate` stamp, and safe under parallel `make`.
rendered:
	mkdir -p rendered
	cp -r static/* rendered

rendered/index.html: README.rst render.sh | rendered
	./render.sh --rst $< $@

rendered/%.html: zips/%.rst render.sh | rendered
	./render.sh --rst $< $@

rendered/%.html: zips/%.md render.sh | rendered
	./render.sh $(MARKDOWN_OPTION) $< $@

# Render-regression test fixtures, kept out of zips/ so the ZIP set stays clean.
# Output goes under rendered/test/, with css/ and assets/ symlinked from the parent
# rendered/ dir so the pages are viewable with correct styling in a browser.
rendered/test/%.html: test/render/%.rst render.sh | rendered/test
	./render.sh --rst $< $@

rendered/test/%.html: test/render/%.md render.sh | rendered/test
	./render.sh $(MARKDOWN_OPTION) $< $@

rendered/test:
	mkdir -p rendered/test
	ln -sfn ../css rendered/test/css
	ln -sfn ../assets rendered/test/assets

README.rst: .zipfilelist.current .draftfilelist.current makeindex.sh README.template $(wildcard zips/zip-*.rst) $(wildcard zips/zip-*.md) $(wildcard zips/draft-*.rst) $(wildcard zips/draft-*.md)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: linkcheck updatecheck clean all-clean test
test:
	./test/render-test.sh

linkcheck: all
	./links_and_dests.py --check $(filter-out $(wildcard rendered/draft-*.html),$(wildcard rendered/*.html)) $(filter-out rendered/protocol/sprout.pdf,$(wildcard rendered/protocol/*.pdf))

updatecheck:
	./update_check.sh

clean:
	rm -f .zipfilelist.* README.rst rendered/index.html $(addprefix rendered/,$(addsuffix .html,$(basename $(patsubst zips/%,%,$(sort $(wildcard zips/*.rst) $(wildcard zips/*.md))))))
	rm -rf temp

all-clean:
	$(MAKE) clean
	$(MAKE) -C protocol clean

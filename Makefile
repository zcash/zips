# Dependencies:
# sudo apt-get install python3-pip pandoc
# sudo pip3 install rst2html5

.PHONY: all all-zips protocol
all-zips: .Makefile.uptodate
	find . -name 'zip-*.rst' -o -name 'zip-*.md' |sort >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	$(MAKE) README.rst
	$(MAKE) index.html $(addsuffix .html,$(filter-out README,$(basename $(wildcard *.rst) $(wildcard *.md))))

all: all-zips protocol

protocol: .Makefile.uptodate
	$(MAKE) -C protocol

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

README.rst: .zipfilelist.current makeindex.sh README.template $(wildcard zip-*.rst) $(wildcard zip-*.md)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: clean
clean:
	rm -f .zipfilelist.* README.rst index.html $(addsuffix .html,$(basename $(wildcard *.rst) $(wildcard *.md)))

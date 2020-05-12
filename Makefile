# Dependencies:
# sudo apt-get install python3-pip
# sudo pip3 install rst2html5

.PHONY: all all-zips protocol
all-zips: .Makefile.uptodate
	find . -name 'zip-*.rst' |sort >.zipfilelist.new
	diff .zipfilelist.current .zipfilelist.new || cp -f .zipfilelist.new .zipfilelist.current
	rm -f .zipfilelist.new
	$(MAKE) README.rst
	$(MAKE) index.html $(addsuffix .html,$(filter-out README,$(basename $(wildcard *.rst))))

all: all-zips protocol

protocol: .Makefile.uptodate
	$(MAKE) -C protocol

.Makefile.uptodate: Makefile
	$(MAKE) clean
	touch .Makefile.uptodate

define PROCESSRST
$(eval TITLE := $(shell echo '$(basename $<)' | sed -E 's|zip-0{0,3}|ZIP |'): $(shell grep -E '^(\.\.)?\s*Title:' $< |sed -E 's|.*Title:\s*||'))
rst2html5 -v --title="$(TITLE)" $< >$@
./edithtml.sh $@
endef

index.html: README.rst edithtml.sh
	$(PROCESSRST)

%.html: %.rst edithtml.sh
	$(PROCESSRST)

README.rst: .zipfilelist.current makeindex.sh README.template $(wildcard zip-*.rst)
	./makeindex.sh | cat README.template - >README.rst

.PHONY: clean
clean:
	rm -f .zipfilelist.* README.rst index.html $(addsuffix .html,$(basename $(wildcard *.rst)))

# Dependencies: see zip-guide.rst and protocol/README.rst

SHELL=/bin/bash -eo pipefail

# Experimental; options are pdflatex, lualatex, or xelatex.
# On Debian, LuaLaTeX needs the texlive-luatex package, and XeLaTeX needs the texlive-xetex package.
# Make sure to read <https://github.com/zcash/zips/issues/249>.
ENGINE=pdflatex

LATEXMKOPT_pdflatex=
LATEXMKOPT_xelatex=-pdflatex=xelatex -dvi- -ps-
LATEXMKOPT_lualatex=-pdflatex=lualatex -dvi- -ps-

LATEXMK=max_print_line=10000 latexmk $(LATEXMKOPT_$(ENGINE)) --halt-on-error --file-line-error -bibtex -pdf -logfilewarnings- -e '$$max_repeat=8'
LATEX=$(ENGINE) --halt-on-error --file-line-error
NOCRUFT?=|perl -pe 's|[{\<\(]\/[^ ]* ?||g;s|^.* has been referenced but does not exist.*||g;s|^\n||g'

PDFDIR=../rendered/protocol

# Use EXTRAOPT=-pvc for "continuous preview" mode. For example, "make auxblossom EXTRAOPT=-pvc".
# In this case the updated .pdf will be in the aux/ directory.

.PHONY: all protocol protocol-dark all-specs tag-release discard
all: .Makefile.uptodate
	$(MAKE) $(PDFDIR)/protocol.pdf $(PDFDIR)/protocol-dark.pdf $(PDFDIR)/nu5.pdf $(PDFDIR)/canopy.pdf $(PDFDIR)/heartwood.pdf $(PDFDIR)/blossom.pdf $(PDFDIR)/sapling.pdf

protocol: $(PDFDIR)/protocol.pdf

protocol-dark: $(PDFDIR)/protocol-dark.pdf

all-specs: .Makefile.uptodate
	$(MAKE) nu6 nu6-dark nu5 canopy heartwood blossom sapling

tag-release:
ifeq ($(shell git tag --points-at HEAD |wc -l),0)
	echo "Set a tag at HEAD first."
else
	$(eval TAG := $(shell git tag --points-at HEAD))
	git fetch origin
	git merge-base --is-ancestor origin/main HEAD || (echo "The current branch is dirty and/or not up-to-date with origin's main branch."; false)
	$(MAKE) clean all
	git add $(PDFDIR)/*.pdf
	git commit -m "Regenerate PDFs." $(PDFDIR)/*.pdf
	git tag "v$(TAG)"
endif

discard:
	git checkout -- "$(PDFDIR)/*.pdf"

.Makefile.uptodate: Makefile
	$(MAKE) clean
	touch .Makefile.uptodate

$(PDFDIR)/sapling.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) sapling

$(PDFDIR)/blossom.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) blossom

$(PDFDIR)/heartwood.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) heartwood

$(PDFDIR)/canopy.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) canopy

$(PDFDIR)/nu5.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) nu5

$(PDFDIR)/protocol.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) nu6

$(PDFDIR)/protocol-dark.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard_dark.png incremental_merkle_dark.png
	$(MAKE) nu6-dark

.PHONY: auxsapling sapling
auxsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=sapling -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

sapling:
	$(MAKE) auxsapling
	mv -f aux/sapling.pdf $(PDFDIR)

.PHONY: auxblossom blossom
auxblossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/blossom.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=blossom -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

blossom:
	$(MAKE) auxblossom
	mv -f aux/blossom.pdf $(PDFDIR)

.PHONY: auxheartwood heartwood
auxheartwood:
	printf '\\toggletrue{isheartwood}\n\\renewcommand{\\docversion}{Version %s [\\HeartwoodSpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/heartwood.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=heartwood -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

heartwood:
	$(MAKE) auxheartwood
	mv -f aux/heartwood.pdf $(PDFDIR)

.PHONY: auxcanopy canopy
auxcanopy:
	printf '\\toggletrue{iscanopy}\n\\renewcommand{\\docversion}{Version %s [\\CanopySpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/canopy.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=canopy -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

canopy:
	$(MAKE) auxcanopy
	mv -f aux/canopy.pdf $(PDFDIR)

.PHONY: auxnu5 nu5
auxnu5:
	printf '\\toggletrue{isnufive}\n\\renewcommand{\\docversion}{Version %s [\\NUFiveSpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu5.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu5 -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu5:
	$(MAKE) auxnu5
	mv -f aux/nu5.pdf $(PDFDIR)

.PHONY: auxnu6 nu6
auxnu6:
	printf '\\toggletrue{isnusix}\n\\renewcommand{\\docversion}{Version %s [\\NUSixSpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu6.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu6 -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu6:
	$(MAKE) auxnu6
	mv -f aux/nu6.pdf $(PDFDIR)/protocol.pdf

.PHONY: auxnu6-dark nu6-dark
auxnu6-dark:
	printf '\\toggletrue{darkmode}\\toggletrue{isnusix}\n\\renewcommand{\\docversion}{Version %s [\\NUSixSpec]}\n' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu6-dark.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu6-dark -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu6-dark:
	$(MAKE) auxnu6-dark
	mv -f aux/nu6-dark.pdf $(PDFDIR)/protocol-dark.pdf

.PHONY: clean
clean:
	rm -f aux/* protocol.ver $(PDFDIR)/protocol.pdf $(PDFDIR)/protocol-dark.pdf $(PDFDIR)/nu5.pdf $(PDFDIR)/canopy.pdf $(PDFDIR)/heartwood.pdf $(PDFDIR)/blossom.pdf $(PDFDIR)/sapling.pdf

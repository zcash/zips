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

.PHONY: all all-specs release discard
all: .Makefile.uptodate
	$(MAKE) nu5 canopy heartwood blossom sapling

all-specs: .Makefile.uptodate
	$(MAKE) $(PDFDIR)/nu5.pdf $(PDFDIR)/canopy.pdf $(PDFDIR)/heartwood.pdf $(PDFDIR)/blossom.pdf $(PDFDIR)/sapling.pdf

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

$(PDFDIR)/sapling.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) sapling

$(PDFDIR)/blossom.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) blossom

$(PDFDIR)/heartwood.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) heartwood

$(PDFDIR)/canopy.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) canopy

$(PDFDIR)/nu5.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) nu5

.PHONY: auxsapling
auxsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=sapling -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

.PHONY: sapling
sapling:
	$(MAKE) auxsapling
	mv -f aux/sapling.pdf $(PDFDIR)

.PHONY: auxblossom
auxblossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/blossom.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=blossom -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

.PHONY: blossom
blossom:
	$(MAKE) auxblossom
	mv -f aux/blossom.pdf $(PDFDIR)

.PHONY: auxheartwood
auxheartwood:
	printf '\\toggletrue{isheartwood}\n\\renewcommand{\\docversion}{Version %s [\\HeartwoodSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/heartwood.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=heartwood -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

.PHONY: heartwood
heartwood:
	$(MAKE) auxheartwood
	mv -f aux/heartwood.pdf $(PDFDIR)

.PHONY: auxcanopy
auxcanopy:
	printf '\\toggletrue{iscanopy}\n\\renewcommand{\\docversion}{Version %s [\\CanopySpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/canopy.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=canopy -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

.PHONY: canopy
canopy:
	$(MAKE) auxcanopy
	mv -f aux/canopy.pdf $(PDFDIR)

.PHONY: auxnu5
auxnu5:
	printf '\\toggletrue{isnufive}\n\\renewcommand{\\docversion}{Version %s [\\NUFiveSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu5.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu5 -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

.PHONY: nu5
nu5:
	$(MAKE) auxnu5
	mv -f aux/nu5.pdf $(PDFDIR)
	cp -f $(PDFDIR)/nu5.pdf $(PDFDIR)/protocol.pdf

.PHONY: nolatexmk-sapling
nolatexmk-sapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f sapling.aux sapling.bbl sapling.blg sapling.brf sapling.bcf
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber sapling
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }
	sh mymakeindex.sh -o sapling.ind sapling.idx
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: nolatexmk-blossom
nolatexmk-blossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f blossom.aux blossom.bbl blossom.blg blossom.brf blossom.bcf
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber blossom
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	sh mymakeindex.sh -o blossom.ind blossom.idx
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	cp -f blossom.pdf protocol.pdf

.PHONY: nolatexmk-heartwood
nolatexmk-heartwood:
	printf '\\toggletrue{isheartwood}\n\\renewcommand{\\docversion}{Version %s [\\HeartwoodSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f heartwood.aux heartwood.bbl heartwood.blg heartwood.brf heartwood.bcf
	$(LATEX) -jobname=heartwood protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber heartwood
	$(LATEX) -jobname=heartwood protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=heartwood protocol.tex || { touch incremental_merkle.png; exit 1; }
	sh mymakeindex.sh -o heartwood.ind heartwood.idx
	$(LATEX) -jobname=heartwood protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: nolatexmk-canopy
nolatexmk-canopy:
	printf '\\toggletrue{iscanopy}\n\\renewcommand{\\docversion}{Version %s [\\CanopySpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f canopy.aux canopy.bbl canopy.blg canopy.brf canopy.bcf
	$(LATEX) -jobname=canopy protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber canopy
	$(LATEX) -jobname=canopy protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=canopy protocol.tex || { touch incremental_merkle.png; exit 1; }
	sh mymakeindex.sh -o canopy.ind canopy.idx
	$(LATEX) -jobname=canopy protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: nolatexmk-nu5
nolatexmk-nu5:
	printf '\\toggletrue{isnufive}\n\\renewcommand{\\docversion}{Version %s [\\NUFiveSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f nu5.aux nu5.bbl nu5.blg nu5.brf nu5.bcf
	$(LATEX) -jobname=nu5 protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber nu5
	$(LATEX) -jobname=nu5 protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=nu5 protocol.tex || { touch incremental_merkle.png; exit 1; }
	sh mymakeindex.sh -o nu5.ind nu5.idx
	$(LATEX) -jobname=nu5 protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: clean
clean:
	rm -f aux/* html/* protocol.ver $(PDFDIR)/protocol.pdf $(PDFDIR)/nu5.pdf $(PDFDIR)/canopy.pdf $(PDFDIR)/heartwood.pdf $(PDFDIR)/blossom.pdf $(PDFDIR)/sapling.pdf

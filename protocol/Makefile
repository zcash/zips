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

.PHONY: all protocol protocol-dark all-pdfs all-specs discard
all: .Makefile.uptodate
	# Make `all-pdfs` in CI only if anything under `protocol/` has changed. For local builds
	# this does not need to be conditional, since each PDF will only be built if its dependencies
	# have changed. However, when checking renderability of a PR in CI the `rendered/` directory
	# will not exist, so the PDFs would always be built from scratch. This is quite slow, so we
	# want to avoid it for PRs that have not changed anything under `protocol/`.
	#
	# For a build from the CI workflow, the base ref hash should be written to `../base_ref`.
	# If that file does not exist (the expected case locally), we make `all-pdfs` unconditionally.
	# If it contains a hash (the expected case for CI), we make `all-pdfs` if
	# `git diff --name-only` shows changes relative to that base ref under `protocol/`.
	# Finally, just in case we have `../base_ref` locally, we make `all-pdfs` if any status
	# entry under `protocol/` is dirty, i.e. if its second status character is not " "
	# (see the documentation for "Porcelain Format Version 1" in `git status --help`).
	#
	# Note that in Makefiles, a dollar sign must be doubled to get a literal dollar sign in *any*
	# context. Be very careful if refactoring this to ensure that the contents of `../base_ref`
	# are only expanded if they are a hash.
	if ( /bin/true ) || \
	   ( ! [ -e ../base_ref ] ) || \
	   ( git diff --name-only "$$(grep -E '^[0-9a-f]{40}$$' ../base_ref).." -- |grep '^protocol/' ) || \
	   ( git status --porcelain=v1 |grep '^.[^ ] protocol/' ); then \
	    $(MAKE) all-pdfs; fi

protocol: $(PDFDIR)/protocol.pdf

protocol-dark: $(PDFDIR)/protocol-dark.pdf

all-pdfs: .Makefile.uptodate
	$(MAKE) $(PDFDIR)/protocol.pdf $(PDFDIR)/protocol-dark.pdf $(PDFDIR)/nu6.pdf $(PDFDIR)/nu5.pdf $(PDFDIR)/canopy.pdf $(PDFDIR)/heartwood.pdf $(PDFDIR)/blossom.pdf $(PDFDIR)/sapling.pdf

all-specs: .Makefile.uptodate
	$(MAKE) nu6_1 nu6_1-dark nu6 nu5 canopy heartwood blossom sapling

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

$(PDFDIR)/nu6.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) nu6

$(PDFDIR)/protocol.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard.png incremental_merkle.png
	$(MAKE) nu6_1

$(PDFDIR)/protocol-dark.pdf: protocol.tex zcash.bib jubjub.png key_components_sapling.png key_components_orchard_dark.png incremental_merkle_dark.png
	$(MAKE) nu6_1-dark

.PHONY: auxsapling sapling
auxsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=sapling -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

sapling:
	$(MAKE) auxsapling
	mkdir -p $(PDFDIR)
	mv -f aux/sapling.pdf $(PDFDIR)

.PHONY: auxblossom blossom
auxblossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/blossom.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=blossom -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

blossom:
	$(MAKE) auxblossom
	mkdir -p $(PDFDIR)
	mv -f aux/blossom.pdf $(PDFDIR)

.PHONY: auxheartwood heartwood
auxheartwood:
	printf '\\toggletrue{isheartwood}\n\\renewcommand{\\docversion}{Version %s [\\HeartwoodSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/heartwood.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=heartwood -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

heartwood:
	$(MAKE) auxheartwood
	mkdir -p $(PDFDIR)
	mv -f aux/heartwood.pdf $(PDFDIR)

.PHONY: auxcanopy canopy
auxcanopy:
	printf '\\toggletrue{iscanopy}\n\\renewcommand{\\docversion}{Version %s [\\CanopySpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/canopy.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=canopy -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

canopy:
	$(MAKE) auxcanopy
	mkdir -p $(PDFDIR)
	mv -f aux/canopy.pdf $(PDFDIR)

.PHONY: auxnu5 nu5
auxnu5:
	printf '\\toggletrue{isnufive}\n\\renewcommand{\\docversion}{Version %s [\\NUFiveSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu5.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu5 -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu5:
	$(MAKE) auxnu5
	mkdir -p $(PDFDIR)
	mv -f aux/nu5.pdf $(PDFDIR)

.PHONY: auxnu6 nu6
auxnu6:
	printf '\\toggletrue{isnusix}\n\\renewcommand{\\docversion}{Version %s [\\NUSixSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu6.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu6 -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu6:
	$(MAKE) auxnu6
	mkdir -p $(PDFDIR)
	mv -f aux/nu6.pdf $(PDFDIR)

.PHONY: auxnu6_1 nu6_1
auxnu6_1:
	printf '\\toggletrue{isnusixone}\n\\renewcommand{\\docversion}{Version %s [\\NUSixOneSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu6_1.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu6_1 -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu6_1:
	$(MAKE) auxnu6_1
	mkdir -p $(PDFDIR)
	mv -f aux/nu6_1.pdf $(PDFDIR)/protocol.pdf

.PHONY: auxnu6_1-dark nu6_1-dark
auxnu6_1-dark:
	printf '\\toggletrue{darkmode}\\toggletrue{isnusixone}\n\\renewcommand{\\docversion}{Version %s [\\NUSixOneSpec]}\n' "$$(git describe --tags --abbrev=6 --always |sed 's/-1-g.*//;s/-auto//')" |tee protocol.ver
	mkdir -p aux
	rm -f aux/nu6_1-dark.*
	cp mymakeindex.sh aux
	$(LATEXMK) -jobname=nu6_1-dark -auxdir=aux -outdir=aux $(EXTRAOPT) protocol $(NOCRUFT)

nu6_1-dark:
	$(MAKE) auxnu6_1-dark
	mkdir -p $(PDFDIR)
	mv -f aux/nu6_1-dark.pdf $(PDFDIR)/protocol-dark.pdf

.PHONY: clean
clean:
	rm -f aux/* protocol.ver $(PDFDIR)/*

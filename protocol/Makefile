# Experimental; options are pdflatex, lualatex, or xelatex.
# On Debian, LuaLaTeX needs the texlive-luatex package, and XeLaTeX needs the texlive-xetex package.
# Make sure to read <https://github.com/zcash/zips/issues/249>.
ENGINE=

LATEXMKOPT_pdflatex=
LATEXMKOPT_xelatex=-pdflatex=xelatex -dvi- -ps-
LATEXMKOPT_lualatex=-pdflatex=lualatex -dvi- -ps-

LATEXMK=latexmk $(LATEXMKOPT_$(ENGINE)) --halt-on-error -bibtex -pdf -logfilewarnings-
LATEX=$(ENGINE) --halt-on-error

sprout.pdf: protocol.tex zcash.bib incremental_merkle.png key_components.png
	$(MAKE) sprout

sapling.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) sapling

blossom.pdf: protocol.tex zcash.bib incremental_merkle.png key_components_sapling.png
	$(MAKE) blossom

.PHONY: auxsprout
auxsprout:
	printf '\\renewcommand{\\docversion}{Version %s [\\SproutSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sprout.* aux/protocol.*
	$(LATEXMK) -jobname=sprout -auxdir=aux -outdir=aux protocol

.PHONY: sprout
sprout:
	$(MAKE) auxsprout
	mv -f aux/sprout.pdf .

.PHONY: pvcsprout
pvcsprout:
	printf '\\renewcommand{\\docversion}{Version %s [\\SproutSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sprout.* aux/protocol.*
	$(LATEXMK) -jobname=sprout -auxdir=aux -pvc protocol

.PHONY: auxsapling
auxsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	$(LATEXMK) -jobname=sapling -auxdir=aux -outdir=aux protocol

.PHONY: sapling
sapling:
	$(MAKE) auxsapling
	mv -f aux/sapling.pdf .
	cp -f sapling.pdf protocol.pdf

.PHONY: pvcsapling
pvcsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	$(LATEXMK) -jobname=sapling -auxdir=aux -pvc protocol

.PHONY: auxblossom
auxblossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/blossom.*
	$(LATEXMK) -jobname=blossom -auxdir=aux -outdir=aux protocol

.PHONY: blossom
blossom:
	$(MAKE) auxblossom
	mv -f aux/blossom.pdf .

.PHONY: pvcblossom
pvcblossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/blossom.*
	$(LATEXMK) -jobname=blossom -auxdir=aux -pvc protocol

.PHONY: nolatexmk-sprout
nolatexmk-sprout:
	printf '\\renewcommand{\\docversion}{Version %s [\\SproutSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f sprout.aux sprout.bbl sprout.blg sprout.brf sprout.bcf
	$(LATEX) -jobname=sprout protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber sprout
	$(LATEX) -jobname=sprout protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=sprout protocol.tex || { touch incremental_merkle.png; exit 1; }
	sh mymakeindex.sh -o sprout.ind sprout.idx
	$(LATEX) -jobname=sprout protocol.tex || { touch incremental_merkle.png; exit 1; }

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
	cp -f sapling.pdf protocol.pdf

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

.PHONY: clean
clean:
	rm -f aux/* html/* protocol.ver \
              sprout.dvi  sprout.pdf  sprout.bbl  sprout.blg  sprout.brf      sprout.toc \
              sprout.aux  sprout.out  sprout.log  sprout.bcf  sprout.run.xml  sprout.fls  sprout.fdb_latexmk \
              sprout.idx  sprout.ilg  sprout.ind  sprout.ind.original \
              sapling.dvi sapling.pdf sapling.bbl sapling.blg sapling.brf     sapling.toc \
              sapling.aux sapling.out sapling.log sapling.bcf sapling.run.xml sapling.fls sapling.fdb_latexmk \
              sapling.idx sapling.ilg sapling.ind sapling.ind.original \
              blossom.dvi blossom.pdf blossom.bbl blossom.blg blossom.brf     blossom.toc \
              blossom.aux blossom.out blossom.log blossom.bcf blossom.run.xml blossom.fls blossom.fdb_latexmk \
              blossom.idx blossom.ilg blossom.ind blossom.ind.original

.PHONY: all
all: sapling sprout blossom

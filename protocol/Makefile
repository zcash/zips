LATEXMK=latexmk --halt-on-error -bibtex -pdf
LATEX=pdflatex --halt-on-error

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
	$(LATEX) protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber protocol
	$(LATEX) protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: nolatexmk-sapling
nolatexmk-sapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f sapling.aux sapling.bbl sapling.blg sapling.brf sapling.bcf
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber sapling
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: nolatexmk-blossom
nolatexmk-blossom:
	printf '\\toggletrue{isblossom}\n\\renewcommand{\\docversion}{Version %s [\\BlossomSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f blossom.aux blossom.bbl blossom.blg blossom.brf blossom.bcf
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	biber sapling
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }
	$(LATEX) -jobname=blossom protocol.tex || { touch incremental_merkle.png; exit 1; }

.PHONY: html
html: sapling.pdf sprout.pdf blossom.pdf
	# Can't use --split-pages 1 because XHR doesn't work by default on local files in Chrome.
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 65 --fit-width 1000 --dest-dir html sprout.pdf
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 65 --fit-width 1000 --dest-dir html sapling.pdf
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 65 --fit-width 1000 --dest-dir html blossom.pdf

.PHONY: clean
clean:
	rm -f aux/* html/* protocol.ver \
              sprout.dvi  sprout.pdf  sprout.bbl  sprout.blg  sprout.brf      sprout.toc \
              sprout.aux  sprout.out  sprout.log  sprout.bcf  sprout.run.xml  sprout.fls  sprout.fdb_latexmk \
              sapling.dvi sapling.pdf sapling.bbl sapling.blg sapling.brf     sapling.toc \
              sapling.aux sapling.out sapling.log sapling.bcf sapling.run.xml sapling.fls sapling.fdb_latexmk \
              blossom.dvi blossom.pdf blossom.bbl blossom.blg blossom.brf     blossom.toc \
              blossom.aux blossom.out blossom.log blossom.bcf blossom.run.xml blossom.fls blossom.fdb_latexmk

optimizer-installed.flag2:
	rm -rf sam2p tif22pnm pdfsizeopt
	# Nail down git commits to make backdooring somewhat harder.
	git clone https://github.com/pts/sam2p.git
	cd sam2p && git reset --hard cafd4b8910a56e4b0af833f943a2ae85c7bc0a4d && $(MAKE)
	git clone https://github.com/pts/tif22pnm.git
	cd tif22pnm && git reset --hard 22217c1a3ea355a899e9c7c79903488ca13d1dfe && $(MAKE)
	git clone https://github.com/pts/pdfsizeopt.git
	cd pdfsizeopt && git reset --hard 5a42db5bef4df1652adb3ef49a9d14bcb58442eb
	touch optimizer-installed.flag2

.PHONY: clean-optimizer
clean-optimizer:
	rm -rf sam2p tif22pnm pdfsizeopt optimizer-installed.flag*

.PHONY: optsprout
optsprout: optimizer-installed.flag2
	$(MAKE) auxsprout
	PATH="${PATH}:$(CURDIR)/sam2p:$(CURDIR)/tif22pnm" pdfsizeopt/pdfsizeopt --v=40 --use-image-optimizer=sam2p \
              --tmp-dir=aux aux/sprout.pdf sprout.pdf

.PHONY: optsapling
optsapling: optimizer-installed.flag2
	$(MAKE) auxsapling
	PATH="${PATH}:$(CURDIR)/sam2p:$(CURDIR)/tif22pnm" pdfsizeopt/pdfsizeopt --v=40 --use-image-optimizer=sam2p \
              --tmp-dir=aux aux/sapling.pdf sapling.pdf
	cp -f sapling.pdf protocol.pdf

.PHONY: optblossom
optblossom: optimizer-installed.flag2
	$(MAKE) auxblossom
	PATH="${PATH}:$(CURDIR)/sam2p:$(CURDIR)/tif22pnm" pdfsizeopt/pdfsizeopt --v=40 --use-image-optimizer=sam2p \
              --tmp-dir=aux aux/blossom.pdf blossom.pdf

.PHONY: optimized
optimized: optsapling optsprout optblossom

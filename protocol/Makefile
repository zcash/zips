protocol.pdf: protocol.tex zcash.bib incremental_merkle.pdf key_components.pdf
	$(MAKE) pdf

sapling.pdf: protocol.tex zcash.bib incremental_merkle.pdf key_components_sapling.pdf
	$(MAKE) sapling

.PHONY: pdf
pdf:
	printf '\\renewcommand{\\docversion}{Version %s}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/protocol.*
	latexmk -bibtex -pdf -auxdir=aux -outdir=aux protocol
	mv -f aux/protocol.pdf .

.PHONY: html
html: pdf sapling
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 60 --split-pages 1 --dest-dir html protocol.pdf
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 60 --split-pages 1 --dest-dir saplinghtml sapling.pdf

.PHONY: pvcpdf
pvcpdf:
	printf '\\renewcommand{\\docversion}{Version %s}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/protocol.*
	latexmk -bibtex -pdf -pvc -auxdir=aux protocol

.PHONY: sapling
sapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	latexmk -bibtex -pdf -jobname=sapling -auxdir=aux -outdir=aux protocol
	mv -f aux/sapling.pdf .

.PHONY: pvcsapling
pvcsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	mkdir -p aux
	rm -f aux/sapling.*
	latexmk -bibtex -pdf -jobname=sapling -auxdir=aux -pvc protocol

LATEX=pdflatex

.PHONY: nolatexmk-pdf
nolatexmk-pdf:
	printf '\\renewcommand{\\docversion}{Version %s}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f protocol.aux protocol.bbl protocol.blg protocol.brf protocol.bcf
	$(LATEX) protocol.tex || { touch incremental_merkle.pdf; exit 1; }
	biber protocol
	$(LATEX) protocol.tex || { touch incremental_merkle.pdf; exit 1; }
	$(LATEX) protocol.tex || { touch incremental_merkle.pdf; exit 1; }
	$(LATEX) protocol.tex || { touch incremental_merkle.pdf; exit 1; }

.PHONY: nolatexmk-sapling
nolatexmk-sapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [\\SaplingSpec]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f sapling.aux sapling.bbl sapling.blg sapling.brf sapling.bcf
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.pdf; exit 1; }
	biber sapling
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.pdf; exit 1; }
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.pdf; exit 1; }
	$(LATEX) -jobname=sapling protocol.tex || { touch incremental_merkle.pdf; exit 1; }

.PHONY: clean
clean:
	rm -f aux/* protocol.ver \
              protocol.dvi protocol.pdf protocol.bbl protocol.blg protocol.brf     protocol.toc \
              protocol.aux protocol.out protocol.log protocol.bcf protocol.run.xml protocol.fls protocol.fdb_latexmk \
              sapling.dvi  sapling.pdf  sapling.bbl  sapling.blg  sapling.brf      sapling.toc \
              sapling.aux  sapling.out  sapling.log  sapling.bcf  sapling.run.xml  sapling.fls  sapling.fdb_latexmk

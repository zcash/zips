LATEXMK=latexmk --halt-on-error -bibtex -pdf -logfilewarnings-
LATEX=pdflatex --halt-on-error

# extractpdfmark is needed to produce optimized PDFs that preserve "named destinations"
# (needed for external links into the file to work correctly).
# <https://github.com/trueroad/extractpdfmark>
EXTRACTPDFMARK=extractpdfmark

# Options are documented at <http://web.mit.edu/ghostscript/www/Ps2pdf.htm>
OPTIMIZER=gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dBATCH \
          -r450 -dDownsampleColorImages=false -dDownsampleGrayImages=false -dDownsampleMonoImages=false -dFastWebView=true \
          -dSubsetFonts=true -dCompressPages=true

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

.PHONY: optsprout
optsprout:
	$(MAKE) auxsprout
	$(EXTRACTPDFMARK) aux/sprout.pdf >aux/sprout-pdfmark.ps
	$(OPTIMIZER) -sOutputFile=sprout.pdf aux/sprout.pdf aux/sprout-pdfmark.ps 2>/dev/null |awk '{printf "."}'
	ls -l aux/sprout.pdf sprout.pdf

.PHONY: optsapling
optsapling:
	$(MAKE) auxsapling
	$(EXTRACTPDFMARK) aux/sapling.pdf >aux/sapling-pdfmark.ps
	$(OPTIMIZER) -sOutputFile=sapling.pdf aux/sapling.pdf aux/sapling-pdfmark.ps 2>/dev/null |awk '{printf "."}'
	ls -l aux/sapling.pdf sapling.pdf
	cp -f sapling.pdf protocol.pdf

.PHONY: optblossom
optblossom:
	$(MAKE) auxblossom
	$(EXTRACTPDFMARK) aux/blossom.pdf >aux/blossom-pdfmark.ps
	$(OPTIMIZER) -sOutputFile=blossom.pdf aux/blossom.pdf aux/blossom-pdfmark.ps 2>/dev/null |awk '{printf "."}'
	ls -l aux/blossom.pdf blossom.pdf

.PHONY: optimized
optimized: optsapling optsprout optblossom

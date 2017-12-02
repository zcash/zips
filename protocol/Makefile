protocol.pdf: protocol.tex zcash.bib incremental_merkle.pdf key_components.pdf
	$(MAKE) pdf

sapling.pdf: protocol.tex zcash.bib incremental_merkle.pdf key_components.pdf
	$(MAKE) sapling

.PHONY: pdf
pdf:
	printf '\\renewcommand{\\docversion}{Version %s}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If latexmk fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f protocol.aux protocol.bbl protocol.blg protocol.brf protocol.bcf
	latexmk -bibtex -pdf protocol || { touch incremental_merkle.pdf; exit 1; }

.PHONY: html
html: pdf sapling
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 60 --split-pages 1 --dest-dir html protocol.pdf
	pdf2htmlEX --decompose-ligature 1 --font-size-multiplier 60 --split-pages 1 --dest-dir saplinghtml sapling.pdf

.PHONY: pvcpdf
pvcpdf:
	printf '\\renewcommand{\\docversion}{Version %s}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If latexmk fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f protocol.aux protocol.bbl protocol.blg protocol.brf protocol.bcf
	latexmk -bibtex -pdf -pvc protocol

.PHONY: sapling
sapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [Sapling]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If latexmk fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f sapling.aux sapling.bbl sapling.blg sapling.brf sapling.bcf
	latexmk -bibtex -pdf -jobname=sapling protocol || { touch incremental_merkle.pdf; exit 1; }

.PHONY: pvcsapling
pvcsapling:
	printf '\\toggletrue{issapling}\n\\renewcommand{\\docversion}{Version %s [Sapling]}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If latexmk fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f sapling.aux sapling.bbl sapling.blg sapling.brf sapling.bcf
	latexmk -bibtex -pdf -jobname=sapling -pvc protocol

.PHONY: clean
clean:
	rm -f protocol.dvi protocol.pdf protocol.bbl protocol.blg protocol.brf     protocol.toc \
              protocol.aux protocol.out protocol.log protocol.bcf protocol.run.xml protocol.ver \
              sapling.dvi  sapling.pdf  sapling.bbl  sapling.blg  sapling.brf      sapling.toc \
              sapling.aux  sapling.out  sapling.log  sapling.bcf  sapling.run.xml

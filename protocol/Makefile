protocol.pdf: protocol.tex zcash.bib incremental_merkle.pdf key_components.pdf
	$(MAKE) pdf

LATEX=pdflatex

.PHONY: pdf
pdf:
	printf '\\renewcommand{\\docversion}{Version %s}' "$$(git describe --tags --abbrev=6)" |tee protocol.ver
	# If $(LATEX) fails, touch an input so that 'make' won't think it is up-to-date next time.
	rm -f protocol.aux
	$(LATEX) protocol.tex || touch incremental_merkle.pdf
	bibtex protocol
	$(LATEX) protocol.tex || touch incremental_merkle.pdf
	$(LATEX) protocol.tex || touch incremental_merkle.pdf

.PHONY: clean
clean:
	rm -f protocol.dvi protocol.pdf protocol.bbl protocol.blg protocol.brf protocol.toc protocol.aux protocol.log

protocol.pdf: protocol.tex zcash.bib incremental_merkle.pdf key_components.pdf
	$(MAKE) pdf

.PHONY: pdf
pdf:
	# If pdflatex fails, touch an input so that 'make' won't think it is up-to-date next time.
	pdflatex protocol.tex || touch incremental_merkle.pdf
	bibtex protocol
	pdflatex protocol.tex || touch incremental_merkle.pdf
	pdflatex protocol.tex || touch incremental_merkle.pdf

.PHONY: clean
clean:
	rm -f protocol.dvi protocol.pdf

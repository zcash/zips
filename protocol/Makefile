protocol.pdf: protocol.tex incremental_merkle.pdf
	# If pdflatex fails, touch an input so that 'make' won't think it is up-to-date next time.
	pdflatex protocol.tex || touch incremental_merkle.pdf

.PHONY: clean
clean:
	rm -f protocol.dvi protocol.pdf

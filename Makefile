%.md: %.rst
	pandoc -s -o $@ $<

default: $(addsuffix .md,$(basename $(wildcard *.rst)))

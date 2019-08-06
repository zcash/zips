%.md: %.rst
	pandoc -s -o $@ $<

%.html: %.rst
	pandoc -s -o $@ $<

default: $(addsuffix .html,$(basename $(wildcard *.rst)))

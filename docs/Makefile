#
# A simple way to get all the diagrams as SVG
#

DIAGRAMS := \
    site-flow \
    services \

all: $(addsuffix .svg,$(DIAGRAMS))
all: $(addsuffix .pdf,$(DIAGRAMS))

clean:
	rm -f $(addsuffix .svg,$(DIAGRAMS))

%.svg: %.dot
	dot -Tsvg >$@.tmp $<
	mv $@.tmp $@

%.pdf: %.dot
	dot -Tpdf >$@.tmp $<
	mv $@.tmp $@

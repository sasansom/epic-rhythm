PYTHON = python3

WINDOW_SIZE = 181

WORKS = \
	aratus \
	argonautica \
	callimachushymns \
	homerichymns \
	iliad \
	nonnusdionysiaca \
	odyssey \
	quintussmyrnaeus \
	shield \
	theocritus \
	theogony \
	worksanddays

WORKS_ARCHAIC = iliad odyssey homerichymns theogony worksanddays shield
WORKS_HELLENISTIC = argonautica callimachushymns aratus theocritus
WORKS_IMPERIAL = quintussmyrnaeus nonnusdionysiaca

.PHONY: all
all: \
	expectancy.sedes-work,metrical_shape.csv \
	expectancy.sedes-metrical_shape.archaic.csv \
	expectancy.sedes-metrical_shape.archaic+hellenistic.csv \
	expectancy.sedes-metrical_shape.csv \
	tables.html \
	summary-table.html \
	table-ssl.html \
	unexpected-table.html \
	unexpected.txt

.PHONY: test
test:
	$(PYTHON) -m unittest

corpus-appositive/%.csv: corpus/%.csv
	Rscript merge-appositives.r "$<" > "$@"

# Rules that depend on sedes-var will raise an error if $SEDES is not set.
.PHONY: sedes-var
sedes-var:
ifndef SEDES
	$(error You must define the SEDES variable: `make SEDES=../sedes/`)
endif

CSV_ARCHAIC = $(addprefix corpus-appositive/,$(addsuffix .csv,$(WORKS_ARCHAIC)))
CSV_HELLENISTIC = $(addprefix corpus-appositive/,$(addsuffix .csv,$(WORKS_HELLENISTIC)))
CSV_IMPERIAL = $(addprefix corpus-appositive/,$(addsuffix .csv,$(WORKS_IMPERIAL)))

expectancy.sedes-work,metrical_shape.csv: $(CSV_ARCHAIC) $(CSV_HELLENISTIC) $(CSV_IMPERIAL) | sedes-var
	"$(SEDES)/src/expectancy" --by sedes/work,metrical_shape $^ > "$@"

expectancy.sedes-metrical_shape.archaic.csv: $(CSV_ARCHAIC) | sedes-var
expectancy.sedes-metrical_shape.archaic+hellenistic.csv: $(CSV_ARCHAIC) $(CSV_HELLENISTIC) | sedes-var
expectancy.sedes-metrical_shape.csv: $(CSV_ARCHAIC) $(CSV_HELLENISTIC) $(CSV_IMPERIAL) | sedes-var
expectancy.sedes-metrical_shape.archaic.csv \
expectancy.sedes-metrical_shape.archaic+hellenistic.csv \
expectancy.sedes-metrical_shape.csv \
:
	"$(SEDES)/src/expectancy" --by sedes/metrical_shape $^ > "$@"

joined.sedes-metrical_shape.csv:
	( \
		"$(SEDES)/src/join-expectancy" --by sedes/metrical_shape $(CSV_ARCHAIC) expectancy.sedes-metrical_shape.archaic.csv; # Keep the header line on the first one. \
		"$(SEDES)/src/join-expectancy" --by sedes/metrical_shape $(CSV_HELLENISTIC) expectancy.sedes-metrical_shape.archaic+hellenistic.csv | sed -e '1d'; \
		"$(SEDES)/src/join-expectancy" --by sedes/metrical_shape $(CSV_IMPERIAL) expectancy.sedes-metrical_shape.csv | sed -e '1d'; \
	) > "$@"

tables.html: .EXTRA_PREREQS = tables.py
tables.html: expectancy.sedes-work,metrical_shape.csv
	$(PYTHON) tables.py < "$<" > "$@"

summary-table.html: .EXTRA_PREREQS = summary-table.py
summary-table.html: expectancy.sedes-metrical_shape.csv
	$(PYTHON) summary-table.py < "$<" > "$@"

table-ssl.html: .EXTRA_PREREQS = table-ssl.py
table-ssl.html: expectancy.sedes-work,metrical_shape.csv
	$(PYTHON) table-ssl.py < "$<" > "$@"

unexpected-table.html: .EXTRA_PREREQS = unexpected-table.py
unexpected-table.html: joined.sedes-metrical_shape.csv
	$(PYTHON) unexpected-table.py < "$<" > "$@"

unexpected.txt \
unexpected-window-$(WINDOW_SIZE).archaic.png \
unexpected-window-$(WINDOW_SIZE)-cumul.archaic.png \
: .EXTRA_PREREQS = unexpected.r
unexpected.txt \
unexpected-window-$(WINDOW_SIZE).archaic.png \
unexpected-window-$(WINDOW_SIZE)-cumul.archaic.png \
&: joined.sedes-metrical_shape.csv
	Rscript unexpected.r > "$@"

.DELETE_ON_ERROR:

https://github.com/sasansom/sedes
2ec2a1240e75acec2588838f18e18220ecced9f1

Let the `$SEDES` environment variable point to the sedes clone.
Let this clone be the current working directory.

1. Generate original SEDES corpus/*.csv files.
   ```
   SEDES=/path/to/sedes
   (cd "$SEDES" && source venv/bin/activate && make clean && make -j4)
   ```
1. Merge appositive groups in the original files to make corpus-appositive/*.csv files.
   ```
   mkdir -p corpus-appositive/
   for work_csv in "$SEDES"/corpus/*.csv; do Rscript merge-appositives.r "$work_csv" > "corpus-appositive/$(basename "$work_csv")"; done
   ```
1. Compute expectancy of the appositive-group files.
   ```
   WORKS_ARCHAIC="iliad odyssey homerichymns theogony worksanddays shield"
   WORKS_HELLENISTIC="argonautica callimachushymns aratus theocritus"
   WORKS_IMPERIAL="quintussmyrnaeus nonnusdionysiaca"
   "$SEDES/src/expectancy" --by sedes/work,metrical_shape $(for work in $WORKS_ARCHAIC $WORKS_HELLENISTIC $WORKS_IMPERIAL; do echo "corpus-appositive/$work.csv"; done) > expectancy.sedes-work,metrical_shape.csv
   "$SEDES/src/expectancy" --by sedes/metrical_shape $(for work in $WORKS_ARCHAIC; do echo "corpus-appositive/$work.csv"; done) > expectancy.sedes-metrical_shape.archaic.csv
   "$SEDES/src/expectancy" --by sedes/metrical_shape $(for work in $WORKS_ARCHAIC $WORKS_HELLENISTIC; do echo "corpus-appositive/$work.csv"; done) > expectancy.sedes-metrical_shape.archaic+hellenistic.csv
   "$SEDES/src/expectancy" --by sedes/metrical_shape $(for work in $WORKS_ARCHAIC $WORKS_HELLENISTIC $WORKS_IMPERIAL; do echo "corpus-appositive/$work.csv"; done) > expectancy.sedes-metrical_shape.csv
   ("$SEDES/src/join-expectancy" --by sedes/metrical_shape $(for work in $WORKS_ARCHAIC; do echo "corpus-appositive/$work.csv"; done) expectancy.sedes-metrical_shape.archaic.csv; "$SEDES/src/join-expectancy" --by sedes/metrical_shape $(for work in $WORKS_HELLENISTIC; do echo "corpus-appositive/$work.csv"; done) expectancy.sedes-metrical_shape.archaic+hellenistic.csv | sed -e '1d'; "$SEDES/src/join-expectancy" --by sedes/metrical_shape $(for work in $WORKS_IMPERIAL; do echo "corpus-appositive/$work.csv"; done) expectancy.sedes-metrical_shape.csv | sed -e '1d') > joined.sedes-metrical_shape.csv
   ```
1. Generate tables and stats outputs.
   ```
   ./tables.py < expectancy.sedes-work,metrical_shape.csv > tables.html
   ./summary-table.py < expectancy.sedes-metrical_shape.csv > summary-table.html
   ./table-ssl.py < expectancy.sedes-work,metrical_shape.csv > table-ssl.html
   ./unexpected-table.py < joined.sedes-metrical_shape.csv > unexpected-table.html
   Rscript unexpected.r
   ```

## Known bugs

Both Firefox and Chrome fail to preserve non-breaking spaces
when copying selected text in the browser window.

In Firefox, the issue is discussed in:

* [359303 - Non-breaking spaces (nbsp) not copied as such](https://bugzilla.mozilla.org/show_bug.cgi?id=359303) (closed but without fixing the problem)
* [1769534 - Preserve non-breaking spaces when copying HTML content](https://bugzilla.mozilla.org/show_bug.cgi?id=1769534) (open as of 2024-01-01)

Chromium issue 887511 seems to suggest that Chrome
retains non-breaking spaces, but it does not work for me in
Chromium 120.0.6099.129.
A [Stack Overflow post](https://stackoverflow.com/a/73584742)
says there is a "well-known bug in both Gecko (Firefox) and Blink (Google Chrome)."

* [887511: Linux clipboard for text/plain contains U+00A0](https://bugs.chromium.org/p/chromium/issues/detail?id=887511)

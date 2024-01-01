https://github.com/sasansom/sedes
d6435a798ae02bff8af4c4fba84c11d22689cc43

In the sedes working directory:
```
make -j4
src/expectancy --by sedes/work,metrical_shape corpus/*.csv > expectancy.sedes-work,metrical_shape.csv
src/expectancy --by sedes/metrical_shape corpus/*.csv > expectancy.sedes-metrical_shape.csv
src/expectancy --by sedes/metrical_shape corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv > expectancy.sedes-metrical_shape.archaic.csv
src/expectancy --by sedes/metrical_shape corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv corpus/argonautica.csv corpus/callimachushymns.csv corpus/aratus.csv corpus/theocritus.csv > expectancy.sedes-metrical_shape.archaic+hellenistic.csv
(src/join-expectancy --by sedes/metrical_shape corpus/iliad.csv corpus/odyssey.csv corpus/homerichymns.csv corpus/theogony.csv corpus/worksanddays.csv corpus/shield.csv expectancy.sedes-metrical_shape.archaic.csv; src/join-expectancy --by sedes/metrical_shape corpus/argonautica.csv corpus/callimachushymns.csv corpus/aratus.csv corpus/theocritus.csv expectancy.sedes-metrical_shape.archaic+hellenistic.csv | sed -e '1d'; src/join-expectancy --by sedes/metrical_shape corpus/quintussmyrnaeus.csv corpus/nonnusdionysiaca.csv expectancy.sedes-metrical_shape.csv | sed -e '1d') > joined.sedes-metrical_shape.csv
```

In this working directory:
```
./tables.py < expectancy.sedes-work,metrical_shape.csv > tables.html
./summary-table.py < expectancy.sedes-metrical_shape.csv > summary-table.html
./table-ssl.py < expectancy.sedes-work,metrical_shape.csv > table-ssl.html
Rscript unexpected.r
./unexpected-table.py < joined.sedes-metrical_shape.csv > unexpected-table.html
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

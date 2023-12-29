https://github.com/sasansom/sedes
8fe7296ab179d1e0e25de75bbce406cdc4ca7290

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
```

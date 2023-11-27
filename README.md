https://github.com/sasansom/sedes
8fe7296ab179d1e0e25de75bbce406cdc4ca7290

In the sedes working directory:
```
make -j4
src/expectancy --by sedes/work,metrical_shape corpus/*.csv > expectancy.sedes-work,metrical_shape.csv
src/expectancy --by sedes/metrical_shape corpus/*.csv > expectancy.sedes-metrical_shape.csv
```

In this working directory:
```
./tables.py < expectancy.sedes-work,metrical_shape.csv > tables.html
./summary-table.py < expectancy.sedes-metrical_shape.csv > summary-table.html
```

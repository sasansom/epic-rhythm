Support data and programs for the article "Epic Rhythm: Metrical Shapes in Greek Hexameter" _Greek, Roman, and Byzantine Studies_ 64.3 ([forthcoming](https://grbs.library.duke.edu/index.php/grbs/forth)).

The Online Appendix can be found [here](https://sasansom.github.io/epic-rhythm/tables.html).

## Source data

The source data for analysis are the preprocessed corpus CSV files in the corpus directory.
They come from the
[sedes](https://github.com/sasansom/sedes) repository at commit
[2ec2a1240e75acec2588838f18e18220ecced9f1](https://github.com/sasansom/sedes/tree/2ec2a1240e75acec2588838f18e18220ecced9f1).
To recreate the source files:

```
$ cd sedes/
$ git checkout 2ec2a1240e75acec2588838f18e18220ecced9f1
$ (source venv/bin/activate && make clean && make -j4)
```

Then copy sedes/corpus/*.csv into the corpus directory here.


## Derived data

Processing the source data requires some programs from the sedes repository.
Set the `$SEDES` environment variable to the path to a
clone of the sedes repository.
It may be a relative path.

For example, if epic-rhythm is cloned next to sedes,

```
SEDES=../sedes/
```

Then run

```
make
```

Alternatively, you can provide the `$SEDES` path on the `make` command line,
rather than setting it as an environment variable:

```
make SEDES=../sedes/
```

Running `make` will produce the following output files:

* corpus-appositive/\*.csv: Corpus CSV files, but where the `word` column represents appositive groups, rather than single words.
* expectancy.sedes-work,metrical_shape.csv: Expectancy of sedes by work and metrical shape, in the complete appositive-group corpus.
* expectancy.sedes-metrical_shape.archaic.csv: Expectancy of sedes by metrical shape, in the Archaic corpus (iliad, odyssey, homerichymns, theogony, worksanddays, shield).
* expectancy.sedes-metrical_shape.archaic+hellenistic.csv: Expectancy of sedes by metrical shape, in the Archaic and Hellenistic corpus (Archaic plus argonautica, callimachushymns, aratus, theocritus).
* expectancy.sedes-metrical_shape.csv: Expectancy of sedes by metrical shape, in the complete appositive-group corpus (Archaic and Hellenistic plus quintussmyrnaeus, nonnusdionysiaca).
* joined.sedes-metrical_shape.csv: Appositive-group corpus joined with expectancy of sedes by metrical shape.
* tables.html: HTML tables of sedes expectancy by work, with one table for each metrical shape.
* summary-ssl.html: HTML table of sedes expectancy by work, for the metrical shape ⏑⏑– only (except from tables.html).
* summary-table.html: HTML table of sedes expectancy by metrical shape, over the complete appositive-group corpus.
* unexpected-table.html: HTML table of numbers and rates of unexpected metrical shapes per work, and the books with the highest and lowest rates.
* unexpected.txt: Various one-off calculations of rates of unexpected metrical shapes.
* Hom.Hymn.4-windows.png: Graph of unexpected shapes per window in *Hom.Hymn* 4.


## Known bugs

The HTML tables are meant to be copied and pasted
into a word processor.
They include non-breaking space characters where
text in a cell should not line-break.
But both Firefox and Chrome fail to preserve non-breaking spaces
when copying selected text in the browser window.
So you may have to patch up bad line breaks manually.

In Firefox, the issue is discussed in:

* [359303 - Non-breaking spaces (nbsp) not copied as such](https://bugzilla.mozilla.org/show_bug.cgi?id=359303) (closed but without fixing the problem)
* [1769534 - Preserve non-breaking spaces when copying HTML content](https://bugzilla.mozilla.org/show_bug.cgi?id=1769534) (open as of 2024-01-01)

Chromium issue 887511 seems to suggest that Chrome
retains non-breaking spaces, but it does not work for me in
Chromium 120.0.6099.129.
A [Stack Overflow post](https://stackoverflow.com/a/73584742)
says there is a "well-known bug in both Gecko (Firefox) and Blink (Google Chrome)."

* [887511: Linux clipboard for text/plain contains U+00A0](https://bugs.chromium.org/p/chromium/issues/detail?id=887511)

#!/usr/bin/env python3

import csv
import html
import re
import sys

import pandas as pd

import common

Z_THRESHOLD = -2.0

STYLE_TABLE = (
    ("border-collapse", "collapse"),
    ("border-spacing", "1pt"),
)
STYLE_LEFT = (
    ("text-align", "left"),
)
STYLE_CELL = (
    ("font-size", "9pt"),
    ("vertical-align", "top"),
    ("padding", "2pt"),
    ("line-height", "100%"),
    ("border", "solid 1pt black"),
) + STYLE_LEFT
STYLE_TH = (
    ("font-weight", "bold"),
) + STYLE_CELL

def parse_line_n(line_n):
    n, tag = re.match(r'^(\d+)(\w*)$', line_n).groups()
    return (int(n), tag)

data = pd.read_csv(sys.stdin, dtype = {
    "work": str,
    "book_n": str,
    "line_n": str,
    "word": str,
    "lemma": str,
    "sedes": float,
    "metrical_shape": str,
    "scanned": str,
    "num_scansions": int,
    "line_text": str,
    "x": int,
    "z": float,
}, usecols = [
    "work",
    "book_n",
    "line_n",
    "sedes",
    "metrical_shape",
    "x",
    "z",
])

data = (
    data
        .assign(
            num_words = 1,
            num_unexpected = lambda df: df["z"] <= Z_THRESHOLD,
        )
        .groupby(["work", "book_n"], dropna = False)
            .agg({"num_words": "size", "num_unexpected": "sum"})
        .reset_index()
        .assign(
            frac_unexpected = lambda df: df["num_unexpected"] / df["num_words"],
        )
)

work_data = (
    data
        .groupby(["work"], dropna = False)
            .agg({"num_words": "sum", "num_unexpected": "sum"})
        .reset_index()
        .assign(
            frac_unexpected = lambda df: df["num_unexpected"] / df["num_words"],
        )
)

print("""\
<html>
<head>
<meta charset=utf-8>
</head>
<body>
""")

print(common.html_start_tag_style("table", STYLE_TABLE))

print(common.html_start_tag("tr"))
print(
    common.html_start_tag_style("th", STYLE_TH + (("width", "28ex"),)) +
    html.escape("Work") +
    common.html_end_tag("th")
)
print(
    common.html_start_tag_style("th", STYLE_TH) +
    html.escape("Overall rate of unexpected metrical shapes") +
    common.html_end_tag("th")
)
print(
    common.html_start_tag_style("th", STYLE_TH) +
    html.escape("Book with lowest rate of unexpected metrical shapes") +
    common.html_end_tag("th")
)
print(
    common.html_start_tag_style("th", STYLE_TH) +
    html.escape("Book with highest rate of unexpected metrical shapes") +
    common.html_end_tag("th")
)
print(common.html_end_tag("tr"))

for work in common.KNOWN_WORKS:
    print(common.html_start_tag("tr"))
    print(
        common.html_start_tag_style("td", STYLE_CELL) +
        work.long_html_name +
        common.html_end_tag("td")
    )

    total = work_data.loc[work_data["work"] == work.id].iloc[0]
    print(common.html_start_tag_style("td", STYLE_CELL))
    print(f"{total['num_unexpected'] / total['num_words'] * 100:.02f}%\xa0({total['num_unexpected']:,}\u202f/\u202f{total['num_words']:,})")
    if work.id == "Hom.Hymn":
        # Special case: show Hom.Hymns 2–5 separately.
        print("<br>")
        sub = data.loc[data["work"] == work.id]
        sub = sub.loc[(2 <= sub["book_n"].apply(int)) & (sub["book_n"].apply(int) <= 5)]
        sub = sub.agg({"num_words": "sum", "num_unexpected": "sum"})
        print(f"{sub['num_unexpected'] / sub['num_words'] * 100:.02f}%\xa0({sub['num_unexpected']:,}\u202f/\u202f{sub['num_words']:,})\xa0[<i>Hy.</i>\xa02–5]")
    print(common.html_end_tag("td"))

    books = data.loc[data["work"] == work.id]
    if len(books) <= 1:
        print(
            common.html_start_tag_style("td", STYLE_CELL) +
            html.escape("-") +
            common.html_end_tag("td")
        )
        print(
            common.html_start_tag_style("td", STYLE_CELL) +
            html.escape("-") +
            common.html_end_tag("td")
        )
    else:
        for fn in (pd.Series.min, pd.Series.max):
            vals = (
                books
                    .loc[books["frac_unexpected"] == fn(books["frac_unexpected"])]
                    .sort_values(by = "book_n", key = lambda v: v.apply(int))
            )
            parts = []
            for _, row in vals.iterrows():
                parts.append(f"{row['num_unexpected'] / row['num_words'] * 100:.02f}%\xa0({row['num_unexpected']:,}\u202f/\u202f{row['num_words']:,})\xa0{work.segment_html_name}\xa0{row['book_n']}")
            print(
                common.html_start_tag_style("td", STYLE_CELL) +
                "<br>".join(parts) +
                common.html_end_tag("td")
            )

    print(common.html_end_tag("tr"))

print(common.html_end_tag("table"))

print("""\
</body>
</html>
""")

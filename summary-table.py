#!/usr/bin/env python3

import collections
import csv
import html
import sys

import common

STYLE_TABLE = (
    ("border-collapse", "collapse"),
    ("border-spacing", "1pt"),
)
STYLE_X = (
    ("font-size", "8pt"),
)
STYLE_Z = (
    ("font-size", "7pt"),
)
STYLE_PERCENT = (
    ("font-size", "7pt"),
)
STYLE_CELL = (
    ("font-size", "8pt"),
    ("vertical-align", "middle"),
    ("padding", "1pt"),
    ("min-width", "28pt"),
    ("line-height", "100%"),
    ("border", "solid 1pt #d3d3d3"),
)
STYLE_IMPERMISSIBLE = (
    ("color", "#d3d3d3"),
    ("text-align", "center"),
    ("background-color", "cornsilk"),
) + STYLE_CELL
STYLE_HEADER = (
    ("background-color", "lavender"),
) + STYLE_CELL
STYLE_TH = (
    ("font-weight", "bold"),
) + STYLE_HEADER
STYLE_LEFT = (
    ("text-align", "left"),
)
STYLE_RIGHT = (
    ("text-align", "right"),
)

Entry = collections.namedtuple("Entry", ("x", "z"))

M = {}
r = csv.DictReader(sys.stdin)
for row in r:
    key = (row["metrical_shape"], float(row["sedes"]))
    assert key not in M
    M[key] = Entry(int(row["x"]), float(row["z"]) if row["z"] != "" else None)

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
    common.html_start_tag_style("th", STYLE_TH + STYLE_LEFT) +
    html.escape("Shape") +
    common.html_end_tag("th")
)
for sedes in common.KNOWN_SEDES:
    print(
        common.html_start_tag_style("th", STYLE_TH + STYLE_RIGHT) +
        html.escape(sedes) +
        common.html_end_tag("th")
    )
print(
    common.html_start_tag_style("th", STYLE_TH + STYLE_RIGHT) +
    "Total&nbsp;(Σ<var>x</var>)" +
    common.html_end_tag("th")
)
print(common.html_end_tag("tr"))

for shape in common.shapes_gen():
    if len(shape) > 12:
        break

    xvec = []
    for sedes in map(float, common.KNOWN_SEDES):
        entry = M.get((shape, sedes))
        if entry is not None:
            xvec.append(entry.x)

    if sum(xvec) == 0:
        for sedes in map(float, common.KNOWN_SEDES):
            assert M.get((shape, sedes)) is None, (shape, sedes)
        continue

    if not common.is_metrically_permissible_anywhere(shape):
        assert sum(xvec) == 0, xvec

    print(common.html_start_tag("tr"))
    print(
        common.html_start_tag_style("td", STYLE_HEADER + STYLE_LEFT) +
        html.escape(' '.join(shape)) +
        common.html_end_tag("td")
    )
    for sedes in map(float, common.KNOWN_SEDES):
        entry = M.get((shape, sedes))
        if not common.is_metrically_permissible(shape, sedes):
            assert entry is None, entry
            print(
                common.html_start_tag_style("td", STYLE_IMPERMISSIBLE) +
                html.escape("✖") +
                common.html_end_tag("td")
            )
        else:
            if entry is None:
                entry = Entry(0, common.expectancy(0, xvec))
            try:
                del M[(shape, sedes)]
            except KeyError:
                pass
            contents = ""
            contents += (
                common.html_start_tag_style("span", STYLE_X) +
                html.escape(f"{entry.x:,}") +
                common.html_end_tag("span")
            )
            contents += common.html_start_tag("br")
            if sum(xvec) > 0:
                contents += (
                    common.html_start_tag_style("span", STYLE_PERCENT) +
                    html.escape(f"({entry.x/sum(xvec)*100:.1f}%)") +
                    common.html_end_tag("span")
                )
            else:
                contents += "\u200c"
            contents += common.html_start_tag("br")
            if entry.z is not None:
                contents += (
                    common.html_start_tag_style("span", STYLE_Z) +
                    html.escape("{:+.02f}".format(entry.z).replace("-", "−")) +
                    common.html_end_tag("span")
                )
            else:
                contents += "\u200c"
            print(
                common.html_start_tag_style("td", STYLE_CELL + common.z_css(entry.z) + STYLE_RIGHT) +
                contents +
                common.html_end_tag("td")
            )
    print(common.html_start_tag_style("td", STYLE_CELL + STYLE_RIGHT))
    print(
        common.html_start_tag_style("span", STYLE_X) +
        html.escape('{:,}'.format(sum(xvec))) +
        common.html_end_tag("span")
    )
    print(common.html_end_tag("td"))
    print("</tr>")
assert len(M) == 0, M

print(common.html_end_tag("table"))

print("""\
</body>
</html>
""")

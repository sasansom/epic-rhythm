#!/usr/bin/env python3

import collections
import csv
import html
import sys

import common

STYLE_X = (
    ("font-size", "small"),
)
STYLE_Z = (
    ("font-size", "x-small"),
)
STYLE_CELL = (
    ("vertical-align", "middle"),
    ("padding", "1pt"),
    ("min-width", "28pt"),
)
STYLE_IMPERMISSIBLE = (
    ("color", "lightgray"),
    ("text-align", "center"),
    ("background-color", "cornsilk"),
    ("font-size", "inherit"),
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

print(common.html_start_tag("table"))
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
    html.escape("Total") +
    common.html_end_tag("th")
)
print(common.html_end_tag("tr"))

for shape in common.shapes_gen():
    if len(shape) > 8:
        break
    if not common.is_metrically_permissible_anywhere(shape):
        print("<!--")
        for sedes in map(float, common.KNOWN_SEDES):
            assert M.get((shape, sedes)) is None, (shape, sedes)
    print(common.html_start_tag("tr"))
    print(
        common.html_start_tag_style("td", STYLE_HEADER + STYLE_LEFT) +
        html.escape(' '.join(shape)) +
        common.html_end_tag("td")
    )
    xvec = []
    for sedes in map(float, common.KNOWN_SEDES):
        entry = M.get((shape, sedes))
        if entry is not None:
            xvec.append(entry.x)
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
            contents = common.html_start_tag_style("span", STYLE_X) + html.escape(f"{entry.x:,}") + common.html_end_tag("span")
            if entry.z is not None:
                contents += (
                    common.html_start_tag("br") +
                    common.html_start_tag_style("span", STYLE_Z) +
                    html.escape("{:+.03f}".format(entry.z).replace("-", "−")) +
                    common.html_end_tag("span")
                )
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
    if not common.is_metrically_permissible_anywhere(shape):
        print("-->")
assert len(M) == 0, M

print(common.html_end_tag("table"))

print("""\
</body>
</html>
""")

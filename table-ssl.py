#!/usr/bin/env python3

# Outputs a table for SHAPE, in the style of Table 1 in the paper:
# - includes a percentage with each x count
# - sedes following the anchor sedes are also colored, for as far as SHAPE
#   reaches.

import collections
import csv
import html
import sys

import common

SHAPE = "⏑⏑–"

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
    ("min-width", "12pt"),
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

# Format 1.0 as "100%", other less percentages with 1 digit of precision.
def format_percent(x):
    if x >= 1.0:
        return f"{x*100:g}%"
    else:
        return f"{x*100:.1f}%"

Entry = collections.namedtuple("Entry", ("x", "z"))

M = {}
r = csv.DictReader(sys.stdin)
for row in r:
    key = (row["metrical_shape"], row["work"], float(row["sedes"]))
    assert key not in M
    M[key] = Entry(int(row["x"]), float(row["z"]) if row["z"] != "" else None)

def metrical_length(shape):
    return sum({"⏑": 0.5, "–": 1.0}[c] for c in shape)

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
    html.escape("Work") +
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

for sedes in map(float, common.KNOWN_SEDES):
    if common.is_metrically_permissible(SHAPE, sedes):
        M[(SHAPE, "total", sedes)] = Entry(0, 0)

for work in common.KNOWN_WORKS + (common.Work("total", "TOTAL", "TOTAL", "Book"),):
    print(common.html_start_tag("tr"))
    print(
        common.html_start_tag_style("td", STYLE_HEADER + STYLE_LEFT) +
        work.html_name +
        common.html_end_tag("td")
    )

    xvec = []
    for sedes in map(float, common.KNOWN_SEDES):
        entry = M.get((SHAPE, work.id, sedes))
        if entry is not None:
            xvec.append(entry.x)

    recent_sedes = None
    recent_entry = None
    for sedes in map(float, common.KNOWN_SEDES):
        styles = []
        entry = M.get((SHAPE, work.id, sedes))
        if not common.is_metrically_permissible(SHAPE, sedes):
            assert entry is None, entry
            if recent_entry is not None and sedes - recent_sedes < metrical_length(SHAPE):
                styles.extend(common.z_css(recent_entry.z))
                styles.extend(STYLE_CELL)
                styles.append(("border-left-style", "dashed"))
                styles.append(("border-right-style", "none"))
                contents = ""
            else:
                styles.extend(STYLE_IMPERMISSIBLE)
                contents = html.escape("✖")
        else:
            if entry is None:
                entry = Entry(0, common.expectancy(0, xvec))
            try:
                del M[(SHAPE, work.id, sedes)]
            except KeyError:
                pass
            if work.id != "total":
                M[(SHAPE, "total", sedes)] = Entry(M[(SHAPE, "total", sedes)].x + entry.x, 0)
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
                    html.escape(format_percent(entry.x/sum(xvec))) +
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
            styles.extend(common.z_css(entry.z))
            styles.extend(STYLE_CELL)
            styles.extend(STYLE_RIGHT)
            try:
                next_sedes = float(common.KNOWN_SEDES[common.KNOWN_SEDES.index(f"{sedes:g}") + 1])
                if not common.is_metrically_permissible(SHAPE, next_sedes) and next_sedes - sedes < metrical_length(SHAPE):
                    styles.append(("border-right-style", "none"))
            except ValueError:
                pass
            recent_sedes = sedes
            recent_entry = entry
        print(
            common.html_start_tag_style("td", styles) +
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
    print(common.html_end_tag("tr"))

    total_xvec = []
    for sedes in map(float, common.KNOWN_SEDES):
        try:
            total_xvec.append(M[(SHAPE, "total", sedes)].x)
        except KeyError:
            pass
    for sedes in map(float, common.KNOWN_SEDES):
        try:
            M[(SHAPE, "total", sedes)] = Entry(M[(SHAPE, "total", sedes)].x, common.expectancy(M[(SHAPE, "total", sedes)].x, total_xvec))
        except KeyError:
            pass
print("</table>")

print("""\
</body>
</html>
""")

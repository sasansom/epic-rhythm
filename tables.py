#!/usr/bin/env python3

import collections
import csv
import html
import sys

import common

Entry = collections.namedtuple("Entry", ("x", "z"))

M = {}
r = csv.DictReader(sys.stdin)
for row in r:
    key = (row["metrical_shape"], row["work"], float(row["sedes"]))
    assert key not in M
    M[key] = Entry(int(row["x"]), float(row["z"]) if row["z"] != "" else None)

print("""\
<html>
<head>
<meta charset=utf-8>
<style>
th, td {
    padding: 0 0.5ex;
    width: 5ex;
    vertical-align: top;
}
th {
    background-color: lavender;
    font-weight: bold;
}
tr th:first-child, tr td:first-child {
    background-color: lavender;
    text-align: left;
}
th, tr td {
    text-align: right;
}
td.impermissible {
    color: lightgray;
    text-align: center;
    background-color: cornsilk;
    font-size: inherit;
    vertical-align: middle;
}
.x {
    font-size: small;
}
.z {
    font-size: x-small;
}
</style>
</head>
<body>
""")

for shape in common.shapes_gen():
    if len(shape) > 8:
        break

    if not common.is_metrically_permissible_anywhere(shape):
        print("<!--")
        for work in common.KNOWN_WORKS:
            for sedes in map(float, common.KNOWN_SEDES):
                assert M.get((shape, work, sedes)) is None, (shape, work, sedes)

    print(f"<h2 id=\"shape-{html.escape(shape)}\">{html.escape(' '.join(shape) if shape else '(empty shape)')}</h2>")

    print("<table>")
    print("<tr>")
    print("<th>Work</th>")
    for sedes in common.KNOWN_SEDES:
        print(f"<th>{html.escape(sedes)}</th>")
    print("<th>Total</th>")
    print("</tr>")

    print("<tr>")
    for work in common.KNOWN_WORKS:
        print(f"<td>{html.escape(work)}</td>")
        xvec = []
        for sedes in map(float, common.KNOWN_SEDES):
            entry = M.get((shape, work, sedes))
            if entry is not None:
                xvec.append(entry.x)
        for sedes in map(float, common.KNOWN_SEDES):
            entry = M.get((shape, work, sedes))
            if not common.is_metrically_permissible(shape, sedes):
                assert entry is None, entry
                print("<td class=impermissible>✖</td>")
            else:
                if entry is None:
                    entry = Entry(0, common.expectancy(0, xvec))
                try:
                    del M[(shape, work, sedes)]
                except KeyError:
                    pass
                contents = "<span class=x>" + html.escape("{:,}".format(entry.x)) + "</span>"
                if entry.z is not None:
                    contents += "<br><span class=z>" + html.escape("{:+.03f}".format(entry.z).replace("-", "−")) + "</span>"
                print(f"<td style=\"{html.escape(common.z_css(entry.z))}\">{contents}</td>")
        print(f"<td><span class=x>{html.escape('{:,}'.format(sum(xvec)))}</span></td>")
        print("</tr>")
    print("</table>")

    if not common.is_metrically_permissible_anywhere(shape):
        print("-->")
assert len(M) == 0, M

print("""\
</body>
</html>
""")

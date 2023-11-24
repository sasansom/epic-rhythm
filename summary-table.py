#!/usr/bin/env python3

import collections
import csv
import html
import math
import sys

import common

# Colors for low-to-high color scale.
COLOR_LOW  = (0x00, 0x00, 0x00)
COLOR_HIGH = (0xe6, 0xe6, 0xe6)

# Increase this to increase the steepness of the tone mapping operation.
SHADE_MAPPING_ADJUST = 1.5

# Text on a background of luminance less than this will be displayed as
# light-on-dark rather than dark-on-light.
LUMINANCE_INVERSION_THRESHOLD = 0.2

def srgb_component_to_linear(s):
    # https://en.wikipedia.org/wiki/SRGB#The_reverse_transformation
    u = s / 255.0
    if u <= 0.04045:
        return u / 12.92
    else:
        return math.pow((u + 0.055)/1.055, 12.0/5.0)

def linear_component_to_srgb(u):
    # https://en.wikipedia.org/wiki/SRGB#The_forward_transformation_(CIE_XYZ_to_sRGB)
    if u <= 0.0031308:
        s = 12.92 * u
    else:
        s = 1.055 * math.pow(u, 5.0/12.0) - 0.055
    return int(s * 255 + 0.5)

def srgb_to_linear(sr, sg, sb):
    return tuple(srgb_component_to_linear(c) for c in (sr, sg, sb))

def linear_to_srgb(r, g, b):
    return tuple(linear_component_to_srgb(u) for u in (r, g, b))

def interpolate_srgb(x, s1, s2):
    return linear_to_srgb(*((1.0 - x) * u1 + x * u2 for (u1, u2) in zip(srgb_to_linear(*s1), srgb_to_linear(*s2))))

def srgb_luminance(sr, sg, sb):
    # https://en.wikipedia.org/wiki/Relative_luminance#Relative_luminance_in_colorimetric_spaces
    r, g, b = srgb_to_linear(sr, sg, sb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;

def tone_map(z):
    # Logistic function.
    return 1.0 / (1.0 + math.exp(-z * SHADE_MAPPING_ADJUST))

def css_color(sr, sg, sb):
    return f"#{sr:02x}{sg:02x}{sb:02x}"

def z_css(z):
    if z is None:
        z = 0.0
    srgb = interpolate_srgb(tone_map(z), COLOR_LOW, COLOR_HIGH)
    return "; ".join((
        "background-color:" + css_color(*srgb),
        "color:" + "white" if srgb_luminance(*srgb) < LUMINANCE_INVERSION_THRESHOLD else "black",
    ))

# Return the mean of the sequence that arises from repeating each element e of
# x, e times.
def weighted_mean(x):
    return sum(e*e for e in x) / sum(x)

# Weighted population standard deviation, as in weighted_mean.
def weighted_sd_pop(x):
    μ = weighted_mean(x)
    return math.sqrt(sum(e*(e - μ)**2 for e in x) / sum(x))

Entry = collections.namedtuple("Entry", ("x", "z"))

def shapes_gen_sub(length):
    if length <= 0:
        yield ""
    else:
        for x in shapes_gen_sub(length - 1):
            yield "–" + x
        for x in shapes_gen_sub(length - 1):
            yield "⏑" + x

def shapes_gen():
    i = 0
    while True:
        yield from shapes_gen_sub(i)
        i += 1

def is_metrically_permissible_anywhere(shape):
    return any(common.is_metrically_permissible(shape, sedes) for sedes in map(float, common.KNOWN_SEDES))

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

print("<table>")
print("<tr>")
print("<th>Shape</th>")
for sedes in common.KNOWN_SEDES:
    print(f"<th>{html.escape(sedes)}</th>")
print("<th>Total</th>")
print("</tr>")

for shape in shapes_gen():
    if len(M) == 0:
        break
    if not is_metrically_permissible_anywhere(shape):
        print("<!--")
        for sedes in map(float, common.KNOWN_SEDES):
            assert M.get((shape, sedes)) is None, (shape, sedes)
    print("<tr>")
    print(f"<td>{html.escape(' '.join(shape))}</td>")
    xvec = []
    for sedes in map(float, common.KNOWN_SEDES):
        entry = M.get((shape, sedes))
        if entry is not None:
            xvec.append(entry.x)
    for sedes in map(float, common.KNOWN_SEDES):
        entry = M.get((shape, sedes))
        if not common.is_metrically_permissible(shape, sedes):
            assert entry is None, entry
            print("<td class=impermissible>✖</td>")
        else:
            if entry is None:
                if sum(xvec) > 0:
                    μ = weighted_mean(xvec)
                    σ = weighted_sd_pop(xvec)
                    z = None if σ == 0.0 else (0 - μ) / σ
                else:
                    z = None
                entry = Entry(0, z)
            try:
                del M[(shape, sedes)]
            except KeyError:
                pass
            contents = "<span class=x>" + html.escape("{:,}".format(entry.x)) + "</span>"
            if entry.z is not None:
                contents += "<br><span class=z>" + html.escape("{:+.03f}".format(entry.z).replace("-", "−")) + "</span>"
            print(f"<td style=\"{html.escape(z_css(entry.z))}\">{contents}</td>")
    print(f"<td><span class=x>{html.escape('{:,}'.format(sum(xvec)))}</span></td>")
    print("</tr>")
    if not is_metrically_permissible_anywhere(shape):
        print("-->")
assert len(M) == 0, M

print("</table>")

print("""\
</body>
</html>
""")

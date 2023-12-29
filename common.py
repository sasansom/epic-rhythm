import collections
import html
import itertools
import math

KNOWN_SEDES = ("1", "2", "2.5", "3", "4", "4.5", "5", "6", "6.5", "7", "8", "8.5", "9", "10", "10.5", "11", "12")

Work = collections.namedtuple("Work", ("id", "html_name"))
KNOWN_WORKS = (
    Work("Il.", "<i>Iliad</i>"),
    Work("Od.", "<i>Odyssey</i>"),
    Work("Hom.Hymn", "<i>Hom.&nbsp;Hymns</i>"),
    Work("Theog.", "<i>Theog.</i>"),
    Work("W.D.", "<i>WD</i>"),
    Work("Sh.", "<i>Shield</i>"),
    Work("Argon.", "<i>Argon.</i>"),
    Work("Callim.Hymn", "Callim.&nbsp;<i>Hymns</i>"),
    Work("Phaen.", "<i>Phaen.</i>"),
    Work("Theoc.", "Theoc."),
    Work("Q.S.", "Quint.&nbsp;Smyrn."),
    Work("Dion.", "<i>Dion.</i>"),
)

def is_metrically_permissible(shape, sedes):
    """Returns True iff shape is metrically permitted at sedes."""
    s = (sedes - 1) * 2
    if s != int(s) or s < 0 or s > 24:
        raise ValueError("invalid sedes {sedes}")
    if s == 23 or s % 4 not in (0, 2, 3):
        return False
    for c in shape:
        s += {"⏑": 1, "–": 2}[c]
        if s > 24 or s == 23 or s % 4 not in (0, 2, 3):
            return False
    return True

def is_metrically_permissible_anywhere(shape):
    return any(is_metrically_permissible(shape, sedes) for sedes in map(float, KNOWN_SEDES))

def shapes_gen_length(length):
    if length <= 0:
        yield ""
    else:
        for x in shapes_gen_length(length - 1):
            yield "–" + x
        for x in shapes_gen_length(length - 1):
            yield "⏑" + x

def shapes_gen():
    i = 0
    while True:
        yield from shapes_gen_length(i)
        i += 1

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
    return (
        ("background-color", css_color(*srgb)),
        ("color", ("white" if srgb_luminance(*srgb) < LUMINANCE_INVERSION_THRESHOLD else "black")),
    )

# Return the mean of the sequence that arises from repeating each element e of
# x, e times.
def weighted_mean(x):
    return sum(e*e for e in x) / sum(x)

# Weighted population standard deviation, as in weighted_mean.
def weighted_sd_pop(x):
    μ = weighted_mean(x)
    return math.sqrt(sum(e*(e - μ)**2 for e in x) / sum(x))

def expectancy(x, xvec):
    if sum(xvec) > 0:
        μ = weighted_mean(xvec)
        σ = weighted_sd_pop(xvec)
        z = None if σ == 0.0 else (x - μ) / σ
    else:
        z = None
    return z

# https://html.spec.whatwg.org/multipage/syntax.html#start-tags
def html_start_tag(name, attrs = ()):
    return "<" + name + "".join(" " + key + "=\"" + html.escape(value) + "\"" for key, value in attrs) + ">"

# https://html.spec.whatwg.org/multipage/syntax.html#end-tags
def html_end_tag(name):
    return "</" + name + ">"

# https://www.w3.org/TR/css-syntax-3/#escape-codepoint
# https://mathiasbynens.be/notes/css-escapes
def css_escape_codepoint(c):
    return f"\\{ord(c):x} "

def css_escape_predicate(s, needs_escaping):
    return "".join(c if not needs_escaping(c) else css_escape_codepoint(c) for c in s)

def css_escape_ident(s):
    escaped = []
    first = True
    for c in s:
        # https://www.w3.org/TR/css-syntax-3/#ident-start-code-point
        # https://www.w3.org/TR/css-syntax-3/#ident-code-point
        if (first and not c.isalpha()) or (not first and not (c.isalnum() or c == "-")):
            c = css_escape_codepoint(c)
        escaped.append(c)
        first = False
    return "".join(escaped)

def css_escape_value(s):
    return "".join(c if not (c == ";" or c == "\\") else css_escape_codepoint(c) for c in s)

def html_start_tag_style(name, style = (), attrs = ()):
    return html_start_tag(name, itertools.chain(
        attrs,
        (("style", " ".join(css_escape_ident(property) + ": " + css_escape_value(value) + ";" for property, value in style)),),
    ))

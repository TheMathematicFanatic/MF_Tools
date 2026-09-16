"""
Normalize dvisvgm SVG output (as produced by manimgl's Tex) for morphing.

normalize_svg(svg) applies both steps below:

1. merge_extensible_delimiters: multi-piece delimiters -> single glyphs.
2. normalize_glyph_outlines: canonical contour direction, start point
and contour order for every glyph path.

Merge TeX extensible delimiters in dvisvgm output into single glyph paths.

When TeX needs a delimiter taller than the largest single glyph in the
extension font (cmex10 and friends), it assembles it from pieces:

	top piece, repeater x n, [middle piece, repeater x n], bottom piece

This covers tall parentheses, brackets, braces, vertical bars, arrows and
radical signs. dvisvgm writes each piece as its own <use> element, so manim turns each one
into its own submobject. merge_extensible_delimiters() finds those runs,
unions the pieces into one closed outline with skia-pathops, adds it to
<defs>, and replaces the run with a single <use>. Everything else in the file
is left byte-for-byte unchanged.

Requires: skia-pathops, fonttools (both are manimgl dependencies).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pathops
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path

__all__ = ["merge_extensible_delimiters", "normalize_glyph_outlines", "normalize_tex_svg_globally"]

# Extensible recipes in TeX's OMX encoding (Computer Modern, Latin Modern, ...),
# as listed in cmex10.tfm (checked with tftopl).
# name: (top, middle, bottom, repeater); None means the recipe has no such piece.
OMX_RECIPES: dict[str, tuple[int | None, int | None, int | None, int]] = {
	"(": (48, None, 64, 66),
	")": (49, None, 65, 67),
	"[": (50, None, 52, 54),
	"]": (51, None, 53, 55),
	"lfloor": (None, None, 52, 54),
	"rfloor": (None, None, 53, 55),
	"lceil": (50, None, None, 54),
	"rceil": (51, None, None, 55),
	"{": (56, 60, 58, 62),
	"}": (57, 61, 59, 62),
	"lgroup": (56, None, 58, 62),
	"rgroup": (57, None, 59, 62),
	"lmoustache": (56, None, 59, 62),
	"rmoustache": (57, None, 58, 62),
	"|": (None, None, None, 12),        # \left| \right|, \vert
	"||": (None, None, None, 13),       # \left\| \right\|, \Vert
	"arrowvert": (None, None, None, 63),
	"Arrowvert": (None, None, None, 119),
	"bracevert": (None, None, None, 62),
	"uparrow": (120, None, None, 63),
	"downarrow": (None, None, 121, 63),
	"updownarrow": (120, None, 121, 63),
	"Uparrow": (126, None, None, 119),
	"Downarrow": (None, None, 127, 119),
	"Updownarrow": (126, None, 127, 119),
	# Radical sign (everything except the overbar, which is a separate <rect>).
	"sqrt": (118, None, 116, 117),
}

DEFAULT_DELIMITERS = tuple(OMX_RECIPES)
SEAM_MARGIN = 0.1  # pt; how far beyond a piece overlap seam cleanup may reach

_USE_RE = re.compile(
	r"<use x='(?P<x>[^']*)' y='(?P<y>[^']*)' xlink:href='#(?P<id>g(?P<font>\d+)-(?P<slot>\d+))'/>"
)
_PATH_RE = re.compile(r"<path id='(?P<id>[^']*)' d='(?P<d>[^']*)'/>")


@dataclass
class _Use:
	x: float
	y: float
	glyph_id: str
	font: int
	slot: int


def _fmt(v: float) -> str:
	"""Format a number the way dvisvgm does: <=6 decimals, no trailing zeros,
	no leading zero before the decimal point."""
	s = f"{v:.6f}".rstrip("0").rstrip(".")
	if s in ("-0", ""):
		s = "0"
	if s.startswith("0."):
		s = s[1:]
	elif s.startswith("-0."):
		s = "-" + s[2:]
	return s


class _SVGPathWriter:
	"""Pen that writes an SVG path string in dvisvgm's compact style."""

	def __init__(self):
		self.parts: list[str] = []

	def _cmd(self, letter: str, *pts):
		out = letter
		for x, y in pts:
			for n in (_fmt(x), _fmt(y)):
				if out[-1].isalpha() or n.startswith("-"):
					out += n
				else:
					out += " " + n
		self.parts.append(out)

	def moveTo(self, pt):
		self._cmd("M", pt)

	def lineTo(self, pt):
		self._cmd("L", pt)

	def curveTo(self, *pts):
		self._cmd("C", *pts)

	def qCurveTo(self, *pts):
		# skia-pathops yields one off-curve point per quadratic segment
		for i in range(0, len(pts) - 1):
			ctrl = pts[i]
			end = pts[i + 1] if i == len(pts) - 2 else (
				((pts[i][0] + pts[i + 1][0]) / 2, (pts[i][1] + pts[i + 1][1]) / 2)
			)
			self._cmd("Q", ctrl, end)

	def closePath(self):
		self.parts.append("Z")

	def endPath(self):
		pass

	def d(self) -> str:
		return "".join(self.parts)


class _RecordingPen:
	def __init__(self):
		self.contours: list[list[tuple[str, tuple]]] = []

	def moveTo(self, pt):
		self.contours.append([("M", (pt,))])

	def lineTo(self, pt):
		self.contours[-1].append(("L", (pt,)))

	def curveTo(self, *pts):
		self.contours[-1].append(("C", pts))

	def qCurveTo(self, *pts):
		self.contours[-1].append(("Q", pts))

	def closePath(self):
		self.contours[-1].append(("Z", ()))

	def endPath(self):
		pass


def _replay(contour, pen):
	for cmd, pts in contour:
		if cmd == "M":
			pen.moveTo(*pts)
		elif cmd == "L":
			pen.lineTo(*pts)
		elif cmd == "C":
			pen.curveTo(*pts)
		elif cmd == "Q":
			pen.qCurveTo(*pts)
		else:
			pen.closePath()


def _dist_to_chord(p, a, b):
	ax, ay = a
	dx, dy = b[0] - ax, b[1] - ay
	L2 = dx * dx + dy * dy
	if L2 == 0:
		return ((p[0] - ax) ** 2 + (p[1] - ay) ** 2) ** 0.5
	t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
	return ((p[0] - ax - t * dx) ** 2 + (p[1] - ay - t * dy) ** 2) ** 0.5


def _flatten_seams(contour, eps, bands):
	"""Within the seam bands (y-intervals where two pieces overlap), replace
	maximal runs of segments that deviate less than `eps` from a straight
	chord with a single line segment. This removes the microscopic notches
	left where extensible pieces meet; geometry outside the bands is never
	touched."""
	def in_band(q):
		return any(lo <= q[1] <= hi for lo, hi in bands)

	start = contour[0][1][0]
	closed = contour[-1][0] == "Z"
	segs = [s for s in contour[1:] if s[0] != "Z"]
	out = [("M", (start,))]
	cur = start
	i = 0
	while i < len(segs):
		best = None
		pts = []
		for j in range(i, len(segs)):
			pts.extend(segs[j][1])
			end = segs[j][1][-1]
			if not (in_band(cur) and all(in_band(q) for q in pts)):
				break
			if all(_dist_to_chord(q, cur, end) <= eps for q in pts):
				best = j
			elif sum(len(s[1]) for s in segs[i:j + 1]) > 64:
				break
		if best is None:
			out.append(segs[i])
			cur = segs[i][1][-1]
			i += 1
		else:
			end = segs[best][1][-1]
			out.append(("L", (end,)))
			cur = end
			i = best + 1
	# Merge consecutive line segments that are collinear.
	merged_out = [out[0]]
	for seg in out[1:]:
		if (seg[0] == "L" and merged_out[-1][0] == "L" and len(merged_out) > 1
				and _dist_to_chord(merged_out[-1][1][0], _seg_start(merged_out), seg[1][0]) < 1e-6):
			merged_out[-1] = seg
		else:
			merged_out.append(seg)
	if closed:
		merged_out.append(("Z", ()))
	return merged_out


def _seg_start(segs):
	"""Start point of the last segment in a list of recorded segments."""
	return segs[-2][1][-1]


def _recipe_matcher(names):
	"""Build one regex per chosen delimiter, over comma-joined slot sequences."""
	alts = []
	for name in names:
		top, mid, bot, rep = OMX_RECIPES[name]
		r = f"(?:{rep},)*"
		pat = ""
		if top is not None:
			pat += f"{top},"
		pat += r
		if mid is not None:
			pat += f"{mid}," + r
		if bot is not None:
			pat += f"{bot},"
		alts.append(re.compile(pat))
	return alts


def _bbox_y(d: str) -> tuple[float, float]:
	p = pathops.Path()
	parse_path(d, p.getPen())
	_, ymin, _, ymax = p.bounds
	return ymin, ymax


def merge_extensible_delimiters(
	svg: str,
	delimiters=DEFAULT_DELIMITERS,
	tol: float = 1e-3,
	seam_eps: float = 0.01,
	clockwise: bool = True,
) -> str:
	"""Return a copy of a dvisvgm SVG string with each multi-piece extensible
	delimiter replaced by a single merged glyph.

	delimiters: names from OMX_RECIPES to merge; default is all of them.
	tol: tolerance (pt) for "same x" and for pieces touching vertically.
	seam_eps: near the joins between pieces, nearly-straight runs deviating
		less than this (pt) are replaced by straight lines, removing tiny
		notches. Geometry away from the joins is untouched. 0 disables.
	clockwise: outer-contour direction of the merged path (in SVG's y-down
		coordinates this matches dvisvgm's glyphs, which keeps manim's
		cubic-to-quadratic conversion behaving the same as on the pieces).
	"""
	defs = {m["id"]: m["d"] for m in _PATH_RE.finditer(svg)}
	lines = svg.split("\n")
	uses = {}
	for i, line in enumerate(lines):
		m = _USE_RE.fullmatch(line.strip())
		if m:
			uses[i] = _Use(float(m["x"]), float(m["y"]), m["id"], int(m["font"]), int(m["slot"]))

	matcher = _recipe_matcher(delimiters)
	replacements: dict[int, str | None] = {}   # line index -> new text (None = delete)
	new_defs: dict[str, str] = {}              # merged id -> d
	d_to_id: dict[str, str] = {}

	idxs = sorted(uses)
	k = 0
	while k < len(idxs):
		# Grow a run of consecutive <use> lines with the same font and x.
		run = [idxs[k]]
		while (
			k + len(run) < len(idxs)
			and idxs[k + len(run)] == run[-1] + 1
			and uses[idxs[k + len(run)]].font == uses[run[0]].font
			and abs(uses[idxs[k + len(run)]].x - uses[run[0]].x) < tol
		):
			run.append(idxs[k + len(run)])

		piece_lines = _match_delimiter(run, uses, defs, matcher, tol)
		if piece_lines:
			first = uses[piece_lines[0]]
			merged = pathops.Path()
			pen = merged.getPen()
			bands, prev_bottom = [], None
			for li in piece_lines:
				u = uses[li]
				ymin, ymax = _bbox_y(defs[u.glyph_id])
				top, bottom = u.y - first.y + ymin, u.y - first.y + ymax
				if prev_bottom is not None:
					bands.append((top - SEAM_MARGIN, prev_bottom + SEAM_MARGIN))
				prev_bottom = bottom
				tp = TransformPen(pen, (1, 0, 0, 1, u.x - first.x, u.y - first.y))
				parse_path(defs[u.glyph_id], tp)
			merged.simplify(fix_winding=True, keep_starting_points=False, clockwise=clockwise)
			rec = _RecordingPen()
			merged.draw(rec)
			writer = _SVGPathWriter()
			for contour in rec.contours:
				if seam_eps:
					contour = _flatten_seams(contour, seam_eps, bands)
				_replay(contour, writer)
			d = writer.d()

			slots = [uses[li].slot for li in piece_lines]
			if d in d_to_id:
				new_id = d_to_id[d]
			else:
				base = f"g{first.font}-" + "-".join(map(str, slots))
				new_id, n = base, 1
				while new_id in defs or new_id in new_defs:
					n += 1
					new_id = f"{base}v{n}"
				new_defs[new_id] = d
				d_to_id[d] = new_id

			first_line = lines[piece_lines[0]]
			replacements[piece_lines[0]] = first_line.replace(
				f"xlink:href='#{first.glyph_id}'", f"xlink:href='#{new_id}'"
			)
			for li in piece_lines[1:]:
				replacements[li] = None
			k = idxs.index(piece_lines[-1]) + 1
		else:
			k += 1

	if not new_defs:
		return svg

	out = []
	for i, line in enumerate(lines):
		if line.strip() == "</defs>":
			out.extend(f"<path id='{i_}' d='{d}'/>" for i_, d in new_defs.items())
		if i in replacements:
			if replacements[i] is not None:
				out.append(replacements[i])
		else:
			out.append(line)
	return "\n".join(out)


def _match_delimiter(run, uses, defs, matcher, tol):
	"""Return the line indices of the longest valid delimiter at the start of
	`run`, or None. Valid means: slot sequence matches a recipe, has at least
	two pieces, and consecutive pieces touch/overlap vertically."""
	seq = "".join(f"{uses[li].slot}," for li in run)
	count = 0
	for rx in matcher:  # longest match over all recipes
		m = rx.match(seq)
		if m:
			count = max(count, m.group(0).count(","))
	if count < 2:
		return None
	pieces = run[:count]
	prev_bottom = None
	for li in pieces:
		u = uses[li]
		if u.glyph_id not in defs:
			return None
		ymin, ymax = _bbox_y(defs[u.glyph_id])
		top, bottom = u.y + ymin, u.y + ymax
		if prev_bottom is not None and top > prev_bottom + tol:
			return None  # gap: not one delimiter
		prev_bottom = bottom
	return pieces



# ---------------------------------------------------------------------------
# Glyph outline normalization
# ---------------------------------------------------------------------------
#
# Every <path> in <defs> is rewritten so that equivalent glyphs have
# equivalent point structure:
#   * outer contours run counterclockwise as seen on screen, holes run
#     clockwise (nesting depth decides which is which), so nonzero filling
#     is unchanged;
#   * each contour starts at its "top-right" point: the point of the contour
#     that maximizes  (x - xmin)/w - (y - ymin)/h  within the contour's own
#     bounding box, found exactly (splitting a curve there if necessary);
#   * contours are ordered outer-before-holes, then top to bottom, then
#     right to left.

_SNAP = 1e-4  # pt; don't create curve pieces shorter than this
TOP_WEIGHT = 1.5  # start-point score is  right + TOP_WEIGHT * up  (bbox-normalized)


def _lerp(a, b, t):
	return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def _eval_seg(p0, seg, t):
	cmd, pts = seg
	if cmd == "L":
		return _lerp(p0, pts[0], t)
	if cmd == "Q":
		return _lerp(_lerp(p0, pts[0], t), _lerp(pts[0], pts[1], t), t)
	a, b, c = _lerp(p0, pts[0], t), _lerp(pts[0], pts[1], t), _lerp(pts[1], pts[2], t)
	return _lerp(_lerp(a, b, t), _lerp(b, c, t), t)


def _split_seg(p0, seg, t):
	"""Split a segment at t, returning (first, second) segments."""
	cmd, pts = seg
	if cmd == "L":
		m = _lerp(p0, pts[0], t)
		return ("L", (m,)), ("L", (pts[0],))
	if cmd == "Q":
		a, b = _lerp(p0, pts[0], t), _lerp(pts[0], pts[1], t)
		m = _lerp(a, b, t)
		return ("Q", (a, m)), ("Q", (b, pts[1]))
	a, b, c = _lerp(p0, pts[0], t), _lerp(pts[0], pts[1], t), _lerp(pts[1], pts[2], t)
	d, e = _lerp(a, b, t), _lerp(b, c, t)
	m = _lerp(d, e, t)
	return ("C", (a, d, m)), ("C", (e, c, pts[2]))


def _reverse_seg(p0, seg):
	"""Segment traversed backwards; it ends at p0."""
	cmd, pts = seg
	return (cmd, tuple(reversed(pts[:-1])) + (p0,))


def _extremum_params(p0, seg, f):
	"""Parameters in (0,1) where f(seg(t)) has a local extremum, for a linear f."""
	cmd, pts = seg
	if cmd == "L":
		return []
	vals = [f(p0)] + [f(q) for q in pts]
	if cmd == "Q":
		a, b, c = vals
		den = a - 2 * b + c
		return [(a - b) / den] if abs(den) > 1e-15 else []
	a, b, c, d = vals
	# derivative of cubic Bezier / 3: A t^2 + B t + C
	A = -a + 3 * b - 3 * c + d
	B = 2 * (a - 2 * b + c)
	C = b - a
	if abs(A) < 1e-15:
		return [-C / B] if abs(B) > 1e-15 else []
	disc = B * B - 4 * A * C
	if disc < 0:
		return []
	r = disc ** 0.5
	return [(-B + r) / (2 * A), (-B - r) / (2 * A)]


def _closed_loop(contour):
	"""Recorded contour -> (start, [segments]) with an explicit closing line."""
	start = contour[0][1][0]
	segs = []
	for cmd, pts in contour[1:]:
		if cmd == "Z":
			continue
		if cmd == "Q" and len(pts) > 2:  # expand implied on-curve points
			for i in range(len(pts) - 1):
				end = pts[i + 1] if i == len(pts) - 2 else _lerp(pts[i], pts[i + 1], 0.5)
				segs.append(("Q", (pts[i], end)))
		else:
			segs.append((cmd, tuple(pts)))
	last = segs[-1][1][-1] if segs else start
	if abs(last[0] - start[0]) > 1e-9 or abs(last[1] - start[1]) > 1e-9:
		segs.append(("L", (start,)))
	return start, segs


def _anchors(start, segs):
	out = [start]
	for _, pts in segs[:-1]:
		out.append(pts[-1])
	return out


def _polygon(start, segs, n=8):
	poly, cur = [], start
	for seg in segs:
		k = 1 if seg[0] == "L" else n
		for i in range(k):
			poly.append(_eval_seg(cur, seg, i / k))
		cur = seg[1][-1]
	return poly


def _signed_area(poly):
	"""Shoelace area in SVG (y-down) coordinates: negative = counterclockwise on screen."""
	s = 0.0
	for i in range(len(poly)):
		x0, y0 = poly[i]
		x1, y1 = poly[(i + 1) % len(poly)]
		s += x0 * y1 - x1 * y0
	return s / 2


def _point_in_poly(pt, poly):
	x, y = pt
	inside = False
	for i in range(len(poly)):
		x0, y0 = poly[i]
		x1, y1 = poly[(i + 1) % len(poly)]
		if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
			inside = not inside
	return inside


def _bbox(poly):
	xs = [p[0] for p in poly]
	ys = [p[1] for p in poly]
	return min(xs), min(ys), max(xs), max(ys)


def _reverse_loop(start, segs):
	anchors = _anchors(start, segs) + [start]
	new = [_reverse_seg(anchors[i], segs[i]) for i in range(len(segs))]
	new.reverse()
	return start, new


def _rotate_to_top_right(start, segs, bbox):
	xmin, ymin, xmax, ymax = bbox
	ax = 1 / (xmax - xmin) if xmax - xmin > 1e-9 else 0.0
	ay = 1 / (ymax - ymin) if ymax - ymin > 1e-9 else 0.0

	def f(p):
		return (p[0] - xmin) * ax - TOP_WEIGHT * (p[1] - ymin) * ay

	# Best location: (value, segment index, t). Anchors are t=0 of their segment.
	best = None
	cur = start
	for i, seg in enumerate(segs):
		cands = [0.0] + [t for t in _extremum_params(cur, seg, f) if 0 < t < 1]
		for t in cands:
			v = f(_eval_seg(cur, seg, t))
			if best is None or v > best[0] + 1e-9:
				best = (v, i, t)
		cur = seg[1][-1]
	_, i, t = best

	anchors = _anchors(start, segs)
	p0 = anchors[i]
	if 0 < t < 1:
		m = _eval_seg(p0, segs[i], t)
		end = segs[i][1][-1]
		d0 = abs(m[0] - p0[0]) + abs(m[1] - p0[1])
		d1 = abs(m[0] - end[0]) + abs(m[1] - end[1])
		if d0 < _SNAP:
			t = 0.0
		elif d1 < _SNAP:
			i, t = (i + 1) % len(segs), 0.0
		else:
			first, second = _split_seg(p0, segs[i], t)
			segs = segs[:i] + [first, second] + segs[i + 1:]
			anchors = _anchors(start, segs)
			i += 1
	return anchors[i], segs[i:] + segs[:i]


def _normalize_d(d: str, counterclockwise: bool = True) -> str:
	path = pathops.Path()
	parse_path(d, path.getPen())
	path.simplify(fix_winding=True, keep_starting_points=True)
	rec = _RecordingPen()
	path.draw(rec)

	loops = [_closed_loop(c) for c in rec.contours if len(c) > 1]
	polys = [_polygon(s, g) for s, g in loops]

	items = []
	for k, ((start, segs), poly) in enumerate(zip(loops, polys)):
		probe = poly[len(poly) // 3]
		depth = sum(
			1 for j, other in enumerate(polys)
			if j != k and _point_in_poly(probe, other)
		)
		want_ccw = (depth % 2 == 0) == counterclockwise
		if (_signed_area(poly) < 0) != want_ccw:
			start, segs = _reverse_loop(start, segs)
		bbox = _bbox(poly)
		start, segs = _rotate_to_top_right(start, segs, bbox)
		items.append((depth, bbox, start, segs))

	if not items:
		return d
	gx0 = min(b[0] for _, b, _, _ in items)
	gy0 = min(b[1] for _, b, _, _ in items)
	gx1 = max(b[2] for _, b, _, _ in items)
	gy1 = max(b[3] for _, b, _, _ in items)
	gw, gh = max(gx1 - gx0, 1e-9), max(gy1 - gy0, 1e-9)
	items.sort(key=lambda it: (
		it[0],
		round((it[1][1] - gy0) / gh * 20),   # top edge, coarse buckets
		-round((it[1][2] - gx0) / gw * 20),  # then right edge, right first
	))

	writer = _SVGPathWriter()
	for _, _, start, segs in items:
		if segs and segs[-1][0] == "L":
			segs = segs[:-1]  # implied by Z
		writer.moveTo(start)
		for cmd, pts in segs:
			if cmd == "L":
				writer.lineTo(*pts)
			elif cmd == "Q":
				writer.qCurveTo(*pts)
			else:
				writer.curveTo(*pts)
		writer.closePath()
	return writer.d()


def normalize_glyph_outlines(svg: str, counterclockwise: bool = True) -> str:
	"""Return a copy of a dvisvgm SVG string with every glyph <path> in <defs>
	rewritten to a canonical form: outer contours counterclockwise on screen
	(holes the opposite way), each contour starting at its top-right point,
	contours in a consistent order. Shapes are unchanged; only point
	structure is. Everything outside the path data is left untouched."""
	def repl(m):
		return f"<path id='{m['id']}' d='{_normalize_d(m['d'], counterclockwise)}'/>"
	return _PATH_RE.sub(repl, svg)





def normalize_tex_svg_globally():
	from .dual_compatibility import MANIM_TYPE
	if MANIM_TYPE == 'GL':
		from manimlib import Tex
		original_tex_get_svg = Tex.get_svg_string_by_content
		def normalized_tex_get_svg(*args, **kwargs):
			from .svg_normalization import merge_extensible_delimiters
			svg = original_tex_get_svg(*args, **kwargs)
			svg = merge_extensible_delimiters(svg)
			svg = normalize_glyph_outlines(svg)
			return svg
		Tex.get_svg_string_by_content = normalized_tex_get_svg
	elif MANIM_TYPE == 'CE':
		import xml.etree.ElementTree as ET
		from manim import SVGMobject, SingleStringMathTex
		def normalized_modify_xml_tree(self, element_tree):
			svg = self.get_file_path().read_text()
			svg = merge_extensible_delimiters(svg)
			svg = normalize_glyph_outlines(svg)
			return SVGMobject.modify_xml_tree(self, ET.ElementTree(ET.fromstring(svg)))
		SingleStringMathTex.modify_xml_tree = normalized_modify_xml_tree



"""Hand-laid-out, fully wired schematic (rev 0.2). Keeps symbol UUIDs so the PCB stays linked."""
import re, uuid, json, sys
sys.path.insert(0, "/home/claude/gen")
from design import PARTS

PRJ = "/home/claude/coax_relay"
SCH = f"{PRJ}/coax_relay.kicad_sch"
SYMDIR = "/usr/share/kicad/symbols"

old = open(SCH).read()
ROOT = re.search(r"\(kicad_sch[^\n]*\n\s*\(uuid ([0-9a-f-]+)\)", old).group(1)
OLD_UUID = {r: u_ for u_, r in re.findall(
    r'\(symbol \(lib_id "[^"]+"\).*?\(uuid ([0-9a-f-]+)\).*?\(reference "([^"]+)"\)', old, re.S)}


def u():
    return str(uuid.uuid4())


def r2(v):
    return round(v + 0.0, 3)


def extract(lib, name):
    t = open(f"{PRJ}/CoaxRelay.kicad_sym").read() if lib == "CoaxRelay" else open(f"{SYMDIR}/{lib}.kicad_sym").read()
    i = t.find(f'(symbol "{name}"')
    d = 0
    for j in range(i, len(t)):
        if t[j] == "(":
            d += 1
        elif t[j] == ")":
            d -= 1
            if d == 0:
                break
    return t[i:j + 1].replace(f'(symbol "{name}"', f'(symbol "{lib}:{name}"', 1)


def pins_of(s):
    return {m.group(4): (float(m.group(1)), float(m.group(2)))
            for m in re.finditer(r'\(pin \w+ \w+\s+\(at ([-\d.]+) ([-\d.]+) (\d+)\).*?\(number "([^"]*)"', s, re.S)}


# ---------------------------------------------------------------- layout
# ref: (x, y, rot, mirror, (ref dx, dy, justify), (val dx, dy, justify))
V = ((2.54, -1.27, "left"), (2.54, 1.27, "left"))          # vertical 2-pin parts: text to the right
H = ((0, -2.54, None), (0, 2.54, None))                     # horizontal 2-pin parts: text above/below
HD = ((0, -3.81, None), (0, 3.81, None))                    # horizontal diodes
L = {
    "J1": (27.94, 53.34, 0, None, (0, -6.35, None), (0, 7.62, None)),
    "F1": (49.53, 50.8, 90, None) + H,
    "D1": (64.77, 50.8, 180, None) + HD,
    "C1": (76.2, 54.61, 0, None) + V,
    "C2": (93.98, 54.61, 0, None) + V,
    "R3": (106.68, 54.61, 0, None) + V,
    "R4": (106.68, 67.31, 0, None) + V,
    "C3": (118.11, 67.31, 0, None) + V,
    "U1": (147.32, 106.68, 0, None, (0, -15.24, None), (0, 15.24, None)),
    "R1": (170.18, 101.6, 90, None, (0, -3.81, None), (0, 2.54, None)),
    "R2": (177.8, 107.95, 0, None) + V,
    "Q1": (186.69, 101.6, 0, None, (5.08, -1.27, "left"), (5.08, 1.27, "left")),
    "R7": (193.04, 76.2, 0, None) + V,
    "Q2": (203.2, 83.82, 0, "x", (5.08, -1.27, "left"), (5.08, 1.27, "left")),
    "D2": (215.9, 104.14, 270, None) + V,
    "R5": (231.14, 104.14, 0, None) + V,
    "LED1": (231.14, 116.84, 90, None, (2.54, -1.27, "right"), (2.54, 1.27, "right")),
    "J4": (256.54, 96.52, 0, None, (2.54, -3.81, "left"), (2.54, 6.35, "left")),
    "H1": (30.48, 160.02, 0, None, (0, -3.81, None), (0, 3.81, None)),
    "H2": (40.64, 160.02, 0, None, (0, -3.81, None), (0, 3.81, None)),
    "H3": (50.8, 160.02, 0, None, (0, -3.81, None), (0, 3.81, None)),
    "H4": (60.96, 160.02, 0, None, (0, -3.81, None), (0, 3.81, None)),
}

lib_ids = sorted({p[0] for p in PARTS.values()} | {"power:+12V", "power:GND", "power:PWR_FLAG"})
libsyms = {lid: extract(*lid.split(":")) for lid in lib_ids}
pinmap = {lid: pins_of(s) for lid, s in libsyms.items()}


def pin_xy(lid, x, y, rot, mirror, n):
    px, py = pinmap[lid][n]
    sx, sy = px, -py                      # library y-up -> sheet y-down
    if mirror == "x":
        sy = -sy
    elif mirror == "y":
        sx = -sx
    sx, sy = {0: (sx, sy), 90: (sy, -sx), 180: (-sx, -sy), 270: (-sy, sx)}[rot]
    return (r2(x + sx), r2(y + sy))


P = {}  # "J1.1" -> (x, y)
for ref, (lid, *_rest) in PARTS.items():
    x, y, rot, mir = L[ref][:4]
    for n in pinmap[lid]:
        P[f"{ref}.{n}"] = pin_xy(lid, x, y, rot, mir, n)

# ---------------------------------------------------------------- wiring (polylines)
RAIL12 = 50.8      # +12V rail
GND_T = 71.12      # top GND rail
GND_B = 124.46     # bottom GND rail
W = [
    # (1) power input
    [P["J1.1"], P["F1.1"]],
    [P["F1.2"], P["D1.2"]],
    [P["D1.1"], (205.74, RAIL12), P["Q2.3"]],                     # +12V rail -> Q2 source
    [P["J1.2"], (38.1, P["J1.2"][1]), (38.1, GND_T), (118.11, GND_T)],
    [P["C1.2"], (76.2, GND_T)], [P["C2.2"], (93.98, GND_T)],
    # (2) voltage monitor
    [P["R3.2"], P["R4.1"]],
    [(106.68, 60.96), (118.11, 60.96), P["C3.1"]],
    [(118.11, 60.96), (127.0, 60.96), (127.0, P["U1.7"][1]), P["U1.7"]],
    [P["U1.2"], (130.81, P["U1.2"][1]), (130.81, 101.6)],
    # (3) drive
    [P["U1.12"], P["R1.1"]],
    [P["R1.2"], P["Q1.3"]],
    [(177.8, 101.6), P["R2.1"]],
    [P["R2.2"], (177.8, GND_B), (246.38, GND_B)],
    [P["Q1.1"], (189.23, GND_B)],
    [P["Q1.2"], (189.23, 83.82), P["Q2.1"]],
    [(193.04, RAIL12), P["R7.1"]],
    [P["R7.2"], (193.04, 83.82)],
    # (4) output
    [P["Q2.2"], (205.74, 96.52), P["J4.1"]],
    [(215.9, 96.52), P["D2.1"]],
    [P["D2.2"], (215.9, GND_B)],
    [(231.14, 96.52), P["R5.1"]],
    [P["R5.2"], P["LED1.2"]],
    [P["LED1.1"], (231.14, GND_B)],
    [P["J4.2"], (246.38, P["J4.2"][1]), (246.38, GND_B)],
]

# power symbols / flags: (lib, x, y, rot)
PWR = [("power:+12V", 71.12, RAIL12, 0), ("power:PWR_FLAG", 85.09, RAIL12, 0),
       ("power:GND", 55.88, GND_T, 0), ("power:PWR_FLAG", 45.72, GND_T, 0),
       ("power:GND", 130.81, 101.6, 0), ("power:GND", 205.74, GND_B, 0)]

# net labels (name, x, y, angle)
LABELS = [("VIN_RAW", 36.83, RAIL12, 0), ("VIN_F", 54.61, RAIL12, 0), ("VMON", 120.65, 60.96, 0),
          ("RELAY_DRV", 161.29, 101.6, 0), ("Q_BASE", 175.26, 101.6, 0), ("GATE", 194.31, 83.82, 0),
          ("OUT", 220.98, 96.52, 0), ("LED_A", 231.14, 109.22, 270)]

# ---------------------------------------------------------------- build segment list, split, junctions
segs = []
for pl in W:
    for a, b in zip(pl, pl[1:]):
        a, b = (r2(a[0]), r2(a[1])), (r2(b[0]), r2(b[1]))
        assert a[0] == b[0] or a[1] == b[1], ("not orthogonal", a, b)
        if a != b:
            segs.append((a, b))

points = set()
for a, b in segs:
    points |= {a, b}
pin_pts = {}
for k, p in P.items():
    pin_pts.setdefault(p, []).append(k)
points |= set(pin_pts)
points |= {(r2(x), r2(y)) for _, x, y, _ in PWR}
points |= {(r2(x), r2(y)) for _, x, y, _ in LABELS}


def inside(p, a, b):
    if a[0] == b[0] == p[0]:
        return min(a[1], b[1]) < p[1] < max(a[1], b[1])
    if a[1] == b[1] == p[1]:
        return min(a[0], b[0]) < p[0] < max(a[0], b[0])
    return False


changed = True
while changed:
    changed = False
    for i, (a, b) in enumerate(segs):
        for p in points:
            if inside(p, a, b):
                segs[i:i + 1] = [(a, p), (p, b)]
                changed = True
                break
        if changed:
            break

deg = {}
for a, b in segs:
    deg[a] = deg.get(a, 0) + 1
    deg[b] = deg.get(b, 0) + 1
for p, ks in pin_pts.items():
    if p in deg:
        deg[p] += len(ks)
for _, x, y, _ in PWR:
    p = (r2(x), r2(y))
    if p in deg:
        deg[p] += 1
junctions = [p for p, d in deg.items() if d >= 3]

# ---------------------------------------------------------------- emit
items = []


def fld(name, val, x, y, just=None, hide=False, ang=0):
    j = f" (justify {just})" if just else ""
    h = " hide" if hide else ""
    return f'    (property "{name}" "{val}" (at {r2(x)} {r2(y)} {ang}) (effects (font (size 1.27 1.27)){j}{h}))\n'


def symbol(lid, ref, val, fp, x, y, rot, mir, rf, vf, sym_uuid, inbom=True):
    fa = 90 if rot in (90, 270) else 0
    m = f" (mirror {mir})" if mir else ""
    s = f'  (symbol (lib_id "{lid}") (at {r2(x)} {r2(y)} {rot}){m} (unit 1)\n'
    s += f'    (in_bom {"yes" if inbom else "no"}) (on_board yes) (dnp no)\n    (uuid {sym_uuid})\n'
    s += fld("Reference", ref, x + rf[0], y + rf[1], rf[2], hide=ref.startswith("#"), ang=fa)
    s += fld("Value", val, x + vf[0], y + vf[1], vf[2], ang=fa)
    s += fld("Footprint", fp, x, y, hide=True)
    s += fld("Datasheet", "~", x, y, hide=True)
    for n in pinmap[lid]:
        s += f'    (pin "{n}" (uuid {u()}))\n'
    s += f'    (instances (project "coax_relay" (path "/{ROOT}" (reference "{ref}") (unit 1))))\n  )\n'
    items.append(s)


for ref, (lid, val, fp, _, nets) in PARTS.items():
    x, y, rot, mir, rf, vf = L[ref]
    symbol(lid, ref, val, fp, x, y, rot, mir, rf, vf, OLD_UUID.get(ref, u()))
    for n in pinmap[lid]:
        if n not in nets and not ref.startswith("H"):
            px, py = P[f"{ref}.{n}"]
            items.append(f'  (no_connect (at {px} {py}) (uuid {u()}))\n')

npwr = nflg = 0
for lid, x, y, rot in PWR:
    if lid == "power:PWR_FLAG":
        nflg += 1
        symbol(lid, f"#FLG{nflg:02d}", "PWR_FLAG", "", x, y, rot, None, (0, 0, None), (0, -3.81, None), u(), inbom=False)
    else:
        npwr += 1
        net = lid.split(":")[1]
        vy = 5.08 if net == "GND" else -3.81
        symbol(lid, f"#PWR{npwr:02d}", net, "", x, y, rot, None, (0, 0, None), (0, vy, None), u(), inbom=False)

for a, b in segs:
    items.append(f'  (wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {u()}))\n')
for p in junctions:
    items.append(f'  (junction (at {p[0]} {p[1]}) (diameter 0) (color 0 0 0 0) (uuid {u()}))\n')
for name, x, y, ang in LABELS:
    jb = "right bottom" if ang == 270 else "left bottom"
    items.append(f'  (label "{name}" (at {x} {y} {ang}) (effects (font (size 1.0 1.0)) (justify {jb})) (uuid {u()}))\n')

NOTES = [
    ("同軸リレー制御基板 rev0.2   PC(Chrome) -USB- RP2040-Zero -GP2-> 12V出力 -> Fコネクタ → 同軸リレー", 25.4, 27.94, 2.0),
    ("[1] 電源入力：DCジャック → ポリスイッチ0.5A(過電流) → 1N5819(逆接保護) → +12V", 25.4, 38.1, 1.5),
    ("[2] 12V監視：47k/10k分圧(1/5.7) → GP26(ADC0)", 99.06, 43.18, 1.5),
    ("[3] マイコン：RP2040-Zero（USB給電・Web Serial）", 129.54, 86.36, 1.5),
    ("1×9ピンソケット2本に挿す。5V/3V3は未使用", 134.62, 127.0, 1.27),
    ("[4] 12V出力スイッチ（ハイサイド）", 210.82, 63.5, 1.5),
    ("GP2=H → Q1 ON → Q2ゲートがGNDへ → Q2 ON → OUT=12V（ANT2）", 210.82, 67.31, 1.27),
    ("GP2=L/リセット中 → R2がQ1をOFF, R7がQ2をOFF → OUT=0V（ANT1）", 210.82, 70.61, 1.27),
    ("[5] 出力：J4 → ケースのF-J（中心=12V／外側=GND）→ 同軸リレー", 177.8, 134.62, 1.5),
    ("D2：リレーコイルの逆起電力を吸収　LED1：出力中に点灯", 177.8, 138.43, 1.27),
    ("取付穴 M3 ×4", 25.4, 152.4, 1.27),
]
for t, x, y, sz in NOTES:
    items.append(f'  (text "{t}" (at {x} {y} 0) (effects (font (size {sz} {sz})) (justify left bottom)) (uuid {u()}))\n')

sch = (f'(kicad_sch (version 20230121) (generator eeschema)\n\n  (uuid {ROOT})\n\n  (paper "A4")\n\n'
       '  (title_block\n    (title "Coax relay controller (RP2040-Zero)")\n    (date "2026-11-07")\n    (rev "0.2")\n'
       '    (comment 1 "12V high-side output to chassis F-J, Web Serial control")\n  )\n\n'
       '  (lib_symbols\n' + "".join("    " + libsyms[l].replace("\n", "\n    ") + "\n" for l in lib_ids) + '  )\n\n'
       + "".join(items) + '\n  (sheet_instances\n    (path "/" (page "1"))\n  )\n)\n')
open(SCH, "w").write(sch)
print("wires", len(segs), "junctions", len(junctions), "kept uuids", sum(r in OLD_UUID for r in PARTS))

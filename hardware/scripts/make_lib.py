"""Project footprint / symbol library for coax_relay (KiCad 7 format, opens in KiCad 8-10)."""
import os, uuid

PRJ = "/home/claude/coax_relay"
FPDIR = os.path.join(PRJ, "CoaxRelay.pretty")
os.makedirs(FPDIR, exist_ok=True)


def u():
    return str(uuid.uuid4())


def fp_text(kind, text, x, y, layer, size=1.0, thick=0.15, hide=False):
    h = " hide" if hide else ""
    return (f'  (fp_text {kind} "{text}" (at {x} {y}) (layer "{layer}"){h}\n'
            f'    (effects (font (size {size} {size}) (thickness {thick}))) (tstamp {u()}))\n')


def line(x1, y1, x2, y2, layer, w):
    return f'  (fp_line (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (layer "{layer}") (tstamp {u()}))\n'


def rect(x1, y1, x2, y2, layer, w):
    return (line(x1, y1, x2, y1, layer, w) + line(x2, y1, x2, y2, layer, w) +
            line(x2, y2, x1, y2, layer, w) + line(x1, y2, x1, y1, layer, w))


def write_fp(name, descr, body, attr="through_hole"):
    s = (f'(footprint "{name}" (version 20221018) (generator pcbnew)\n'
         f'  (layer "F.Cu")\n  (descr "{descr}")\n  (attr {attr})\n' + body + ')\n')
    open(os.path.join(FPDIR, name + ".kicad_mod"), "w").write(s)


# ---------------- MJ-179PH (Marushin) ----------------
# Datasheet "FOOT PRINT (REFERENCE)": from the plug face, slot S at 7.7 mm (3 mm long),
# slot B centre at 10.75 mm offset 4.9 mm (3 mm long, crosswise), slot C at 13.7 mm (3.5 mm long).
# Origin = centre pin C (same convention as KiCad BarrelJack_Horizontal). Body 14.5 x 9 mm.
b = ""
b += fp_text("reference", "REF**", -7, -5.8, "F.SilkS")
b += fp_text("value", "MJ-179PH", -7, 6.8, "F.Fab")
b += f'  (pad "1" thru_hole roundrect (at 0 0) (size 2.2 4.6) (drill oval 1.0 3.5) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.25) (tstamp {u()}))\n'
b += f'  (pad "2" thru_hole roundrect (at -6 0) (size 2.2 4.1) (drill oval 1.0 3.0) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.25) (tstamp {u()}))\n'
b += f'  (pad "3" thru_hole roundrect (at -2.95 4.9) (size 4.1 2.2) (drill oval 3.0 1.0) (layers "*.Cu" "*.Mask") (roundrect_rratio 0.25) (tstamp {u()}))\n'
b += rect(-13.7, -4.5, 0.8, 4.5, "F.Fab", 0.1)
b += line(-10.2, -4.5, -10.2, 4.5, "F.Fab", 0.1)
b += line(-13.2, -4.61, 0.91, -4.61, "F.SilkS", 0.12)
b += line(-13.2, 4.61, -7.2, 4.61, "F.SilkS", 0.12)
b += line(0.91, -4.61, 0.91, -2.6, "F.SilkS", 0.12)
b += rect(-14.2, -5.0, 1.6, 6.3, "F.CrtYd", 0.05)
write_fp("MJ-179PH", "2.1mm DC jack Marushin MJ-179PH (Akizuki 106568), slots per datasheet", b)

# ---------------- Bourns MF-R050 radial PTC, 5.1 mm lead spacing ----------------
b = ""
b += fp_text("reference", "REF**", 2.55, -3.0, "F.SilkS")
b += fp_text("value", "MF-R050", 2.55, 3.0, "F.Fab")
b += f'  (pad "1" thru_hole rect (at 0 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask") (tstamp {u()}))\n'
b += f'  (pad "2" thru_hole circle (at 5.1 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask") (tstamp {u()}))\n'
b += rect(-1.4, -1.55, 6.5, 1.55, "F.Fab", 0.1)
b += rect(-1.52, -1.67, 6.62, 1.67, "F.SilkS", 0.12)
b += rect(-1.8, -1.95, 6.9, 1.95, "F.CrtYd", 0.05)
write_fp("Fuse_Bourns_MF-R050_P5.10mm", "Bourns MF-R050 PTC, body 7.9x3.1mm, lead spacing 5.1mm", b)

# ---------------- RP2040-Zero on two 1x9 sockets ----------------
# Waveshare RP2040-Zero: 18 x 23.5 mm, rows 15.24 mm apart, 2.54 mm pitch, USB-C at the top edge.
# Pads 1-9 = left row top->bottom (5V, GND, 3V3, GP29, GP28, GP27, GP26, GP15, GP14)
# Pads 10-18 = right row top->bottom (GP0 .. GP8)
left = ["5V", "GND", "3V3", "GP29", "GP28", "GP27", "GP26", "GP15", "GP14"]
right = [f"GP{i}" for i in range(9)]
b = ""
b += fp_text("reference", "REF**", 0, -14.2, "F.SilkS")
b += fp_text("value", "RP2040-Zero", 0, 0, "F.Fab")
for i in range(9):
    y = round(-10.16 + 2.54 * i, 2)
    shape = "rect" if i == 0 else "oval"
    b += f'  (pad "{i+1}" thru_hole {shape} (at -7.62 {y}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask") (tstamp {u()}))\n'
    b += f'  (pad "{i+10}" thru_hole oval (at 7.62 {y}) (size 1.7 1.7) (drill 1.0) (layers "*.Cu" "*.Mask") (tstamp {u()}))\n'
    b += fp_text("user", left[i], -4.6, y, "F.SilkS", size=0.8, thick=0.12)
    b += fp_text("user", right[i], 4.9, y, "F.SilkS", size=0.8, thick=0.12)
b += rect(-9, -11.75, 9, 11.75, "F.Fab", 0.1)
b += rect(-9.1, -11.85, 9.1, 11.85, "F.SilkS", 0.12)
# USB-C position marker (top edge)
b += rect(-4.5, -11.85, 4.5, -11.2, "F.SilkS", 0.12)
b += fp_text("user", "USB", 0, -9.0, "F.SilkS", size=0.8, thick=0.12)
b += rect(-9.5, -12.25, 9.5, 12.25, "F.CrtYd", 0.05)
write_fp("RP2040-Zero_Socket", "Waveshare RP2040-Zero plugged into 2x 1x9 2.54mm sockets, 15.24mm row spacing", b)

# ---------------- RP2040-Zero schematic symbol ----------------
pins = ""
for i in range(9):
    y = round(10.16 - 2.54 * i, 2)
    pins += (f'      (pin bidirectional line (at -12.7 {y} 0) (length 5.08)\n'
             f'        (name "{left[i]}" (effects (font (size 1.27 1.27))))\n'
             f'        (number "{i+1}" (effects (font (size 1.27 1.27)))))\n')
    pins += (f'      (pin bidirectional line (at 12.7 {y} 180) (length 5.08)\n'
             f'        (name "{right[i]}" (effects (font (size 1.27 1.27))))\n'
             f'        (number "{i+10}" (effects (font (size 1.27 1.27)))))\n')
for p, n in (("2", "GND"), ("1", "5V")):
    pass
sym_body = (
    '    (pin_names (offset 1.016)) (in_bom yes) (on_board yes)\n'
    '    (property "Reference" "U" (at 0 13.97 0) (effects (font (size 1.27 1.27))))\n'
    '    (property "Value" "RP2040-Zero" (at 0 -13.97 0) (effects (font (size 1.27 1.27))))\n'
    '    (property "Footprint" "CoaxRelay:RP2040-Zero_Socket" (at 0 -16.51 0) (effects (font (size 1.27 1.27)) hide))\n'
    '    (property "Datasheet" "https://www.waveshare.com/wiki/RP2040-Zero" (at 0 -19.05 0) (effects (font (size 1.27 1.27)) hide))\n'
    '    (symbol "RP2040-Zero_0_1"\n'
    '      (rectangle (start -7.62 12.7) (end 7.62 -12.7) (stroke (width 0.254) (type default)) (fill (type background)))\n'
    '    )\n'
    '    (symbol "RP2040-Zero_1_1"\n' + pins + '    )\n')
SYMBOL_RP2040 = sym_body
open(os.path.join(PRJ, "CoaxRelay.kicad_sym"), "w").write(
    '(kicad_symbol_lib (version 20220914) (generator kicad_symbol_editor)\n'
    '  (symbol "RP2040-Zero"\n' + sym_body + '  )\n)\n')

open(os.path.join(PRJ, "fp-lib-table"), "w").write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "CoaxRelay")(type "KiCad")(uri "${KIPRJMOD}/CoaxRelay.pretty")(options "")(descr "coax relay project footprints"))\n)\n')
open(os.path.join(PRJ, "sym-lib-table"), "w").write(
    '(sym_lib_table\n  (version 7)\n  (lib (name "CoaxRelay")(type "KiCad")(uri "${KIPRJMOD}/CoaxRelay.kicad_sym")(options "")(descr "coax relay project symbols"))\n)\n')
print("lib ok")

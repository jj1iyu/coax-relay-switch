"""KiCad の rev0.3 基板から部品の外形(コートヤード)・高さ・パッドを OpenSCAD 用に書き出す"""
import pcbnew, sys
sys.path.insert(0, "/home/claude/gen03")
from design import BOARD
X0, Y0, W, D = BOARD
H = {"F1": 13.7, "Q2": 13.5, "J4": 12.5, "J1": 11, "C1": 11.5, "D1": 2.7, "D2": 2.7, "C2": 5, "C3": 5,
     "Q1": 5, "LED1": 3.5, "R1": 2.5, "R2": 2.5, "R3": 2.5, "R4": 2.5, "R5": 2.5, "R7": 2.5}
b = pcbnew.LoadBoard("/home/claude/rev03/coax_relay.kicad_pcb")
mm = pcbnew.ToMM
out = ["// generated from rev0.3 coax_relay.kicad_pcb (board coords: x right, y down, origin = board rear-left)", "pcb_parts = ["]
pads = []
for f in b.GetFootprints():
    r = f.GetReference()
    if r in H:
        bb = f.GetCourtyard(pcbnew.F_Cu).BBox()
        out.append(f'  ["{r}", {mm(bb.GetX())-X0:.2f}, {mm(bb.GetY())-Y0:.2f}, {mm(bb.GetRight())-X0:.2f}, {mm(bb.GetBottom())-Y0:.2f}, {H[r]}],')
    if r == "U1":
        u1 = (mm(f.GetPosition().x) - X0, mm(f.GetPosition().y) - Y0)
    for p in f.Pads():
        pads.append(f"  [{mm(p.GetPosition().x)-X0:.2f}, {mm(p.GetPosition().y)-Y0:.2f}, {mm(min(p.GetSize().x, p.GetSize().y)):.2f}],")
out.append("];")
out.append("pcb_pads = [")
out += pads
out.append("];")
out.append(f"u1_center = [{u1[0]:.2f}, {u1[1]:.2f}];   // USB-C は前（y=pcb_d）側")
open("/home/claude/case03/pcb_real.scad", "w").write("\n".join(out) + "\n")
print("ok", u1)

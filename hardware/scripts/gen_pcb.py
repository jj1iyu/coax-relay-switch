"""Stage 1: create board, place footprints, assign nets, outline. Usage: gen_pcb.py place|route|finish"""
import sys, json, os
sys.path.insert(0, "/home/claude/gen03")
import pcbnew
from design import PARTS, PLACE, BOARD

PRJ = "/home/claude/rev03"
PCB = f"{PRJ}/coax_relay.kicad_pcb"
FPLIB = "/usr/share/kicad/footprints"
MM = pcbnew.FromMM
POWER = ["+12V", "/VIN_RAW", "/VIN_F", "/OUT", "GND"]


def netname(n):
    return n if n in ("+12V", "GND") else "/" + n


def sym_paths():
    import re
    t = open(f"{PRJ}/coax_relay.kicad_sch").read()
    root = re.search(r"\(kicad_sch[^\n]*\n\s*\(uuid ([0-9a-f-]+)\)", t).group(1)
    out = {}
    for m in re.finditer(r'\(symbol \(lib_id "[^"]+"\).*?\(uuid ([0-9a-f-]+)\).*?\(reference "([^"]+)"\)', t, re.S):
        out[m.group(2)] = m.group(1)
    return out



def write_project():
    pro = {
        "board": {
            "design_settings": {
                "defaults": {"board_outline_line_width": 0.1, "copper_line_width": 0.2, "silk_line_width": 0.15,
                             "silk_text_size_h": 1.0, "silk_text_size_v": 1.0, "silk_text_thickness": 0.15},
                "rules": {"min_clearance": 0.2, "min_track_width": 0.2, "min_via_diameter": 0.6,
                          "min_via_annular_width": 0.15, "min_through_hole_diameter": 0.3,
                          "min_hole_to_hole": 0.5, "min_hole_clearance": 0.25, "min_copper_edge_clearance": 0.4,
                          "min_silk_clearance": 0.0, "solder_mask_to_copper_clearance": 0.0},
                "track_widths": [0.0, 0.3, 0.5, 0.8, 1.0],
                "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.8, "drill": 0.4}],
            },
        },
        "meta": {"filename": "coax_relay.kicad_pro", "version": 1},
        "net_settings": {
            "classes": [
                {"name": "Default", "clearance": 0.25, "track_width": 0.3, "via_diameter": 0.8, "via_drill": 0.4,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "bus_width": 12, "wire_width": 6, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
                 "schematic_color": "rgba(0, 0, 0, 0.000)"},
                {"name": "Power", "clearance": 0.3, "track_width": 0.8, "via_diameter": 1.0, "via_drill": 0.5,
                 "microvia_diameter": 0.3, "microvia_drill": 0.1, "diff_pair_width": 0.2, "diff_pair_gap": 0.25,
                 "diff_pair_via_gap": 0.25, "bus_width": 12, "wire_width": 6, "line_style": 0, "pcb_color": "rgba(0, 0, 0, 0.000)",
                 "schematic_color": "rgba(0, 0, 0, 0.000)"},
            ],
            "meta": {"version": 3},
            "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in POWER],
        },
        "pcbnew": {"last_paths": {}, "page_layout_descr_file": ""},
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [], "text_variables": {},
    }
    json.dump(pro, open(f"{PRJ}/coax_relay.kicad_pro", "w"), indent=2)


def fp_path(fpid):
    lib, name = fpid.split(":")
    d = f"{PRJ}/CoaxRelay.pretty" if lib == "CoaxRelay" else f"{FPLIB}/{lib}.pretty"
    return d, name


def place():
    write_project()
    if os.path.exists(PCB):
        os.remove(PCB)
    board = pcbnew.NewBoard(PCB)
    board.SetCopperLayerCount(2)
    paths = sym_paths()
    nets = {}
    for ref, (lid, val, fpid, _, pinnets) in PARTS.items():
        for n in pinnets.values():
            if n not in nets:
                ni = pcbnew.NETINFO_ITEM(board, netname(n))
                board.Add(ni)
                nets[n] = ni
    for ref, (lid, val, fpid, _, pinnets) in PARTS.items():
        d, name = fp_path(fpid)
        fp = pcbnew.FootprintLoad(d, name)
        assert fp is not None, fpid
        fp.SetParent(board)
        fp.SetFPID(pcbnew.LIB_ID(*fpid.split(":")))
        fp.SetPath(pcbnew.KIID_PATH("/" + paths[ref]))
        try:
            fp.SetProperty("Sheetname", "")
            fp.SetProperty("Sheetfile", "coax_relay.kicad_sch")
        except Exception as e:
            print("prop", e)
        fp.SetReference(ref)
        fp.SetValue(val)
        x, y, rot = PLACE[ref]
        fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        fp.SetOrientation(pcbnew.EDA_ANGLE(rot, pcbnew.DEGREES_T))
        board.Add(fp)
        for pad in fp.Pads():
            n = pinnets.get(pad.GetNumber())
            if n:
                pad.SetNet(nets[n])
    # outline with 1 mm corner radius
    x0, y0, w, h = BOARD
    r = 1.0
    segs = [((x0 + r, y0), (x0 + w - r, y0)), ((x0 + w, y0 + r), (x0 + w, y0 + h - r)),
            ((x0 + w - r, y0 + h), (x0 + r, y0 + h)), ((x0, y0 + h - r), (x0, y0 + r))]
    for (a, b) in segs:
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(b[0]), MM(b[1])))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)
    for cx, cy, sa in ((x0 + r, y0 + r, 180), (x0 + w - r, y0 + r, 270), (x0 + w - r, y0 + h - r, 0), (x0 + r, y0 + h - r, 90)):
        s = pcbnew.PCB_SHAPE(board)
        s.SetShape(pcbnew.SHAPE_T_ARC)
        s.SetCenter(pcbnew.VECTOR2I(MM(cx), MM(cy)))
        import math
        sx = cx + r * math.cos(math.radians(sa)); sy = cy + r * math.sin(math.radians(sa))
        s.SetStart(pcbnew.VECTOR2I(MM(sx), MM(sy)))
        s.SetArcAngleAndEnd(pcbnew.EDA_ANGLE(90, pcbnew.DEGREES_T))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)
    board.Save(PCB)
    print("placed", len(PARTS))


def check():
    board = pcbnew.LoadBoard(PCB)
    x0, y0, w, h = BOARD
    boxes = {}
    for fp in board.GetFootprints():
        cy = fp.GetCourtyard(pcbnew.F_Cu)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False, False)
        boxes[fp.GetReference()] = (pcbnew.ToMM(bb.GetX()), pcbnew.ToMM(bb.GetY()),
                                    pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))
    refs = sorted(boxes)
    for i, a in enumerate(refs):
        ax0, ay0, ax1, ay1 = boxes[a]
        if ax0 < x0 - 0.01 or ay0 < y0 - 0.01 or ax1 > x0 + w + 0.01 or ay1 > y0 + h + 0.01:
            print("OUTSIDE", a, [round(v, 2) for v in boxes[a]])
        for b in refs[i + 1:]:
            bx0, by0, bx1, by1 = boxes[b]
            if ax0 < bx1 and bx0 < ax1 and ay0 < by1 and by0 < ay1:
                print("OVERLAP", a, b, round(min(ax1, bx1) - max(ax0, bx0), 2), round(min(ay1, by1) - max(ay0, by0), 2))
    print("check done")


if __name__ == "__main__":
    if sys.argv[1] in ("place", "check"): {"place": place, "check": check}[sys.argv[1]]()


def import_ses(board, path):
    import re
    txt = open(path).read()
    res = re.search(r"\(resolution um (\d+)\)", txt.split("(routes")[1])
    scale = 1000.0 / int(res.group(1))  # SES units -> nm
    layers = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu}
    body = txt.split("(network_out", 1)[1]
    ntr = nvia = 0
    for nm in re.finditer(r'\(net\s+("[^"]+"|\S+)(.*?)(?=\(net\s|\Z)', body, re.S):
        net = board.FindNet(nm.group(1).strip('"'))
        for w in re.finditer(r'\(wire\s*\(path\s+(\S+)\s+(\d+)\s+([-\d\s]+)\)', nm.group(2)):
            layer, width = layers[w.group(1)], int(int(w.group(2)) * scale)
            c = [int(v) for v in w.group(3).split()]
            pts = [(int(c[i] * scale), int(-c[i + 1] * scale)) for i in range(0, len(c), 2)]
            for a, b in zip(pts, pts[1:]):
                t = pcbnew.PCB_TRACK(board)
                t.SetStart(pcbnew.VECTOR2I(*a)); t.SetEnd(pcbnew.VECTOR2I(*b))
                t.SetWidth(width); t.SetLayer(layer); t.SetNet(net)
                board.Add(t); ntr += 1
        for v in re.finditer(r'\(via\s+("[^"]+"|\S+)\s+(-?\d+)\s+(-?\d+)', nm.group(2)):
            dm = re.search(r"_(\d+):(\d+)_um", v.group(1))
            via = pcbnew.PCB_VIA(board)
            via.SetPosition(pcbnew.VECTOR2I(int(int(v.group(2)) * scale), int(-int(v.group(3)) * scale)))
            via.SetWidth(MM(int(dm.group(1)) / 1000)); via.SetDrill(MM(int(dm.group(2)) / 1000))
            via.SetNet(net); board.Add(via); nvia += 1
    # drop dangling stubs left by the router
    removed = 0
    while True:
        tracks = list(board.GetTracks())
        ends = {}
        for t in tracks:
            for p in (t.GetStart(), t.GetEnd()):
                ends[(p.x, p.y, t.GetLayer())] = ends.get((p.x, p.y, t.GetLayer()), 0) + 1
        dead = []
        for t in tracks:
            for p in (t.GetStart(), t.GetEnd()):
                if ends[(p.x, p.y, t.GetLayer())] > 1:
                    continue
                if any(pad.HitTest(p) and pad.IsOnLayer(t.GetLayer()) for pad in board.GetPads()):
                    continue
                dead.append(t)
                break
        if not dead:
            break
        for t in dead:
            board.Remove(t); removed += 1
    print("imported tracks", ntr, "vias", nvia, "removed stubs", removed)


def finish():
    board = pcbnew.LoadBoard(PCB)
    import_ses(board, "/home/claude/gen03/board.ses")
    # reference text placement (silk) for the dense bottom row
    refpos = {"U1": (117.0, 126.0, 0), "J1": (133.0, 142.0, 0), "F1": (132.05, 126.5, 0), "LED1": (141.3, 139.6, 0),
              "R1": (131.81, 111.0, 0), "R2": (131.81, 107.0, 0), "R3": (113.81, 112.0, 0), "R4": (113.81, 116.0, 0),
              "R7": (133.81, 116.0, 0)}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in refpos:
            x, y, a = refpos[ref]
            t = fp.Reference()
            t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            t.SetTextAngle(pcbnew.EDA_ANGLE(a, pcbnew.DEGREES_T))
        if ref.startswith("H"):
            fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
    # board texts
    texts = [("DC12V", 133.0, 145.0, 0.9), ("ON", 146.3, 143.3, 0.8),
             ("F-J", 152.0, 140.0, 1.0), ("12V", 149.46, 134.6, 0.8), ("GND", 154.54, 134.6, 0.8),
             ("COAX RELAY CTRL v0.3", 116.0, 101.3, 0.9)]
    for s, x, y, sz in texts:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(s)
        t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
        t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(pcbnew.VECTOR2I(MM(sz), MM(sz)))
        t.SetTextThickness(MM(0.15))
        board.Add(t)
    # GND pour on both layers
    x0, y0, w, h = BOARD
    gnd = board.FindNet("GND")
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(gnd)
        ol = z.Outline()
        ol.NewOutline()
        for (px, py) in ((x0, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h)):
            ol.Append(MM(px), MM(py))
        z.SetLocalClearance(MM(0.3))
        z.SetMinThickness(MM(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(MM(0.4))
        z.SetThermalReliefSpokeWidth(MM(0.5))
        z.SetIsFilled(False)
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(PCB)
    pcbnew.WriteDRCReport(board, "/home/claude/gen03/drc.rpt", pcbnew.EDA_UNITS_MILLIMETRES, True)
    print("finished")


if __name__ == "__main__" and sys.argv[1] == "finish":
    finish()

// 実際の基板データ(KiCad)とケースを重ねて確認するためのファイル
include <coax_relay_case.scad>
include <pcb_real.scad>
part = "none";
view = "top";          // "top" / "cut_usb" / "cut_dc" / "iso"

// 部品の高さ（基板上面から）
sock_h   = 8.5;        // 1x9 ピンソケット
hdr_sp   = 2.5;        // ピンヘッダのプラスチック
zero_t   = 1.0;        // RP2040-Zero 基板厚
usbc_h   = 3.26;       // USB-C レセプタクル高さ
usbc_w   = 8.94;
usbc_d   = 7.35;

module real_board() {
    // 基板
    color("darkgreen") translate([cx(0), cy(pcb_d), floor_t + standoff_h])
        difference() {
            cube([pcb_w, pcb_d, pcb_t]);
            for (p = pcb_pads) translate([p[0], pcb_d - p[1], -1]) cylinder(d = p[2]*0.6, h = 4, $fn = 16);
        }
    // 部品（KiCadのコートヤード外形 × 部品高さ）
    for (q = pcb_parts) if (q[5] > 0)
        color(q[0] == "J1" ? "dimgray" : q[0] == "J4" ? "limegreen" : q[0] == "F1" ? "khaki" : "steelblue", 0.85)
            translate([cx(q[1]), cy(q[4]), pcb_top]) cube([q[3]-q[1], q[4]-q[2], q[5]]);
    // U1: ソケット2本 + RP2040-Zero + USB-C
    ux = u1_center[0]; uy = u1_center[1];
    color("black") for (sx = [-7.62, 7.62]) translate([cx(ux + sx) - 1.27, cy(uy + 11.43), pcb_top]) cube([2.54, 22.86, sock_h]);
    color("dimgray") for (sx = [-7.62, 7.62]) translate([cx(ux + sx) - 1.27, cy(uy + 11.43), pcb_top + sock_h]) cube([2.54, 22.86, hdr_sp]);
    color("royalblue") translate([cx(ux) - 9, cy(uy + 11.75), pcb_top + sock_h + hdr_sp]) cube([18, 23.5, zero_t]);
    color("silver") translate([cx(ux) - usbc_w/2, cy(uy - 11.75) - usbc_d + 0.6, pcb_top + sock_h + hdr_sp + zero_t]) cube([usbc_w, usbc_d, usbc_h]);
}

module fj() {   // F-J（内側: 六角2.8mm + はんだ端子, 外側: ネジ部）
    translate([cx(fj_x), 0, pcb_top + fj_z]) rotate([-90,0,0]) {
        color("gold") cylinder(d=12.7, h=2.8, $fn=6);
        color("gold") translate([0,0,2.8]) cylinder(d=2, h=6);
        color("gold") translate([0,0,-wall-16.5+wall]) cylinder(d=9.5, h=16.5 - 0.01);
    }
}
module whole() { color("orange", 0.55) case_body(); real_board(); fj(); }

if (view == "top") whole();
if (view == "iso") whole();
if (view == "cut_usb")          // USB-C の中心を通る断面（右側を切り落として右から見る）
    intersection() { whole(); translate([-50, -50, -1]) cube([cx(u1_center[0]) + 50, 200, 100]); }
if (view == "cut_fj")           // F-J中心を通る断面（配線スペースの確認）
    intersection() { whole(); translate([-50, -50, -1]) cube([cx(fj_x) + 50, 200, 100]); }
if (view == "cut_dc")           // DCジャック中心を通る断面
    intersection() { whole(); translate([-50, cy(j1_center_pin[1]) - 100, -1]) cube([200, 100, 100]); }

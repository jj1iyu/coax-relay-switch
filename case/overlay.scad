// KiCad の rev0.3 部品配置をケースに重ねて干渉を確認するためのファイル
include <coax_relay_case.scad>
include <pcb_real.scad>
part = "none";
view = "iso";          // "iso" / "front" / "cut_usb" / "cut_fj"
which = 0;             // 1: ケース×部品, 2: フタ×部品, 3: フタ×ケース（干渉チェック用）

hdr_sp = 2.5;  zero_t = 1.0;  usbc_h = 3.26;  usbc_w = 8.94;  usbc_d = 7.35;
sock_h = sock_top - hdr_sp;

module real_board() {
    color("darkgreen") translate([cx(0), cy(pcb_d), floor_t + standoff_h])
        difference() {
            cube([pcb_w, pcb_d, pcb_t]);
            for (p = pcb_pads) translate([p[0], pcb_d - p[1], -1]) cylinder(d = p[2]*0.6, h = 4, $fn = 16);
        }
    for (q = pcb_parts) if (q[0] != "LED1")
        color(q[0] == "J1" ? "dimgray" : q[0] == "J4" ? "limegreen" : q[0] == "F1" ? "khaki" : "steelblue", 0.85)
            translate([cx(q[1]), cy(min(q[4], pcb_d)), pcb_top]) cube([q[3]-q[1], min(q[4], pcb_d)-q[2], q[5]]);
    // U1: ソケット + ヘッダ + RP2040-Zero + USB-C（前向き）
    ux = u1_center[0]; uy = u1_center[1];
    color("black") for (sx = [-7.62, 7.62]) translate([cx(ux + sx) - 1.27, cy(uy + 11.43), pcb_top]) cube([2.54, 22.86, sock_h]);
    color("dimgray") for (sx = [-7.62, 7.62]) translate([cx(ux + sx) - 1.27, cy(uy + 11.43), pcb_top + sock_h]) cube([2.54, 22.86, hdr_sp]);
    color("royalblue") translate([cx(ux) - 9, cy(uy + 11.75), pcb_top + sock_top]) cube([18, 23.5, zero_t]);
    color("silver") translate([cx(ux) - usbc_w/2, cy(uy + 11.75), pcb_top + sock_top + zero_t]) cube([usbc_w, usbc_d, usbc_h]);
    // LED（足を90°曲げて前面の穴へ）
    color("red") translate([cx(led_x), -1.0, pcb_top + led_z]) rotate([-90,0,0]) cylinder(d=3, h=5.3);
    // M3 ネジ頭
    color("gray") for (h = holes) translate([cx(h[0]), cy(h[1]), pcb_top]) cylinder(d=5.5, h=2.5);
}
// 外から挿すもの（F-J 本体・ナット、DCプラグ、USB-Cプラグ）
module plugs() {
    color("gold") translate([cx(fj_x), 0, pcb_top + fj_z]) {
        rotate([-90,0,0]) cylinder(d=12.7, h=2.8, $fn=6);              // 内側ナット
        rotate([-90,0,0]) translate([0,0,2.8]) cylinder(d=4, h=8);     // 中心ピン・はんだ部
        rotate([90,0,0]) cylinder(d=9.5, h=16.5);                       // ネジ部（外）
    }
    color("orange", 0.6) translate([cx(usb_x) - 6.25, -wall - 18, pcb_top + usb_z - 3.75]) cube([12.5, 18 + 0.8 - 0.01, 7.5]);  // USB-C プラグ（樹脂 12.5x7.5）
    color("orange", 0.6) translate([cx(dc_x), -wall - 20, pcb_top + dc_z]) rotate([-90,0,0]) cylinder(d=9.5, h=20 + wall - 1.2 - 0.01);   // DCプラグ樹脂部
}
module fj_inside() { translate([cx(fj_x), 0.01, pcb_top + fj_z]) rotate([-90,0,0]) { cylinder(d=12.7, h=2.8, $fn=6); translate([0,0,2.8]) cylinder(d=4, h=8); } }

if (which == 1) intersection() { case_body(); union() { real_board(); fj_inside(); } }
else if (which == 2) intersection() { translate([0,0,oh]) lid_assembled(); union() { real_board(); fj_inside(); } }
else if (which == 3) intersection() { translate([0,0,oh]) lid_assembled(); case_body(); }
else if (which == 4) intersection() { union() { real_board(); } fj_inside(); }
else if (which == 5) intersection() { case_body(); plugs(); }
else if (view == "cut_usb") intersection() { union() { case_body(); translate([0,0,oh]) lid_assembled(); real_board(); plugs(); } translate([cx(usb_x), -50, -1]) cube([100, 200, 100]); }
else if (view == "cut_fj")  intersection() { union() { case_body(); translate([0,0,oh]) lid_assembled(); real_board(); plugs(); } translate([cx(fj_x), -50, -1]) cube([100, 200, 100]); }
else { color("ivory", view == "front" ? 1 : 0.45) case_body(); real_board(); plugs(); }

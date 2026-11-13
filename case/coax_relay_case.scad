// =====================================================================
//  同軸リレー制御基板 rev0.3 用ケース（3Dプリント用・サポート不要）
//  基板 66 x 46 mm / M3取付穴 4隅（端から3.5mm）
//    前面だけにすべての穴をまとめる（左から）:
//      USB-C (RP2040-Zero) | DCジャック (J1) | LED (足を90°曲げて前面へ) | F-J (シャーシ用, J4から配線)
//    背面・側面・フタには穴なし。フタは M3 ネジ2本で固定
//
//  part = "case" / "lid" / "both"(印刷用に並べる) / "assembly"(確認用)
//  寸法の単位は mm。実物に合わせて ★ の値を調整してください。
// =====================================================================
part = "assembly";

// ---------- 基本寸法 ----------
pcb_w   = 66;      // 基板 X
pcb_d   = 46;      // 基板 Y（前面=コネクタ側が y=46）
pcb_t   = 1.6;
gap     = 0.5;     // 基板と左右・奥の内壁のすき間
gap_f   = 0.8;     // ★基板の前端と前面内壁のすき間（DCジャック・USBの前面が当たる）
back_margin = 2;   // 奥の余裕（配線は全部前面なので小さくてよい）
wall    = 2.4;
floor_t = 2.0;
r_out   = 3.0;     // 外側の角の丸み
standoff_h = 5.0;  // 底面から基板裏まで（リード足の逃げ）
inner_h = 32.0;    // 床上面から壁の上端まで（rev0.2 は 26）
lid_t   = 2.0;
lip_h   = 3.0;     // フタの位置決めリップ
lip_t   = 1.2;
lip_clr = 0.3;     // リップと内壁のすき間（きつい時は増やす）

// ---------- 前面の穴（x は基板左端から, z は基板上面から）★ ----------
sock_top  = 12.0;   // ★基板上面から RP2040-Zero 基板の下面まで（実測 12mm）
usb_x     = 17.0;   // RP2040-Zero 中心
usb_z     = sock_top + 1.0 + 1.6;   // USB-C 中心 = ソケット + Zero基板1.0 + USB-C高さの半分
usb_w     = 13.5;   // USB開口 幅（ケーブルの樹脂部分が通る大きさ）
usb_h     = 9.5;    // USB開口 高さ（±0.5mm の高さずれを吸収）
dc_x      = 33.0;   // J1 中心
dc_z      = 6.5;    // J1 穴中心の高さ（データシート値）
dc_hole   = 10.0;   // DCプラグ用の穴径
led_x     = 42.27;  // LED1 の2本の足の中間
led_z     = 2.8;    // ★足を曲げたLEDの中心高さ
led_hole  = 3.3;
fj_x      = 52.0;   // F-J 中心: J4 の正面
fj_z      = 8.0;    // F-J 中心の高さ（ナットが基板に当たらない高さ）
fj_d      = 9.8;    // F-J 取付穴径（ネジ 3/8-32 = 9.53）
fj_flat   = 8.1;    // F-J 取付穴のDカット幅（データシート 7.9）

// ---------- 派生寸法 ----------
iw = pcb_w + 2*gap;
id = gap_f + pcb_d + back_margin;
ow = iw + 2*wall;
od = id + 2*wall;
oh = floor_t + inner_h;
pcb_top = floor_t + standoff_h + pcb_t;
holes = [[3.5,3.5],[62.5,3.5],[3.5,42.5],[62.5,42.5]];
// 基板座標(x右, y=0が奥, y=46が前) → ケース内側座標（前面内壁が y=0, 奥へ +Y）
function cx(x) = gap + x;
function cy(y) = gap_f + (pcb_d - y);
// フタ固定ボス: 左右の壁の中ほど。基板上の部品の無い帯の真上（下面は基板上面から約11mm上）
lid_bosses = [[3.4, cy(25)], [iw - 3.4, cy(31)]];
boss_r = 3.5;  boss_h = 7;  screw_pilot = 2.6;  screw_clear = 3.4;

$fn = 48;
eps = 0.01;

module rbox(w, d, h, r) {
    translate([r, r, 0]) linear_extrude(h) offset(r) square([w-2*r, d-2*r]);
}

module dcut_hole(d, flat, len) {          // Dカット（両側）穴, Y方向に貫通
    rotate([90,0,0]) linear_extrude(len, center=true)
        intersection() { circle(d=d); square([flat, d+1], center=true); }
}

module label(t, size=4) {
    linear_extrude(1) text(t, size=size, font="DejaVu Sans:style=Bold", halign="center", valign="center");
}
// 前面への刻印（外から見て読める向き）
module front_label(x, z, t, size) {
    translate([cx(x), -wall + 0.6, z]) rotate([90,0,0]) label(t, size);
}

// ---------------------------------------------------------------- case
module case_body() {
    difference() {
        translate([-wall, -wall, 0]) rbox(ow, od, oh, r_out);
        // 内部
        translate([0, 0, floor_t]) cube([iw, id, inner_h + 1]);
        // USB-C: ケーブルの樹脂部分ごと入る開口 + 外側の座ぐり（壁1.0mmまで）。上辺は短いブリッジ
        translate([cx(usb_x) - usb_w/2, -wall - 1, pcb_top + usb_z - usb_h/2]) cube([usb_w, wall + 2, usb_h]);
        translate([cx(usb_x) - 8, -wall - 1, pcb_top + usb_z - 5.5]) cube([16, 1 + wall - 1.0, 11]);
        // DCジャック: 穴 + 外側の座ぐり（壁を薄くしてプラグを届かせる）
        translate([cx(dc_x), 1, pcb_top + dc_z]) rotate([90,0,0]) cylinder(d=dc_hole, h=wall + 2);
        translate([cx(dc_x), -1.2, pcb_top + dc_z]) rotate([90,0,0]) cylinder(d=13, h=wall);
        // LED
        translate([cx(led_x), 1, pcb_top + led_z]) rotate([90,0,0]) cylinder(d=led_hole, h=wall + 2);
        // F-J
        translate([cx(fj_x), -wall/2, pcb_top + fj_z]) dcut_hole(fj_d, fj_flat, wall + 2);
        // 前面の刻印
        front_label(usb_x, pcb_top + usb_z + usb_h/2 + 3.0, "USB", 3.2);
        front_label(dc_x,  pcb_top + dc_z + 10.5, "DC12V", 3.2);
        front_label(led_x, pcb_top + led_z + 4.0, "B", 2.6);
        front_label(fj_x,  pcb_top + fj_z + 10.5, "ANT SW", 3.2);
    }
    // 基板スタンドオフ（M3 タッピング下穴, 深さ6.2mm）
    for (h = holes) translate([cx(h[0]), cy(h[1]), floor_t - eps])
        difference() {
            cylinder(d=6.5, h=standoff_h + eps);
            translate([0,0,-(floor_t - 0.8)]) cylinder(d=screw_pilot, h=standoff_h + floor_t);
        }
    // フタ固定ボス（壁から張り出し, 下面45°でサポート不要）
    for (b = lid_bosses) {
        side = b[0] < iw/2 ? -1 : 1;
        wx = side < 0 ? 0 : iw;
        difference() {
            hull() {
                translate([b[0], b[1], oh - boss_h]) cylinder(r=boss_r, h=boss_h);
                translate([wx - (side < 0 ? 0 : 0.01), b[1] - boss_r, oh - boss_h - (boss_r*2)]) cube([0.01, 2*boss_r, 0.01]);
            }
            translate([b[0], b[1], oh - boss_h - 1]) cylinder(d=screw_pilot, h=boss_h + 2);
        }
    }
}

// ---------------------------------------------------------------- lid
// 組み付けた状態の座標で作る（上面 z=0..lid_t, リップは下向き）
module lid_assembled() {
    difference() {
        union() {
            translate([-wall, -wall, 0]) rbox(ow, od, lid_t, r_out);
            translate([0, 0, -lip_h]) difference() {
                translate([lip_clr, lip_clr, 0]) cube([iw - 2*lip_clr, id - 2*lip_clr, lip_h + eps]);
                translate([lip_clr + lip_t, lip_clr + lip_t, -1]) cube([iw - 2*lip_clr - 2*lip_t, id - 2*lip_clr - 2*lip_t, lip_h + 2]);
                for (b = lid_bosses) translate([b[0], b[1], -1]) cylinder(r=boss_r + 1.2, h=lip_h + 2);
            }
        }
        for (b = lid_bosses) translate([b[0], b[1], -lip_h - 1]) cylinder(d=screw_clear, h=lid_t + lip_h + 2);
        translate([iw/2, id/2 + 5, lid_t - 0.6]) label("COAX SW", 6);
        translate([iw/2, id/2 - 5, lid_t - 0.6]) label("A: OFF   B: ON", 3.5);
    }
}
// 印刷用: 上面を下にする
module lid() { rotate([180,0,0]) translate([0, 0, -lid_t]) lid_assembled(); }

if (part == "case") case_body();
else if (part == "lid") lid();
else if (part == "both") { case_body(); translate([ow + 6, id, 0]) lid(); }
else if (part == "assembly") {
    case_body();
    translate([0, 0, oh + 15]) color("white", 0.5) lid_assembled();
}

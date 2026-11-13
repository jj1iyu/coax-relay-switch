// =====================================================================
//  同軸リレー制御基板 rev0.2 用ケース（3Dプリント用）
//  基板 60 x 46 mm / M3取付穴 4隅（端から3.5mm）
//    左側面 : DCジャック (J1, MJ-179PH)
//    奥側面 : USB-C (RP2040-Zero)
//    手前側面: Fコネクタ ジャック（秋月 F-J シャーシ用, 3/8-32, Dカット穴）
//             基板との間に配線スペース（front_margin）
//    フタ   : LED窓, M3ネジ2本で固定
//
//  part = "case" / "lid" / "both"(印刷用に並べる) / "assembly"(確認用)
//  寸法の単位は mm。実物に合わせて ★ の値を調整してください。
// =====================================================================
part = "assembly";

// ---------- 基本寸法 ----------
pcb_w   = 60;      // 基板 X
pcb_d   = 46;      // 基板 Y
pcb_t   = 1.6;
gap     = 0.5;     // 基板と内壁のすき間
front_margin = 15; // ★手前（F-J側）の配線スペース：J4端子台→F-Jの配線用
back_margin  = 10; // ★奥（USB側）の余裕。USBプラグは樹脂部分ごと開口から差し込む
wall    = 2.4;
floor_t = 2.0;
r_out   = 3.0;     // 外側の角の丸み
standoff_h = 5.0;  // 底面から基板裏まで（リード足の逃げ）
inner_h = 26.0;    // 床上面から壁の上端まで
lid_t   = 2.0;
lip_h   = 3.0;     // フタの位置決めリップ
lip_t   = 1.2;
lip_clr = 0.3;     // リップと内壁のすき間（きつい時は増やす）

// ---------- コネクタ位置（基板座標: 左上=USB側の左端を原点, X右, Y下）★ ----------
dc_y      = 20.0;   // J1 中心（基板上辺から）
dc_z      = 6.5;    // J1 穴中心の基板上面からの高さ（データシート値）
dc_hole   = 10.0;   // DCプラグ用の穴径
usb_x     = 43.0;   // RP2040-Zero 中心（基板左端から）
usb_z     = 13.6;   // ★USB-C中心の基板上面からの高さ（ソケット8.5+ヘッダ2.5+基板1.0+USB1.6）
usb_w     = 13.5;   // USB開口 幅（ケーブルの樹脂部分が通る大きさ）
usb_h     = 8.5;    // USB開口 高さ
fj_x      = 44.0;   // F-J 中心（基板左端から）: J4の12V端子の正面
fj_z      = 5.0;    // F-J 中心の基板上面からの高さ（配線スペース内なので低めでよい）
fj_d      = 9.8;    // F-J 取付穴径（ネジ 3/8-32 = 9.53）
fj_flat   = 8.1;    // F-J 取付穴のDカット幅（データシート 7.9）
led_x     = 15.0;   // LED1（基板左端から）
led_y     = 36.5;   // LED1（基板上辺から）
led_hole  = 3.3;    // フタのLED窓（3mm LEDを足を伸ばして差し込む）

// ---------- 派生寸法 ----------
iw = pcb_w + 2*gap;
id = pcb_d + 2*gap + front_margin + back_margin;   // 基板の手前と奥に余裕
ow = iw + 2*wall;
od = id + 2*wall;
oh = floor_t + inner_h;
pcb_top = floor_t + standoff_h + pcb_t;
holes = [[3.5,3.5],[56.5,3.5],[3.5,42.5],[56.5,42.5]];
// 基板座標 → ケース内側座標（上から見て基板と同じ向き。USB辺が奥=+Y）
function cx(x) = gap + x;
function cy(y) = id - gap - back_margin - y;
lid_bosses = [[3.4, 7], [iw-3.4, id-4.5]];   // フタ固定ネジ（手前左・奥右とも基板の外の余白に置く）
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

// ---------------------------------------------------------------- case
module case_body() {
    difference() {
        translate([-wall, -wall, 0]) rbox(ow, od, oh, r_out);
        // 内部
        translate([0, 0, floor_t]) cube([iw, id, inner_h + 1]);
        // DCジャック（左側面）: 穴 + 外側の座ぐり（壁を薄くしてプラグを届かせる）
        translate([-wall-1, cy(dc_y), pcb_top + dc_z]) rotate([0,90,0]) cylinder(d=dc_hole, h=wall+2);
        translate([-wall-1, cy(dc_y), pcb_top + dc_z]) rotate([0,90,0]) cylinder(d=13, h=1 + wall - 1.2);
        // USB-C（奥側面）: 壁の上端まで切り欠いた開口（上はフタで塞ぐ。サポート不要で、高さのずれにも強い）
        //                  + 外側の座ぐり（壁1.0mmまで、こちらも上端まで）
        translate([cx(usb_x) - usb_w/2, id - 1, pcb_top + usb_z - usb_h/2]) cube([usb_w, wall + 2, oh]);
        translate([cx(usb_x) - 8, id + 1.0, pcb_top + usb_z - 5.5]) cube([16, wall, oh]);
        // F-J（手前側面）
        translate([cx(fj_x), -wall/2, pcb_top + fj_z]) dcut_hole(fj_d, fj_flat, wall + 2);
        // 底の基板ネジ用の下穴は貫通させない（底面はフラット）
        // 刻印
        translate([-wall + 0.6, cy(dc_y), pcb_top + dc_z + 8.5]) rotate([90,0,-90]) label("DC12V", 3.5);
        translate([cx(usb_x), id + wall - 0.6, pcb_top + usb_z - 8]) rotate([90,0,180]) label("USB", 3.5);
        translate([cx(fj_x), -wall + 0.6, pcb_top + fj_z + 8.5]) rotate([90,0,0]) label("ANT SW", 3.5);
    }
    // 基板スタンドオフ（M3 タッピング下穴）
    for (h = holes) translate([cx(h[0]), cy(h[1]), floor_t - eps])
        difference() {
            cylinder(d=6.5, h=standoff_h + eps);
            translate([0,0,-(floor_t - 0.8)]) cylinder(d=screw_pilot, h=standoff_h + floor_t);   // 下穴深さ 6.2mm（底は0.8mm残す）
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
                translate([cx(usb_x) - 9, id - 4, -1]) cube([18, 6, lip_h + 2]);
            }
        }
        for (b = lid_bosses) translate([b[0], b[1], -lip_h - 1]) cylinder(d=screw_clear, h=lid_t + lip_h + 2);
        translate([cx(led_x), cy(led_y), -1]) cylinder(d=led_hole, h=lid_t + 2);
        translate([cx(led_x), cy(led_y) + 4.5, lid_t - 0.6]) label("ANT B", 2.8);
        translate([iw/2 + 4, id/2 + 6, lid_t - 0.6]) label("COAX SW", 5);
    }
}
// 印刷用: 上面を下にする
module lid() { rotate([180,0,0]) translate([0, 0, -lid_t]) lid_assembled(); }

// ---------------------------------------------------------------- 確認用ダミー
module dummy_parts() {
    color("green", 0.8) translate([cx(0), cy(pcb_d), floor_t + standoff_h]) cube([pcb_w, pcb_d, pcb_t]);
    // J1 DCジャック 14.5 x 9 x 11
    color("dimgray") translate([cx(0), cy(dc_y) - 4.5, pcb_top]) cube([14.5, 9, 11]);
    // RP2040-Zero on sockets
    color("black") translate([cx(usb_x) - 9, cy(26.25), pcb_top]) cube([18, 23.5, 11]);
    color("royalblue") translate([cx(usb_x) - 9, cy(26.25), pcb_top + 11]) cube([18, 23.5, 1.0]);
    color("silver") translate([cx(usb_x) - 4.5, cy(2.75) - 7.3, pcb_top + 12]) cube([9, 7.3, 3.2]);
    // C1
    color("navy") translate([cx(23), cy(4.5), pcb_top]) cylinder(d=6.3, h=11.5);
    // J4 terminal
    color("limegreen") translate([cx(41.4), cy(44.7), pcb_top]) cube([10.2, 9.9, 12.5]);
    // F-J
    color("gold") translate([cx(fj_x), 0, pcb_top + fj_z]) rotate([90,0,0]) {
        translate([0,0,-2.8]) cylinder(d=12.7, h=2.8, $fn=6);
        cylinder(d=9.5, h=16.5);
    }
    // LED (legs extended up to lid)
    color("red") translate([cx(led_x), cy(led_y), oh - 5.5]) cylinder(d=3, h=5.3);
}

if (part == "case") case_body();
else if (part == "lid") lid();
else if (part == "both") { case_body(); translate([ow + 6, id, 0]) lid(); }
else if (part == "assembly") {
    case_body();
    dummy_parts();
    translate([0, 0, oh + 15]) color("white", 0.5) lid_assembled();
}

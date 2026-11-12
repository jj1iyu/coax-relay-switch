include <coax_relay_case.scad>
part = "none";
which = 0;
module parts_no_fj_thread() {
    color("green") translate([cx(0), cy(pcb_d), floor_t + standoff_h]) cube([pcb_w, pcb_d, pcb_t]);
    translate([cx(0), cy(dc_y) - 4.5, pcb_top]) cube([14.5, 9, 11]);
    translate([cx(usb_x) - 9, cy(26.25), pcb_top]) cube([18, 23.5, 12]);
    translate([cx(usb_x) - 4.5, cy(2.75) - 7.3, pcb_top + 12]) cube([9, 7.3 + 0.5, 3.2]);
    translate([cx(23), cy(4.5), pcb_top]) cylinder(d=6.3, h=11.5);
    translate([cx(41.4), cy(44.7), pcb_top]) cube([10.2, 9.9, 12.5]);
    translate([cx(fj_x), -0.01, pcb_top + fj_z]) rotate([-90,0,0]) cylinder(d=12.7, h=2.8, $fn=6);
    for (h = holes) translate([cx(h[0]), cy(h[1]), pcb_top]) cylinder(d=5.5, h=3); // M3 screw heads
}
if (which == 1) intersection() { case_body(); parts_no_fj_thread(); }
if (which == 2) intersection() { translate([0,0,oh]) lid_assembled(); parts_no_fj_thread(); }
if (which == 3) intersection() { translate([0,0,oh]) lid_assembled(); case_body(); }

// Bedside power-brick caddy — parametric. All units mm.
// Open in OpenSCAD, tweak the numbers, F6 then F7 to export STL.

width        = 180;  // outer, left-right
depth        = 90;   // outer, front-back
height       = 60;   // outer
wall         = 2.4;
floor_t      = 2.4;
corner_r     = 6;
compartments = 2;

slot_w       = 14;   // cable notch width (fits a plug's cord, not the plug)
back_slot_d  = 30;   // depth of back notch from top (wall cord in)
front_slot_d = 20;   // depth of front notch from top (charging cable out)

vent_w   = 4;        // floor vent slots let bricks breathe
vent_len = depth - 2*wall - 20;
vent_gap = 10;

$fn = 48;

module rbox(w, d, h, r) {
    linear_extrude(h)
        offset(r) offset(-r) square([w, d]);
}

module notch(x, y_wall, d) {
    // U-shaped cut down from the top edge, rounded bottom
    translate([x, y_wall, height - d + slot_w/2]) rotate([-90, 0, 0])
        cylinder(d = slot_w, h = wall + 2, center = true);
    translate([x - slot_w/2, y_wall - wall/2 - 1, height - d + slot_w/2])
        cube([slot_w, wall + 2, d]);
}

inner_w = width - 2*wall;
cell_w  = (inner_w - (compartments - 1)*wall) / compartments;

difference() {
    rbox(width, depth, height, corner_r);
    // hollow, leaving dividers
    for (i = [0 : compartments - 1])
        translate([wall + i*(cell_w + wall), wall, floor_t])
            rbox(cell_w, depth - 2*wall, height, max(corner_r - wall, 0.5));
    for (i = [0 : compartments - 1]) {
        cx = wall + i*(cell_w + wall) + cell_w/2;
        notch(cx, depth - wall/2, back_slot_d);   // back wall
        notch(cx, wall/2,         front_slot_d);  // front wall
        // floor vents
        n = floor((cell_w - 16) / vent_gap);
        for (j = [0 : n - 1])
            translate([cx - (n-1)*vent_gap/2 + j*vent_gap - vent_w/2,
                       (depth - vent_len)/2, -1])
                rbox(vent_w, vent_len, floor_t + 2, vent_w/2 - 0.01);
    }
}

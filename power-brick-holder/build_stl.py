"""Cradle for a 4-outlet power board (AU style) to sit beside the bed.

Generates:
  power_board_cradle_full.stl      - one piece, needs a ~350 mm bed
  power_board_cradle_half_A.stl    - left half  } for normal 220-256 mm printers:
  power_board_cradle_half_B.stl    - right half } print both + 2 keys, glue together
  power_board_cradle_key.stl       - bow-tie key (print 2) that locks the halves

Edit the BOARD_* numbers to your board, measured with calipers/ruler.
pip install manifold3d trimesh numpy
"""
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

# --- your power board (outer size, mm) ---
BOARD_L, BOARD_W, BOARD_H = 340, 62, 38
CLEAR = 1.5            # gap all round so it drops in easily

# --- cradle ---
WALL, FLOOR = 3.0, 4.0
WALL_H = 22            # wall height above the floor; keep below BOARD_H so plugs clear
R_OUT = 12
CORD_SIDE = +1         # +1 = mains lead exits right end, -1 = left end
CORD_SLOT_W = 12       # mains lead diameter ~7 mm; plug won't need to pass
FINGER_W = 40          # scoops in the long walls so you can lift the board out
SCREW_HOLES = True     # two countersunk holes to screw it to a nightstand/bed frame
KEY_DEPTH, KEY_CLEAR = 2.6, 0.15
SEG = 64

IN_L, IN_W = BOARD_L + 2 * CLEAR, BOARD_W + 2 * CLEAR
L, W, H = IN_L + 2 * WALL, IN_W + 2 * WALL, FLOOR + WALL_H


def rrect(l, w, r):
    r = min(r, l / 2 - 1e-3, w / 2 - 1e-3)
    return CrossSection.square([l - 2 * r, w - 2 * r]).translate([r, r]).offset(r, circular_segments=SEG)


def u_slot(cx, y0, depth_y, width, bottom_z):
    """U-shaped cut from the top down to bottom_z, through a wall lying along X."""
    rad = width / 2
    cyl = Manifold.cylinder(depth_y, rad, circular_segments=SEG).rotate([-90, 0, 0]).translate([cx, y0, bottom_z + rad])
    box = Manifold.cube([width, depth_y, H]).translate([cx - rad, y0, bottom_z + rad])
    return cyl + box



body = Manifold.extrude(rrect(L, W, R_OUT), H)
body -= Manifold.extrude(rrect(IN_L, IN_W, R_OUT - WALL), H).translate([WALL, WALL, FLOOR])

# mains-lead exit through the end wall, down to the floor
end_x = L - WALL - 1 if CORD_SIDE > 0 else -1
slot = u_slot(0, -(WALL + 2) / 2, WALL + 2, CORD_SLOT_W, FLOOR).rotate([0, 0, 90])
body -= slot.translate([end_x + (WALL + 2) / 2, W / 2, 0])

# finger scoops, both long walls, centred
for y in (-1, W - WALL - 1):
    scoop = Manifold.cylinder(WALL + 2, FINGER_W / 2, circular_segments=SEG).rotate([-90, 0, 0])
    body -= scoop.translate([L / 2, y, H + FINGER_W / 2 - 14])

if SCREW_HOLES:
    for x in (L * 0.25, L * 0.75):
        hole = Manifold.cylinder(FLOOR + 2, 2.25, circular_segments=SEG).translate([x, W / 2, -1])
        csk = Manifold.cylinder(2.3, 2.25, 4.6, circular_segments=SEG).translate([x, W / 2, FLOOR - 2.3 + 0.01])
        body -= hole + csk

# bow-tie key pockets under the floor, across the centre seam
pocket = Manifold.extrude(CrossSection([[(-12, -9), (0, -4), (12, -9), (12, 9), (0, 4), (-12, 9)]]).offset(KEY_CLEAR), KEY_DEPTH + 0.01).translate([0, 0, -0.01])
key_ys = (W * 0.27, W * 0.73)
for y in key_ys:
    body -= pocket.translate([L / 2, y, 0])


def save(m, name):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    assert t.is_watertight, name
    t.export(name)
    ext = t.bounds[1] - t.bounds[0]
    print(f"{name}: {ext[0]:.0f} x {ext[1]:.0f} x {ext[2]:.0f} mm, {t.volume/1000:.0f} cm^3")
    return t


save(body, "power_board_cradle_full.stl")
big = 1000
half_a = body ^ Manifold.cube([L / 2, big, big]).translate([0, -big / 2, -1])
half_b = body ^ Manifold.cube([L / 2, big, big]).translate([L / 2, -big / 2, -1])
save(half_a, "power_board_cradle_half_A.stl")
save(half_b.translate([-L / 2, 0, 0]), "power_board_cradle_half_B.stl")
key = Manifold.extrude(CrossSection([[(-12, -9), (0, -4), (12, -9), (12, 9), (0, 4), (-12, 9)]]), KEY_DEPTH - 0.2)
save(key, "power_board_cradle_key.stl")

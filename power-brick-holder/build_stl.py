"""Builds power_brick_holder.stl (same geometry as the .scad) without OpenSCAD.
pip install manifold3d trimesh numpy"""
import math
import numpy as np
import trimesh
from manifold3d import Manifold, CrossSection

W, D, H = 180, 90, 60
WALL, FLOOR, R = 2.4, 2.4, 6
N = 2
SLOT_W, BACK_D, FRONT_D = 14, 30, 20
VENT_W, VENT_GAP = 4, 10
VENT_LEN = D - 2 * WALL - 20
SEG = 48


def rbox(w, d, h, r):
    r = min(r, w / 2 - 1e-3, d / 2 - 1e-3)
    cs = CrossSection.square([w - 2 * r, d - 2 * r]).translate([r, r]).offset(r, circular_segments=SEG)
    return Manifold.extrude(cs, h)


def notch(x, y_wall, d):
    z = H - d + SLOT_W / 2
    cyl = Manifold.cylinder(WALL + 2, SLOT_W / 2, circular_segments=SEG, center=True)
    cyl = cyl.rotate([90, 0, 0]).translate([x, y_wall, z])
    box = Manifold.cube([SLOT_W, WALL + 2, d]).translate([x - SLOT_W / 2, y_wall - WALL / 2 - 1, z])
    return cyl + box


body = rbox(W, D, H, R)
cell_w = (W - 2 * WALL - (N - 1) * WALL) / N
for i in range(N):
    x0 = WALL + i * (cell_w + WALL)
    cx = x0 + cell_w / 2
    body -= rbox(cell_w, D - 2 * WALL, H, max(R - WALL, 0.5)).translate([x0, WALL, FLOOR])
    body -= notch(cx, D - WALL / 2, BACK_D)
    body -= notch(cx, WALL / 2, FRONT_D)
    n = math.floor((cell_w - 16) / VENT_GAP)
    for j in range(n):
        vx = cx - (n - 1) * VENT_GAP / 2 + j * VENT_GAP - VENT_W / 2
        body -= rbox(VENT_W, VENT_LEN, FLOOR + 2, VENT_W / 2 - 0.01).translate([vx, (D - VENT_LEN) / 2, -1])

m = body.to_mesh()
mesh = trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts))
assert mesh.is_watertight
mesh.export("power_brick_holder.stl")
print("bounds", mesh.bounds.tolist(), "volume cm^3", round(mesh.volume / 1000, 1))

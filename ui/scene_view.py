"""Orbit a point cloud or a triangulated surface derived from one depth map."""
import tkinter as tk
from tkinter import ttk

import cv2
import numpy as np
from PIL import Image, ImageTk

from ui.layout import dialog_bounds, place_dialog

BG = "#0b111d"


def make_geometry(near, image, max_side):
    h, w = near.shape
    factor = min(1.0, max_side / max(h, w))
    size = max(1, round(w * factor)), max(1, round(h * factor))
    disparity = cv2.resize(near, size, interpolation=cv2.INTER_AREA)
    z = 1.0 + 2.0 * (1.0 - disparity)
    y, x = np.indices(z.shape, dtype=np.float32)
    focal = max(size) * .94
    points = np.stack(((x - (size[0] - 1) / 2) * z / focal,
                       (y - (size[1] - 1) / 2) * z / focal, z - np.median(z)), axis=-1)
    colors = np.asarray(image.convert("RGB").resize(size, Image.Resampling.BILINEAR))
    return points, colors


def make_faces(points):
    indices = np.arange(points.shape[0] * points.shape[1], dtype=np.int32).reshape(points.shape[:2])
    a, b = indices[:-1, :-1].ravel(), indices[:-1, 1:].ravel()
    c, d = indices[1:, :-1].ravel(), indices[1:, 1:].ravel()
    faces = np.concatenate((np.stack((a, b, d), axis=1), np.stack((a, d, c), axis=1)))
    z = points.reshape(-1, 3)[faces, 2]
    # Leave holes across sharp depth discontinuities instead of stitching foreground to background.
    return faces[np.ptp(z, axis=1) < .13]


def project(points, width, height, yaw, pitch, zoom):
    c, s = np.cos(yaw), np.sin(yaw)
    cp, sp = np.cos(pitch), np.sin(pitch)
    x0, y0, z0 = points.T
    x = c * x0 + s * z0
    rotated = c * z0 - s * x0
    y = cp * y0 - sp * rotated
    z = cp * rotated + sp * y0 + 3.25
    focal = min(width, height) * 1.7 * zoom
    pixels = np.stack((x * focal / z + width / 2, y * focal / z + height / 2), axis=1)
    return np.rint(pixels).astype(np.int32), z


def draw_scene(points, colors, faces, width, height, yaw, pitch, zoom, wireframe=False):
    pixels, z = project(points, width, height, yaw, pitch, zoom)
    frame = np.full((height, width, 3), (11, 17, 29), dtype=np.uint8)
    if faces is None:
        orders = np.argsort(-z)
        px, py = pixels[orders].T
        radius = max(1, min(2, min(width, height) // 200))
        valid = (px >= radius) & (px < width - radius) & (py >= radius) & (py < height - radius)
        xx, yy = np.meshgrid(np.arange(-radius, radius + 1), np.arange(-radius, radius + 1))
        circle = xx**2 + yy**2 <= radius**2 + 1
        frame[py[valid, None] + yy[circle], px[valid, None] + xx[circle]] = colors[orders[valid], None, :]
    else:
        order = np.argsort(-z[faces].mean(axis=1))
        triangles = pixels[faces[order]]
        shades = colors[faces[order]].mean(axis=1).astype(np.uint8)
        for triangle, shade in zip(triangles, shades):
            color = tuple(map(int, shade))
            if wireframe:
                cv2.fillConvexPoly(frame, triangle, (20, 30, 50))
                cv2.polylines(frame, (triangle,), True, (114, 175, 245), 1, cv2.LINE_AA)
            else:
                cv2.fillConvexPoly(frame, triangle, color)
    return Image.fromarray(frame)


def show_scene(root, near, image, depth, polish=False):
    win = tk.Toplevel(root)
    win.title("Peeky 3 - Podgl\u0105d 3D" if polish else "Peeky 3 - 3D Preview")
    win.configure(bg=BG)
    scene = tk.Canvas(win, background=BG, highlightthickness=0, cursor="fleur", width=2, height=2)
    scene.pack(fill="both", expand=True, padx=12, pady=(10, 6))
    bar = ttk.Frame(win, padding=(10, 4))
    bar.pack(fill="x")
    note = ("Przeci\u0105gnij, aby obr\u00f3ci\u0107. Rolka zmienia zoom. Geometria z jednego uj\u0119cia."
            if polish else "Drag to orbit. Scroll to zoom. Geometry from one image.")
    tk.Label(win, text=note, bg=BG, fg="#bbc8e0").pack(padx=12, pady=(5, 10), anchor="w")

    cloud, cloud_rgb = make_geometry(near, image, 230)
    surface, surface_rgb = make_geometry(near, image, 80)
    _, surface_depth = make_geometry(near, depth, 80)
    faces = make_faces(surface)
    modes = ("Punkty RGB", "Siatka", "Siatka RGB", "Siatka g\u0142\u0119bi") if polish else (
        "RGB points", "Wireframe", "RGB mesh", "Depth mesh")
    selected = tk.StringVar(value=modes[0])
    yaw, pitch, zoom = .52, -.21, .82
    anchor = pending = picture = None
    rendered = scene.create_image(0, 0, anchor="nw")

    def redraw():
        nonlocal picture, pending
        pending = None
        w, h = scene.winfo_width(), scene.winfo_height()
        if w < 16 or h < 16:
            return
        mode = modes.index(selected.get())
        points = cloud if mode == 0 else surface
        colors = cloud_rgb if mode == 0 else surface_depth if mode == 3 else surface_rgb
        view = draw_scene(points.reshape(-1, 3), colors.reshape(-1, 3), None if mode == 0 else faces,
                          w, h, yaw, pitch, zoom, wireframe=mode == 1)
        picture = ImageTk.PhotoImage(view)
        scene.itemconfigure(rendered, image=picture)

    def update(_=None):
        nonlocal pending
        if pending is None:
            pending = win.after(16, redraw)

    def start(event):
        nonlocal anchor
        anchor = event.x, event.y

    def orbit(event):
        nonlocal anchor, yaw, pitch
        if anchor is None:
            return
        yaw += (event.x - anchor[0]) * .008
        pitch = float(np.clip(pitch + (event.y - anchor[1]) * .008, -1.45, 1.45))
        anchor = event.x, event.y
        update()

    def wheel(event):
        nonlocal zoom
        zoom = float(np.clip(zoom * 1.12 ** (event.delta / 120), .45, 2.7))
        update()

    def pose(angle, tilt, scale):
        nonlocal yaw, pitch, zoom
        yaw, pitch, zoom = angle, tilt, scale
        update()

    selector = ttk.Combobox(bar, state="readonly", textvariable=selected, values=modes, width=13)
    selector.pack(side="left", padx=(0, 8))
    selector.bind("<<ComboboxSelected>>", update)
    ttk.Button(bar, text="Prz\u00f3d" if polish else "Front", command=lambda: pose(0, 0, .9)).pack(side="left")
    ttk.Button(bar, text="Pod k\u0105tem" if polish else "Orbit angle",
               command=lambda: pose(.52, -.21, .82)).pack(side="left", padx=5)
    scene.bind("<Configure>", update)
    scene.bind("<ButtonPress-1>", start)
    scene.bind("<B1-Motion>", orbit)
    scene.bind("<MouseWheel>", wheel)
    win.bind("<Escape>", lambda _: win.destroy())
    max_w, max_h = dialog_bounds(win)
    place_dialog(win, width=min(960, max_w), height=min(690, max_h), min_width=350, min_height=265)
    return win


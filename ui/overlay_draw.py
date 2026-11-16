"""Resizable result window for screenshots and interactive UI annotations."""
import tkinter as tk
from tkinter import scrolledtext, ttk

from PIL import Image, ImageDraw, ImageFont, ImageTk

from i18n import Translator
from ui.layout import dialog_bounds, place_dialog

BG = "#0b1220"
PANEL = "#131e30"
FG = "#e5edfb"


def _font(size=14):
    for name in ("segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render(pil_img, shapes, size=None, selected=None):
    img = pil_img.copy() if size is None else pil_img.resize(size, Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(img)
    scale = img.width / pil_img.width, img.height / pil_img.height
    font = _font(max(12, min(20, img.width // 38)))
    for shape in shapes:
        kind = shape["kind"]
        color = shape.get("color", "#38bdf8")
        label = shape.get("label", "")
        if selected is not None:
            if label != str(selected):
                continue
            color = "#ffdf61"
        if kind == "point":
            x, y = [round(v * scale[i]) for i, v in enumerate(shape["xy"])]
            draw.ellipse((x - 10, y - 10, x + 10, y + 10), outline="white", width=5)
            draw.ellipse((x - 10, y - 10, x + 10, y + 10), outline=color, width=3)
            draw.line((x - 15, y, x + 15, y), fill=color, width=2)
            draw.line((x, y - 15, x, y + 15), fill=color, width=2)
            x1, y1 = x + 11, y
        else:
            x1, y1, x2, y2 = [round(v * scale[i % 2]) for i, v in enumerate(shape["xyxy"])]
            draw.rectangle((x1, y1, x2, y2), outline="#111827", width=5)
            draw.rectangle((x1, y1, x2, y2), outline=color, width=3)
            if kind == "text":
                continue
        if label:
            label = label[:60]
            tw = round(draw.textlength(label, font=font))
            while tw + 8 > img.width and len(label) > 1:
                label = label[:-1]
                tw = round(draw.textlength(label, font=font))
            height = font.size + 8 if hasattr(font, "size") else 22
            x = max(0, min(x1, img.width - tw - 9))
            y = max(0, min(y1 - height, img.height - height))
            draw.rectangle((x, y, x + tw + 8, y + height), fill="#101827", outline=color, width=2)
            draw.text((x + 4, y + 3), label, fill="#ffffff", font=font)
    return img


def show_overlay(root, pil_img, shapes, title="Result", body_text="", controls=(), alternate=None, legend=()):
    pl = Translator().lang == "pl"
    win = tk.Toplevel(root)
    win.title(f"Peeky 3 · {title}")
    win.configure(bg=BG)

    buttons = ttk.Frame(win, padding=(10, 6))
    buttons.pack(side="bottom", fill="x")
    original = tk.BooleanVar(value=False)

    def copy():
        win.clipboard_clear()
        win.clipboard_append(copy_text)

    ttk.Button(buttons, text="Zamknij" if pl else "Close", command=win.destroy).pack(side="right")
    if body_text or controls:
        ttk.Button(buttons, text="Kopiuj" if pl else "Copy", command=copy).pack(side="right", padx=6)
    if alternate is not None:
        ttk.Checkbutton(buttons, text="Oryginał" if pl else "Original", variable=original,
                        command=lambda: redraw()).pack(side="left")

    selection = None
    copy_text = body_text
    if controls:
        copy_text = "\n".join(f'{item["number"]}. {item["name"]}  [{item["type"]}]' for item in controls)
        bottom = ttk.Frame(win, padding=(12, 3))
        bottom.pack(side="bottom", fill="x")
        ttk.Label(bottom, text=("Wybierz wiersz, aby podświetlić element na obrazie." if pl
                                else "Select a row to highlight the control on the image.")).pack(anchor="w")
        table = ttk.Treeview(bottom, columns=("num", "name", "type"), show="headings",
                             selectmode="browse", height=min(5, len(controls)))
        for key, label, width in (("num", "#", 42), ("name", "Element" if pl else "Control", 145),
                                  ("type", "Typ" if pl else "Type", 90)):
            table.heading(key, text=label)
            table.column(key, width=width, minwidth=30, stretch=key != "num")
        scroll = ttk.Scrollbar(bottom, command=table.yview)
        table.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        table.pack(side="left", fill="x", expand=True)
        for item in controls:
            table.insert("", "end", iid=str(item["number"]),
                         values=(item["number"], item["name"], item["type"]))

        def select(_=None):
            nonlocal selection
            rows = table.selection()
            selection = rows[0] if rows else None
            redraw()

        def clear():
            table.selection_remove(*table.selection())
            select()

        table.bind("<<TreeviewSelect>>", select)
        ttk.Button(buttons, text="Pokaż wszystkie" if pl else "Show all",
                   command=clear).pack(side="left")
    elif body_text:
        text_box = scrolledtext.ScrolledText(win, wrap="word", width=28, height=5,
                                             bg=PANEL, fg=FG, relief="flat", padx=8, pady=6)
        text_box.insert("1.0", body_text)
        if legend:
            for i, (label, color) in enumerate(legend):
                tag = f"legend-{i}"
                text_box.tag_configure(tag, foreground="#%02x%02x%02x" % color)
                text_box.insert("end", "\n● " + (label or str(i + 1)), tag)
        text_box.configure(state="disabled")
        text_box.pack(side="bottom", fill="x", padx=12, pady=(2, 4))

    canvas = tk.Canvas(win, bg=BG, highlightthickness=0, width=2, height=2)
    canvas.pack(fill="both", expand=True, padx=12, pady=(10, 6))
    canvas_item = canvas.create_image(0, 0, anchor="center")
    pending = None
    photo = None

    def redraw():
        nonlocal photo, pending
        pending = None
        w, h = canvas.winfo_width(), canvas.winfo_height()
        if w < 2 or h < 2:
            return
        source = alternate if original.get() else pil_img
        factor = min(w / source.width, h / source.height, 2.2)
        size = max(1, round(source.width * factor)), max(1, round(source.height * factor))
        photo = ImageTk.PhotoImage(render(source, () if original.get() else shapes, size, selection))
        canvas.itemconfigure(canvas_item, image=photo)
        canvas.coords(canvas_item, w / 2, h / 2)

    def layout(_):
        nonlocal pending
        if pending is None:
            pending = win.after_idle(redraw)

    canvas.bind("<Configure>", layout)
    win.bind("<Escape>", lambda _: win.destroy())
    max_w, max_h = dialog_bounds(win)
    place_dialog(win, width=min(max_w, 800), height=min(max_h, 630), min_width=330, min_height=320)
    return win


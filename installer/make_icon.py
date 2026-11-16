from PIL import Image, ImageDraw

icon = Image.new("RGBA", (256, 256))
draw = ImageDraw.Draw(icon)
draw.rounded_rectangle((8, 8, 248, 248), radius=60, fill="#141b2e", outline="#4e64bb", width=8)
draw.rounded_rectangle((39, 66, 217, 190), radius=52, fill="#242c51", outline="#b098ff", width=7)
draw.ellipse((71, 106, 108, 143), fill="#99d4ff")
draw.ellipse((148, 106, 185, 143), fill="#99d4ff")
draw.arc((108, 127, 148, 157), 12, 168, fill="#e1ebff", width=5)
icon.save("peeky.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])


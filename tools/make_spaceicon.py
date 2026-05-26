from pathlib import Path

from PIL import Image, ImageDraw


OUT_DIR = Path("assets")
OUT_DIR.mkdir(parents=True, exist_ok=True)

size = 256
img = Image.new("RGBA", (size, size), (5, 10, 25, 255))
draw = ImageDraw.Draw(img)

for i in range(9):
    pad = 12 + i * 7
    draw.ellipse((pad, pad, size - pad, size - pad), outline=(20 + i * 18, 80 + i * 10, 180, 255), width=2)

ship = [(128, 44), (80, 132), (108, 132), (108, 188), (148, 188), (148, 132), (176, 132)]
draw.polygon(ship, fill=(115, 255, 185, 255), outline=(220, 255, 235, 255))
draw.rectangle((118, 104, 138, 144), fill=(245, 250, 255, 255))

enemy = [(72, 196), (98, 178), (158, 178), (184, 196), (172, 218), (84, 218)]
draw.polygon(enemy, fill=(255, 122, 102, 255), outline=(255, 230, 220, 255))

png_path = OUT_DIR / "spaceicon.png"
ico_path = OUT_DIR / "spaceicon.ico"
img.save(png_path)
img.save(ico_path, sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

print(f"Wrote {png_path} and {ico_path}")

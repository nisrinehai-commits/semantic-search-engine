from pathlib import Path
from PIL import Image, ImageDraw

source = Path("output/rapport/pdf_render")
target = Path("output/rapport/contact_sheets")
target.mkdir(parents=True, exist_ok=True)
pages = sorted(source.glob("page-*.png"))

for group_start in range(0, len(pages), 4):
    group = pages[group_start:group_start + 4]
    thumbs = []
    for page in group:
        image = Image.open(page).convert("RGB")
        image.thumbnail((470, 650))
        thumbs.append((page, image.copy()))
    canvas = Image.new("RGB", (1000, 1420), "white")
    draw = ImageDraw.Draw(canvas)
    for index, (page, image) in enumerate(thumbs):
        x = 18 + (index % 2) * 500
        y = 32 + (index // 2) * 700
        draw.text((x, y - 20), page.stem, fill="black")
        canvas.paste(image, (x, y))
    canvas.save(target / f"sheet-{group_start // 4 + 1}.png")

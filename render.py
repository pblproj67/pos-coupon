from PIL import Image, ImageDraw, ImageFont
import json
import os

WIDTH = 576
MARGIN = 18

DATA_FILE = "data/coupon.json"
ART_FILE = "assets/whiskey.png"
OUTPUT_FILE = "output/coupon.png"


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]

    for f in candidates:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)

    return ImageFont.load_default()


def load_lines():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = data.get("lines", [])

    # Remove trailing blanks only
    while lines and str(lines[-1]).strip() == "":
        lines.pop()

    return [str(x) for x in lines]


def fit_font(draw, text, max_width, start_size, bold=True):
    size = start_size

    while size > 10:
        f = font(size, bold)
        box = draw.textbbox((0, 0), text, font=f)

        if box[2] - box[0] <= max_width:
            return f

        size -= 1

    return font(10, bold)


def main():

    print("Current directory:", os.getcwd())
    print("Artwork path:", ART_FILE)
    print("Artwork exists:", os.path.exists(ART_FILE))

    if os.path.exists("assets"):
        print("Assets folder contains:", os.listdir("assets"))

    lines = load_lines()

    HEIGHT = 400

    img = Image.new(
        "L",
        (WIDTH, HEIGHT),
        255
    )

    draw = ImageDraw.Draw(img)

    # ------------------------------------------
    # BORDER
    # ------------------------------------------

    draw.rectangle(
        [3, 3, WIDTH - 4, HEIGHT - 4],
        outline=0,
        width=3
    )

    # ------------------------------------------
    # LAYOUT
    # ------------------------------------------

    reserved_art_width = 155

    text_left = MARGIN
    text_right = WIDTH - reserved_art_width - 22
    text_width = text_right - text_left

    # ------------------------------------------
    # WHISKEY BOTTLE
    # ------------------------------------------

    if os.path.exists(ART_FILE):

        art = Image.open(ART_FILE).convert("L")

        print("Original artwork size:", art.size)

        # Detect actual non-white artwork
        mask = art.point(
            lambda p: 255 if p < 245 else 0
        )

        bbox = mask.getbbox()

        print("Artwork bounding box:", bbox)

        if bbox:
            art = art.crop(bbox)

        print("Cropped artwork size:", art.size)

        # Maximum bottle dimensions
        max_art_width = 155
        max_art_height = HEIGHT - 30

        scale = min(
            max_art_width / art.width,
            max_art_height / art.height
        )

        new_width = max(
            1,
            int(art.width * scale)
        )

        new_height = max(
            1,
            int(art.height * scale)
        )

        art = art.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

        # Thermal-friendly B/W
        art = art.point(
            lambda p: 0 if p < 190 else 255
        )

        # Put bottle against RIGHT edge
        art_x = WIDTH - new_width - 14

        # Vertically center bottle
        art_y = (HEIGHT - new_height) // 2

        print(
            "Final artwork:",
            new_width,
            "x",
            new_height,
            "at",
            art_x,
            art_y
        )

        img.paste(
            art,
            (art_x, art_y)
        )

    else:
        print("WARNING: whiskey.png NOT FOUND")

    # ------------------------------------------
    # TEXT
    # ------------------------------------------

    y = 24

    for i, text in enumerate(lines):

        if text.strip() == "":
            y += 15
            continue

        if i == 0:

            f = fit_font(
                draw,
                text,
                text_width,
                58,
                True
            )

            spacing = 10

        elif i == 1:

            f = fit_font(
                draw,
                text,
                text_width,
                27,
                True
            )

            spacing = 14

        else:

            f = fit_font(
                draw,
                text,
                text_width,
                18,
                True
            )

            spacing = 9

        draw.text(
            (text_left, y),
            text,
            fill=0,
            font=f
        )

        box = draw.textbbox(
            (text_left, y),
            text,
            font=f
        )

        y = box[3] + spacing

    # ------------------------------------------
    # TRUE 1-BIT B/W
    # ------------------------------------------

    img = img.point(
        lambda p: 0 if p < 160 else 255
    ).convert("1")

    # ------------------------------------------
    # SAVE
    # ------------------------------------------

    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    img.save(
        OUTPUT_FILE,
        "PNG",
        optimize=True
    )

    print(
        f"Created {OUTPUT_FILE}: "
        f"{img.width}x{img.height}"
    )


if __name__ == "__main__":
    main()

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

    # Remove trailing blanks only.
    # Intentional blank lines inside A1:A10 remain.
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

    lines = load_lines()

    # Temporary height. We can make this dynamic later.
    HEIGHT = 400

    img = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(img)

    # Border
    draw.rectangle(
        [3, 3, WIDTH - 4, HEIGHT - 4],
        outline=0,
        width=3
    )

    # Whiskey artwork area
    art_width = 155
    art_x = WIDTH - art_width - 12
    art_y = 60

    text_left = MARGIN
    text_right = art_x - 10
    text_width = text_right - text_left

    if os.path.exists(ART_FILE):

        art = Image.open(ART_FILE).convert("L")

        # Remove near-white background
        art = art.point(
            lambda p: 255 if p > 225 else p
        )

        ratio = art_width / art.width

        art = art.resize(
            (
                art_width,
                int(art.height * ratio)
            ),
            Image.Resampling.LANCZOS
        )

        if art.height > HEIGHT - 90:
            ratio = (HEIGHT - 90) / art.height

            art = art.resize(
                (
                    int(art.width * ratio),
                    HEIGHT - 90
                ),
                Image.Resampling.LANCZOS
            )

        img.paste(
            art,
            (
                WIDTH - art.width - 12,
                art_y
            )
        )

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

    # Convert to TRUE 1-bit black/white
    img = img.point(
        lambda p: 0 if p < 160 else 255
    ).convert("1")

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

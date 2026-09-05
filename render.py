from PIL import Image, ImageDraw, ImageFont
import json
import os

WIDTH = 576
HEIGHT = 300

DATA_FILE = "data/coupon.json"
ART_FILE = "assets/whiskey.png"
OUTPUT_FILE = "output/coupon.png"


# --------------------------------------------------
# FONTS
# --------------------------------------------------

def get_font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",

        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
        if bold else
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"
    ]

    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def fit_font(draw, text, max_width, start_size, bold=True):
    size = start_size

    while size >= 9:
        f = get_font(size, bold)
        box = draw.textbbox((0, 0), text, font=f)

        if box[2] - box[0] <= max_width:
            return f

        size -= 1

    return get_font(9, bold)


# --------------------------------------------------
# SHEET DATA
# --------------------------------------------------

def load_lines():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = [str(x) for x in data.get("lines", [])]

    # Remove trailing blanks only
    while lines and lines[-1].strip() == "":
        lines.pop()

    return lines


# --------------------------------------------------
# BOTTLE
# --------------------------------------------------

def prepare_bottle(max_width, max_height):

    art = Image.open(ART_FILE).convert("L")

    # Find actual artwork, ignoring white surrounding area
    mask = art.point(lambda p: 255 if p < 245 else 0)
    bbox = mask.getbbox()

    if bbox:
        art = art.crop(bbox)

    scale = min(
        max_width / art.width,
        max_height / art.height
    )

    new_w = max(1, int(art.width * scale))
    new_h = max(1, int(art.height * scale))

    art = art.resize(
        (new_w, new_h),
        Image.Resampling.LANCZOS
    )

    # Thermal-friendly true B/W
    art = art.point(
        lambda p: 0 if p < 150 else 255
    ).convert("1")

    return art


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    lines = load_lines()

    img = Image.new(
        "1",
        (WIDTH, HEIGHT),
        1
    )

    draw = ImageDraw.Draw(img)

    # ----------------------------------------------
    # FIXED LAYOUT
    # ----------------------------------------------

    LEFT = 16

    # Bottle occupies right side
    BOTTLE_AREA_W = 125
    BOTTLE_RIGHT = WIDTH - 8

    TEXT_RIGHT = WIDTH - BOTTLE_AREA_W - 16
    TEXT_WIDTH = TEXT_RIGHT - LEFT

    # ----------------------------------------------
    # OFFER
    # ----------------------------------------------

    if len(lines) > 0:

        # Expected example: SAVE $5.00
        first = lines[0].strip()

        parts = first.split(" ", 1)

        if len(parts) == 2:
            save_word = parts[0]
            amount = parts[1]
        else:
            save_word = ""
            amount = first

        # SAVE
        save_font = get_font(27, True)

        draw.text(
            (LEFT, 6),
            save_word,
            fill=0,
            font=save_font
        )

        # $5.00 -- dominant element
        amount_font = fit_font(
            draw,
            amount,
            TEXT_WIDTH,
            76,
            True
        )

        draw.text(
            (LEFT, 28),
            amount,
            fill=0,
            font=amount_font
        )

    # ----------------------------------------------
    # BLACK OFFER BAND
    # ----------------------------------------------

    band_top = 112
    band_bottom = 170

    draw.rectangle(
        [
            LEFT,
            band_top,
            TEXT_RIGHT,
            band_bottom
        ],
        fill=0
    )

    if len(lines) > 1:

        offer = lines[1].strip()

        # Split long offer intelligently
        if " WHISKEY " in offer:

            before, after = offer.split(
                " WHISKEY ",
                1
            )

            band_lines = [
                before,
                "WHISKEY " + after
            ]

        else:
            band_lines = [offer]

        y = band_top + 7

        for line in band_lines:

            f = fit_font(
                draw,
                line,
                TEXT_WIDTH - 18,
                21,
                True
            )

            draw.text(
                (LEFT + 9, y),
                line,
                fill=1,
                font=f
            )

            box = draw.textbbox(
                (0, 0),
                line,
                font=f
            )

            y += (
                box[3] - box[1]
            ) + 5

    # ----------------------------------------------
    # LEGAL / EXPIRATION AREA
    # ----------------------------------------------

    # Divider
    draw.line(
        [
            LEFT,
            181,
            TEXT_RIGHT,
            181
        ],
        fill=0,
        width=2
    )

    y = 190

    # Everything after first two A1:A10 lines
    for text in lines[2:]:

        if text.strip() == "":
            y += 6
            continue

        f = fit_font(
            draw,
            text,
            TEXT_WIDTH,
            17,
            True
        )

        draw.text(
            (LEFT, y),
            text,
            fill=0,
            font=f
        )

        box = draw.textbbox(
            (0, 0),
            text,
            font=f
        )

        y += (
            box[3] - box[1]
        ) + 5

    # ----------------------------------------------
    # FIXED BOTTLE ARTWORK
    # ----------------------------------------------

    if os.path.exists(ART_FILE):

        bottle = prepare_bottle(
            max_width=115,
            max_height=275
        )

        bottle_x = (
            BOTTLE_RIGHT -
            bottle.width
        )

        bottle_y = (
            HEIGHT -
            bottle.height -
            7
        )

        img.paste(
            bottle,
            (bottle_x, bottle_y)
        )

    # ----------------------------------------------
    # SAVE
    # ----------------------------------------------

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
        f"{WIDTH}x{HEIGHT}"
    )


if __name__ == "__main__":
    main()

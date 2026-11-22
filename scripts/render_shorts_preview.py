import os
import csv
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = r"e:\App Dev\comparison-video-automation"
CSV_PATH = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\all chara evo.csv"
CACHE_DIR = os.path.join(BASE_DIR, "output", ".cache_images")

FONT_ANTON = os.path.join(BASE_DIR, "assets", "fonts", "Anton-Regular.ttf")
FONT_BEBAS = os.path.join(BASE_DIR, "assets", "fonts", "BebasNeue-Regular.ttf")
FONT_OSWALD = os.path.join(BASE_DIR, "assets", "fonts", "Oswald-Regular.ttf")

CANVAS_W, CANVAS_H = 1080, 1920

CARD_W = 760
IMG_H = 700
BANNER_H = 110
CARD_H = IMG_H + BANNER_H + IMG_H # 1510px

CARD_X = (CANVAS_W - CARD_W) // 2 # 160
CARD_Y = (CANVAS_H - CARD_H) // 2 # 205

def create_gold_banner(width, height):
    c0 = np.array([172, 155, 1], dtype=float)
    c1 = np.array([255, 255, 4], dtype=float)
    c2 = np.array([215, 194, 1], dtype=float)
    row = np.zeros((width, 3), dtype=np.uint8)
    split = int(width * 0.48)
    for x in range(split):
        t = x / max(split, 1)
        row[x] = (1.0 - t) * c0 + t * c1
    for x in range(split, width):
        t = (x - split) / max(width - split, 1)
        row[x] = (1.0 - t) * c1 + t * c2
    return Image.fromarray(np.tile(row[np.newaxis, :, :], (height, 1, 1)))

def get_cached_image(url):
    h = hashlib.md5(url.encode("utf-8")).hexdigest()
    local_path = os.path.join(CACHE_DIR, f"{h}.jpg")
    if os.path.exists(local_path):
        return Image.open(local_path).convert("RGB")
    return Image.new("RGB", (CARD_W, IMG_H), (30, 30, 35))

def fit_image_rect(src_img, target_w=CARD_W, target_h=IMG_H):
    if src_img is None:
        return Image.new("RGB", (target_w, target_h), (25, 25, 30))
    w, h = src_img.size
    ratio = max(target_w / w, target_h / h)
    new_w, new_h = int(w * ratio), int(h * ratio)
    resized = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    x0 = (new_w - target_w) // 2
    y0 = max(0, int((new_h - target_h) * 0.15))
    if y0 + target_h > new_h:
        y0 = new_h - target_h
    return resized.crop((x0, y0, x0 + target_w, y0 + target_h))

def render_vertical_card(char_data):
    card = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 255))

    img_top = fit_image_rect(get_cached_image(char_data["top_url"]), CARD_W, IMG_H)
    img_bot = fit_image_rect(get_cached_image(char_data["bot_url"]), CARD_W, IMG_H)

    card.paste(img_top, (0, 0))

    banner = create_gold_banner(CARD_W, BANNER_H)
    card.paste(banner, (0, IMG_H))

    card.paste(img_bot, (0, IMG_H + BANNER_H))

    draw = ImageDraw.Draw(card)

    # 1px border lines around banner
    draw.line([(0, IMG_H), (CARD_W, IMG_H)], fill=(0, 0, 0), width=2)
    draw.line([(0, IMG_H + BANNER_H), (CARD_W, IMG_H + BANNER_H)], fill=(0, 0, 0), width=2)

    # Character Name in Anton
    font_name = ImageFont.truetype(FONT_ANTON, 56) if os.path.exists(FONT_ANTON) else ImageFont.load_default()
    name = str(char_data["name"]).strip().upper()
    bbox = font_name.getbbox(name)
    tw = bbox[2] - bbox[0]
    max_w = CARD_W - 30
    if tw > max_w:
        font_name = ImageFont.truetype(FONT_ANTON, max(28, int(56 * (max_w / tw))))
        bbox = font_name.getbbox(name)
        tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    name_x = (CARD_W - tw) // 2
    name_y = IMG_H + (BANNER_H - th) // 2 - bbox[1]
    draw.text((name_x, name_y), name, fill=(0, 0, 0), font=font_name)

    # Badges: "PAST" on top-left, "FUTURE" on bottom-left
    font_badge = ImageFont.truetype(FONT_BEBAS, 32) if os.path.exists(FONT_BEBAS) else ImageFont.load_default()
    
    # PAST Badge
    draw.rounded_rectangle([(20, 20), (120, 65)], radius=8, fill=(0, 0, 0, 200), outline=(255, 215, 0), width=2)
    b_past = font_badge.getbbox("PAST")
    pw = b_past[2] - b_past[0]
    draw.text((20 + (100 - pw) // 2, 24), "PAST", fill=(255, 215, 0), font=font_badge)

    # FUTURE Badge
    bot_badge_y = IMG_H + BANNER_H + 20
    draw.rounded_rectangle([(20, bot_badge_y), (145, bot_badge_y + 45)], radius=8, fill=(0, 0, 0, 200), outline=(0, 220, 255), width=2)
    b_fut = font_badge.getbbox("FUTURE")
    fw = b_fut[2] - b_fut[0]
    draw.text((20 + (125 - fw) // 2, bot_badge_y + 4), "FUTURE", fill=(0, 220, 255), font=font_badge)

    # Outer 2px sharp frame
    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(255, 255, 255), width=3)
    return card

def render_shorts_frame(char_data, char_index, total_chars):
    # 1. Background: Blurred and darkened top image
    bg_src = get_cached_image(char_data["top_url"])
    bg_scaled = bg_src.resize((CANVAS_W, CANVAS_H), Image.Resampling.BILINEAR)
    bg_blurred = bg_scaled.filter(ImageFilter.GaussianBlur(radius=35))
    
    # Darken overlay
    dark_overlay = Image.new("RGBA", (CANVAS_W, CANVAS_H), (10, 10, 15, 170))
    bg_blurred.paste(dark_overlay, (0, 0), dark_overlay)

    frame = bg_blurred.convert("RGB")
    draw = ImageDraw.Draw(frame)

    # 2. Header
    font_sub = ImageFont.truetype(FONT_OSWALD, 32) if os.path.exists(FONT_OSWALD) else ImageFont.load_default()
    font_title = ImageFont.truetype(FONT_ANTON, 56) if os.path.exists(FONT_ANTON) else ImageFont.load_default()

    sub_text = "TOKYO REVENGERS"
    sb = font_sub.getbbox(sub_text)
    draw.text(((CANVAS_W - (sb[2] - sb[0])) // 2, 45), sub_text, fill=(255, 215, 0), font=font_sub)

    title_text = "CHARACTER EVOLUTION"
    tb = font_title.getbbox(title_text)
    draw.text(((CANVAS_W - (tb[2] - tb[0])) // 2, 90), title_text, fill=(255, 255, 255), font=font_title)

    # 3. Card in Center
    card = render_vertical_card(char_data)
    frame.paste(card, (CARD_X, CARD_Y))

    # 4. Footer: Ranking / Counter & Progress Bar
    font_counter = ImageFont.truetype(FONT_BEBAS, 36) if os.path.exists(FONT_BEBAS) else ImageFont.load_default()
    counter_str = f"CHARACTER {char_index} / {total_chars}"
    cb = font_counter.getbbox(counter_str)
    draw.text(((CANVAS_W - (cb[2] - cb[0])) // 2, 1745), counter_str, fill=(220, 220, 220), font=font_counter)

    # Progress Bar (x: 140 to 940 = 800px width)
    bar_x, bar_y, bar_w, bar_h = 140, 1815, 800, 10
    draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h)], radius=5, fill=(40, 40, 50))
    
    prog_pct = char_index / total_chars
    fill_w = max(10, int(bar_w * prog_pct))
    draw.rounded_rectangle([(bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h)], radius=5, fill=(255, 215, 0))

    return frame

if __name__ == "__main__":
    with open(CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)
        rows = list(reader)

    # Render first character preview: Atsushi Sendo or Mikey or Chifuyu
    # Let's render Chifuyu Matsuno (row 1)
    sample_data = {
        "name": rows[1][0],
        "top_url": rows[1][1],
        "bot_url": rows[1][2]
    }
    preview_frame = render_shorts_frame(sample_data, 2, len(rows))
    out_path = os.path.join(BASE_DIR, "output", "shorts_preview_sample.png")
    preview_frame.save(out_path)
    print(f"✅ Shorts preview saved to: {out_path}")

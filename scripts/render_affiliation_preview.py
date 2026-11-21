import os
import sys
import re
import csv
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip

BASE_DIR = r"e:\App Dev\comparison-video-automation"
WORKSPACE_ROOT = r"E:\Youtube Project\RankingNoSekai"
SERIES_NAME = "Tokyo Revenger"

SERIES_DIR = os.path.join(WORKSPACE_ROOT, SERIES_NAME)
DATA_DIR = os.path.join(SERIES_DIR, "Data")
IMAGES_DIR = os.path.join(SERIES_DIR, "Images", "Height")
VIDEO_DIR = os.path.join(SERIES_DIR, "Video")

FONT_BEBAS = os.path.join(BASE_DIR, "assets", "fonts", "BebasNeue-Regular.ttf")
FONT_ANTON = os.path.join(BASE_DIR, "assets", "fonts", "Anton-Regular.ttf")
FONT_OSWALD = os.path.join(BASE_DIR, "assets", "fonts", "Oswald-Regular.ttf")

CANVAS_W, CANVAS_H = 1920, 1080
PAD_TOP = 12
PAD_BOTTOM = 12
PAD_LEFT = 12
PAD_RIGHT = 12
CARD_GAP = 12
CARD_W = 480
CARD_H = 1056
STEP_W = CARD_W + CARD_GAP # 492px

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

def fit_image_square(src_img, size=480):
    if src_img is None:
        return Image.new("RGB", (size, size), (25, 25, 30))
    w, h = src_img.size
    if w > h:
        new_h = size
        new_w = int(w * (size / h))
        resized = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        x0 = (new_w - size) // 2
        return resized.crop((x0, 0, x0 + size, size))
    else:
        new_w = size
        new_h = int(h * (size / w))
        resized = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        y0 = max(0, int((new_h - size) * 0.15))
        return resized.crop((0, y0, size, y0 + size))

def clean_name(n):
    base = re.sub(r'\(.*?\)', '', n).strip().lower()
    return re.sub(r'[^a-z0-9]', '', base)

def find_local_image(char_name):
    c_target = clean_name(char_name)
    if os.path.exists(IMAGES_DIR):
        for f in os.listdir(IMAGES_DIR):
            f_base = os.path.splitext(f)[0]
            c_f = clean_name(f_base)
            if c_target == c_f or c_target in c_f or c_f in c_target:
                return os.path.join(IMAGES_DIR, f)
    return None

def render_affiliation_card(char_data):
    card = Image.new("RGB", (CARD_W, CARD_H), (0, 0, 0))
    draw = ImageDraw.Draw(card)

    name = char_data["name"]
    img_path = char_data.get("img_path")
    affiliation_raw = char_data.get("affiliation", "")

    # 1. Top Image (480x480)
    src_img = None
    if img_path and os.path.exists(img_path):
        try:
            src_img = Image.open(img_path).convert("RGB")
        except Exception:
            pass
    card.paste(fit_image_square(src_img, 480), (0, 0))

    # 2. Gold Banner (480x105)
    banner = create_gold_banner(CARD_W, 105)
    card.paste(banner, (0, 480))

    font_name = ImageFont.truetype(FONT_ANTON, 52) if os.path.exists(FONT_ANTON) else ImageFont.load_default()
    name_display = name.upper()
    bbox = font_name.getbbox(name_display)
    tw = bbox[2] - bbox[0]
    max_w = CARD_W - 24
    if tw > max_w:
        font_name = ImageFont.truetype(FONT_ANTON, max(24, int(52 * (max_w / tw))))
        bbox = font_name.getbbox(name_display)
        tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    name_x = (CARD_W - tw) // 2
    name_y = 480 + (105 - th) // 2 - bbox[1]
    draw.text((name_x, name_y), name_display, fill=(0, 0, 0), font=font_name)

    draw.line([(0, 480), (CARD_W, 480)], fill=(0, 0, 0), width=1)
    draw.line([(0, 480 + 105), (CARD_W, 480 + 105)], fill=(0, 0, 0), width=1)

    # 3. Bottom Black Area (y: 585 to 1056 = 471px)
    draw.rectangle([(0, 585), (CARD_W, CARD_H)], fill=(0, 0, 0))

    # Parse affiliation steps
    # Usually "Gang 1 ➔ Gang 2 ➔ Gang 3"
    gangs = [g.strip() for g in affiliation_raw.split("➔") if g.strip()]
    if not gangs:
        gangs = [affiliation_raw.strip()]

    # Format into visual lines
    # If 1 gang: 1 line centered
    # If 2 gangs: Gang 1 \n ↓ \n Gang 2
    # If >= 3 gangs: compact listing with arrows
    lines = []
    if len(gangs) == 1:
        lines = [gangs[0]]
    elif len(gangs) <= 4:
        for idx, g in enumerate(gangs):
            lines.append(g)
            if idx < len(gangs) - 1:
                lines.append("↓")
    else:
        # 5+ gangs (like Kokonoi / Kakucho / Sanzu)
        for idx, g in enumerate(gangs):
            lines.append(g)
            if idx < len(gangs) - 1:
                lines.append("↓")

    # Render lines in bottom area
    # Auto-adjust font size based on number of lines
    num_lines = len(lines)
    if num_lines <= 2:
        base_font_size = 46
        line_gap = 14
    elif num_lines <= 5:
        base_font_size = 38
        line_gap = 10
    elif num_lines <= 7:
        base_font_size = 32
        line_gap = 6
    else:
        base_font_size = 26
        line_gap = 4

    font_text = ImageFont.truetype(FONT_OSWALD, base_font_size) if os.path.exists(FONT_OSWALD) else ImageFont.load_default()
    font_arrow = ImageFont.truetype(FONT_OSWALD, max(18, base_font_size - 8)) if os.path.exists(FONT_OSWALD) else ImageFont.load_default()

    # Calculate total height of text block
    rendered_line_data = []
    total_block_h = 0
    for l in lines:
        f = font_arrow if l == "↓" else font_text
        b = f.getbbox(l)
        lw = b[2] - b[0]
        lh = b[3] - b[1]
        # auto-fit width if line is too wide
        if lw > (CARD_W - 30) and l != "↓":
            f_scaled = ImageFont.truetype(FONT_OSWALD, max(18, int(base_font_size * ((CARD_W - 30) / lw))))
            b = f_scaled.getbbox(l)
            lw = b[2] - b[0]
            lh = b[3] - b[1]
            rendered_line_data.append((l, f_scaled, lw, lh, b[1]))
        else:
            rendered_line_data.append((l, f, lw, lh, b[1]))
        total_block_h += lh + line_gap

    total_block_h -= line_gap
    bottom_h = CARD_H - 585
    start_y = 585 + (bottom_h - total_block_h) // 2

    cur_y = start_y
    for l, f, lw, lh, b_top in rendered_line_data:
        lx = (CARD_W - lw) // 2
        color = (255, 215, 0) if l == "↓" else (255, 255, 255)
        draw.text((lx, cur_y - b_top), l, fill=color, font=f)
        cur_y += lh + line_gap

    # Border frame 1px around card
    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(0, 0, 0), width=1)
    return card

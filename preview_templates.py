import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1920, 1080
CARD_W = 480
CARD_H = 1056
FONT_ANTON = 'assets/fonts/Anton-Regular.ttf'
FONT_BEBAS = 'assets/fonts/BebasNeue-Regular.ttf'
FONT_OSWALD = 'assets/fonts/Oswald-Regular.ttf'

def create_gold_banner(width, height):
    c0 = np.array([172, 155, 1], dtype=float)
    c1 = np.array([255, 255, 4], dtype=float)
    c2 = np.array([215, 194, 1], dtype=float)
    row = np.zeros((width, 3), dtype=np.uint8)
    split = int(width * 0.48)
    for x in range(split):
        t = x / max(split, 1)
        row[x] = (1 - t) * c0 + t * c1
    for x in range(split, width):
        t = (x - split) / max(width - split, 1)
        row[x] = (1 - t) * c1 + t * c2
    return Image.fromarray(np.tile(row[np.newaxis, :, :], (height, 1, 1)))

def fit_image_square(img_path, size=480):
    if not img_path or not os.path.exists(img_path):
        return Image.new('RGB', (size, size), (25, 25, 30))
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    if w > h:
        new_h = size
        new_w = int(w * (size / h))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        x0 = (new_w - size) // 2
        return resized.crop((x0, 0, x0 + size, size))
    else:
        new_w = size
        new_h = int(h * (size / w))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        y0 = max(0, int((new_h - size) * 0.15))
        return resized.crop((0, y0, size, y0 + size))

def render_multistats_card(char_name, img_path, stats_lines):
    card = Image.new('RGB', (CARD_W, CARD_H), (255, 255, 255))
    draw = ImageDraw.Draw(card)
    
    # 1. Top Image (480x480)
    top_img = fit_image_square(img_path, 480)
    card.paste(top_img, (0, 0))
    
    # 2. Middle Banner (Gold Shine 480x105)
    banner = create_gold_banner(CARD_W, 105)
    card.paste(banner, (0, 480))
    
    # Character Name in Anton
    font_name = ImageFont.truetype(FONT_ANTON, 52)
    bbox = font_name.getbbox(char_name.upper())
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    name_x = (CARD_W - tw) // 2
    name_y = 480 + (105 - th) // 2 - bbox[1]
    draw.text((name_x, name_y), char_name.upper(), fill=(0, 0, 0), font=font_name)
    
    # 3. Bottom White Stats Box (y: 585 to 1056 = 471px)
    draw.rectangle([(0, 585), (CARD_W, CARD_H)], fill=(255, 255, 255))
    
    # Lines in Oswald & Anton
    font_stat = ImageFont.truetype(FONT_OSWALD, 32)
    font_stat_val = ImageFont.truetype(FONT_ANTON, 40)
    start_y = 620
    line_spacing = 135
    for idx, (label, val) in enumerate(stats_lines):
        curr_y = start_y + idx * line_spacing
        # Draw Label (Oswald gray)
        l_box = font_stat.getbbox(label.upper())
        l_w = l_box[2] - l_box[0]
        draw.text(((CARD_W - l_w) // 2, curr_y), label.upper(), fill=(110, 110, 120), font=font_stat)
        
        # Draw Val (Anton black)
        v_box = font_stat_val.getbbox(val.upper())
        v_w = v_box[2] - v_box[0]
        draw.text(((CARD_W - v_w) // 2, curr_y + 40), val.upper(), fill=(0, 0, 0), font=font_stat_val)
        
        # Divider line
        if idx < len(stats_lines) - 1:
            div_y = curr_y + 105
            draw.line([(40, div_y), (CARD_W - 40, div_y)], fill=(225, 225, 230), width=1)
        
    # Border
    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(0, 0, 0), width=1)
    return card

c1 = render_multistats_card('MANJIRO SANO', 'assets/images/Manjiro_Sano/past.png', [
    ('HEIGHT', '162 CM (5\'4")'),
    ('POSITION', 'TOMAN PRESIDENT'),
    ('BIRTHDAY', 'AUGUST 20, 1990')
])
c2 = render_multistats_card('KEN RYUGUJI', 'assets/images/height_comparison/Ken_Ryuguji.png', [
    ('HEIGHT', '185 CM (6\'1")'),
    ('POSITION', 'VICE PRESIDENT'),
    ('BIRTHDAY', 'MAY 10, 1990')
])
c3 = render_multistats_card('TAKEMICHI HANAGAKI', 'assets/images/Takemichi_Hanagaki/past.png', [
    ('HEIGHT', '165 CM (5\'5")'),
    ('POSITION', '1ST DIVISION CAPTAIN'),
    ('BIRTHDAY', 'JUNE 25, 1991')
])

preview = Image.new('RGB', (1920, 1080), (255, 255, 255))
preview.paste(c1, (12, 12))
preview.paste(c2, (12 + 492, 12))
preview.paste(c3, (12 + 492 * 2, 12))

os.makedirs('output', exist_ok=True)
preview.save('output/alienart_multistats_preview.png')
print('Preview multi-stats saved successfully to output/alienart_multistats_preview.png!')

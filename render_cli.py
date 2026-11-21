"""
Universal Video Comparison Renderer CLI
Membaca data & gambar dari folder project terpisah (E:/Youtube Project/RankingNoSekai/<Series>/)
dan merender video perbandingan dengan template presisi AlienArt ke folder Video/ target.
"""
import os
import sys
import re
import csv
import json
import argparse
import urllib.request
import hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip, concatenate_videoclips

# Load default config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")
with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
    SETTINGS = json.load(f)

WORKSPACE_ROOT = SETTINGS.get("workspace", {}).get("root_dir", "E:/Youtube Project/RankingNoSekai")
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
    """Gradasi Emas AlienArt (#AC9B01 -> #FFFF04 -> #D7C201)"""
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

def get_image(img_ref, project_images_dir=None, cache_dir=None):
    """Mendapatkan gambar dari path lokal atau URL (dengan auto-cache)"""
    if not img_ref or not str(img_ref).strip():
        return None

    img_ref = str(img_ref).strip()

    # 1. Cek path file lokal langsung
    if os.path.exists(img_ref):
        return Image.open(img_ref).convert("RGB")

    # 2. Cek di dalam folder Images project jika hanya nama file
    if project_images_dir and os.path.exists(project_images_dir):
        for root, _, files in os.walk(project_images_dir):
            if os.path.basename(img_ref) in files:
                return Image.open(os.path.join(root, os.path.basename(img_ref))).convert("RGB")

    # 3. Jika berupa URL (misal AlienArt CDN digitaloceanspaces)
    if img_ref.startswith("http://") or img_ref.startswith("https://"):
        if not cache_dir:
            cache_dir = os.path.join(BASE_DIR, "output", ".cache_images")
        os.makedirs(cache_dir, exist_ok=True)
        h = hashlib.md5(img_ref.encode("utf-8")).hexdigest()
        local_cached = os.path.join(cache_dir, f"{h}.jpg")

        if os.path.exists(local_cached) and os.path.getsize(local_cached) > 500:
            return Image.open(local_cached).convert("RGB")

        try:
            req = urllib.request.Request(img_ref, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as res, open(local_cached, "wb") as f_out:
                f_out.write(res.read())
            return Image.open(local_cached).convert("RGB")
        except Exception as e:
            print(f"⚠️ Gagal mengunduh gambar: {img_ref} ({e})")
            return None

    return None

def fit_image_square(src_img, size=480):
    """Crop 1:1 persegi dengan fokus bagian atas wajah"""
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

# ==========================================================
# 1. RENDER KARTU: EVOLUTION (ALL CHARA EVO)
# ==========================================================
def render_card_evolution(char_data, project_images_dir):
    card = Image.new("RGB", (CARD_W, CARD_H), (0, 0, 0))

    img_top = get_image(char_data.get("img_top"), project_images_dir)
    img_bottom = get_image(char_data.get("img_bottom"), project_images_dir)

    # 1. Top Image (480x480)
    card.paste(fit_image_square(img_top, 480), (0, 0))

    # 2. Middle Banner (480x96)
    banner = create_gold_banner(CARD_W, 96)
    card.paste(banner, (0, 480))

    # 3. Bottom Image (480x480)
    card.paste(fit_image_square(img_bottom, 480), (0, 480 + 96))

    draw = ImageDraw.Draw(card)
    draw.line([(0, 480), (CARD_W, 480)], fill=(0, 0, 0), width=1)
    draw.line([(0, 480 + 96), (CARD_W, 480 + 96)], fill=(0, 0, 0), width=1)

    # Text (Bebas Neue 68)
    font_size = 68
    font = ImageFont.truetype(FONT_BEBAS, font_size) if os.path.exists(FONT_BEBAS) else ImageFont.load_default()
    name = str(char_data.get("name", "UNKNOWN")).strip().upper()

    bbox = font.getbbox(name)
    tw = bbox[2] - bbox[0]
    max_w = CARD_W - 24
    if tw > max_w:
        font_size = max(24, int(font_size * (max_w / tw)))
        font = ImageFont.truetype(FONT_BEBAS, font_size)
        bbox = font.getbbox(name)
        tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    name_x = (CARD_W - tw) // 2
    name_y = 480 + (96 - th) // 2 - bbox[1]
    draw.text((name_x, name_y), name, fill=(0, 0, 0), font=font)

    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(0, 0, 0), width=1)
    return card

# ==========================================================
# 2. RENDER KARTU: HEIGHT COMPARISON (TEMPLATE_HEIGHT.JSON)
# Persis AlienArt: Foto Atas + Pita Emas Anton + Kotak Bawah Hitam Pekat
# Teks Sejajar 1 Baris: "174 cm" Putih Bold Font Oswald (96pt)
# ==========================================================
def render_card_height(char_data, project_images_dir):
    card = Image.new("RGB", (CARD_W, CARD_H), (0, 0, 0)) # Background Kartu Hitam Pekat
    draw = ImageDraw.Draw(card)

    # 1. Top Image (480x480)
    img = get_image(char_data.get("img_main"), project_images_dir)
    card.paste(fit_image_square(img, 480), (0, 0))

    # 2. Middle Banner (Gold Shine 480x105)
    banner = create_gold_banner(CARD_W, 105)
    card.paste(banner, (0, 480))

    # Name in Anton (56pt auto-fit)
    font_name = ImageFont.truetype(FONT_ANTON, 56) if os.path.exists(FONT_ANTON) else ImageFont.load_default()
    name = str(char_data.get("name", "UNKNOWN")).strip().upper()
    bbox = font_name.getbbox(name)
    tw = bbox[2] - bbox[0]
    max_w = CARD_W - 24
    if tw > max_w:
        font_name = ImageFont.truetype(FONT_ANTON, max(24, int(56 * (max_w / tw))))
        bbox = font_name.getbbox(name)
        tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((CARD_W - tw) // 2, 480 + (105 - th) // 2 - bbox[1]), name, fill=(0, 0, 0), font=font_name)

    # Garis pemisah 1px hitam
    draw.line([(0, 480), (CARD_W, 480)], fill=(0, 0, 0), width=1)
    draw.line([(0, 480 + 105), (CARD_W, 480 + 105)], fill=(0, 0, 0), width=1)

    # 3. Bottom Area: Hitam Pekat (y: 585 to 1056 = 471px)
    draw.rectangle([(0, 585), (CARD_W, CARD_H)], fill=(0, 0, 0))

    # Teks Sejajar 1 Baris: "174 cm" (Font Oswald 96)
    val_str = str(char_data.get("val", "0 cm")).strip()
    font_size = 96
    font_stat = ImageFont.truetype(FONT_OSWALD, font_size) if os.path.exists(FONT_OSWALD) else ImageFont.load_default()
    s_bbox = font_stat.getbbox(val_str)
    sw = s_bbox[2] - s_bbox[0]
    max_stat_w = CARD_W - 40
    if sw > max_stat_w:
        font_size = max(36, int(font_size * (max_stat_w / sw)))
        font_stat = ImageFont.truetype(FONT_OSWALD, font_size)
        s_bbox = font_stat.getbbox(val_str)
        sw = s_bbox[2] - s_bbox[0]
    sh = s_bbox[3] - s_bbox[1]

    # Posisi Persis di Tengah Kotak Bawah Hitam
    bottom_h = CARD_H - 585
    stat_x = (CARD_W - sw) // 2
    stat_y = 585 + (bottom_h - sh) // 2 - s_bbox[1]
    draw.text((stat_x, stat_y), val_str, fill=(255, 255, 255), font=font_stat)

    # Border frame hitam tipis di sekeliling kartu
    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(0, 0, 0), width=1)
    return card

# ==========================================================
# 3. RENDER KARTU: HIERARCHY / BIRTHDAY / GENERAL STATS
# ==========================================================
def render_card_general_stats(char_data, project_images_dir, is_dark=False):
    bg_color = (0, 0, 0) if is_dark else (255, 255, 255)
    text_color = (255, 255, 255) if is_dark else (0, 0, 0)
    lbl_color = (180, 180, 180) if is_dark else (110, 110, 120)

    card = Image.new("RGB", (CARD_W, CARD_H), bg_color)
    draw = ImageDraw.Draw(card)

    img = get_image(char_data.get("img_main"), project_images_dir)
    card.paste(fit_image_square(img, 480), (0, 0))

    banner = create_gold_banner(CARD_W, 105)
    card.paste(banner, (0, 480))

    font_name = ImageFont.truetype(FONT_ANTON, 52) if os.path.exists(FONT_ANTON) else ImageFont.load_default()
    name = str(char_data.get("name", "UNKNOWN")).strip().upper()
    bbox = font_name.getbbox(name)
    tw = bbox[2] - bbox[0]
    max_w = CARD_W - 24
    if tw > max_w:
        font_name = ImageFont.truetype(FONT_ANTON, max(24, int(52 * (max_w / tw))))
        bbox = font_name.getbbox(name)
        tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((CARD_W - tw) // 2, 480 + (105 - th) // 2 - bbox[1]), name, fill=(0, 0, 0), font=font_name)

    stats_lines = char_data.get("stats", [])
    font_lbl = ImageFont.truetype(FONT_OSWALD, 32) if os.path.exists(FONT_OSWALD) else ImageFont.load_default()
    font_val = ImageFont.truetype(FONT_ANTON, 40) if os.path.exists(FONT_ANTON) else ImageFont.load_default()

    start_y = 620
    line_spacing = 135 if len(stats_lines) <= 3 else 90
    for idx, (label, val) in enumerate(stats_lines):
        curr_y = start_y + idx * line_spacing
        l_box = font_lbl.getbbox(label.upper())
        draw.text(((CARD_W - (l_box[2] - l_box[0])) // 2, curr_y), label.upper(), fill=lbl_color, font=font_lbl)

        v_box = font_val.getbbox(str(val).upper())
        draw.text(((CARD_W - (v_box[2] - v_box[0])) // 2, curr_y + 40), str(val).upper(), fill=text_color, font=font_val)

        if idx < len(stats_lines) - 1:
            div_col = (50, 50, 50) if is_dark else (230, 230, 235)
            draw.line([(40, curr_y + 100), (CARD_W - 40, curr_y + 100)], fill=div_col, width=1)

    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(0, 0, 0), width=1)
    return card

# ==========================================================
# PARSER CSV & AUTO DETECTOR
# ==========================================================
def parse_csv_data(csv_file_path):
    rows = []
    with open(csv_file_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        headers = [h.strip() for h in next(reader, [])]
        for r in reader:
            if not r or not any(r):
                continue
            rows.append(r)

    print(f"📋 Ditemukan {len(rows)} baris data. Header: {headers}")

    filename_lower = os.path.basename(csv_file_path).lower()

    # 1. Height Comparison
    if "height" in filename_lower or ("Element" in headers and any("cm" in str(r) for r in rows[:5])):
        template_type = "height"
        data_list = []
        name_idx = headers.index("Title") if "Title" in headers else 0
        img_idx = headers.index("Highlight Image") if "Highlight Image" in headers else 0
        stat_idx = headers.index("Element") if "Element" in headers else (headers.index("Description") if "Description" in headers else 1)
        for r in rows:
            data_list.append({
                "name": r[name_idx] if len(r) > name_idx else "",
                "img_main": r[img_idx] if len(r) > img_idx else "",
                "val": r[stat_idx] if len(r) > stat_idx else ""
            })
        return template_type, data_list

    # 2. Evolution (Highlight, Highlight Image, Highlight Image 1)
    if "Highlight Image 1" in headers and "Highlight" in headers and "Highlight 3" not in headers:
        template_type = "evolution"
        data_list = []
        name_idx = headers.index("Highlight")
        img1_idx = headers.index("Highlight Image")
        img2_idx = headers.index("Highlight Image 1")
        for r in rows:
            data_list.append({
                "name": r[name_idx] if len(r) > name_idx else "",
                "img_top": r[img1_idx] if len(r) > img1_idx else "",
                "img_bottom": r[img2_idx] if len(r) > img2_idx else ""
            })
        return template_type, data_list

    # 3. Hierarchy / Birthday / General
    template_type = "general_stats"
    data_list = []
    name_idx = headers.index("Title") if "Title" in headers else 0
    img_idx = headers.index("Highlight Image") if "Highlight Image" in headers else 0
    stat_cols = [h for h in headers if h not in ["Title", "Highlight Image", "Highlight"]]
    for r in rows:
        stats_data = []
        for sc in stat_cols:
            c_idx = headers.index(sc)
            if len(r) > c_idx and r[c_idx]:
                stats_data.append((sc, r[c_idx]))
        data_list.append({
            "name": r[name_idx] if len(r) > name_idx else "",
            "img_main": r[img_idx] if len(r) > img_idx else "",
            "stats": stats_data
        })
    return template_type, data_list

# ==========================================================
# RENDER PIPELINE
# ==========================================================
def render_project_video(csv_name, series_name="Tokyo Revenger", limit=None, scroll_duration=None, preview_only=False):
    series_dir = os.path.join(WORKSPACE_ROOT, series_name)
    data_dir = os.path.join(series_dir, "Data")
    images_dir = os.path.join(series_dir, "Images")
    video_dir = os.path.join(series_dir, "Video")
    os.makedirs(video_dir, exist_ok=True)

    csv_path = os.path.join(data_dir, csv_name) if not os.path.isabs(csv_name) else csv_name
    if not os.path.exists(csv_path):
        found = [f for f in os.listdir(data_dir) if csv_name.lower() in f.lower()] if os.path.exists(data_dir) else []
        if found:
            csv_path = os.path.join(data_dir, found[0])
        else:
            raise FileNotFoundError(f"File CSV tidak ditemukan: {csv_path}")

    print(f"\n🚀 Memproses File: {os.path.basename(csv_path)}")
    template_type, data_list = parse_csv_data(csv_path)

    if limit:
        data_list = data_list[:limit]
        print(f"🔹 Dibatasi untuk {limit} karakter pertama.")

    print(f"🎨 Template Terpilih: {template_type.upper()} ({len(data_list)} karakter)")

    rendered_cards = []
    for idx, item in enumerate(data_list):
        print(f"  Rendering [{idx+1}/{len(data_list)}]: {item.get('name')}")
        if template_type == "height":
            c = render_card_height(item, images_dir)
        elif template_type == "evolution":
            c = render_card_evolution(item, images_dir)
        else:
            c = render_card_general_stats(item, images_dir)
        rendered_cards.append(c)

    n = len(rendered_cards)
    total_w = PAD_LEFT + (n - 1) * STEP_W + CARD_W + PAD_RIGHT
    panorama = Image.new("RGB", (total_w, CANVAS_H), (255, 255, 255))

    for idx, card in enumerate(rendered_cards):
        pos_x = PAD_LEFT + idx * STEP_W
        panorama.paste(card, (pos_x, PAD_TOP))

    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    preview_output = os.path.join(video_dir, f"{base_name}_preview.png")
    first_frame = panorama.crop((0, 0, CANVAS_W, CANVAS_H))
    first_frame.save(preview_output)
    print(f"🖼️ Preview 1 frame berhasil disimpan ke: {preview_output}")

    if preview_only:
        return preview_output

    if not scroll_duration:
        scroll_duration = max(12.0, len(rendered_cards) * 2.2)

    panorama_np = np.array(panorama)
    max_scroll = max(0, total_w - CANVAS_W)
    start_pause = 2.0
    end_pause = 2.5
    total_duration = start_pause + scroll_duration + end_pause

    def make_frame(t):
        if t < start_pause:
            x = 0
        elif t > (start_pause + scroll_duration):
            x = max_scroll
        else:
            progress = (t - start_pause) / scroll_duration
            if progress > 0.92:
                t_sub = (progress - 0.92) / 0.08
                ease_sub = np.sin(t_sub * (np.pi / 2))
                effective_progress = 0.92 + (0.08 * ease_sub)
            else:
                effective_progress = progress

            x = int(effective_progress * max_scroll)
            x = min(x, max_scroll)

        return panorama_np[:, x:x + CANVAS_W]

    output_video_path = os.path.join(video_dir, f"{base_name}_AlienArt_Scroll.mp4")
    print(f"⏱️ Total Durasi: {total_duration:.1f}s (Scroll: {scroll_duration:.1f}s)")
    print(f"🎬 Merender Video HD 1080p -> {output_video_path}...")

    video_clip = VideoClip(frame_function=make_frame, duration=total_duration).with_fps(30)
    video_clip.write_videofile(
        output_video_path,
        fps=30,
        codec="libx264",
        preset="fast",
        threads=4
    )

    print(f"✅ Video selesai dirender ke: {output_video_path}")
    return output_video_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AlienArt Comparison Video Automation CLI")
    parser.add_argument("--csv", required=True, help="Nama file CSV di folder Data (misal: 'all chara evo.csv' atau 'height tokrev.csv')")
    parser.add_argument("--series", default="Tokyo Revenger", help="Nama subfolder series anime di E:/Youtube Project/RankingNoSekai/")
    parser.add_argument("--limit", type=int, default=None, help="Batasi jumlah karakter untuk tes cepat")
    parser.add_argument("--duration", type=float, default=None, help="Durasi scroll dalam detik")
    parser.add_argument("--preview", action="store_true", help="Hanya simpan gambar preview 1 frame tanpa render video full")

    args = parser.parse_args()
    render_project_video(
        csv_name=args.csv,
        series_name=args.series,
        limit=args.limit,
        scroll_duration=args.duration,
        preview_only=args.preview
    )

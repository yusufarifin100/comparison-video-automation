"""
AlienArt-Accurate Horizontal Scrolling Comparison Generator
Replikasi 100% presisi dari template AlienArt.io:
- 16:9 Landscape (1920x1080)
- Background Canvas: Putih Bersih (#FFFFFF)
- Padding Atas & Bawah: 12px (Frame Putih)
- Padding Kiri & Kanan: 12px (Presisi tanpa space kosong kebablasan di akhir)
- Gap Antar Kartu: 12px (Pemisah Putih Bersih)
- Lebar Tiap Kartu: 480px
- Bagian Atas: 480x480 (1:1 Persegi) - Foto Karakter Past / Evolution 1
- Bagian Tengah: 480x96 - Pita Gradasi Emas Mengkilap (#AC9B01 -> #FFFF04 -> #D7C201)
  dengan Teks Bebas Neue 68pt All-Caps Hitam Pekat (#000000)
- Bagian Bawah: 480x480 (1:1 Persegi) - Foto Karakter Present / Evolution 2
- Total Tinggi Kartu: 1056px (1056 + 12px atas + 12px bawah = 1080px)
- Smooth horizontal scrolling carousel with smooth ease deceleration at the end
"""
import os
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip, concatenate_videoclips

CANVAS_W, CANVAS_H = 1920, 1080
PAD_TOP = 12
PAD_BOTTOM = 12
PAD_LEFT = 12
PAD_RIGHT = 12
CARD_GAP = 12

CARD_W = 480
TOP_IMG_H = 480
BANNER_H = 96
BOTTOM_IMG_H = 480
CARD_H = TOP_IMG_H + BANNER_H + BOTTOM_IMG_H # 1056px

STEP_W = CARD_W + CARD_GAP # 492px per langkah kartu
FONT_PATH = "assets/fonts/BebasNeue-Regular.ttf"

# Data sample karakter Tokyo Revengers Evolution
CHARACTERS_DATA = [
    {
        "name": "MANJIRO SANO",
        "top_img": "assets/images/Manjiro_Sano/past.png",
        "bottom_img": "assets/images/Manjiro_Sano/present.png"
    },
    {
        "name": "TAKEMICHI HANAGAKI",
        "top_img": "assets/images/Takemichi_Hanagaki/past.png",
        "bottom_img": "assets/images/Takemichi_Hanagaki/present.png"
    },
    {
        "name": "KEN RYUGUJI",
        "top_img": "assets/images/height_comparison/Ken_Ryuguji.png",
        "bottom_img": "assets/images/height_comparison/Ken_Ryuguji.png"
    },
    {
        "name": "CHIFUYU MATSUNO",
        "top_img": "assets/images/height_comparison/Chifuyu_Matsuno.png",
        "bottom_img": "assets/images/height_comparison/Chifuyu_Matsuno.png"
    },
    {
        "name": "KEISUKE BAJI",
        "top_img": "assets/images/height_comparison/Keisuke_Baji.png",
        "bottom_img": "assets/images/height_comparison/Keisuke_Baji.png"
    },
    {
        "name": "TAKASHI MITSUYA",
        "top_img": "assets/images/height_comparison/Takashi_Mitsuya.png",
        "bottom_img": "assets/images/height_comparison/Takashi_Mitsuya.png"
    },
    {
        "name": "KAZUTORA HANEMIYA",
        "top_img": "assets/images/height_comparison/Kazutora_Hanemiya.png",
        "bottom_img": "assets/images/height_comparison/Kazutora_Hanemiya.png"
    },
    {
        "name": "HINATA TACHIBANA",
        "top_img": "assets/images/height_comparison/Hinata_Tachibana.png",
        "bottom_img": "assets/images/height_comparison/Hinata_Tachibana.png"
    }
]

def create_gold_gradient_banner(width, height):
    """
    Menghasilkan gradasi emas AlienArt persis:
    linear-gradient(90deg, #AC9B01 0%, #FFFF04 48%, #D7C201 100%)
    """
    c0 = np.array([172, 155, 1], dtype=float)   # #AC9B01 (Dark Antique Gold)
    c1 = np.array([255, 255, 4], dtype=float)   # #FFFF04 (Bright Electric Yellow)
    c2 = np.array([215, 194, 1], dtype=float)   # #D7C201 (Warm Medium Gold)

    row = np.zeros((width, 3), dtype=np.uint8)
    split = int(width * 0.48)
    for x in range(split):
        t = x / max(split, 1)
        row[x] = (1.0 - t) * c0 + t * c1
    for x in range(split, width):
        t = (x - split) / max(width - split, 1)
        row[x] = (1.0 - t) * c1 + t * c2

    return Image.fromarray(np.tile(row[np.newaxis, :, :], (height, 1, 1)))

def fit_image_square(img_path, size=480):
    """Memotong & memposisikan gambar ke rasio 1:1 persegi dengan fokus wajah di atas"""
    if not img_path or not os.path.exists(img_path):
        return Image.new("RGB", (size, size), (25, 25, 30))

    img = Image.open(img_path).convert("RGB")
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

def render_alienart_column(char_info):
    """Merender 1 kartu individu (480x1056)"""
    card = Image.new("RGB", (CARD_W, CARD_H), (0, 0, 0))

    # 1. Top Image (Past) - 480x480
    top_img = fit_image_square(char_info.get("top_img"), TOP_IMG_H)
    card.paste(top_img, (0, 0))

    # 2. Middle Banner (Gold Shine) - 480x96
    banner = create_gold_gradient_banner(CARD_W, BANNER_H)
    card.paste(banner, (0, TOP_IMG_H))

    # 3. Bottom Image (Present) - 480x480
    bottom_img = fit_image_square(char_info.get("bottom_img"), BOTTOM_IMG_H)
    card.paste(bottom_img, (0, TOP_IMG_H + BANNER_H))

    draw = ImageDraw.Draw(card)
    
    # Border 1px hitam di atas & bawah pita banner
    draw.line([(0, TOP_IMG_H), (CARD_W, TOP_IMG_H)], fill=(0, 0, 0), width=1)
    draw.line([(0, TOP_IMG_H + BANNER_H), (CARD_W, TOP_IMG_H + BANNER_H)], fill=(0, 0, 0), width=1)

    # 4. Teks Nama Karakter (Bebas Neue, Ukuran 68, Hitam Pekat, Centered)
    font_size = 68
    font = ImageFont.truetype(FONT_PATH, font_size) if os.path.exists(FONT_PATH) else ImageFont.load_default()
    name_str = char_info.get("name", "UNKNOWN").upper()

    bbox = font.getbbox(name_str)
    tw = bbox[2] - bbox[0]
    max_w = CARD_W - 24
    if tw > max_w:
        font_size = max(24, int(font_size * (max_w / tw)))
        font = ImageFont.truetype(FONT_PATH, font_size) if os.path.exists(FONT_PATH) else ImageFont.load_default()
        bbox = font.getbbox(name_str)
        tw = bbox[2] - bbox[0]

    th = bbox[3] - bbox[1]
    name_x = (CARD_W - tw) // 2
    name_y = TOP_IMG_H + (BANNER_H - th) // 2 - bbox[1]
    draw.text((name_x, name_y), name_str, fill=(0, 0, 0), font=font)

    # 1px border tipis membingkai kartu
    draw.rectangle([(0, 0), (CARD_W - 1, CARD_H - 1)], outline=(0, 0, 0), width=1)
    return card

def generate_full_panorama(characters):
    """
    Menyusun seluruh kartu di atas kanvas dengan background PUTIH BERSIH (#FFFFFF),
    dengan batas kanan pas (PAD_RIGHT = 12px) tanpa sisa ruang putih berlebihan di akhir.
    """
    n = len(characters)
    # Total lebar eksak: Padding kiri + (n-1)*jarak + lebar kartu terakhir + padding kanan
    total_w = PAD_LEFT + (n - 1) * STEP_W + CARD_W + PAD_RIGHT
    print(f"🖼️ Menyusun panorama horizontal presisi: {total_w}x{CANVAS_H} untuk {n} karakter...")
    panorama = Image.new("RGB", (total_w, CANVAS_H), (255, 255, 255))

    for idx, char_info in enumerate(characters):
        col_img = render_alienart_column(char_info)
        pos_x = PAD_LEFT + idx * STEP_W
        panorama.paste(col_img, (pos_x, PAD_TOP))

    return panorama

def build_scrolling_video(characters, output_path="output/alienart_evolution_scroll.mp4", scroll_duration=16.0):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    panorama_img = generate_full_panorama(characters)
    panorama_np = np.array(panorama_img)
    total_w = panorama_img.width
    max_scroll = max(0, total_w - CANVAS_W)

    start_pause = 2.0
    end_pause = 2.5
    total_duration = start_pause + scroll_duration + end_pause

    print(f"⏱️ Total durasi: {total_duration:.1f}s (Scroll: {scroll_duration}s, Pause: {start_pause + end_pause}s)")
    print(f"📏 Max Scroll: {max_scroll}px (Berhenti pas di kartu terakhir dengan padding 12px)")

    def make_frame(t):
        if t < start_pause:
            x = 0
        elif t > (start_pause + scroll_duration):
            x = max_scroll
        else:
            # Linear scroll dengan gentle ease-out di 8% terakhir agar mendarat mulus di posisi akhir
            progress = (t - start_pause) / scroll_duration
            if progress > 0.92:
                # Easing perlahan melambat saat mendekati kartu terakhir
                t_sub = (progress - 0.92) / 0.08
                ease_sub = np.sin(t_sub * (np.pi / 2))
                effective_progress = 0.92 + (0.08 * ease_sub)
            else:
                effective_progress = progress

            x = int(effective_progress * max_scroll)
            x = min(x, max_scroll)

        return panorama_np[:, x:x + CANVAS_W]

    print(f"🚀 Merender video AlienArt Horizontal Scroll (1920x1080 30FPS) -> {output_path}...")
    video_clip = VideoClip(frame_function=make_frame, duration=total_duration).with_fps(30)

    # Sematkan audio jika tersedia
    assets_audio_dir = "assets/audio"
    if os.path.exists(assets_audio_dir):
        audio_files = [os.path.join(assets_audio_dir, f) for f in os.listdir(assets_audio_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
        if audio_files:
            try:
                bgm = AudioFileClip(audio_files[0])
                if bgm.duration < total_duration:
                    repeats = int(total_duration // bgm.duration) + 1
                    bgm = concatenate_videoclips([bgm] * repeats)
                video_clip = video_clip.with_audio(bgm.subclipped(0, total_duration))
                print(f"🎵 Audio BGM disematkan: {os.path.basename(audio_files[0])}")
            except Exception as e:
                print(f"⚠️ Gagal menyematkan audio: {e}")

    video_clip.write_videofile(
        output_path,
        fps=30,
        codec="libx264",
        audio_codec="aac" if video_clip.audio else None,
        preset="fast",
        threads=4
    )
    print(f"✅ Video AlienArt berhasil dirender sempurna: {output_path}")

    # Simpan juga preview frame terakhir untuk verifikasi
    last_frame_img = Image.fromarray(panorama_np[:, max_scroll:max_scroll + CANVAS_W])
    last_frame_path = "output/alienart_last_frame_preview.png"
    last_frame_img.save(last_frame_path)
    print(f"🖼️ Preview frame akhir berhasil disimpan di: {last_frame_path}")

    return output_path

if __name__ == "__main__":
    # 1. Simpan preview frame awal (1920x1080)
    panorama = generate_full_panorama(CHARACTERS_DATA)
    first_frame = panorama.crop((0, 0, CANVAS_W, CANVAS_H))
    first_frame.save("output/alienart_exact_preview.png")

    # 2. Render video dengan batas scroll eksak
    build_scrolling_video(CHARACTERS_DATA, output_path="output/alienart_evolution_scroll.mp4", scroll_duration=16.0)

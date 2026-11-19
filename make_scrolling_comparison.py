"""
Exact YouTube Template: Horizontal Scrolling Character Height Comparison
Mereplikasi persis template video YouTube referensi:
- 16:9 Landscape (1920x1080)
- 4 Kolom karakter berdampingan (masing-masing 480px)
- Bagian Atas (520px): Foto / Close-up Karakter
- Bagian Tengah (100px): Pita Kuning (#FFD700) + Nama Karakter Bold Hitam (Impact)
- Bagian Bawah (460px): Background Hitam Pekat + Angka Tinggi Badan Bold Putih (Impact)
- Border pemisah putih bersih
- Animasi smooth scrolling dari karakter terpendek hingga karakter tertinggi
"""
import os
import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import VideoClip, AudioFileClip, concatenate_videoclips

W, H = 1920, 1080
COL_W = 480
IMG_H = 520
NAME_H = 100
STAT_H = H - IMG_H - NAME_H # 460px

CHARACTERS_DATA = [
    {"name": "Emma Sano", "height": "150 cm", "img": "assets/images/height_comparison/Emma_Sano.png"},
    {"name": "Hinata Tachibana", "height": "153 cm", "img": "assets/images/height_comparison/Hinata_Tachibana.png"},
    {"name": "Senju Kawaragi", "height": "154 cm", "img": "assets/images/height_comparison/Senju_Kawaragi.png"},
    {"name": "Manjiro Sano", "height": "162 cm", "img": "assets/images/height_comparison/Manjiro_Sano.png"},
    {"name": "Tetta Kisaki", "height": "164 cm", "img": "assets/images/height_comparison/Tetta_Kisaki.png"},
    {"name": "Takemichi Hanagaki", "height": "165 cm", "img": "assets/images/height_comparison/Takemichi_Hanagaki.png"},
    {"name": "Izana Kurokawa", "height": "165 cm", "img": "assets/images/height_comparison/Izana_Kurokawa.png"},
    {"name": "Chifuyu Matsuno", "height": "168 cm", "img": "assets/images/height_comparison/Chifuyu_Matsuno.png"},
    {"name": "Takashi Mitsuya", "height": "170 cm", "img": "assets/images/height_comparison/Takashi_Mitsuya.png"},
    {"name": "Kazutora Hanemiya", "height": "174 cm", "img": "assets/images/height_comparison/Kazutora_Hanemiya.png"},
    {"name": "Keisuke Baji", "height": "175 cm", "img": "assets/images/height_comparison/Keisuke_Baji.png"},
    {"name": "Hakkai Shiba", "height": "183 cm", "img": "assets/images/height_comparison/Hakkai_Shiba.png"},
    {"name": "Ken Ryuguji", "height": "185 cm", "img": "assets/images/height_comparison/Ken_Ryuguji.png"},
    {"name": "Shuji Hanma", "height": "192 cm", "img": "assets/images/height_comparison/Shuji_Hanma.png"},
    {"name": "Taiju Shiba", "height": "195 cm", "img": "assets/images/height_comparison/Taiju_Shiba.png"},
    {"name": "South Terano", "height": "210 cm", "img": "assets/images/height_comparison/South_Terano.png"},
]

def render_character_column(char_info):
    """Merender 1 kolom karakter utuh (480x1080) persis seperti template"""
    col = Image.new("RGB", (COL_W, H), (0, 0, 0))
    
    # 1. Top Image Box (480 x 520)
    img_path = char_info.get("img")
    if img_path and os.path.exists(img_path):
        src = Image.open(img_path).convert("RGB")
        src_w, src_h = src.size
        target_ratio = COL_W / IMG_H
        src_ratio = src_w / max(src_h, 1)
        
        if src_ratio > target_ratio:
            new_h = IMG_H
            new_w = int(new_h * src_ratio)
            scaled = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
            x_crop = (new_w - COL_W) // 2
            cropped = scaled.crop((x_crop, 0, x_crop + COL_W, IMG_H))
        else:
            new_w = COL_W
            new_h = int(new_w / src_ratio)
            scaled = src.resize((new_w, new_h), Image.Resampling.LANCZOS)
            cropped = scaled.crop((0, 0, COL_W, IMG_H))
            
        col.paste(cropped, (0, 0))
    else:
        draw_temp = ImageDraw.Draw(col)
        draw_temp.rectangle([(0, 0), (COL_W, IMG_H)], fill=(30, 30, 40))

    draw = ImageDraw.Draw(col)
    
    # 2. Middle Yellow Bar (480 x 100)
    yellow_y0 = IMG_H
    yellow_y1 = IMG_H + NAME_H
    draw.rectangle([(0, yellow_y0), (COL_W, yellow_y1)], fill=(255, 215, 0)) # Kuning cerah khas template
    
    # Border garis hitam pembatas pita kuning
    draw.line([(0, yellow_y0), (COL_W, yellow_y0)], fill=(0, 0, 0), width=3)
    draw.line([(0, yellow_y1), (COL_W, yellow_y1)], fill=(0, 0, 0), width=3)
    
    # Teks Nama Karakter (Hitam, Bold Condensed / Impact)
    font_name = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 46)
    name_str = char_info.get("name", "Unknown")
    
    bbox = font_name.getbbox(name_str)
    nw = bbox[2] - bbox[0]
    if nw > COL_W - 20:
        font_name = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 36)
        bbox = font_name.getbbox(name_str)
        nw = bbox[2] - bbox[0]
        
    nh = bbox[3] - bbox[1]
    name_x = (COL_W - nw) // 2
    name_y = yellow_y0 + (NAME_H - nh) // 2 - bbox[1]
    draw.text((name_x, name_y), name_str, fill=(0, 0, 0), font=font_name)
    
    # 3. Bottom Black Area (480 x 460)
    draw.rectangle([(0, yellow_y1), (COL_W, H)], fill=(0, 0, 0))
    
    # Teks Tinggi Badan (Putih, Besar, Bold / Impact)
    font_height = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 76)
    h_str = char_info.get("height", "0 cm")
    h_bbox = font_height.getbbox(h_str)
    hw = h_bbox[2] - h_bbox[0]
    hh = h_bbox[3] - h_bbox[1]
    h_x = (COL_W - hw) // 2
    h_y = yellow_y1 + (STAT_H - hh) // 2 - h_bbox[1]
    draw.text((h_x, h_y), h_str, fill=(255, 255, 255), font=font_height)
    
    # 4. White Divider Lines (Garis pemisah vertikal putih)
    draw.line([(COL_W - 2, 0), (COL_W - 2, H)], fill=(255, 255, 255), width=4)
    draw.line([(0, 0), (0, H)], fill=(255, 255, 255), width=2)
    draw.line([(0, 0), (COL_W, 0)], fill=(255, 255, 255), width=4)

    return col

def generate_full_panorama(characters):
    """Menyusun seluruh kolom karakter menjadi 1 gambar strip horizontal panjang"""
    total_w = len(characters) * COL_W
    print(f"🖼️ Membuat strip panorama horizontal: {total_w}x{H} untuk {len(characters)} karakter...")
    panorama = Image.new("RGB", (total_w, H), (0, 0, 0))
    
    for idx, char_info in enumerate(characters):
        col_img = render_character_column(char_info)
        panorama.paste(col_img, (idx * COL_W, 0))
        
    return panorama

def build_scrolling_video(characters, output_path="output/tokyo_revengers_scrolling_comparison.mp4", scroll_duration=45.0):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    
    # 1. Bangun strip gambar panorama
    panorama_img = generate_full_panorama(characters)
    panorama_np = np.array(panorama_img)
    total_w = panorama_img.width
    max_scroll = total_w - W
    
    # 2. Timing scroll
    start_pause = 2.5 # Jeda di awal
    end_pause = 3.5   # Jeda di akhir
    total_duration = start_pause + scroll_duration + end_pause
    
    print(f"⏱️ Total durasi video: {total_duration:.1f} detik (Scroll: {scroll_duration}s, Start/End Pause: {start_pause + end_pause}s)")

    def make_frame(t):
        if t < start_pause:
            x = 0
        elif t > (start_pause + scroll_duration):
            x = max_scroll
        else:
            progress = (t - start_pause) / scroll_duration
            x = int(progress * max_scroll)
            x = min(x, max_scroll)
            
        return panorama_np[:, x:x + W]

    print(f"🚀 Merender video scroll horizontal (1920x1080 30FPS) ke {output_path}...")
    video_clip = VideoClip(frame_function=make_frame, duration=total_duration).with_fps(30)
    
    # Cek audio di assets/audio/
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
    print(f"✅ Video berhasil dirender persis sesuai template: {output_path}")
    return output_path

if __name__ == "__main__":
    build_scrolling_video(CHARACTERS_DATA)

"""
Tokyo Revengers Height Comparison Generator
Mendukung:
- Format Landscape (16:9 - 1920x1080) untuk YouTube Video Biasa (Long-Form)
- Format Shorts (9:16 - 1080x1920) untuk YouTube Shorts / Reels / TikTok
- Pengaturan durasi per karakter yang fleksibel (misal 5-7 detik per karakter untuk long video)
"""
import os
import re
import urllib.request
import urllib.parse
import json
import argparse
import numpy as np
from bs4 import BeautifulSoup
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

CHARACTERS_LIST = [
    ("Emma Sano", "EMMA SANO"),
    ("Hinata Tachibana", "HINATA TACHIBANA"),
    ("Senju Kawaragi", "SENJU KAWARAGI"),
    ("Manjiro Sano", "MANJIRO SANO (MIKEY)"),
    ("Tetta Kisaki", "TETTA KISAKI"),
    ("Takemichi Hanagaki", "TAKEMICHI HANAGAKI"),
    ("Izana Kurokawa", "IZANA KUROKAWA"),
    ("Chifuyu Matsuno", "CHIFUYU MATSUNO"),
    ("Takashi Mitsuya", "TAKASHI MITSUYA"),
    ("Kazutora Hanemiya", "KAZUTORA HANEMIYA"),
    ("Keisuke Baji", "KEISUKE BAJI"),
    ("Hakkai Shiba", "HAKKAI SHIBA"),
    ("Ken Ryuguji", "KEN RYUGUJI (DRAKEN)"),
    ("Shuji Hanma", "SHUJI HANMA"),
    ("Taiju Shiba", "TAIJU SHIBA"),
    ("South Terano", "SOUTH TERANO")
]

def fetch_character_data(char_wiki_name, display_name):
    url = f"https://tokyorevengers.fandom.com/api.php?action=parse&page={urllib.parse.quote(char_wiki_name)}&prop=text&format=json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
        html = data.get('parse', {}).get('text', {}).get('*', '')
        soup = BeautifulSoup(html, 'html.parser')
        
        height_str = None
        for item in soup.find_all('div', class_='pi-item'):
            label = item.find('h3', class_='pi-data-label')
            val = item.find('div', class_='pi-data-value')
            if label and 'height' in label.text.lower() and val:
                height_str = val.get_text(separator=' ').strip()
                height_str = re.sub(r'\[\s*\d+\s*\]', '', height_str).strip()
                break
                
        cm = None
        if height_str:
            m = re.search(r'(\d{2,3})\s*cm', height_str)
            if m:
                cm = int(m.group(1))
                
        feet_str = ""
        if height_str:
            feet_match = re.search(r'\(\s*(\d+[\'’]\s*\d+["”]?)\s*\)', height_str)
            if feet_match:
                feet_str = f"({feet_match.group(1).replace('’', chr(39)).replace('”', chr(34))})"
                
        img_url = None
        fig = soup.find('figure', class_='pi-item pi-image')
        if fig and fig.find('a'):
            img_url = fig.find('a')['href'].split('/revision')[0]
            
        return {
            'wiki_name': char_wiki_name,
            'name': display_name,
            'cm': cm,
            'feet': feet_str,
            'image_url': img_url
        }
    except Exception as e:
        print(f"Error fetching {char_wiki_name}: {e}")
        return None

def download_image(url, save_path):
    if os.path.exists(save_path) and os.path.getsize(save_path) > 1000:
        return save_path
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as res, open(save_path, 'wb') as f:
        f.write(res.read())
    return save_path

# ==========================================
# 1. SHORTS FRAME BUILDER (9:16 - 1080x1920)
# ==========================================
def create_card_frame_shorts(char_data, rank, total, min_cm=145, max_cm=215):
    W, H = 1080, 1920
    canvas = Image.new("RGB", (W, H), (12, 13, 20))
    img_path = char_data.get('local_image')
    
    if img_path and os.path.exists(img_path):
        src_img = Image.open(img_path).convert("RGB")
        bg = src_img.resize((W, H), Image.Resampling.BILINEAR)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=35))
        dim = Image.new("RGBA", (W, H), (0, 0, 0, 175))
        bg.paste(dim, (0, 0), dim)
        canvas.paste(bg, (0, 0))
    else:
        src_img = Image.new("RGB", (400, 600), (30, 30, 45))

    draw = ImageDraw.Draw(canvas)
    
    font_impact = "C:/Windows/Fonts/impact.ttf"
    font_bold = "C:/Windows/Fonts/arialbd.ttf"
    
    f_rank = ImageFont.truetype(font_impact, 48)
    f_title = ImageFont.truetype(font_bold, 32)
    f_name = ImageFont.truetype(font_impact, 56)
    f_height_big = ImageFont.truetype(font_impact, 96)
    f_feet = ImageFont.truetype(font_bold, 36)
    f_meter_label = ImageFont.truetype(font_bold, 26)
    
    # Header Banner
    draw.rectangle([(0, 0), (W, 140)], fill=(8, 9, 15, 230))
    t1 = "TOKYO REVENGERS"
    t2 = "HEIGHT COMPARISON"
    b1 = f_title.getbbox(t1)
    b2 = f_title.getbbox(t2)
    draw.text(((W - (b1[2]-b1[0])) // 2, 22), t1, fill=(255, 215, 0), font=f_title)
    draw.text(((W - (b2[2]-b2[0])) // 2, 68), t2, fill=(0, 229, 255), font=f_title)
    
    # Rank Badge
    rank_text = f"#{rank:02d} / {total}"
    draw.rounded_rectangle([(40, 165), (230, 235)], radius=15, fill=(255, 51, 102), outline=(255, 255, 255), width=2)
    draw.text((60, 173), rank_text, fill=(255, 255, 255), font=f_rank)

    # Foreground Character Box
    box_w, box_h = 760, 1060
    box_x = (W - box_w) // 2
    box_y = 255
    
    src_w, src_h = src_img.size
    img_ratio = src_w / max(src_h, 1)
    box_ratio = box_w / box_h
    scale = 0.94
    if img_ratio > box_ratio:
        new_w = int(box_w * scale)
        new_h = int(new_w / img_ratio)
    else:
        new_h = int(box_h * scale)
        new_w = int(new_h * img_ratio)
        
    fg = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    draw.rounded_rectangle([(box_x, box_y), (box_x + box_w, box_y + box_h)], radius=20, fill=(12, 15, 24, 210), outline=(0, 229, 255), width=3)
    fg_x = box_x + (box_w - new_w) // 2
    fg_y = box_y + (box_h - new_h) // 2
    canvas.paste(fg, (fg_x, fg_y))
    
    # Info Card
    info_y = 1345
    draw.rounded_rectangle([(50, info_y), (W - 50, H - 75)], radius=25, fill=(10, 12, 20, 245), outline=(255, 51, 102), width=3)
    
    char_name = char_data.get('name', 'UNKNOWN').upper()
    nb = f_name.getbbox(char_name)
    nw = nb[2] - nb[0]
    draw.text(((W - nw) // 2, info_y + 22), char_name, fill=(255, 255, 255), font=f_name)
    
    cm = char_data.get('cm', 0)
    feet_str = char_data.get('feet', '')
    h_text = f"{cm} cm"
    hb = f_height_big.getbbox(h_text)
    hw = hb[2] - hb[0]
    draw.text(((W - hw) // 2, info_y + 98), h_text, fill=(255, 215, 0), font=f_height_big)
    
    if feet_str:
        fb = f_feet.getbbox(feet_str)
        fw = fb[2] - fb[0]
        draw.text(((W - fw) // 2, info_y + 208), feet_str, fill=(0, 229, 255), font=f_feet)

    # Meter bar
    bar_x0, bar_x1 = 100, W - 100
    bar_y = info_y + 278
    bar_w = bar_x1 - bar_x0
    bar_h = 24
    draw.rounded_rectangle([(bar_x0, bar_y), (bar_x1, bar_y + bar_h)], radius=12, fill=(35, 40, 55))
    pct = max(0.06, min(1.0, (cm - min_cm) / (max_cm - min_cm)))
    fill_w = int(bar_w * pct)
    draw.rounded_rectangle([(bar_x0, bar_y), (bar_x0 + fill_w, bar_y + bar_h)], radius=12, fill=(255, 51, 102))
    draw.text((bar_x0, bar_y + 32), f"{min_cm} cm", fill=(170, 175, 195), font=f_meter_label)
    draw.text((bar_x1 - 95, bar_y + 32), f"{max_cm} cm", fill=(170, 175, 195), font=f_meter_label)

    return canvas

# =============================================
# 2. LANDSCAPE FRAME BUILDER (16:9 - 1920x1080)
# =============================================
def create_card_frame_landscape(char_data, rank, total, min_cm=140, max_cm=215):
    W, H = 1920, 1080
    canvas = Image.new("RGB", (W, H), (12, 13, 20))
    img_path = char_data.get('local_image')
    
    if img_path and os.path.exists(img_path):
        src_img = Image.open(img_path).convert("RGB")
        bg = src_img.resize((W, H), Image.Resampling.BILINEAR)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=45))
        dim = Image.new("RGBA", (W, H), (0, 0, 0, 180))
        bg.paste(dim, (0, 0), dim)
        canvas.paste(bg, (0, 0))
    else:
        src_img = Image.new("RGB", (400, 600), (30, 30, 45))

    draw = ImageDraw.Draw(canvas)
    
    font_impact = "C:/Windows/Fonts/impact.ttf"
    font_bold = "C:/Windows/Fonts/arialbd.ttf"
    
    f_header = ImageFont.truetype(font_impact, 42)
    f_sub = ImageFont.truetype(font_bold, 24)
    f_rank = ImageFont.truetype(font_impact, 52)
    f_name = ImageFont.truetype(font_impact, 64)
    f_height_big = ImageFont.truetype(font_impact, 110)
    f_feet = ImageFont.truetype(font_bold, 42)
    f_label = ImageFont.truetype(font_bold, 28)
    f_ruler = ImageFont.truetype(font_bold, 20)

    # Header
    draw.rectangle([(0, 0), (W, 90)], fill=(8, 9, 15, 230))
    draw.text((60, 22), "TOKYO REVENGERS", fill=(255, 215, 0), font=f_header)
    draw.text((450, 30), "|  OFFICIAL CHARACTER HEIGHT COMPARISON", fill=(0, 229, 255), font=f_sub)
    
    # Left Ruler
    ruler_x = 140
    ruler_top_y = 140
    ruler_bot_y = 1000
    ruler_height_px = ruler_bot_y - ruler_top_y
    draw.line([(ruler_x, ruler_top_y), (ruler_x, ruler_bot_y)], fill=(120, 130, 160), width=4)
    
    for cm_val in range(min_cm, max_cm + 1, 5):
        pct = (cm_val - min_cm) / (max_cm - min_cm)
        tick_y = int(ruler_bot_y - pct * ruler_height_px)
        is_major = (cm_val % 10 == 0)
        tick_len = 35 if is_major else 20
        tick_color = (255, 215, 0) if is_major else (140, 150, 180)
        draw.line([(ruler_x, tick_y), (ruler_x + tick_len, tick_y)], fill=tick_color, width=3 if is_major else 2)
        if is_major:
            draw.text((ruler_x - 85, tick_y - 12), f"{cm_val}cm", fill=(255, 255, 255), font=f_ruler)

    # Middle Character Portrait
    char_box_w = 680
    char_box_h = 880
    char_box_x = 260
    char_box_y = 130
    
    draw.rounded_rectangle([(char_box_x, char_box_y), (char_box_x + char_box_w, char_box_y + char_box_h)], radius=25, fill=(12, 15, 24, 210), outline=(0, 229, 255), width=3)
    
    src_w, src_h = src_img.size
    img_ratio = src_w / max(src_h, 1)
    box_ratio = char_box_w / char_box_h
    scale = 0.94
    if img_ratio > box_ratio:
        new_w = int(char_box_w * scale)
        new_h = int(new_w / img_ratio)
    else:
        new_h = int(char_box_h * scale)
        new_w = int(new_h * img_ratio)
        
    fg = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    fg_x = char_box_x + (char_box_w - new_w) // 2
    fg_y = char_box_y + (char_box_h - new_h) // 2
    canvas.paste(fg, (fg_x, fg_y))
    
    # Neon pointer line to ruler
    char_cm = char_data.get('cm', 162)
    char_pct = (char_cm - min_cm) / (max_cm - min_cm)
    pointer_y = int(ruler_bot_y - char_pct * ruler_height_px)
    draw.line([(ruler_x, pointer_y), (char_box_x + char_box_w, pointer_y)], fill=(255, 51, 102), width=3)
    draw.polygon([(ruler_x + 10, pointer_y - 8), (ruler_x + 10, pointer_y + 8), (ruler_x - 4, pointer_y)], fill=(255, 51, 102))

    # Right Card
    card_x0, card_y0 = 1000, 130
    card_x1, card_y1 = 1860, 1010
    draw.rounded_rectangle([(card_x0, card_y0), (card_x1, card_y1)], radius=25, fill=(10, 12, 22, 245), outline=(255, 51, 102), width=3)
    
    # Rank
    draw.rounded_rectangle([(card_x0 + 40, card_y0 + 40), (card_x0 + 360, card_y0 + 115)], radius=15, fill=(255, 51, 102))
    draw.text((card_x0 + 65, card_y0 + 48), f"RANK #{rank:02d} OF {total}", fill=(255, 255, 255), font=f_rank)
    
    # Name
    char_name = char_data.get('name', 'UNKNOWN').upper()
    draw.text((card_x0 + 40, card_y0 + 150), char_name, fill=(255, 255, 255), font=f_name)
    draw.line([(card_x0 + 40, card_y0 + 245), (card_x1 - 40, card_y0 + 245)], fill=(40, 45, 65), width=2)
    
    # Height
    draw.text((card_x0 + 40, card_y0 + 270), "OFFICIAL HEIGHT:", fill=(170, 175, 195), font=f_label)
    feet_str = char_data.get('feet', '')
    draw.text((card_x0 + 40, card_y0 + 320), f"{char_cm} cm", fill=(255, 215, 0), font=f_height_big)
    if feet_str:
        draw.text((card_x0 + 40, card_y0 + 445), feet_str, fill=(0, 229, 255), font=f_feet)

    draw.line([(card_x0 + 40, card_y0 + 520), (card_x1 - 40, card_y0 + 520)], fill=(40, 45, 65), width=2)
    draw.text((card_x0 + 40, card_y0 + 545), "SERIES:", fill=(170, 175, 195), font=f_label)
    draw.text((card_x0 + 180, card_y0 + 545), "Tokyo Revengers", fill=(255, 255, 255), font=f_label)
    
    draw.text((card_x0 + 40, card_y0 + 600), "DIFFERENCE:", fill=(170, 175, 195), font=f_label)
    diff_text = f"{char_cm - min_cm:+d} cm from shortest"
    draw.text((card_x0 + 240, card_y0 + 600), diff_text, fill=(0, 229, 255), font=f_label)

    # Meter
    draw.text((card_x0 + 40, card_y0 + 680), "HEIGHT PERCENTAGE METER:", fill=(170, 175, 195), font=f_sub)
    bar_x0 = card_x0 + 40
    bar_x1 = card_x1 - 40
    bar_y = card_y0 + 725
    bar_w = bar_x1 - bar_x0
    bar_h = 28
    draw.rounded_rectangle([(bar_x0, bar_y), (bar_x1, bar_y + bar_h)], radius=14, fill=(35, 40, 55))
    fill_w = int(bar_w * char_pct)
    draw.rounded_rectangle([(bar_x0, bar_y), (bar_x0 + fill_w, bar_y + bar_h)], radius=14, fill=(255, 51, 102))
    draw.text((bar_x0, bar_y + 36), f"Min: {min_cm} cm", fill=(140, 145, 165), font=f_sub)
    draw.text((bar_x1 - 130, bar_y + 36), f"Max: {max_cm} cm", fill=(140, 145, 165), font=f_sub)

    return canvas

def create_intro_clip(is_landscape=False, duration=3.0):
    W, H = (1920, 1080) if is_landscape else (1080, 1920)
    img = Image.new("RGB", (W, H), (10, 11, 18))
    draw = ImageDraw.Draw(img)
    f_impact = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 80 if is_landscape else 74)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40 if is_landscape else 36)
    
    t1 = "TOKYO REVENGERS"
    t2 = "CHARACTER HEIGHT RANKING"
    t3 = "SHORTEST ➡️ TALLEST"
    
    b1 = f_impact.getbbox(t1)
    b2 = f_impact.getbbox(t2)
    b3 = f_sub.getbbox(t3)
    
    draw.text(((W - (b1[2]-b1[0])) // 2, H // 2 - 140), t1, fill=(255, 215, 0), font=f_impact)
    draw.text(((W - (b2[2]-b2[0])) // 2, H // 2 - 40), t2, fill=(255, 255, 255), font=f_impact)
    
    pw = b3[2] - b3[0]
    draw.rounded_rectangle([(W // 2 - pw // 2 - 30, H // 2 + 70), (W // 2 + pw // 2 + 30, H // 2 + 145)], radius=20, fill=(255, 51, 102))
    draw.text(((W - pw) // 2, H // 2 + 85), t3, fill=(255, 255, 255), font=f_sub)
    return ImageClip(np.array(img)).with_duration(duration)

def create_outro_clip(is_landscape=False, duration=3.5):
    W, H = (1920, 1080) if is_landscape else (1080, 1920)
    img = Image.new("RGB", (W, H), (10, 11, 18))
    draw = ImageDraw.Draw(img)
    f_impact = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 74 if is_landscape else 66)
    f_sub = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40 if is_landscape else 38)
    
    t1 = "WHO IS TALLER THAN YOU?"
    t2 = "COMMENT YOUR HEIGHT BELOW!"
    t3 = "🔔 LIKE & SUBSCRIBE FOR MORE ANIME RANKINGS 🔔"
    
    b1 = f_impact.getbbox(t1)
    b2 = f_impact.getbbox(t2)
    b3 = f_sub.getbbox(t3)
    
    draw.text(((W - (b1[2]-b1[0])) // 2, H // 2 - 110), t1, fill=(255, 255, 255), font=f_impact)
    draw.text(((W - (b2[2]-b2[0])) // 2, H // 2 - 20), t2, fill=(255, 215, 0), font=f_impact)
    
    pw = b3[2] - b3[0]
    draw.rounded_rectangle([(W // 2 - pw // 2 - 30, H // 2 + 80), (W // 2 + pw // 2 + 30, H // 2 + 155)], radius=20, fill=(255, 51, 102))
    draw.text(((W - pw) // 2, H // 2 + 95), t3, fill=(255, 255, 255), font=f_sub)
    return ImageClip(np.array(img)).with_duration(duration)

def build_height_video(format_type="landscape", duration_per_char=4.5, output_file=None):
    is_landscape = (format_type.lower() == "landscape")
    W, H = (1920, 1080) if is_landscape else (1080, 1920)
    
    if not output_file:
        output_file = f"output/tokyo_revengers_height_{format_type}.mp4"
        
    print("=" * 65)
    print(f"📊 TOKYO REVENGERS HEIGHT COMPARISON ({format_type.upper()})")
    print(f"📐 Resolusi: {W}x{H} | Durasi per karakter: {duration_per_char}s")
    print("=" * 65)
    
    save_img_dir = "assets/images/height_comparison"
    os.makedirs(save_img_dir, exist_ok=True)
    
    data_list = []
    print("\n[1/3] Menyiapkan data & gambar karakter...")
    for wiki_name, display_name in CHARACTERS_LIST:
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', wiki_name)
        local_p = os.path.join(save_img_dir, f"{safe_name}.png")
        
        # Jika gambar lokal sudah ada dari unduhan sebelumnya, langsung gunakan
        if os.path.exists(local_p):
            cdata = fetch_character_data(wiki_name, display_name)
            if cdata and cdata.get('cm'):
                cdata['local_image'] = local_p
                data_list.append(cdata)
                print(f" - {display_name}: OK ({cdata['cm']} cm)")
        else:
            cdata = fetch_character_data(wiki_name, display_name)
            if cdata and cdata.get('cm') and cdata.get('image_url'):
                download_image(cdata['image_url'], local_p)
                cdata['local_image'] = local_p
                data_list.append(cdata)
                print(f" - {display_name}: OK ({cdata['cm']} cm)")

    data_list.sort(key=lambda x: x['cm'])
    total_chars = len(data_list)
    print(f"\n✅ Total karakter siap: {total_chars}")
    
    # Build clips
    print("\n[2/3] Merender frame video...")
    clips = [create_intro_clip(is_landscape=is_landscape, duration=3.0)]
    
    for rank, char in enumerate(data_list, 1):
        if is_landscape:
            frame = create_card_frame_landscape(char, rank=rank, total=total_chars)
        else:
            frame = create_card_frame_shorts(char, rank=rank, total=total_chars)
        np_frame = np.array(frame)
        clip = ImageClip(np_frame).with_duration(duration_per_char)
        clips.append(clip)
        
    clips.append(create_outro_clip(is_landscape=is_landscape, duration=3.5))
    
    final_video = concatenate_videoclips(clips, method="compose")
    total_duration = final_video.duration
    print(f"⏱️ Total durasi video: {total_duration:.1f} detik ({len(clips)} segmen).")
    
    # Audio
    audio_dir = "assets/audio"
    if os.path.exists(audio_dir):
        audio_files = [os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
        if audio_files:
            try:
                bgm = AudioFileClip(audio_files[0])
                if bgm.duration < total_duration:
                    repeats = int(total_duration // bgm.duration) + 1
                    bgm = concatenate_videoclips([bgm] * repeats)
                final_video = final_video.with_audio(bgm.subclipped(0, total_duration))
                print(f"🎵 Menggunakan audio: {os.path.basename(audio_files[0])}")
            except Exception as e:
                print(f"⚠️ Audio gagal: {e}")
                
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    print(f"\n[3/3] Mengekspor video ke {output_file}...")
    final_video.write_videofile(
        output_file,
        fps=30,
        codec="libx264",
        audio_codec="aac" if final_video.audio else None,
        preset="fast",
        threads=4
    )
    print(f"\n🎉 SUKSES! Video tersimpan di: {output_file}")
    return output_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tokyo Revengers Height Video")
    parser.add_argument("--format", choices=["landscape", "shorts"], default="landscape", help="Format video: landscape (16:9 Long Video) atau shorts (9:16)")
    parser.add_argument("--duration", type=float, default=4.5, help="Durasi per karakter dalam detik (misal: 4.5 atau 6.0 untuk long video)")
    args = parser.parse_args()
    
    build_height_video(format_type=args.format, duration_per_char=args.duration)

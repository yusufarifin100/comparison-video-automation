"""
Video Engine Module
Merakit video perbandingan karakter anime:
- Mode Shorts (9:16 - 1080x1920): Atas (Past) vs Bawah (Present)
- Mode Landscape (16:9 - 1920x1080): Kiri (Past) vs Kanan (Present)
Menggunakan Pillow untuk compositing grafis ultra-HD dan MoviePy untuk encoding video & audio.
"""
import os
import json
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from moviepy import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips
)

class VideoEngine:
    def __init__(self, config_path=None):
        self.config = self._load_config(config_path)
        self.video_cfg = self.config.get("video", {})
        
        # Resolusi: mendukung 1080x1920 (Shorts) atau 1920x1080 (Landscape)
        res = self.video_cfg.get("resolution", [1080, 1920])
        self.width = res[0]
        self.height = res[1]
        self.fps = self.video_cfg.get("fps", 30)
        self.duration_per_char = self.video_cfg.get("duration_per_character", 3.5)
        self.transition_duration = self.video_cfg.get("transition_duration", 0.4)
        
        # Load fonts
        self.font_impact = self._find_font(["C:/Windows/Fonts/impact.ttf", "impact.ttf", "arialbd.ttf"])
        self.font_bold = self._find_font(["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/segoeuib.ttf", "arialbd.ttf"])

    def _load_config(self, config_path):
        if not config_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_path = os.path.join(base_dir, "config", "settings.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _find_font(self, font_candidates):
        for candidate in font_candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _get_font(self, font_path, size):
        try:
            if font_path and os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
            return ImageFont.load_default()
        except Exception:
            return ImageFont.load_default()

    def _fit_image_to_box(self, img_path, target_w, target_h):
        """
        Membuat background blur cinematic dari gambar asli,
        lalu menempatkan gambar tajam di tengah dengan aspect ratio yang terjaga.
        """
        if isinstance(img_path, str) and os.path.exists(img_path):
            src_img = Image.open(img_path).convert("RGB")
        elif isinstance(img_path, Image.Image):
            src_img = img_path.convert("RGB")
        else:
            # Fallback jika gambar tidak ditemukan
            src_img = Image.new("RGB", (target_w, target_h), (30, 30, 45))

        # 1. Background blur + ambient darkening
        bg = src_img.resize((target_w, target_h), Image.Resampling.BILINEAR)
        bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
        dim = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 150))
        bg.paste(dim, (0, 0), dim)

        # 2. Foreground sharp image (fit to 90% of box)
        src_w, src_h = src_img.size
        img_ratio = src_w / max(src_h, 1)
        box_ratio = target_w / max(target_h, 1)

        scale = 0.90
        if img_ratio > box_ratio:
            new_w = int(target_w * scale)
            new_h = int(new_w / img_ratio)
        else:
            new_h = int(target_h * scale)
            new_w = int(new_h * img_ratio)

        fg = src_img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Subtle shadow di belakang foreground
        shadow = Image.new("RGBA", (new_w + 20, new_h + 20), (0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=10))
        
        pos_x = (target_w - new_w) // 2
        pos_y = (target_h - new_h) // 2
        
        bg.paste(shadow, (pos_x - 10, pos_y - 10), shadow)
        bg.paste(fg, (pos_x, pos_y))
        return bg

    def _draw_pill_badge(self, draw, text, center_x, center_y, font, bg_color, text_color, border_color=None):
        """Menggambar rounded pill badge"""
        bbox = font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        pad_x, pad_y = 24, 12
        x0 = center_x - text_w // 2 - pad_x
        y0 = center_y - text_h // 2 - pad_y
        x1 = center_x + text_w // 2 + pad_x
        y1 = center_y + text_h // 2 + pad_y
        
        radius = (y1 - y0) // 2
        draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bg_color, outline=border_color, width=3)
        
        text_x = center_x - text_w // 2 - bbox[0]
        text_y = center_y - text_h // 2 - bbox[1]
        draw.text((text_x, text_y), text, fill=text_color, font=font)

    def generate_comparison_frame(self, char_data):
        """
        Merender frame perbandingan:
        - Mode Vertikal (Shorts): Top (Past) vs Bottom (Present)
        - Mode Horizontal (Landscape): Left (Past) vs Right (Present)
        """
        W, H = self.width, self.height
        is_vertical = H >= W
        
        canvas = Image.new("RGB", (W, H), (15, 15, 25))
        past_img_path = char_data.get("past_image")
        present_img_path = char_data.get("present_image")
        
        neon_color = (255, 51, 102) # Pink/Neon Red
        cyan_color = (0, 229, 255)  # Neon Cyan
        
        font_title = self._get_font(self.font_impact, 54 if is_vertical else 58)
        font_badge = self._get_font(self.font_bold, 30 if is_vertical else 34)
        font_vs = self._get_font(self.font_impact, 42)
        
        char_name = char_data.get("name", "CHARACTER").upper()
        past_label = char_data.get("past_label", "PAST").upper()
        present_label = char_data.get("present_label", "PRESENT").upper()

        if is_vertical:
            # === MODE SHORTS (TOP vs BOTTOM) ===
            half_h = H // 2
            top_box = self._fit_image_to_box(past_img_path, W, half_h)
            bot_box = self._fit_image_to_box(present_img_path, W, half_h)
            
            canvas.paste(top_box, (0, 0))
            canvas.paste(bot_box, (0, half_h))
            
            draw = ImageDraw.Draw(canvas)
            
            # Divider Horizontal
            for offset in [-3, -1, 1, 3]:
                draw.line([(0, half_h + offset), (W, half_h + offset)], fill=neon_color, width=2)
            draw.line([(0, half_h), (W, half_h)], fill=(255, 255, 255), width=2)
            
            # Header Name
            draw.rectangle([(0, 0), (W, 110)], fill=(0, 0, 0, 190))
            t_bbox = font_title.getbbox(char_name)
            tw = t_bbox[2] - t_bbox[0]
            draw.text(((W - tw) // 2, 28), char_name, fill=(255, 255, 255), font=font_title)
            
            # Badges
            self._draw_pill_badge(draw, f"◀ {past_label}", W // 2, half_h - 65, font_badge, (15, 25, 45, 220), cyan_color, cyan_color)
            self._draw_pill_badge(draw, "⚡ VS ⚡", W // 2, half_h, font_vs, (20, 10, 20), (255, 255, 255), neon_color)
            self._draw_pill_badge(draw, f"▶ {present_label}", W // 2, half_h + 65, font_badge, (45, 15, 25, 220), neon_color, neon_color)

        else:
            # === MODE LANDSCAPE (LEFT vs RIGHT) ===
            half_w = W // 2
            left_box = self._fit_image_to_box(past_img_path, half_w, H)
            right_box = self._fit_image_to_box(present_img_path, half_w, H)
            
            canvas.paste(left_box, (0, 0))
            canvas.paste(right_box, (half_w, 0))
            
            draw = ImageDraw.Draw(canvas)
            
            # Divider Vertikal
            for offset in [-3, -1, 1, 3]:
                draw.line([(half_w + offset, 0), (half_w + offset, H)], fill=neon_color, width=2)
            draw.line([(half_w, 0), (half_w, H)], fill=(255, 255, 255), width=2)
            
            # Header Name di Top Center
            t_bbox = font_title.getbbox(char_name)
            tw = t_bbox[2] - t_bbox[0]
            self._draw_pill_badge(draw, char_name, W // 2, 60, font_title, (0, 0, 0, 220), (255, 255, 255), (255, 215, 0))
            
            # Badges
            self._draw_pill_badge(draw, f"◀ {past_label}", half_w // 2, H - 70, font_badge, (15, 25, 45, 220), cyan_color, cyan_color)
            self._draw_pill_badge(draw, "⚡ VS ⚡", half_w, H // 2, font_vs, (20, 10, 20), (255, 255, 255), neon_color)
            self._draw_pill_badge(draw, f"▶ {present_label}", half_w + half_w // 2, H - 70, font_badge, (45, 15, 25, 220), neon_color, neon_color)

        return canvas

    def create_character_clip(self, char_data, duration=None):
        dur = duration or self.duration_per_char
        pil_frame = self.generate_comparison_frame(char_data)
        np_frame = np.array(pil_frame)
        return ImageClip(np_frame).with_duration(dur)

    def create_intro_clip(self, title="ANIME EVOLUTION", subtitle="PAST VS PRESENT", duration=2.5):
        W, H = self.width, self.height
        img = Image.new("RGB", (W, H), (12, 13, 20))
        draw = ImageDraw.Draw(img)
        
        font_main = self._get_font(self.font_impact, 68 if H >= W else 76)
        font_sub = self._get_font(self.font_bold, 36 if H >= W else 40)
        
        m_bbox = font_main.getbbox(title)
        mw = m_bbox[2] - m_bbox[0]
        draw.text(((W - mw) // 2, H // 2 - 80), title, fill=(255, 215, 0), font=font_main)
        
        self._draw_pill_badge(
            draw,
            text=subtitle,
            center_x=W // 2,
            center_y=H // 2 + 35,
            font=font_sub,
            bg_color=(255, 51, 102),
            text_color=(255, 255, 255)
        )
        return ImageClip(np.array(img)).with_duration(duration)

    def create_outro_clip(self, message="WHO CHANGED THE MOST?", sub="LIKE & SUBSCRIBE", duration=2.5):
        W, H = self.width, self.height
        img = Image.new("RGB", (W, H), (12, 13, 20))
        draw = ImageDraw.Draw(img)
        
        font_main = self._get_font(self.font_impact, 54 if H >= W else 64)
        font_sub = self._get_font(self.font_bold, 34 if H >= W else 38)
        
        m_bbox = font_main.getbbox(message)
        mw = m_bbox[2] - m_bbox[0]
        draw.text(((W - mw) // 2, H // 2 - 60), message, fill=(255, 255, 255), font=font_main)
        
        self._draw_pill_badge(
            draw,
            text=sub,
            center_x=W // 2,
            center_y=H // 2 + 45,
            font=font_sub,
            bg_color=(255, 51, 102),
            text_color=(255, 255, 255)
        )
        return ImageClip(np.array(img)).with_duration(duration)

    def build_video(self, characters, output_path="output/anime_comparison.mp4", bgm_path=None, include_intro=True):
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        clips = []
        if include_intro:
            clips.append(self.create_intro_clip())
            
        for char in characters:
            clip = self.create_character_clip(char)
            clips.append(clip)
            
        if include_intro:
            clips.append(self.create_outro_clip())
            
        print(f"🎬 Merakit video dengan {len(clips)} segmen klip ({self.width}x{self.height})...")
        final_video = concatenate_videoclips(clips, method="compose")
        total_duration = final_video.duration
        
        # Audio handler
        if bgm_path and os.path.exists(bgm_path):
            try:
                bgm = AudioFileClip(bgm_path)
                if bgm.duration < total_duration:
                    repeats = int(total_duration // bgm.duration) + 1
                    bgm = concatenate_videoclips([bgm] * repeats)
                final_video = final_video.with_audio(bgm.subclipped(0, total_duration))
                print(f"🎵 Audio BGM '{os.path.basename(bgm_path)}' disematkan.")
            except Exception as e:
                print(f"⚠️ Gagal menyematkan audio: {e}")
        else:
            assets_audio_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "audio")
            if os.path.exists(assets_audio_dir):
                audio_files = [os.path.join(assets_audio_dir, f) for f in os.listdir(assets_audio_dir) if f.endswith(('.mp3', '.wav', '.m4a'))]
                if audio_files:
                    try:
                        bgm = AudioFileClip(audio_files[0])
                        if bgm.duration < total_duration:
                            repeats = int(total_duration // bgm.duration) + 1
                            bgm = concatenate_videoclips([bgm] * repeats)
                        final_video = final_video.with_audio(bgm.subclipped(0, total_duration))
                        print(f"🎵 Menggunakan audio assets: '{os.path.basename(audio_files[0])}'")
                    except Exception as e:
                        print(f"⚠️ Gagal memuat audio assets: {e}")

        print(f"🚀 Rendering video ke {output_path}...")
        final_video.write_videofile(
            output_path,
            fps=self.fps,
            codec="libx264",
            audio_codec="aac" if final_video.audio else None,
            preset="fast",
            threads=4
        )
        print(f"✅ Video berhasil dirender: {output_path}")
        return output_path

if __name__ == "__main__":
    engine = VideoEngine()
    sample_data = [{
        "name": "Manjiro Sano (Mikey)",
        "past_label": "2005 (Toman)",
        "past_image": "assets/images/sample/mikey_past_2005.png",
        "present_label": "2017 (Bonten)",
        "present_image": "assets/images/sample/mikey_present_2017.png"
    }]
    engine.build_video(sample_data, output_path="output/test_mikey_landscape.mp4")

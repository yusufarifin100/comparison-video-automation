"""
Pipeline Orchestrator
Menjalankan seluruh alur kerja otomasi video anime:
1. Ekstraksi karakter & unduh gambar (scraper.py)
2. Pengecekan / pewarnaan AI jika ada manga hitam-putih (colorizer.py)
3. Perakitan video MP4 Ultra-HD 1080p (video_engine.py)
4. Upload otomatis / terjadwal ke YouTube (youtube_uploader.py)
"""
import os
import sys
import argparse
import json
from modules.scraper import WikiaScraper
from modules.colorizer import ImageColorizer
from modules.video_engine import VideoEngine
from modules.youtube_uploader import YouTubeUploader

def run_pipeline(characters=None, max_characters=4, format_type="shorts", upload=False):
    print("=" * 65)
    print("🎬 ANIME VIDEO AUTOMATION PIPELINE")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, "config", "settings.json")

    # Inisialisasi modul-modul
    scraper = WikiaScraper()
    colorizer = ImageColorizer()
    video_engine = VideoEngine(config_path=config_file)
    uploader = YouTubeUploader()

    # Atur resolusi sesuai format
    if format_type.lower() == "shorts":
        video_engine.width = 1080
        video_engine.height = 1920
    else:
        video_engine.width = 1920
        video_engine.height = 1080

    # 1. Tentukan karakter yang akan diproses
    if not characters:
        print("\n🔍 Mencari karakter populer dari Wikia...")
        # Daftar karakter utama Tokyo Revengers sebagai default handal
        default_pool = [
            "Manjiro Sano",
            "Takemichi Hanagaki",
            "Ken Ryuguji",
            "Chifuyu Matsuno",
            "Takashi Mitsuya",
            "Keisuke Baji"
        ]
        characters = default_pool[:max_characters]
    
    print(f"📋 Karakter terpilih ({len(characters)}): {', '.join(characters)}")

    # 2. Scrape & Download gambar perbandingan
    comparison_data_list = []
    print("\n[Langkah 1/3] Mengunduh aset gambar Past vs Present...")
    for char in characters:
        try:
            data = scraper.get_comparison_data(char)
            if data:
                # 3. Pengecekan pewarnaan gambar hitam-putih
                data["past_image"] = colorizer.colorize_image(data["past_image"], character_name=char)
                data["present_image"] = colorizer.colorize_image(data["present_image"], character_name=char)
                comparison_data_list.append(data)
            else:
                print(f"⚠️ Gambar perbandingan tidak lengkap untuk {char}. Melewati.")
        except Exception as e:
            print(f"⚠️ Gagal memproses {char}: {e}")

    if not comparison_data_list:
        print("❌ Tidak ada karakter yang berhasil diunduh. Pipeline berhenti.")
        return None

    # 4. Perakitan Video
    print(f"\n[Langkah 2/3] Merakit video ({format_type.upper()})...")
    output_filename = f"anime_evolution_{format_type}_{len(comparison_data_list)}chars.mp4"
    output_path = os.path.join(base_dir, "output", output_filename)
    
    rendered_file = video_engine.build_video(
        characters=comparison_data_list,
        output_path=output_path,
        include_intro=True
    )

    print(f"\n🎉 Video berhasil dibuat: {rendered_file}")

    # 5. Upload YouTube
    if upload:
        print("\n[Langkah 3/3] Menjalankan upload ke YouTube...")
        title = f"Tokyo Revengers Characters Evolution (Past vs Present) 🔥 #{format_type}"
        char_tags = [c.lower() for c in characters]
        desc = (
            f"Tokyo Revengers Character Comparison - Past vs Present Evolution.\n\n"
            f"Characters in this video:\n" +
            "\n".join([f"- {c['name']} ({c['past_label']} ➡️ {c['present_label']})" for c in comparison_data_list]) +
            "\n\nWhich character changed the most? Drop your comments below!\n"
            "#tokyorevengers #anime #pastvspresent #evolution #shorts"
        )
        uploader.upload_video(
            video_path=rendered_file,
            title=title,
            description=desc,
            tags=["tokyo revengers", "anime", "evolution", "past vs present", "anime comparison"] + char_tags,
            privacy_status="private"
        )
    else:
        print("\n💡 Video disimpan secara lokal di folder 'output/'.")
        print("   Gunakan flag '--upload' jika ingin langsung mengunggah ke YouTube.")

    print("\n" + "=" * 65)
    print("✅ PIPELINE SELESAI DENGAN SUKSES!")
    print("=" * 65)
    return rendered_file

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Anime Video Automation Pipeline")
    parser.add_argument("--mode", choices=["comparison", "height", "scroll"], default="scroll", help="Mode video: scroll (YouTube Side-by-Side Scrolling Bar), height (Card Ranking), atau comparison (Past vs Present)")
    parser.add_argument("--chars", nargs="+", help="Daftar nama karakter yang ingin dibandingkan")
    parser.add_argument("--limit", type=int, default=3, help="Jumlah maksimal karakter (default: 3)")
    parser.add_argument("--format", choices=["shorts", "landscape"], default="shorts", help="Format video (shorts: 9:16, landscape: 16:9)")
    parser.add_argument("--upload", action="store_true", help="Upload ke YouTube setelah render selesai")

    args = parser.parse_args()
    
    if args.mode == "scroll":
        from make_scrolling_comparison import build_scrolling_video, CHARACTERS_DATA
        rendered = build_scrolling_video(CHARACTERS_DATA)
        if args.upload:
            uploader = YouTubeUploader()
            uploader.upload_video(
                video_path=rendered,
                title="Height of All Tokyo Revengers Characters (Shortest to Tallest) 📏",
                description="Official Tokyo Revengers Characters Height Comparison from Shortest to Tallest.\nAll stats based on official Character Books!\n#tokyorevengers #mikey #draken #anime #comparison",
                tags=["tokyo revengers", "height comparison", "mikey", "draken", "anime height"],
                privacy_status="private"
            )
    elif args.mode == "height":
        from make_height_video import build_height_video
        rendered = build_height_video()
        if args.upload:
            uploader = YouTubeUploader()
            uploader.upload_video(
                video_path=rendered,
                title="Tokyo Revengers Characters Height Comparison (Shortest to Tallest) 📏 #shorts",
                description="Tokyo Revengers Character Height Comparison from Shortest to Tallest.\nWho is taller than you? Drop your height in the comments!\n#tokyorevengers #mikey #draken #anime #shorts",
                tags=["tokyo revengers", "height comparison", "mikey", "draken", "anime height", "shorts"],
                privacy_status="private"
            )
    else:
        run_pipeline(
            characters=args.chars,
            max_characters=args.limit,
            format_type=args.format,
            upload=args.upload
        )

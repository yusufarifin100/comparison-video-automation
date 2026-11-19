# Comparison Video Automation Pipeline

Sistem otomasi end-to-end untuk membuat video YouTube Comparison (Past vs Present / Height Ranking / Scrolling Comparison / Evolution) secara otomatis dari data Wikia, pewarnaan AI, perakitan video MP4, hingga upload otomatis ke YouTube.

---

## 📁 Struktur Direktori

```text
comparison-video-automation/
├── assets/
│   ├── audio/              # File musik latar (BGM phonk / anime soundtrack)
│   ├── fonts/              # Font khusus video (Impact, Bebas Neue, dll)
│   └── images/             # Gambar karakter yang di-download (Past & Present / Height)
├── config/
│   ├── settings.json       # Konfigurasi video (resolusi, durasi, template)
│   └── client_secrets.json # Kredensial OAuth YouTube Data API v3
├── modules/
│   ├── __init__.py
│   ├── scraper.py          # Modul ekstraksi karakter & gambar dari Wikia
│   ├── colorizer.py        # Modul pewarnaan gambar hitam-putih via Gemini API
│   ├── video_engine.py     # Modul perakitan video (Top vs Bottom / Ranking)
│   └── youtube_uploader.py # Modul upload video otomatis ke YouTube
├── output/                 # Folder hasil render video (.mp4) siap tayang
├── make_height_video.py    # Generator khusus video ranking tinggi badan karakter (1080x1920)
├── pipeline.py             # Script utama untuk menjalankan seluruh alur sekaligus
├── requirements.txt        # Daftar pustaka Python yang dibutuhkan
└── README.md
```

---

## 🚀 Mode Video yang Didukung

1. **Past vs Present Evolution (`--mode comparison`)**:
   - Membandingkan masa lalu (era SMP/2005) vs masa depan/dewasa (era Bonten/2017–2018).
   - Format:
     - **Shorts (9:16)**: Split Atas vs Bawah dengan divider neon & badge era.
     - **Landscape (16:9)**: Split Kiri vs Kanan dengan divider neon.

2. **Height Ranking Comparison (`--mode height`)**:
   - Merangking tinggi badan seluruh karakter anime dari yang paling pendek hingga paling tinggi (*Shortest to Tallest*).
   - Dilengkapi kartu karakter HD, rank badge (`#01 / 16`), tinggi dalam `cm` dan `feet`, serta *visual progress meter bar* yang dinamis!

---

## ⚡ Cara Menjalankan

```bash
# 1. Jalankan video Height Comparison Tokyo Revengers (16 Karakter Lengkap)
python pipeline.py --mode height

# 2. Jalankan video Past vs Present Shorts (4 Karakter Populer)
python pipeline.py --mode comparison --limit 4 --format shorts

# 3. Jalankan video Past vs Present Landscape YouTube (16:9)
python pipeline.py --mode comparison --limit 3 --format landscape

# 4. Langsung upload hasil video ke YouTube (Draft/Private)
python pipeline.py --mode height --upload
```

"""
Tokyo Revengers Complete Gang Affiliations Scraper
Mengambil seluruh karakter Tokyo Revengers dari Wikia:
- Menyaring hanya karakter yang memiliki riwayat geng / delinquency (mengabaikan civilian seperti Hinata, Emma, orang tua, kucing, dll.)
- Mengekstrak riwayat geng lengkap (Former Affiliations, Former Positions, Current Affiliation, Roles)
- Menyusun alur perpindahan geng (Progression Chain: misal 'Brahman ➔ Tokyo Manji Gang')
- Mengambil URL foto beresolusi tinggi untuk setiap karakter
- Menyimpan hasil ke:
  E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data\tokyo_revengers_gang_affiliations.csv
"""
import os
import sys
import re
import csv
import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

OUTPUT_DIR = r"E:\Youtube Project\RankingNoSekai\Tokyo Revenger\Data"
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "tokyo_revengers_gang_affiliations.csv")
OUTPUT_JSON = os.path.join(OUTPUT_DIR, "tokyo_revengers_gang_affiliations.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Daftar geng dan pola pencocokan (diurutkan berdasarkan urutan kemunculan / hirarki umum)
GANG_DEFINITIONS = [
    ("Mizo Mid", [r"mizo\s*middle\s*five", r"mizo\s*mid"]),
    ("Kiyomasa Gang", [r"kiyomasa('?s)?\s*gang", r"kiyomizu('?s)?\s*gang"]),
    ("Moebius", [r"moebius"]),
    ("Black Dragon", [r"black\s*dragons?", r"kuro\s*ryu"]),
    ("Tokyo Manji Gang (1st Gen)", [r"first\s*generation\s*tokyo\s*manji\s*gang"]),
    ("Valhalla", [r"valhalla"]),
    ("S-62 Generation", [r"s-?62\s*generation"]),
    ("Tenjiku", [r"tenjiku"]),
    ("Brahman", [r"brahman"]),
    ("Rokuhara Tandai", [r"rokuhara\s*tandai"]),
    ("Tokyo Manji Gang (2nd Gen)", [r"second\s*generation\s*tokyo\s*manji\s*gang"]),
    ("Kanto Manji Gang", [r"kanto(u)?\s*manji\s*gang"]),
    ("Bonten", [r"bonten"]),
    ("Tokyo Manji Gang", [r"tokyo\s*manji\s*gang", r"\btoman\b"]),
    ("Yotsuya Kaidan", [r"yotsuya\s*kaidan"]),
    ("Ikebukuro Criminal Black Members", [r"ikebukuro\s*criminal", r"\bicbm\b"]),
    ("Ragnarok", [r"ragnarok"]),
    ("Kodo Rengo", [r"kodo\s*rengo"])
]

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\[\s*\d+\s*\]', '', text)
    text = re.sub(r'\(.*?\?.*?\)', '', text) # Hapus romaji/kanji question marks
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_character_list():
    """Mengambil seluruh daftar karakter dari Category:Characters"""
    url = "https://tokyorevengers.fandom.com/api.php?action=query&list=categorymembers&cmtitle=Category:Characters&cmlimit=500&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode('utf-8'))
    
    raw_members = [m['title'] for m in data.get('query', {}).get('categorymembers', []) if m.get('ns') == 0]
    
    # Filter list non-karakter
    exclude_titles = [
        "List of Characters", "List of Characters/Letter from Keisuke Baji",
        "List of Characters/Todai Revengers", "Time Leaper", "Peke J", "Pochi"
    ]
    return [m for m in raw_members if m not in exclude_titles]

def scrape_character_details(char_name):
    """Scrape detail infobox karakter"""
    url = f"https://tokyorevengers.fandom.com/api.php?action=parse&page={urllib.parse.quote(char_name)}&prop=text&format=json"
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
    except Exception as e:
        print(f"⚠️ Gagal fetch {char_name}: {e}")
        return None

    html = data.get('parse', {}).get('text', {}).get('*', '')
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')
    infobox = soup.find('aside', class_='portable-infobox')
    if not infobox:
        return None

    # 1. Foto Karakter Utama
    image_url = ""
    fig = infobox.find('figure', class_='pi-item pi-image')
    if fig and fig.find('a'):
        image_url = fig.find('a')['href'].split('/revision')[0]

    # 2. Extract Data Infobox
    fields = {}
    for h3 in infobox.find_all('h3'):
        lbl = h3.get_text().strip()
        parent = h3.parent
        val = parent.find(['div', 'span', 'p'], class_=lambda c: c and 'pi-data-value' in c)
        txt = val.get_text(separator=' | ').strip() if val else parent.get_text(separator=' | ')
        fields[lbl.lower()] = clean_text(txt)

    affiliation = fields.get('affiliation', '')
    position = fields.get('position', '')
    
    # Ambil former position/affiliation
    former_parts = []
    for k, v in fields.items():
        if 'former' in k and v:
            former_parts.append(v)
    former_text = " | ".join(former_parts)

    combined_text = f"{former_text} | {affiliation} | {position}"

    # 3. Filter: Harus ada afiliasi geng
    # Jika tidak ada satupun geng yang cocok, tandai sebagai civilian (skip)
    detected_gangs = []
    for gang_name, patterns in GANG_DEFINITIONS:
        for p in patterns:
            if re.search(r'\b' + p + r'\b', combined_text, re.IGNORECASE):
                # Normalisasi nama geng
                norm_name = "Tokyo Manji Gang" if "tokyo manji" in gang_name.lower() else gang_name
                if norm_name not in detected_gangs:
                    detected_gangs.append(norm_name)
                break

    if not detected_gangs:
        # Karakter civilian / non-gang (seperti Hinata, Emma, orang tua)
        return None

    # Tentukan Current Gang (biasanya affiliation resmi di infobox)
    current_gang = "Tokyo Manji Gang" if "tokyo manji" in affiliation.lower() else (detected_gangs[-1] if detected_gangs else "Unknown")
    
    # Rapikan alur progression chain
    # Pastikan current_gang berada di akhir jika belum ada
    progression = list(detected_gangs)
    if current_gang in progression:
        progression.remove(current_gang)
    progression.append(current_gang)

    progression_str = " ➔ ".join(progression)

    # Status / Japanese / Romanji
    status = fields.get('status', 'Alive')
    japanese_name = fields.get('japanese', '')
    romaji_name = fields.get('rōmaji', char_name)

    return {
        "name": char_name,
        "japanese": japanese_name,
        "romaji": romaji_name,
        "current_gang": current_gang,
        "current_position": position,
        "former_history": former_text,
        "progression": progression_str,
        "total_gangs": len(progression),
        "status": status,
        "image_url": image_url
    }

def main():
    print("=" * 70)
    print("🚀 SCRAPING AFILIASI GENG LENGKAP KARAKTER TOKYO REVENGERS")
    print("=" * 70)

    char_list = get_character_list()
    print(f"📋 Ditemukan total {len(char_list)} karakter di Wikia.")
    print("🔍 Memfilter karakter yang masuk geng dan mengekstrak datanya...\n")

    gang_characters = []
    skipped_count = 0

    for idx, name in enumerate(char_list):
        print(f"[{idx+1}/{len(char_list)}] Memproses: {name:<25}", end="", flush=True)
        data = scrape_character_details(name)
        if data:
            gang_characters.append(data)
            print(f" ✅ [Geng: {data['progression']}]")
        else:
            skipped_count += 1
            print(f" ❌ (Civilian / Bukan Geng)")

    print("\n" + "=" * 70)
    print(f"📊 Ringkasan:")
    print(f"  - Total Karakter Anggota Geng Ditemukan: {len(gang_characters)}")
    print(f"  - Total Karakter Civilian Diabaikan    : {skipped_count}")
    print("=" * 70)

    # Urutkan berdasarkan nama karakter
    gang_characters.sort(key=lambda x: x['name'])

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Simpan CSV (Kompatibel dengan AlienArt & Excel)
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        # Header komparasi dan data lengkap
        writer.writerow([
            "Highlight",           # Nama Karakter (AlienArt standard)
            "Highlight Image",     # URL Foto (AlienArt standard)
            "Element",             # Alur Geng (misal: Brahman ➔ Tokyo Manji Gang)
            "Current Gang",        # Geng Terakhir / Saat Ini
            "Current Position",    # Jabatan
            "Former History",      # Riwayat Jabatan/Geng Sebelumnya
            "Total Gangs Count"    # Berapa kali pindah geng
        ])
        for c in gang_characters:
            writer.writerow([
                c['name'],
                c['image_url'],
                c['progression'],
                c['current_gang'],
                c['current_position'],
                c['former_history'],
                c['total_gangs']
            ])

    # 2. Simpan JSON juga
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(gang_characters, f, indent=2, ensure_ascii=False)

    print(f"\n🎉 Berhasil menyimpan data ke:")
    print(f"  📁 CSV : {OUTPUT_CSV}")
    print(f"  📁 JSON: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

"""
Scraper Module
Mengambil daftar karakter, era umur/timeline, dan gambar resolusi tinggi dari Wikia.
"""
import os
import urllib.request
import urllib.parse
import json
import re

class WikiaScraper:
    def __init__(self, base_api="https://tokyorevengers.fandom.com/api.php", user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"):
        self.base_api = base_api
        self.headers = {'User-Agent': user_agent}

    def get_category_characters(self, category="Category:Characters", limit=100):
        """Mengambil semua karakter di kategori tertentu"""
        url = f"{self.base_api}?action=query&list=categorymembers&cmtitle={urllib.parse.quote(category)}&cmlimit={limit}&format=json"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
        
        members = data.get('query', {}).get('categorymembers', [])
        return [m['title'] for m in members if m.get('ns') == 0]

    def get_character_timeline_images(self, char_name):
        """Mengambil gambar-gambar per timeline/usia dari halaman infobox karakter"""
        encoded = urllib.parse.quote(char_name)
        url = f"{self.base_api}?action=parse&page={encoded}&prop=text&format=json"
        req = urllib.request.Request(url, headers=self.headers)
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
        
        html = data.get('parse', {}).get('text', {}).get('*', '')
        pattern = r'<figure class="pi-item pi-image">\s*<a href="([^"]+)"[^>]*title="([^"]+)"'
        matches = re.findall(pattern, html)
        
        images = []
        seen = set()
        for link, title in matches:
            clean_url = link.split('/revision')[0]
            if clean_url not in seen:
                seen.add(clean_url)
                clean_label = title.replace('&#39;', "'").strip()
                images.append({
                    'label': clean_label,
                    'url': link,
                    'clean_url': clean_url,
                    'char_name': char_name
                })
        return images

    def download_image(self, img_url, save_path):
        """Download file gambar"""
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        req = urllib.request.Request(img_url, headers=self.headers)
        with urllib.request.urlopen(req) as response, open(save_path, 'wb') as f:
            f.write(response.read())
        return save_path

    def get_comparison_data(self, char_name, save_dir="assets/images"):
        """
        Otomatis memilih pasangan gambar Past vs Present dan men-download keduanya.
        Mengembalikan struktur dict yang siap dipakai VideoEngine.
        """
        imgs = self.get_character_timeline_images(char_name)
        if len(imgs) < 2:
            return None

        # Filter tahun dari label
        year_entries = []
        for img in imgs:
            match = re.search(r'\b(19\d\d|20\d\d)\b', img['label'])
            if match:
                year_entries.append((int(match.group(1)), img))

        past_img = None
        present_img = None

        if len(year_entries) >= 2:
            # Cari era 2005 (era SMP / Toman) jika ada, jika tidak ambil tahun terendah
            past_candidates = [e for e in year_entries if e[0] == 2005]
            if past_candidates:
                past_img = past_candidates[0][1]
            else:
                past_img = min(year_entries, key=lambda x: x[0])[1]

            # Cari era 2017 / 2018 (era Dewasa / Bonten)
            present_candidates = [e for e in year_entries if e[0] in (2017, 2018)]
            if present_candidates:
                present_img = present_candidates[-1][1]
            else:
                present_img = max(year_entries, key=lambda x: x[0])[1]
        else:
            past_img = imgs[0]
            present_img = imgs[-1]

        # Simpan file gambar secara lokal
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', char_name)
        char_folder = os.path.join(save_dir, clean_name)
        
        past_path = os.path.join(char_folder, "past.png")
        present_path = os.path.join(char_folder, "present.png")
        
        print(f"📥 Mengunduh gambar untuk {char_name}:")
        print(f"   - Past ({past_img['label']}) -> {past_path}")
        self.download_image(past_img['clean_url'], past_path)
        
        print(f"   - Present ({present_img['label']}) -> {present_path}")
        self.download_image(present_img['clean_url'], present_path)

        return {
            "name": char_name,
            "past_label": f"PAST ({past_img['label']})",
            "past_image": past_path,
            "present_label": f"PRESENT ({present_img['label']})",
            "present_image": present_path
        }

if __name__ == "__main__":
    scraper = WikiaScraper()
    data = scraper.get_comparison_data("Takemichi Hanagaki")
    print("\nHasil comparison data:")
    print(data)

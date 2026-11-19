"""
YouTube Uploader Module
Mengunggah video hasil render ke YouTube menggunakan YouTube Data API v3.
Mendukung judul SEO, tag, deskripsi otomatis, dan pengaturan privasi (private/unlisted/public).
"""
import os
import json
import httplib2

class YouTubeUploader:
    def __init__(self, secrets_file=None, token_file=None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.secrets_file = secrets_file or os.path.join(base_dir, "config", "client_secrets.json")
        self.token_file = token_file or os.path.join(base_dir, "config", "youtube_token.json")
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]

    def is_configured(self):
        """Mengecek apakah kredensial OAuth client_secrets.json tersedia"""
        return os.path.exists(self.secrets_file)

    def get_authenticated_service(self):
        """Mendapatkan authenticated YouTube service instance"""
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        credentials = None
        if os.path.exists(self.token_file):
            try:
                credentials = Credentials.from_authorized_user_file(self.token_file, self.scopes)
            except Exception as e:
                print(f"⚠️ Token lama tidak valid: {e}")

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    credentials.refresh(Request())
                except Exception:
                    credentials = None
            
            if not credentials:
                if not os.path.exists(self.secrets_file):
                    raise FileNotFoundError(
                        f"File kredensial OAuth '{self.secrets_file}' tidak ditemukan.\n"
                        "Silakan download file OAuth Client ID JSON dari Google Cloud Console "
                        "dan simpan sebagai config/client_secrets.json."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, self.scopes)
                credentials = flow.run_local_server(port=0)

            # Simpan token untuk eksekusi berikutnya tanpa perlu login ulang
            with open(self.token_file, "w", encoding="utf-8") as f:
                f.write(credentials.to_json())

        return build("youtube", "v3", credentials=credentials)

    def upload_video(self, video_path, title, description, tags=None, category_id="24", privacy_status="private"):
        """
        Mengunggah video ke YouTube.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file tidak ditemukan: {video_path}")

        tags = tags or ["anime", "tokyo revengers", "evolution", "past vs present", "shorts"]

        # Jika belum dikonfigurasi, jalankan Dry-Run / Simulasi
        if not self.is_configured():
            print(f"ℹ️ [DRY RUN] Kredensial '{self.secrets_file}' belum ditemukan.")
            print(f"📄 Video siap upload: {video_path}")
            print(f"📌 Judul: {title}")
            print(f"🏷️ Tags: {', '.join(tags)}")
            print(f"🔒 Status: {privacy_status}")
            print(f"💡 Simpan file OAuth Google Console Anda di '{self.secrets_file}' untuk mengaktifkan upload live.")
            return {"status": "dry_run", "video_path": video_path, "title": title}

        from googleapiclient.http import MediaFileUpload

        print(f"🔐 Mengotentikasi akun YouTube...")
        youtube = self.get_authenticated_service()

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags,
                "categoryId": str(category_id)
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        print(f"🚀 Mengunggah '{os.path.basename(video_path)}' ke YouTube ({privacy_status})...")

        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"⏳ Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        print(f"✅ Video berhasil di-upload!")
        print(f"🔗 Tautan: {video_url}")
        return {
            "status": "success",
            "video_id": video_id,
            "url": video_url
        }

if __name__ == "__main__":
    uploader = YouTubeUploader()
    uploader.upload_video(
        video_path="output/test_mikey_comparison.mp4",
        title="Tokyo Revengers - Mikey Evolution (Past vs Present) #shorts",
        description="Tokyo Revengers Character Comparison: Manjiro Sano (Mikey) Past vs Present.\n#tokyorevengers #mikey #anime #shorts",
        tags=["tokyo revengers", "mikey", "anime comparison"]
    )

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- KONFIGURASI ---
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'

# GANTI INI DENGAN ID FOLDER DARI URL GOOGLE DRIVE ANDA
PARENT_FOLDER_ID = '1WM5kz8tdjvb4dC2DAv9vvqk2AyHG5hnE' 

def authenticate():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds)

def upload_photo(file_path, file_name):
    try:
        service = authenticate()

        # Metadata file (Nama & Lokasi Folder)
        file_metadata = {
            'name': file_name,
            'parents': [PARENT_FOLDER_ID]
        }
        
        # Siapkan file fisik
        media = MediaFileUpload(file_path, mimetype='image/jpeg')

        # 1. Eksekusi Upload
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        file_id = file.get('id')
        
        # 2. Ubah Izin jadi "Siapa saja yang punya link bisa lihat" (Public)
        # Agar user tidak perlu login untuk download
        permission = {
            'type': 'anyone',
            'role': 'reader',
        }
        service.permissions().create(
            fileId=file_id,
            body=permission,
        ).execute()

        # 3. Ambil Link Download
        public_link = file.get('webViewLink')
        
        print(f"✅ Sukses Upload ke Drive! Link: {public_link}")
        return public_link

    except Exception as e:
        print(f"❌ Gagal Upload Google Drive: {e}")
        return None
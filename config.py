import os

class Config:
    # Configuration Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Configuration YouTube
    MAX_RETRIES = int(os.environ.get('MAX_RETRIES', '3'))
    RETRY_DELAY_MIN = float(os.environ.get('RETRY_DELAY_MIN', '1.0'))
    RETRY_DELAY_MAX = float(os.environ.get('RETRY_DELAY_MAX', '3.0'))
    
    # Configuration des téléchargements
    DOWNLOAD_FOLDER = os.environ.get('DOWNLOAD_FOLDER', 'downloads')
    MAX_DESCRIPTION_LENGTH = int(os.environ.get('MAX_DESCRIPTION_LENGTH', '500'))
    
    # Configuration Google Drive
    GOOGLE_DRIVE_ENABLED = os.environ.get('GOOGLE_DRIVE_ENABLED', 'True').lower() == 'true'
    GOOGLE_DRIVE_FOLDER_ID = os.environ.get('GOOGLE_DRIVE_FOLDER_ID', '')
    GOOGLE_DRIVE_CREDENTIALS_FILE = os.environ.get('GOOGLE_DRIVE_CREDENTIALS_FILE', 'credentials.json')
    GOOGLE_DRIVE_TOKEN_FILE = os.environ.get('GOOGLE_DRIVE_TOKEN_FILE', 'token.json')
    GOOGLE_DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    # Headers pour simuler un navigateur
    BROWSER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    # Patterns d'URL YouTube valides
    YOUTUBE_URL_PATTERNS = [
        r"^(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?$",
        r"^(https?://)?(www\.)?youtu\.be/[\w-]+(\?\S*)?$",
        r"^(https?://)?(www\.)?youtube\.com/embed/[\w-]+(\?\S*)?$"
    ] 
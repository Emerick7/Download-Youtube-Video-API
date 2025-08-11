import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.errors import HttpError
from config import Config
import tempfile

class GoogleDriveManager:
    def __init__(self):
        self.creds = None
        self.service = None
        self.folder_id = Config.GOOGLE_DRIVE_FOLDER_ID
        
    def authenticate(self):
        """Authentification avec Google Drive API"""
        try:
            # Vérifier si le fichier de token existe
            if os.path.exists(Config.GOOGLE_DRIVE_TOKEN_FILE):
                self.creds = Credentials.from_authorized_user_file(
                    Config.GOOGLE_DRIVE_TOKEN_FILE, 
                    Config.GOOGLE_DRIVE_SCOPES
                )
            
            # Si pas de credentials valides ou expirés, demander une nouvelle authentification
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(Config.GOOGLE_DRIVE_CREDENTIALS_FILE):
                        raise FileNotFoundError(
                            f"Fichier de credentials Google Drive non trouvé: {Config.GOOGLE_DRIVE_CREDENTIALS_FILE}\n"
                            "Veuillez télécharger le fichier credentials.json depuis Google Cloud Console"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        Config.GOOGLE_DRIVE_CREDENTIALS_FILE, 
                        Config.GOOGLE_DRIVE_SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Sauvegarder les credentials pour la prochaine utilisation
                with open(Config.GOOGLE_DRIVE_TOKEN_FILE, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Construire le service Google Drive
            self.service = build('drive', 'v3', credentials=self.creds)
            return True
            
        except Exception as e:
            print(f"Erreur d'authentification Google Drive: {e}")
            return False
    
    def upload_video(self, video_data, filename, mime_type='video/mp4'):
        """Upload une vidéo sur Google Drive"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False, "Échec de l'authentification Google Drive"
            
            # Créer un fichier temporaire en mémoire
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Préparer le contenu du fichier
            media = MediaIoBaseUpload(
                io.BytesIO(video_data),
                mimetype=mime_type,
                resumable=True
            )
            
            # Upload du fichier
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id,name,webViewLink'
            ).execute()
            
            file_id = file.get('id')
            web_view_link = file.get('webViewLink')
            
            return True, {
                'file_id': file_id,
                'filename': filename,
                'web_view_link': web_view_link,
                'message': f'Vidéo uploadée avec succès sur Google Drive: {filename}'
            }
            
        except HttpError as error:
            error_details = f"Erreur Google Drive API: {error}"
            print(error_details)
            return False, error_details
        except Exception as e:
            error_details = f"Erreur lors de l'upload Google Drive: {e}"
            print(error_details)
            return False, error_details
    
    def list_files(self, folder_id=None):
        """Lister les fichiers dans un dossier Google Drive"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False, "Échec de l'authentification Google Drive"
            
            folder_id = folder_id or self.folder_id
            query = f"'{folder_id}' in parents" if folder_id else ""
            
            results = self.service.files().list(
                q=query,
                pageSize=10,
                fields="nextPageToken, files(id, name, mimeType, createdTime, webViewLink)"
            ).execute()
            
            files = results.get('files', [])
            return True, files
            
        except Exception as e:
            return False, f"Erreur lors de la liste des fichiers: {e}"
    
    def get_folder_info(self):
        """Obtenir les informations du dossier de destination"""
        try:
            if not self.service:
                if not self.authenticate():
                    return False, "Échec de l'authentification Google Drive"
            
            if not self.folder_id:
                return False, "Aucun dossier Google Drive configuré"
            
            folder = self.service.files().get(
                fileId=self.folder_id,
                fields="id,name,webViewLink"
            ).execute()
            
            return True, folder
            
        except Exception as e:
            return False, f"Erreur lors de la récupération des infos du dossier: {e}"

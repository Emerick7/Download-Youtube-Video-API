from flask import Flask, request, jsonify
from pytubefix import YouTube
import re
import time
import random
import os
import requests
import json
from config import Config
from google_drive import GoogleDriveManager

app = Flask(__name__)
app.config.from_object(Config)

def get_working_user_agent():
    """Retourne un User-Agent qui fonctionne actuellement"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    return random.choice(user_agents)

TOKEN_FILE = os.path.join(os.getcwd(), 'token_youtube.json')

def load_po_token():
    """Charge visitorData et poToken depuis token_youtube.json"""
    if not os.path.exists(TOKEN_FILE):
        raise RuntimeError("token_youtube.json introuvable. Lancez renew_token.sh d'abord.")
    with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    visitor_data = data.get('visitorData')
    po_token = data.get('poToken') or data.get('po_token')
    if not visitor_data or not po_token:
        raise RuntimeError("token_youtube.json invalide (manque visitorData ou poToken)")
    return visitor_data, po_token

def create_youtube_with_headers(url):
    """Crée un objet YouTube en utilisant visitorData/poToken depuis token_youtube.json si présent.

    Priorité: WEB + use_po_token=True avec visitor_data ; fallback: ANDROID.
    """
    last_error = None
    # Tente d'utiliser token_youtube.json
    try:
        visitor_data, po_token = load_po_token()
        yt = YouTube(
            url,
            client="WEB",
            use_po_token=True,
            visitor_data=visitor_data,
            use_oauth=False,
            allow_oauth_cache=False,
            on_progress_callback=lambda s, c, b: None
        )
        return yt
    except Exception as e:
        last_error = e
        print(f"Echec YouTube(client=WEB avec token_youtube.json): {e}")

    # Fallback ANDROID sans po_token
    try:
        yt = YouTube(
            url,
            client="ANDROID",
            use_po_token=False,
            use_oauth=False,
            allow_oauth_cache=False,
            on_progress_callback=lambda s, c, b: None
        )
        return yt
    except Exception as e:
        last_error = e
        print(f"Echec YouTube(client=ANDROID): {e}")

    # Si tous les essais échouent, lever la dernière erreur
    raise last_error if last_error else RuntimeError("Impossible de créer l'objet YouTube")

def download_video(url, resolution, max_retries=None):
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
        
    for attempt in range(max_retries):
        try:
            # Ajouter un délai aléatoire entre les tentatives
            if attempt > 0:
                time.sleep(random.uniform(Config.RETRY_DELAY_MIN, Config.RETRY_DELAY_MAX))
            
            print(f"Tentative {attempt + 1}/{max_retries} pour télécharger: {url}")
            
            # Créer l'objet YouTube avec pytubefix
            yt = create_youtube_with_headers(url)
            
            # Essayer d'abord la résolution demandée
            stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=resolution).first()
            
            # Si pas trouvé, essayer une résolution inférieure
            if not stream:
                available_streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
                if available_streams:
                    stream = available_streams[0]
                    resolution = stream.resolution
                    print(f"Résolution demandée non disponible, utilisation de: {resolution}")
            
            if stream:
                # Nettoyer le nom de fichier pour éviter les caractères problématiques
                safe_title = "".join(c for c in yt.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{safe_title}_{resolution}.mp4"
                
                print(f"Téléchargement en cours: {filename}")
                
                if Config.GOOGLE_DRIVE_ENABLED:
                    print(f"Upload sur Google Drive en cours: {filename}")
                    
                    # Initialiser Google Drive Manager
                    drive_manager = GoogleDriveManager()
                    
                    # Télécharger temporairement pour l'upload
                    temp_file_path = os.path.join(Config.DOWNLOAD_FOLDER, filename)
                    os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)
                    
                    # Télécharger le fichier temporairement
                    stream.download(output_path=Config.DOWNLOAD_FOLDER, filename=filename)
                    
                    # Lire le fichier pour l'upload
                    with open(temp_file_path, 'rb') as f:
                        video_data = f.read()
                    
                    # Upload sur Google Drive
                    success, result = drive_manager.upload_video(video_data, filename)
                    
                    # Supprimer le fichier temporaire
                    try:
                        os.remove(temp_file_path)
                    except:
                        pass
                    
                    if success:
                        return True, {
                            'message': f'Vidéo téléchargée et uploadée sur Google Drive avec succès: {filename}',
                            'filename': filename,
                            'drive_info': result,
                            'resolution': resolution
                        }
                    else:
                        return False, f"Échec de l'upload Google Drive: {result}"
                else:
                    # Fallback vers téléchargement local si Google Drive est désactivé
                    os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)
                    file_path = os.path.join(Config.DOWNLOAD_FOLDER, filename)
                    
                    # Télécharger directement dans le dossier
                    stream.download(output_path=Config.DOWNLOAD_FOLDER, filename=filename)
                    
                    return True, {
                        'message': f'Video downloaded locally with resolution {resolution} as {filename}',
                        'filename': filename,
                        'resolution': resolution,
                        'file_path': file_path
                    }
            else:
                return False, "No suitable video stream found."
                
        except Exception as e:
            error_msg = str(e)
            print(f"Tentative {attempt + 1} échouée: {error_msg}")
            
            # Analyser l'erreur pour donner des conseils
            if "403" in error_msg or "Forbidden" in error_msg:
                print("   Erreur 403 détectée - YouTube bloque temporairement les requêtes")
                print("   Conseils: Attendez quelques minutes ou essayez une vidéo différente")
            elif "400" in error_msg or "Bad Request" in error_msg:
                print("   Erreur 400 détectée - Problème avec la requête YouTube")
                print("   Conseils: Vérifiez l'URL ou attendez un moment")
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                print("   Erreur 429 détectée - Trop de requêtes")
                print("   Conseils: Attendez plus longtemps avant de réessayer")
            
            # Si c'est la dernière tentative, retourner l'erreur
            if attempt == max_retries - 1:
                return False, f"Failed after {max_retries} attempts. Last error: {error_msg}"
            
            # Continuer avec la prochaine tentative
            continue
    
    return False, "Unexpected error occurred"

def get_video_info(url, max_retries=None):
    if max_retries is None:
        max_retries = Config.MAX_RETRIES
        
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(random.uniform(Config.RETRY_DELAY_MIN, Config.RETRY_DELAY_MAX))
            
            print(f"Tentative {attempt + 1}/{max_retries} pour récupérer les infos: {url}")
            
            # Créer l'objet YouTube avec pytubefix
            yt = create_youtube_with_headers(url)
            
            # Obtenir les streams disponibles
            streams = yt.streams.filter(progressive=True, file_extension='mp4')
            available_resolutions = [stream.resolution for stream in streams if stream.resolution]
            
            # Tronquer la description si elle est trop longue
            description = yt.description
            if len(description) > Config.MAX_DESCRIPTION_LENGTH:
                description = description[:Config.MAX_DESCRIPTION_LENGTH] + "..."
            
            video_info = {
                "title": yt.title,
                "author": yt.author,
                "length": yt.length,
                "views": yt.views,
                "description": description,
                "publish_date": str(yt.publish_date) if yt.publish_date else None,
                "available_resolutions": list(set(available_resolutions)),
                "thumbnail_url": yt.thumbnail_url,
                "video_id": yt.video_id,
            }
            return video_info, None
            
        except Exception as e:
            error_msg = str(e)
            print(f"Tentative {attempt + 1} échouée: {error_msg}")
            
            # Analyser l'erreur pour donner des conseils
            if "403" in error_msg or "Forbidden" in error_msg:
                print("   Erreur 403 détectée - YouTube bloque temporairement les requêtes")
            elif "400" in error_msg or "Bad Request" in error_msg:
                print("   Erreur 400 détectée - Problème avec la requête YouTube")
            elif "429" in error_msg or "Too Many Requests" in error_msg:
                print("   Erreur 429 détectée - Trop de requêtes")
            
            if attempt == max_retries - 1:
                return None, f"Failed after {max_retries} attempts. Last error: {error_msg}"
            continue
    
    return None, "Unexpected error occurred"

def is_valid_youtube_url(url):
    return any(re.match(pattern, url) for pattern in Config.YOUTUBE_URL_PATTERNS)

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
            
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

        if not is_valid_youtube_url(url):
            return jsonify({"error": "Invalid YouTube URL."}), 400
        
        success, result = download_video(url, resolution)
        
        if success:
            # Si result est un dictionnaire, l'utiliser directement
            if isinstance(result, dict):
                return jsonify(result), 200
            # Si result est une string, l'encapsuler dans un dictionnaire
            else:
                return jsonify({"message": result}), 200
        else:
            return jsonify({"error": result}), 500
            
    except Exception as e:
        print(f"Unexpected error in download endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/video_info', methods=['POST'])
def video_info():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be valid JSON"}), 400
            
        url = data.get('url')
        
        if not url:
            return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

        if not is_valid_youtube_url(url):
            return jsonify({"error": "Invalid YouTube URL."}), 400
        
        video_info, error_message = get_video_info(url)
        
        if video_info:
            return jsonify(video_info), 200
        else:
            return jsonify({"error": error_message}), 500
            
    except Exception as e:
        print(f"Unexpected error in video_info endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy", 
        "message": "YouTube Download API is running (pytubefix + Google Drive)",
        "config": {
            "max_retries": Config.MAX_RETRIES,
            "download_folder": Config.DOWNLOAD_FOLDER,
            "debug_mode": Config.DEBUG,
            "library": "pytubefix 9.4.1",
            "token_youtube_present": os.path.exists(TOKEN_FILE),
            "token_youtube_mtime": (os.path.getmtime(TOKEN_FILE) if os.path.exists(TOKEN_FILE) else None),
            "google_drive": {
                "enabled": Config.GOOGLE_DRIVE_ENABLED,
                "folder_id": Config.GOOGLE_DRIVE_FOLDER_ID if Config.GOOGLE_DRIVE_FOLDER_ID else "Non configuré"
            }
        }
    }), 200

@app.route('/available_resolutions/<video_id>', methods=['GET'])
def get_available_resolutions(video_id):
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        video_info, error_message = get_video_info(url)
        
        if video_info:
            return jsonify({
                "video_id": video_id,
                "title": video_info["title"],
                "available_resolutions": video_info["available_resolutions"]
            }), 200
        else:
            return jsonify({"error": error_message}), 500
            
    except Exception as e:
        print(f"Unexpected error in available_resolutions endpoint: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route('/troubleshoot', methods=['GET'])
def troubleshoot():
    """Endpoint pour diagnostiquer les problèmes courants"""
    return jsonify({
        "common_errors": {
            "HTTP Error 403: Forbidden": {
                "description": "YouTube bloque temporairement les requêtes",
                "solutions": [
                    "Attendez 5-10 minutes avant de réessayer",
                    "Essayez une vidéo différente",
                    "Vérifiez que l'URL est accessible dans un navigateur",
                    "L'erreur peut être temporaire",
                    "pytubefix devrait mieux gérer ces erreurs"
                ]
            },
            "HTTP Error 400: Bad Request": {
                "description": "Problème avec la requête YouTube",
                "solutions": [
                    "Vérifiez que l'URL est valide",
                    "Assurez-vous que la vidéo n'est pas privée",
                    "Essayez de copier l'URL directement depuis YouTube",
                    "pytubefix a une meilleure gestion des erreurs"
                ]
            },
            "HTTP Error 429: Too Many Requests": {
                "description": "Trop de requêtes envoyées",
                "solutions": [
                    "Attendez 15-30 minutes avant de réessayer",
                    "Réduisez la fréquence des requêtes",
                    "Utilisez l'endpoint /health pour vérifier le statut"
                ]
            }
        },
        "tips": [
            "L'API utilise maintenant pytubefix (plus robuste que pytube)",
            "Retry logic avec délais aléatoires",
            "Les erreurs 403/400 sont souvent temporaires",
            "Essayez différentes résolutions si une échoue",
            "Vérifiez les logs de l'API pour plus de détails"
        ],
        "library_info": {
            "current": "pytubefix 9.4.1",
            "previous": "pytube 15.0.0",
            "improvements": [
                "Meilleure gestion des erreurs YouTube",
                "Headers de navigateur intégrés",
                "Gestion améliorée des restrictions",
                "Support des dernières versions de Python"
            ]
        },
        "google_drive": {
            "enabled": Config.GOOGLE_DRIVE_ENABLED,
            "status": "Configuré et prêt" if Config.GOOGLE_DRIVE_ENABLED else "Désactivé"
        }
    }), 200

@app.route('/drive/status', methods=['GET'])
def drive_status():
    """Vérifier le statut de Google Drive"""
    try:
        if not Config.GOOGLE_DRIVE_ENABLED:
            return jsonify({
                "enabled": False,
                "message": "Google Drive est désactivé dans la configuration"
            }), 200
        
        drive_manager = GoogleDriveManager()
        auth_result = drive_manager.authenticate()
        
        if auth_result:
            folder_result = drive_manager.get_folder_info()
            if folder_result[0]:  # folder_result est un tuple (success, data)
                return jsonify({
                    "enabled": True,
                    "authenticated": True,
                    "folder_info": folder_result[1],
                    "message": "Google Drive connecté avec succès"
                }), 200
            else:
                return jsonify({
                    "enabled": True,
                    "authenticated": True,
                    "folder_warning": "Authentification réussie mais dossier non configuré",
                    "message": "Utilisez GOOGLE_DRIVE_FOLDER_ID pour spécifier un dossier"
                }), 200
        else:
            return jsonify({
                "enabled": True,
                "authenticated": False,
                "error": "Échec de l'authentification Google Drive",
                "message": "Vérifiez vos credentials et redémarrez l'API"
            }), 500
            
    except Exception as e:
        return jsonify({
            "enabled": Config.GOOGLE_DRIVE_ENABLED,
            "error": str(e),
            "message": "Erreur lors de la vérification du statut Google Drive"
        }), 500

@app.route('/drive/files', methods=['GET'])
def list_drive_files():
    """Lister les fichiers dans le dossier Google Drive configuré"""
    try:
        if not Config.GOOGLE_DRIVE_ENABLED:
            return jsonify({"error": "Google Drive est désactivé"}), 400
        
        drive_manager = GoogleDriveManager()
        files_result = drive_manager.list_files()
        
        if files_result[0]:  # files_result est un tuple (success, data)
            files = files_result[1]
            return jsonify({
                "files": files,
                "count": len(files),
                "message": "Fichiers récupérés avec succès"
            }), 200
        else:
            return jsonify({"error": files_result[1]}), 500
            
    except Exception as e:
        return jsonify({"error": f"Erreur lors de la liste des fichiers: {str(e)}"}), 500

if __name__ == '__main__':
    # Créer le dossier de téléchargement au démarrage (fallback)
    if not Config.GOOGLE_DRIVE_ENABLED:
        os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)
    
    print(f"Starting YouTube Download API with pytubefix + Google Drive...")
    print(f"Google Drive: {'Activé' if Config.GOOGLE_DRIVE_ENABLED else 'Désactivé'}")
    if Config.GOOGLE_DRIVE_ENABLED:
        print(f"Google Drive Folder ID: {Config.GOOGLE_DRIVE_FOLDER_ID or 'Non configuré'}")
        print(f"Credentials file: {Config.GOOGLE_DRIVE_CREDENTIALS_FILE}")
    else:
        print(f"Download folder (fallback): {Config.DOWNLOAD_FOLDER}")
    print(f"Max retries: {Config.MAX_RETRIES}")
    print(f"Debug mode: {Config.DEBUG}")
    print(f"Library: pytubefix 9.4.1")
    print(f"User-Agent: {get_working_user_agent()}")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)

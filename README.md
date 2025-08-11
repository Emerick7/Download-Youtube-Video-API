# YouTube Video Download API + Google Drive

Une API Flask robuste pour télécharger des vidéos YouTube directement sur **Google Drive** avec **pytubefix**, gestion des erreurs et retry logic.

## 🚀 Fonctionnalités

- **Téléchargement de vidéos** directement sur **Google Drive** (plus de stockage local !)
- **Informations sur les vidéos** (titre, auteur, durée, etc.)
- **Gestion robuste des erreurs** avec retry logic
- **pytubefix** : Alternative moderne et robuste à pytube
- **Validation d'URL** flexible
- **Configuration centralisée** via variables d'environnement
- **Mode fallback** : Téléchargement local si Google Drive est désactivé
- **Gestion des dossiers** Google Drive avec organisation automatique

## 🔄 Migration de pytube vers pytubefix

Cette API utilise maintenant **pytubefix** au lieu de pytube pour une meilleure fiabilité :

- ✅ **Meilleure gestion des erreurs 403/400**
- ✅ **Headers de navigateur intégrés**
- ✅ **Gestion améliorée des restrictions YouTube**
- ✅ **Support des dernières versions de Python**
- ✅ **Maintenance active et mises à jour régulières**

## 📋 Prérequis

- Python 3.7+
- pip

## 🛠️ Installation

1. **Cloner le repository :**
```bash
git clone <votre-repo>
cd "Download Youtube Video API"
```

2. **Installer les dépendances :**
```bash
pip install -r requirements.txt
```

3. **Lancer l'API :**
```bash
python main.py
```

L'API sera accessible sur `http://localhost:5000`

## 🔧 Configuration

Vous pouvez configurer l'API via des variables d'environnement :

```bash
# Nombre de tentatives en cas d'échec
export MAX_RETRIES=5

# Délai entre les tentatives (en secondes)
export RETRY_DELAY_MIN=2.0
export RETRY_DELAY_MAX=5.0

# Dossier de téléchargement
export DOWNLOAD_FOLDER=my_downloads

# Mode debug
export FLASK_DEBUG=False

# Configuration Google Drive
export GOOGLE_DRIVE_ENABLED=True
export GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
export GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
export GOOGLE_DRIVE_TOKEN_FILE=token.json
```

## 🚀 Configuration Google Drive

### Prérequis
1. **Projet Google Cloud** avec API Google Drive activée
2. **Fichier credentials.json** téléchargé depuis Google Cloud Console
3. **Dossier Google Drive** créé avec ID récupéré

### Configuration rapide
1. **Suivez le guide complet** : `GUIDE_GOOGLE_DRIVE.md`
2. **Créez un fichier `.env`** avec vos paramètres
3. **Placez `credentials.json`** dans le dossier racine
4. **Redémarrez l'API**

### Vérification
```bash
# Vérifier le statut Google Drive
curl http://localhost:5000/drive/status

# Lister les fichiers
curl http://localhost:5000/drive/files
```

## 📡 Endpoints

### 1. Télécharger une vidéo
**POST** `/download/<resolution>`

**Body :**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Exemple de réponse :**
```json
{
    "message": "Video downloaded successfully with resolution 720p as Ma_Video_720p.mp4"
}
```

### 2. Obtenir les informations d'une vidéo
**POST** `/video_info`

**Body :**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

**Exemple de réponse :**
```json
{
    "title": "Titre de la vidéo",
    "author": "Nom de l'auteur",
    "length": 120,
    "views": 1000,
    "description": "Description de la vidéo...",
    "publish_date": "2024-01-01",
    "available_resolutions": ["720p", "480p", "360p"],
    "thumbnail_url": "https://...",
    "video_id": "VIDEO_ID"
}
```

### 3. Vérifier le statut de l'API
**GET** `/health`

**Exemple de réponse :**
```json
{
    "status": "healthy",
    "message": "YouTube Download API is running (pytubefix)",
    "config": {
        "max_retries": 3,
        "download_folder": "downloads",
        "debug_mode": true,
        "library": "pytubefix 9.4.1"
    }
}
```

### 4. Obtenir les résolutions disponibles
**GET** `/available_resolutions/<video_id>`

**Exemple de réponse :**
```json
{
    "video_id": "VIDEO_ID",
    "title": "Titre de la vidéo",
    "available_resolutions": ["720p", "480p", "360p"]
}
```

### 5. Diagnostic et dépannage
**GET** `/troubleshoot`

Retourne des informations détaillées sur les erreurs courantes et les solutions, incluant les avantages de pytubefix.

### 6. Statut Google Drive
**GET** `/drive/status`

Vérifie la connexion et l'authentification Google Drive.

**Exemple de réponse :**
```json
{
    "enabled": true,
    "authenticated": true,
    "folder_info": {
        "id": "1ABC123DEF456GHI789JKL",
        "name": "Vidéos YouTube",
        "webViewLink": "https://drive.google.com/drive/folders/1ABC123DEF456GHI789JKL"
    },
    "message": "Google Drive connecté avec succès"
}
```

### 7. Lister les fichiers Google Drive
**GET** `/drive/files`

Liste les fichiers dans le dossier Google Drive configuré.

**Exemple de réponse :**
```json
{
    "files": [
        {
            "id": "1ABC123DEF456GHI789JKL",
            "name": "Ma_Video_720p.mp4",
            "mimeType": "video/mp4",
            "createdTime": "2024-01-01T12:00:00.000Z",
            "webViewLink": "https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view"
        }
    ],
    "count": 1,
    "message": "Fichiers récupérés avec succès"
}
```

## 🔍 Résolution des problèmes

### Erreur 500 "HTTP Error 400: Bad Request" ou "HTTP Error 403: Forbidden"

Ces erreurs sont courantes avec les bibliothèques YouTube. **pytubefix** améliore significativement la gestion de ces erreurs :

1. **Headers de navigateur** : pytubefix simule un navigateur moderne
2. **Retry logic** : Tentatives multiples avec délais aléatoires
3. **Gestion des restrictions** : Meilleure gestion des blocages YouTube
4. **Messages d'erreur** : Diagnostics détaillés pour identifier les problèmes

### Solutions supplémentaires

Si l'erreur persiste :

1. **Vérifiez l'URL** : Assurez-vous qu'elle est valide et accessible
2. **Attendez un moment** : YouTube peut temporairement bloquer les requêtes
3. **Changez la résolution** : Essayez une résolution différente
4. **Utilisez le diagnostic** : `python diagnostic.py`

## 📁 Structure des fichiers

```
Download Youtube Video API/
├── main.py                 # API principale avec pytubefix + Google Drive
├── google_drive.py         # Gestionnaire Google Drive
├── config.py               # Configuration centralisée
├── requirements.txt        # Dépendances Python (pytubefix + Google Drive)
├── README.md              # Documentation
├── test_api.py            # Script de test basique
├── test_google_drive.py   # Script de test Google Drive
├── diagnostic.py          # Script de diagnostic avancé
├── GUIDE_RESOLUTION.md    # Guide de résolution des problèmes
├── GUIDE_GOOGLE_DRIVE.md  # Guide de configuration Google Drive
├── env_example.txt        # Exemple de variables d'environnement
├── .gitignore             # Protection des fichiers sensibles
├── credentials.json       # Credentials Google Drive (à télécharger)
├── token.json            # Token d'accès (généré automatiquement)
└── downloads/            # Dossier de fallback (si Google Drive désactivé)
```

## 🧪 Test de l'API

### Script de test automatique
```bash
# Test complet de l'API
python test_api.py

# Test Google Drive
python test_google_drive.py

# Diagnostic avancé
python diagnostic.py
```

### Avec curl

```bash
# Télécharger une vidéo
curl -X POST http://localhost:5000/download/720p \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# Obtenir les informations
curl -X POST http://localhost:5000/video_info \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=VIDEO_ID"}'

# Vérifier le statut
curl http://localhost:5000/health

# Diagnostic
curl http://localhost:5000/troubleshoot
```

### Avec Postman

1. Créez une nouvelle requête POST
2. URL : `http://localhost:5000/download/720p`
3. Headers : `Content-Type: application/json`
4. Body (raw JSON) :
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## 🆚 pytube vs pytubefix

| Fonctionnalité | pytube | pytubefix |
|----------------|---------|-----------|
| Gestion erreurs 403 | ❌ Basique | ✅ Améliorée |
| Gestion erreurs 400 | ❌ Basique | ✅ Améliorée |
| Headers navigateur | ❌ Manuel | ✅ Intégrés |
| Maintenance | ⚠️ Limitée | ✅ Active |
| Python 3.13+ | ❌ Non | ✅ Oui |
| Performance | ⚠️ Moyenne | ✅ Meilleure |

## ⚠️ Limitations

- L'API respecte les conditions d'utilisation de YouTube
- Certaines vidéos peuvent être protégées ou non disponibles
- La vitesse de téléchargement dépend de votre connexion internet
- YouTube peut modifier ses systèmes de protection

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Signaler des bugs
2. Proposer des améliorations
3. Soumettre des pull requests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

Si vous rencontrez des problèmes :

1. **Vérifiez les logs** de l'API
2. **Testez avec l'endpoint** `/health`
3. **Utilisez le diagnostic** : `python diagnostic.py`
4. **Vérifiez que l'URL YouTube** est valide
5. **Consultez le guide** : `GUIDE_RESOLUTION.md`

## 🎯 Avantages de pytubefix

- **Meilleure fiabilité** : Moins d'erreurs 403/400
- **Maintenance active** : Mises à jour régulières
- **Support moderne** : Python 3.7+ et dernières fonctionnalités
- **Gestion des erreurs** : Messages d'erreur plus clairs
- **Performance** : Téléchargements plus rapides et fiables

## 🚀 Avantages de Google Drive

- **Pas de stockage local** : Économise l'espace disque
- **Accès partout** : Vos vidéos sont accessibles depuis n'importe où
- **Partage facile** : Partagez les vidéos avec des liens directs
- **Sauvegarde automatique** : Vos vidéos sont sauvegardées dans le cloud
- **Organisation** : Créez des dossiers organisés pour vos vidéos
- **Mode fallback** : Téléchargement local si Google Drive est indisponible

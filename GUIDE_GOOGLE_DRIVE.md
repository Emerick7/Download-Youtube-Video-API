# 🚀 Guide de Configuration Google Drive - API YouTube

## 📋 Vue d'Ensemble

Votre API YouTube a été modifiée pour télécharger directement les vidéos sur **Google Drive** au lieu du stockage local ! 🎉

### ✨ Avantages de Google Drive
- **Pas de stockage local** : Économise l'espace disque
- **Accès partout** : Vos vidéos sont accessibles depuis n'importe où
- **Partage facile** : Partagez les vidéos avec des liens directs
- **Sauvegarde automatique** : Vos vidéos sont sauvegardées dans le cloud
- **Organisation** : Créez des dossiers organisés pour vos vidéos

## 🔧 Configuration Étape par Étape

### Étape 1: Créer un Projet Google Cloud

1. **Allez sur [Google Cloud Console](https://console.cloud.google.com/)**
2. **Créez un nouveau projet** ou sélectionnez un projet existant
3. **Activez l'API Google Drive** :
   - Menu → APIs & Services → Library
   - Recherchez "Google Drive API"
   - Cliquez sur "Enable"

### Étape 2: Créer des Credentials

1. **Dans votre projet Google Cloud** :
   - Menu → APIs & Services → Credentials
   - Cliquez sur "Create Credentials" → "OAuth 2.0 Client IDs"

2. **Configurez l'écran de consentement** :
   - Application type : "Desktop application"
   - Nom : "YouTube Download API"
   - Description : "API pour télécharger des vidéos YouTube sur Google Drive"

3. **Téléchargez le fichier JSON** :
   - Cliquez sur "Download JSON"
   - Renommez-le en `credentials.json`
   - Placez-le dans le dossier racine de votre projet

### Étape 3: Créer un Dossier Google Drive

1. **Allez sur [Google Drive](https://drive.google.com/)**
2. **Créez un nouveau dossier** (ex: "Vidéos YouTube")
3. **Récupérez l'ID du dossier** :
   - Ouvrez le dossier
   - L'URL sera : `https://drive.google.com/drive/folders/FOLDER_ID`
   - Copiez le `FOLDER_ID` (partie après `/folders/`)

### Étape 4: Configurer les Variables d'Environnement

Créez un fichier `.env` dans votre projet avec ce contenu :

```bash
# Configuration Google Drive
GOOGLE_DRIVE_ENABLED=True
GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789JKL
GOOGLE_DRIVE_CREDENTIALS_FILE=credentials.json
GOOGLE_DRIVE_TOKEN_FILE=token.json

# Configuration YouTube (optionnel)
MAX_RETRIES=3
RETRY_DELAY_MIN=1.0
RETRY_DELAY_MAX=3.0

# Configuration Flask (optionnel)
FLASK_DEBUG=False
```

**⚠️ Important** : Remplacez `1ABC123DEF456GHI789JKL` par votre vrai ID de dossier !

## 🚀 Première Utilisation

### 1. Installer les Dépendances
```bash
pip install -r requirements.txt
```

### 2. Démarrer l'API
```bash
python main.py
```

### 3. Première Authentification
Lors du premier démarrage :
1. **Un navigateur s'ouvrira automatiquement**
2. **Connectez-vous avec votre compte Google**
3. **Autorisez l'accès** à Google Drive
4. **Fermez le navigateur** une fois autorisé

### 4. Vérifier la Configuration
```bash
# Vérifier le statut Google Drive
curl http://localhost:5000/drive/status

# Vérifier la santé de l'API
curl http://localhost:5000/health
```

## 📱 Utilisation de l'API

### Télécharger une Vidéo sur Google Drive
```bash
curl -X POST http://localhost:5000/download/720p \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

### Vérifier les Fichiers sur Google Drive
```bash
# Lister les fichiers
curl http://localhost:5000/drive/files

# Statut Google Drive
curl http://localhost:5000/drive/status
```

## 🔍 Dépannage

### Problème : "Fichier credentials.json non trouvé"
**Solution** : Vérifiez que le fichier `credentials.json` est dans le dossier racine

### Problème : "Échec de l'authentification"
**Solution** : 
1. Supprimez le fichier `token.json`
2. Redémarrez l'API
3. Réautorisez l'accès

### Problème : "Dossier non configuré"
**Solution** : Vérifiez que `GOOGLE_DRIVE_FOLDER_ID` est correct dans votre `.env`

### Problème : "Quota dépassé"
**Solution** : 
- Google Drive a des limites de quota
- Attendez 24h ou utilisez un autre compte

## 📊 Structure des Réponses

### Succès de Téléchargement
```json
{
  "message": "Vidéo téléchargée et uploadée sur Google Drive avec succès: Nom_Video_720p.mp4",
  "drive_info": {
    "file_id": "1ABC123DEF456GHI789JKL",
    "filename": "Nom_Video_720p.mp4",
    "web_view_link": "https://drive.google.com/file/d/1ABC123DEF456GHI789JKL/view",
    "message": "Vidéo uploadée avec succès sur Google Drive: Nom_Video_720p.mp4"
  },
  "resolution": "720p"
}
```

### Statut Google Drive
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

## 🔒 Sécurité

### Fichiers Sensibles
- **`credentials.json`** : Contient vos clés API (ne partagez jamais !)
- **`token.json`** : Contient vos tokens d'accès (généré automatiquement)

### Bonnes Pratiques
1. **Ne committez jamais** `credentials.json` ou `.env` dans Git
2. **Utilisez `.gitignore`** pour exclure ces fichiers
3. **Limitez les permissions** de votre projet Google Cloud
4. **Surveillez l'utilisation** dans Google Cloud Console

## 📁 Organisation des Fichiers

### Structure Recommandée
```
Votre_Projet/
├── main.py                 # API principale
├── google_drive.py         # Gestionnaire Google Drive
├── config.py               # Configuration
├── credentials.json        # Credentials Google (à télécharger)
├── .env                    # Variables d'environnement (à créer)
├── token.json             # Token d'accès (généré automatiquement)
└── downloads/             # Dossier de fallback (si Google Drive désactivé)
```

## 🎯 Fonctionnalités Avancées

### Mode Fallback
Si Google Drive est désactivé, l'API télécharge localement dans le dossier `downloads/`

### Gestion des Erreurs
- **Authentification échouée** : Messages d'erreur clairs
- **Quota dépassé** : Détection automatique
- **Dossier non trouvé** : Vérification de l'ID

### Monitoring
- **Endpoint `/drive/status`** : Vérifier la connexion
- **Endpoint `/drive/files`** : Lister les fichiers
- **Logs détaillés** : Suivre les uploads

## 🚀 Prochaines Étapes

Une fois configuré, vous pourrez :
1. **Télécharger des vidéos** directement sur Google Drive
2. **Partager les liens** avec d'autres personnes
3. **Organiser vos vidéos** dans des dossiers
4. **Accéder à vos vidéos** depuis n'importe où

## 📞 Support

Si vous rencontrez des problèmes :
1. **Vérifiez les logs** de l'API
2. **Testez l'endpoint** `/drive/status`
3. **Vérifiez votre configuration** Google Cloud
4. **Consultez la documentation** Google Drive API

**🎉 Félicitations ! Votre API YouTube est maintenant connectée à Google Drive !**

#!/usr/bin/env python3
"""
Script de test pour l'intégration Google Drive
Teste la connexion et les fonctionnalités de base
"""

import requests
import json
import sys
import time

def test_api_health():
    """Tester la santé de l'API"""
    print("🔍 Test de la santé de l'API...")
    try:
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API en ligne: {data['message']}")
            print(f"   Google Drive: {data['config']['google_drive']['enabled']}")
            if data['config']['google_drive']['enabled']:
                folder_id = data['config']['google_drive']['folder_id']
                print(f"   Dossier ID: {folder_id}")
            return True
        else:
            print(f"❌ API non accessible: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API (port 5000)")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test de santé: {e}")
        return False

def test_google_drive_status():
    """Tester le statut Google Drive"""
    print("\n🔍 Test du statut Google Drive...")
    try:
        response = requests.get("http://localhost:5000/drive/status")
        if response.status_code == 200:
            data = response.json()
            if data['enabled']:
                if data['authenticated']:
                    print("✅ Google Drive connecté avec succès")
                    if 'folder_info' in data:
                        print(f"   Dossier: {data['folder_info']['name']}")
                        print(f"   Lien: {data['folder_info']['webViewLink']}")
                    else:
                        print("   ⚠️  Dossier non configuré")
                else:
                    print("❌ Échec de l'authentification Google Drive")
                    print(f"   Erreur: {data.get('error', 'Inconnue')}")
            else:
                print("ℹ️  Google Drive désactivé")
            return data['enabled'] and data.get('authenticated', False)
        else:
            print(f"❌ Erreur lors du test du statut: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test du statut: {e}")
        return False

def test_google_drive_files():
    """Tester la liste des fichiers Google Drive"""
    print("\n🔍 Test de la liste des fichiers...")
    try:
        response = requests.get("http://localhost:5000/drive/files")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['count']} fichiers trouvés")
            for file in data['files'][:5]:  # Afficher les 5 premiers
                print(f"   📁 {file['name']} ({file['mimeType']})")
            if data['count'] > 5:
                print(f"   ... et {data['count'] - 5} autres fichiers")
            return True
        else:
            print(f"❌ Erreur lors de la liste des fichiers: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la liste des fichiers: {e}")
        return False

def test_video_info():
    """Tester la récupération d'informations vidéo"""
    print("\n🔍 Test de récupération d'informations vidéo...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll
    
    try:
        response = requests.post(
            "http://localhost:5000/video_info",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Informations vidéo récupérées: {data['title']}")
            print(f"   Auteur: {data['author']}")
            print(f"   Durée: {data['length']} secondes")
            print(f"   Résolutions disponibles: {', '.join(data['available_resolutions'])}")
            return True
        else:
            print(f"❌ Erreur lors de la récupération des infos: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test des infos vidéo: {e}")
        return False

def test_download_to_drive():
    """Tester le téléchargement sur Google Drive"""
    print("\n🔍 Test de téléchargement sur Google Drive...")
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll
    
    try:
        print("   Téléchargement en cours (cela peut prendre quelques minutes)...")
        response = requests.post(
            "http://localhost:5000/download/360p",
            json={"url": test_url},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Téléchargement réussi !")
            if 'drive_info' in data:
                drive_info = data['drive_info']
                print(f"   Fichier: {drive_info['filename']}")
                print(f"   ID Google Drive: {drive_info['file_id']}")
                print(f"   Lien: {drive_info['web_view_link']}")
            else:
                print(f"   Message: {data['message']}")
            return True
        else:
            error_data = response.json()
            print(f"❌ Erreur lors du téléchargement: {response.status_code}")
            print(f"   Erreur: {error_data.get('error', 'Inconnue')}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test de téléchargement: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de l'intégration Google Drive - API YouTube")
    print("=" * 60)
    
    # Vérifier que l'API est en ligne
    if not test_api_health():
        print("\n❌ L'API n'est pas accessible. Assurez-vous qu'elle est démarrée sur le port 5000.")
        sys.exit(1)
    
    # Tests Google Drive
    drive_working = test_google_drive_status()
    
    if drive_working:
        print("\n✅ Google Drive est configuré et fonctionnel !")
        
        # Test de la liste des fichiers
        test_google_drive_files()
        
        # Test des informations vidéo
        test_video_info()
        
        # Demander si l'utilisateur veut tester le téléchargement
        print("\n" + "=" * 60)
        response = input("Voulez-vous tester le téléchargement d'une vidéo sur Google Drive ? (o/n): ")
        
        if response.lower() in ['o', 'oui', 'y', 'yes']:
            test_download_to_drive()
        else:
            print("   Test de téléchargement ignoré.")
    else:
        print("\n❌ Google Drive n'est pas configuré ou ne fonctionne pas.")
        print("   Consultez le guide GUIDE_GOOGLE_DRIVE.md pour la configuration.")
    
    print("\n" + "=" * 60)
    print("🏁 Tests terminés !")
    
    if drive_working:
        print("🎉 Votre API YouTube est prête à télécharger sur Google Drive !")
    else:
        print("🔧 Configurez Google Drive pour profiter de toutes les fonctionnalités.")

if __name__ == "__main__":
    main()

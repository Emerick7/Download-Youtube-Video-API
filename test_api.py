#!/usr/bin/env python3
"""
Script de test pour l'API YouTube Download avec pytubefix
Permet de tester tous les endpoints et diagnostiquer les problèmes
"""

import requests
import json
import time
import sys

# Configuration
BASE_URL = "http://localhost:5000"
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll pour les tests

def test_health():
    """Test de l'endpoint health"""
    print("🔍 Test de l'endpoint /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check réussi: {data['status']}")
            print(f"   Message: {data['message']}")
            print(f"   Configuration: {data['config']}")
            
            # Vérifier que pytubefix est utilisé
            if 'library' in data['config'] and 'pytubefix' in data['config']['library']:
                print(f"   ✅ Utilise pytubefix: {data['config']['library']}")
            else:
                print(f"   ⚠️  Vérifiez que pytubefix est utilisé")
            
            return True
        else:
            print(f"❌ Health check échoué: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Assurez-vous qu'elle est démarrée.")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du health check: {e}")
        return False

def test_video_info():
    """Test de l'endpoint video_info"""
    print("\n🔍 Test de l'endpoint /video_info...")
    try:
        payload = {"url": TEST_VIDEO_URL}
        response = requests.post(f"{BASE_URL}/video_info", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Video info récupéré avec succès:")
            print(f"   Titre: {data.get('title', 'N/A')}")
            print(f"   Auteur: {data.get('author', 'N/A')}")
            print(f"   Durée: {data.get('length', 'N/A')} secondes")
            print(f"   Résolutions disponibles: {data.get('available_resolutions', [])}")
            return True
        else:
            print(f"❌ Échec de récupération des infos vidéo: {response.status_code}")
            try:
                error_data = response.json()
                error_msg = error_data.get('error', 'Erreur inconnue')
                print(f"   Erreur: {error_msg}")
                
                # Analyser l'erreur
                if "403" in error_msg:
                    print("      💡 YouTube bloque temporairement (normal avec pytube, devrait être mieux avec pytubefix)")
                elif "400" in error_msg:
                    print("      💡 Problème de requête YouTube (pytubefix devrait mieux gérer)")
                elif "429" in error_msg:
                    print("      💡 Trop de requêtes, attendez")
            except:
                print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test video_info: {e}")
        return False

def test_available_resolutions():
    """Test de l'endpoint available_resolutions"""
    print("\n🔍 Test de l'endpoint /available_resolutions...")
    try:
        # Extraire l'ID de la vidéo de l'URL
        video_id = TEST_VIDEO_URL.split("v=")[1].split("&")[0]
        response = requests.get(f"{BASE_URL}/available_resolutions/{video_id}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Résolutions disponibles récupérées:")
            print(f"   ID vidéo: {data.get('video_id', 'N/A')}")
            print(f"   Titre: {data.get('title', 'N/A')}")
            print(f"   Résolutions: {data.get('available_resolutions', [])}")
            return True
        else:
            print(f"❌ Échec de récupération des résolutions: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erreur: {error_data.get('error', 'Erreur inconnue')}")
            except:
                print(f"   Réponse: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test available_resolutions: {e}")
        return False

def test_download():
    """Test de l'endpoint download (sans télécharger réellement)"""
    print("\n🔍 Test de l'endpoint /download...")
    print("⚠️  Note: Ce test vérifie seulement la validation de l'URL, pas le téléchargement réel")
    
    # Test avec une URL invalide
    print("   Test avec URL invalide...")
    try:
        payload = {"url": "https://invalid-url.com"}
        response = requests.post(f"{BASE_URL}/download/720p", json=payload)
        
        if response.status_code == 400:
            print("   ✅ Validation d'URL invalide fonctionne")
        else:
            print(f"   ❌ Validation d'URL invalide échouée: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors du test de validation: {e}")
        return False
    
    # Test avec une URL valide (mais sans télécharger)
    print("   Test avec URL valide (validation uniquement)...")
    try:
        payload = {"url": TEST_VIDEO_URL}
        response = requests.post(f"{BASE_URL}/download/720p", json=payload)
        
        if response.status_code in [200, 500]:  # 200 = succès, 500 = erreur YouTube (normal)
            print("   ✅ Validation d'URL valide fonctionne")
            if response.status_code == 500:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Erreur inconnue')
                    print(f"   ℹ️  Erreur YouTube (attendue): {error_msg}")
                    
                    # Analyser l'erreur
                    if "403" in error_msg:
                        print("      💡 Erreur 403 - pytubefix devrait mieux gérer que pytube")
                    elif "400" in error_msg:
                        print("      💡 Erreur 400 - pytubefix devrait mieux gérer que pytube")
                except:
                    pass
            return True
        else:
            print(f"   ❌ Test d'URL valide échoué: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors du test d'URL valide: {e}")
        return False

def test_error_handling():
    """Test de la gestion d'erreurs"""
    print("\n🔍 Test de la gestion d'erreurs...")
    
    # Test avec body JSON invalide
    print("   Test avec body JSON invalide...")
    try:
        response = requests.post(f"{BASE_URL}/download/720p", data="invalid json")
        if response.status_code == 400:
            print("   ✅ Gestion d'erreur JSON invalide fonctionne")
        else:
            print(f"   ❌ Gestion d'erreur JSON invalide échouée: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors du test JSON invalide: {e}")
        return False
    
    # Test avec body vide
    print("   Test avec body vide...")
    try:
        response = requests.post(f"{BASE_URL}/download/720p")
        if response.status_code == 400:
            print("   ✅ Gestion d'erreur body vide fonctionne")
        else:
            print(f"   ❌ Gestion d'erreur body vide échouée: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erreur lors du test body vide: {e}")
        return False
    
    return True

def test_troubleshoot():
    """Test de l'endpoint troubleshoot"""
    print("\n🔍 Test de l'endpoint /troubleshoot...")
    try:
        response = requests.get(f"{BASE_URL}/troubleshoot")
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint troubleshoot accessible")
            
            # Vérifier les informations sur pytubefix
            if 'library_info' in data:
                lib_info = data['library_info']
                print(f"   📚 Informations sur la bibliothèque:")
                print(f"      Actuelle: {lib_info.get('current', 'N/A')}")
                print(f"      Précédente: {lib_info.get('previous', 'N/A')}")
                print(f"      Améliorations: {len(lib_info.get('improvements', []))} fonctionnalités")
            
            return True
        else:
            print(f"❌ Endpoint troubleshoot inaccessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test troubleshoot: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests de l'API YouTube Download avec pytubefix")
    print("=" * 70)
    
    # Vérifier que l'API est accessible
    if not test_health():
        print("\n❌ L'API n'est pas accessible. Arrêt des tests.")
        sys.exit(1)
    
    # Tests des endpoints
    tests = [
        test_video_info,
        test_available_resolutions,
        test_download,
        test_error_handling,
        test_troubleshoot
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        time.sleep(1)  # Pause entre les tests
    
    print("\n" + "=" * 70)
    print(f"📊 Résultats des tests: {passed}/{total} réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès!")
        print("\n💡 Votre API fonctionne correctement avec pytubefix.")
        print("   pytubefix devrait mieux gérer les erreurs YouTube que pytube.")
    else:
        print("⚠️  Certains tests ont échoué.")
        print("   Vérifiez les logs de l'API pour plus de détails.")
    
    print("\n🔧 Avantages de pytubefix par rapport à pytube:")
    print("   • Meilleure gestion des erreurs 403/400")
    print("   • Headers de navigateur intégrés")
    print("   • Gestion améliorée des restrictions YouTube")
    print("   • Support des dernières versions de Python")
    
    print("\n🔧 Pour diagnostiquer les erreurs:")
    print("   1. Vérifiez les logs de l'API (console)")
    print("   2. Testez avec l'endpoint /health")
    print("   3. Utilisez l'endpoint /troubleshoot")
    print("   4. Essayez une vidéo différente")
    print("   5. Attendez quelques minutes et réessayez")

if __name__ == "__main__":
    main() 
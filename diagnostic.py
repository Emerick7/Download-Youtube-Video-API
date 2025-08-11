#!/usr/bin/env python3
"""
Script de diagnostic avancé pour l'API YouTube Download avec pytubefix
Analyse les problèmes et propose des solutions
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)

def print_section(title):
    """Affiche une section formatée"""
    print(f"\n📋 {title}")
    print("-" * 40)

def test_api_connectivity():
    """Test de connectivité de base"""
    print_section("Test de connectivité de base")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ API accessible")
            print(f"   Statut: {data['status']}")
            print(f"   Message: {data['message']}")
            print(f"   Configuration: {data['config']}")
            
            # Vérifier que pytubefix est utilisé
            if 'library' in data['config'] and 'pytubefix' in data['config']['library']:
                print(f"   ✅ Utilise pytubefix: {data['config']['library']}")
            else:
                print(f"   ⚠️  Vérifiez que pytubefix est utilisé")
            
            return True
        else:
            print(f"❌ API accessible mais erreur: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("   Vérifiez que l'API est démarrée sur le port 5000")
        return False
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_youtube_accessibility():
    """Test d'accessibilité YouTube avec pytubefix"""
    print_section("Test d'accessibilité YouTube (pytubefix)")
    
    # Test avec une vidéo publique connue
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo (première vidéo YouTube)
        "https://www.youtube.com/watch?v=9bZkp7q19f0"   # Gangnam Style
    ]
    
    working_urls = []
    
    for i, url in enumerate(test_urls, 1):
        print(f"   Test {i}/3: {url}")
        try:
            response = requests.post(f"{BASE_URL}/video_info", 
                                  json={"url": url}, 
                                  timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"      ✅ Succès - Titre: {data.get('title', 'N/A')}")
                working_urls.append(url)
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', 'Erreur inconnue')
                    print(f"      ❌ Échec - {error_msg}")
                    
                    # Analyser l'erreur avec pytubefix
                    if "403" in error_msg:
                        print("         💡 YouTube bloque temporairement")
                        print("         🔧 pytubefix devrait mieux gérer que pytube")
                    elif "400" in error_msg:
                        print("         💡 Problème de requête YouTube")
                        print("         🔧 pytubefix devrait mieux gérer que pytube")
                    elif "429" in error_msg:
                        print("         💡 Trop de requêtes, attendez")
                except:
                    print(f"      ❌ Échec - Code: {response.status_code}")
            
            # Pause entre les tests
            if i < len(test_urls):
                time.sleep(2)
                
        except Exception as e:
            print(f"      ❌ Erreur: {e}")
    
    if working_urls:
        print(f"\n✅ {len(working_urls)} URL(s) fonctionnent")
        print("   🎉 pytubefix fonctionne mieux que pytube!")
        return True
    else:
        print(f"\n❌ Aucune URL ne fonctionne")
        print("   💡 pytubefix devrait améliorer la situation par rapport à pytube")
        print("   🔧 Attendez quelques minutes et réessayez")
        return False

def analyze_error_patterns():
    """Analyse des patterns d'erreur"""
    print_section("Analyse des patterns d'erreur")
    
    # Tester différents types d'erreurs
    error_tests = [
        {"name": "URL invalide", "url": "https://invalid-url.com", "expected": 400},
        {"name": "Body JSON invalide", "data": "invalid json", "expected": 400},
        {"name": "Body vide", "data": None, "expected": 400},
        {"name": "Paramètre manquant", "json": {}, "expected": 400}
    ]
    
    for test in error_tests:
        print(f"   Test: {test['name']}")
        try:
            if test['name'] == "URL invalide":
                response = requests.post(f"{BASE_URL}/download/720p", 
                                      json={"url": test['url']})
            elif test['name'] == "Body JSON invalide":
                response = requests.post(f"{BASE_URL}/download/720p", 
                                      data=test['data'])
            elif test['name'] == "Body vide":
                response = requests.post(f"{BASE_URL}/download/720p")
            elif test['name'] == "Paramètre manquant":
                response = requests.post(f"{BASE_URL}/download/720p", 
                                      json=test['json'])
            
            if response.status_code == test['expected']:
                print(f"      ✅ Comportement attendu: {response.status_code}")
            else:
                print(f"      ❌ Comportement inattendu: {response.status_code} (attendu: {test['expected']})")
                
        except Exception as e:
            print(f"      ❌ Erreur de test: {e}")

def get_troubleshooting_info():
    """Récupère les informations de dépannage"""
    print_section("Informations de dépannage (pytubefix)")
    
    try:
        response = requests.get(f"{BASE_URL}/troubleshoot")
        if response.status_code == 200:
            data = response.json()
            
            print("📚 Erreurs courantes et solutions:")
            for error, info in data['common_errors'].items():
                print(f"\n   🚨 {error}")
                print(f"      Description: {info['description']}")
                print("      Solutions:")
                for solution in info['solutions']:
                    print(f"         • {solution}")
            
            print(f"\n💡 Conseils généraux:")
            for tip in data['tips']:
                print(f"   • {tip}")
            
            # Informations sur pytubefix
            if 'library_info' in data:
                lib_info = data['library_info']
                print(f"\n📚 Informations sur la bibliothèque:")
                print(f"   Actuelle: {lib_info.get('current', 'N/A')}")
                print(f"   Précédente: {lib_info.get('previous', 'N/A')}")
                print(f"   Améliorations:")
                for improvement in lib_info.get('improvements', []):
                    print(f"      • {improvement}")
        else:
            print(f"❌ Impossible de récupérer les infos de dépannage: {response.status_code}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des infos: {e}")

def test_pytubefix_specific_features():
    """Test des fonctionnalités spécifiques à pytubefix"""
    print_section("Test des fonctionnalités pytubefix")
    
    try:
        # Test de l'endpoint health pour vérifier pytubefix
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            if 'library' in data['config'] and 'pytubefix' in data['config']['library']:
                print("✅ pytubefix détecté et configuré")
                print(f"   Version: {data['config']['library']}")
                
                # Test de l'endpoint troubleshoot
                troubleshoot_response = requests.get(f"{BASE_URL}/troubleshoot")
                if troubleshoot_response.status_code == 200:
                    troubleshoot_data = troubleshoot_response.json()
                    if 'library_info' in troubleshoot_data:
                        print("✅ Endpoint troubleshoot avec infos pytubefix accessible")
                        return True
                    else:
                        print("⚠️  Endpoint troubleshoot accessible mais sans infos pytubefix")
                        return False
                else:
                    print("❌ Endpoint troubleshoot inaccessible")
                    return False
            else:
                print("❌ pytubefix non détecté dans la configuration")
                return False
        else:
            print(f"❌ Impossible de vérifier pytubefix: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test pytubefix: {e}")
        return False

def generate_report():
    """Génère un rapport de diagnostic"""
    print_section("Génération du rapport")
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = {
        "timestamp": timestamp,
        "api_url": BASE_URL,
        "tests": {}
    }
    
    # Test de connectivité
    connectivity_ok = test_api_connectivity()
    report["tests"]["connectivity"] = connectivity_ok
    
    if connectivity_ok:
        # Test pytubefix
        pytubefix_ok = test_pytubefix_specific_features()
        report["tests"]["pytubefix"] = pytubefix_ok
        
        # Test YouTube
        youtube_ok = test_youtube_accessibility()
        report["tests"]["youtube"] = youtube_ok
        
        # Analyse des erreurs
        analyze_error_patterns()
        
        # Informations de dépannage
        get_troubleshooting_info()
    
    # Recommandations
    print_section("Recommandations")
    
    if not connectivity_ok:
        print("🔧 Actions immédiates:")
        print("   1. Vérifiez que l'API est démarrée: python main.py")
        print("   2. Vérifiez le port 5000 n'est pas utilisé par un autre service")
        print("   3. Vérifiez les logs de l'API")
    
    elif not report.get("tests", {}).get("pytubefix", False):
        print("🔧 Actions recommandées:")
        print("   1. Vérifiez que pytubefix est installé: pip install pytubefix")
        print("   2. Redémarrez l'API après l'installation")
        print("   3. Vérifiez que pytube est désinstallé: pip uninstall pytube")
    
    elif not report.get("tests", {}).get("youtube", False):
        print("🔧 Actions recommandées:")
        print("   1. Attendez 5-10 minutes avant de réessayer")
        print("   2. Essayez une vidéo différente")
        print("   3. pytubefix devrait améliorer la situation par rapport à pytube")
        print("   4. Vérifiez votre connexion internet")
    
    else:
        print("🎉 L'API fonctionne parfaitement avec pytubefix!")
        print("   Vous pouvez maintenant télécharger des vidéos")
    
    print(f"\n📊 Rapport généré le: {timestamp}")
    return report

def main():
    """Fonction principale"""
    print_header("DIAGNOSTIC AVANCÉ - API YouTube Download avec pytubefix")
    print(f"🔗 URL de l'API: {BASE_URL}")
    print(f"⏰ Démarrage: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📚 Bibliothèque: pytubefix (remplace pytube)")
    
    try:
        report = generate_report()
        
        print_header("RÉSUMÉ DU DIAGNOSTIC")
        print("Tests effectués:")
        for test_name, result in report["tests"].items():
            status = "✅ RÉUSSI" if result else "❌ ÉCHOUÉ"
            print(f"   • {test_name}: {status}")
        
        print(f"\n📋 Rapport complet disponible dans la console ci-dessus")
        
        # Résumé des améliorations pytubefix
        print(f"\n🚀 Améliorations apportées par pytubefix:")
        print("   • Meilleure gestion des erreurs YouTube")
        print("   • Headers de navigateur intégrés")
        print("   • Gestion améliorée des restrictions")
        print("   • Support des dernières versions de Python")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrompu par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur lors du diagnostic: {e}")
        print("   Vérifiez que l'API est accessible et redémarrez le diagnostic")

if __name__ == "__main__":
    main() 
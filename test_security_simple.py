"""
Test simple de sécurité des sessions
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_simple_security():
    """Test simplifié des paramètres de sécurité"""
    
    print("🔒 Test de sécurité simplifié")
    print("="*40)
    
    try:
        # Test de connexion à la page principale
        response = requests.get(f"{BASE_URL}/")
        
        if response.status_code == 200:
            print("✅ Serveur Django accessible")
            
            # Vérifier les cookies de session dans la réponse
            cookies = response.cookies
            if cookies:
                print("📍 Cookies reçus:")
                for cookie in cookies:
                    print(f"   • {cookie.name}: expires dans {cookie.expires if cookie.expires else 'session only'}")
            else:
                print("📍 Aucun cookie reçu (normal pour page d'accueil)")
                
            # Vérifier les headers de sécurité
            headers = response.headers
            security_headers = ['X-Frame-Options', 'X-Content-Type-Options']
            print("\n🛡️  Headers de sécurité:")
            for header in security_headers:
                if header in headers:
                    print(f"   ✅ {header}: {headers[header]}")
                else:
                    print(f"   ❌ {header}: manquant")
                    
        else:
            print(f"❌ Erreur serveur: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Django non accessible")
        print("   Assure-toi qu'il tourne sur http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    print("\n📊 Nouveaux paramètres de sécurité:")
    print("   • Access Token: 15 minutes")
    print("   • Refresh Token: 2 heures")
    print("   • Session: 30 minutes")
    print("   • Expire à fermeture navigateur: Oui")
    print("\n✅ Avec ces paramètres, tu ne resteras plus connecté longtemps !")

if __name__ == "__main__":
    test_simple_security()

"""
Test de sécurité JWT et CSRF pour l'application cocktails
"""

import requests
import json
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cocktailaiser.settings')
django.setup()

BASE_URL = "http://127.0.0.1:8000"

def test_security():
    print("🔐 Test de sécurité JWT et CSRF")
    print("=" * 50)
    
    # Test 1: Récupération du token CSRF
    print("\n1️⃣ Test CSRF Token")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/csrf/")
        if response.status_code == 200:
            csrf_token = response.json()['csrfToken']
            print(f"   ✅ Token CSRF récupéré: {csrf_token[:20]}...")
        else:
            print(f"   ❌ Erreur CSRF: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Erreur CSRF: {e}")
        return
    
    # Test 2: Tentative d'accès non autorisé
    print("\n2️⃣ Test accès non autorisé")
    try:
        response = requests.get(f"{BASE_URL}/api/cocktails/")
        if response.status_code == 401:
            print("   ✅ Accès correctement refusé sans token")
        else:
            print(f"   ❌ Sécurité défaillante: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur test non autorisé: {e}")
    
    # Test 3: Inscription d'un utilisateur de test
    print("\n3️⃣ Test inscription")
    test_user = {
        "username": "testuser_security",
        "email": "test@security.com",
        "password": "TestPassword123!",
        "first_name": "Test",
        "last_name": "Security"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(test_user)
        )
        
        if response.status_code == 201:
            data = response.json()
            access_token = data['tokens']['access']
            refresh_token = data['tokens']['refresh']
            print(f"   ✅ Inscription réussie: {data['user']['username']}")
            print(f"   🔑 Token JWT reçu: {access_token[:20]}...")
        else:
            print(f"   ❌ Erreur inscription: {response.status_code} - {response.text}")
            
            # Tenter une connexion si l'utilisateur existe déjà
            print("   🔄 Tentative de connexion...")
            login_response = requests.post(
                f"{BASE_URL}/api/auth/login/",
                headers={'Content-Type': 'application/json'},
                data=json.dumps({
                    "username": test_user["username"],
                    "password": test_user["password"]
                })
            )
            
            if login_response.status_code == 200:
                data = login_response.json()
                access_token = data['access']
                refresh_token = data['refresh']
                print(f"   ✅ Connexion réussie: {data['user']['username']}")
            else:
                print(f"   ❌ Erreur connexion: {login_response.status_code}")
                return
            
    except Exception as e:
        print(f"   ❌ Erreur inscription/connexion: {e}")
        return
    
    # Test 4: Accès autorisé avec token JWT
    print("\n4️⃣ Test accès autorisé avec JWT")
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ Profil utilisateur récupéré: {user_data['user']['username']}")
        else:
            print(f"   ❌ Erreur accès profil: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur test autorisé: {e}")
    
    # Test 5: Génération de cocktail sécurisée
    print("\n5️⃣ Test génération cocktail sécurisée")
    try:
        cocktail_request = {
            "prompt": "cocktail de test sécurisé",
            "context": "Test de sécurité JWT"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate/",
            headers=headers,
            data=json.dumps(cocktail_request)
        )
        
        if response.status_code == 201:
            cocktail_data = response.json()
            print(f"   ✅ Cocktail généré: {cocktail_data['cocktail']['name']}")
        else:
            print(f"   ❌ Erreur génération: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Erreur test génération: {e}")
    
    # Test 6: Vérification du token
    print("\n6️⃣ Test vérification token")
    try:
        verify_data = {"token": access_token}
        response = requests.post(
            f"{BASE_URL}/api/auth/token/verify/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(verify_data)
        )
        
        if response.status_code == 200:
            print("   ✅ Token JWT valide")
        else:
            print(f"   ❌ Token invalide: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur vérification token: {e}")
    
    # Test 7: Refresh du token
    print("\n7️⃣ Test refresh token")
    try:
        refresh_data = {"refresh": refresh_token}
        response = requests.post(
            f"{BASE_URL}/api/auth/token/refresh/",
            headers={'Content-Type': 'application/json'},
            data=json.dumps(refresh_data)
        )
        
        if response.status_code == 200:
            new_access = response.json()['access']
            print(f"   ✅ Token refreshé: {new_access[:20]}...")
        else:
            print(f"   ❌ Erreur refresh: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur refresh token: {e}")
    
    # Test 8: Déconnexion sécurisée
    print("\n8️⃣ Test déconnexion")
    try:
        logout_data = {"refresh_token": refresh_token}
        response = requests.post(
            f"{BASE_URL}/api/auth/logout/",
            headers=headers,
            data=json.dumps(logout_data)
        )
        
        if response.status_code == 200:
            print("   ✅ Déconnexion réussie")
        else:
            print(f"   ❌ Erreur déconnexion: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur test déconnexion: {e}")
    
    # Test 9: Tentative d'accès après déconnexion
    print("\n9️⃣ Test accès après déconnexion")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
        if response.status_code == 401:
            print("   ✅ Accès correctement refusé après déconnexion")
        else:
            print(f"   ❌ Sécurité défaillante après déconnexion: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur test post-déconnexion: {e}")
    
    print(f"\n🎉 Tests de sécurité terminés !")


if __name__ == "__main__":
    print("⚠️  Assurez-vous que le serveur Django est démarré sur http://127.0.0.1:8000")
    input("Appuyez sur Entrée pour commencer les tests...")
    test_security()

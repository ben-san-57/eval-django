"""
Test de sécurité des sessions
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_session_security():
    """Test des paramètres de sécurité de session"""
    
    print("🔒 Test de sécurité des sessions Django")
    print("="*50)
    
    # 1. Connexion
    login_data = {
        "username": "admin",  # Remplace par ton username
        "password": "admin123"  # Remplace par ton mot de passe
    }
    
    try:
        print("1. Tentative de connexion...")
        response = requests.post(f"{BASE_URL}/api/auth/login/", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get('access')
            print(f"   ✅ Connexion réussie pour: {data.get('user', {}).get('username')}")
            
            # 2. Vérifier les paramètres de sécurité
            headers = {"Authorization": f"Bearer {access_token}"}
            security_response = requests.get(f"{BASE_URL}/api/auth/session-security/", headers=headers)
            
            if security_response.status_code == 200:
                security_info = security_response.json()
                print("\n2. Paramètres de sécurité actuels:")
                print(f"   • Durée session: {security_info['session_cookie_age']} secondes ({security_info['session_cookie_age']//3600}h)")
                print(f"   • Expire à fermeture navigateur: {security_info['session_expire_at_browser_close']}")
                print(f"   • Renouvellement à chaque requête: {security_info['session_save_every_request']}")
                print(f"   • Durée token JWT access: {security_info['jwt_access_token_lifetime']}")
                print(f"   • Durée token JWT refresh: {security_info['jwt_refresh_token_lifetime']}")
                print(f"   • Clé de session: {security_info['session_key']}")
                
                # 3. Test de déconnexion forcée
                print("\n3. Test de déconnexion forcée de toutes les sessions...")
                logout_response = requests.post(f"{BASE_URL}/api/auth/force-logout-all/", headers=headers)
                
                if logout_response.status_code == 200:
                    logout_data = logout_response.json()
                    print(f"   ✅ {logout_data['message']}")
                    
                    # 4. Vérifier que le token n'est plus valide
                    print("\n4. Vérification que le token est invalidé...")
                    test_response = requests.get(f"{BASE_URL}/api/auth/profile/", headers=headers)
                    
                    if test_response.status_code == 401:
                        print("   ✅ Token correctement invalidé")
                    else:
                        print("   ⚠️  Token encore actif")
                else:
                    print(f"   ❌ Erreur lors de la déconnexion: {logout_response.text}")
            else:
                print(f"   ❌ Erreur accès sécurité: {security_response.text}")
        else:
            print(f"   ❌ Erreur de connexion: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur Django")
        print("   Assure-toi que le serveur tourne sur http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_session_security()

#!/usr/bin/env python3
"""Script para testar login via API HTTP."""

import requests
import json

def test_api_login():
    """Testa login via API HTTP."""
    url = "http://localhost:8000/auth/token"
    username = "digomes"
    password = "E@#$%^&12(),.?\":{}|<!a"
    
    print(f"Testando login via API:")
    print(f"URL: {url}")
    print(f"Usuário: '{username}'")
    print(f"Senha: '{password}'")
    print(f"Comprimento da senha: {len(password)} caracteres")
    print()
    
    # Dados do formulário
    data = {
        'username': username,
        'password': password
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        print("Enviando requisição...")
        response = requests.post(url, data=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        if response.status_code == 200:
            print("\n✅ LOGIN BEM-SUCEDIDO via API!")
            if 'access_token' in response_json:
                print(f"Token recebido: {response_json['access_token'][:50]}...")
        else:
            print(f"\n❌ FALHA NO LOGIN via API")
            print(f"Código de erro: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Não foi possível conectar ao servidor")
        print("Verifique se o backend está rodando na porta 8000")
    except Exception as e:
        print(f"❌ ERRO inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_login()
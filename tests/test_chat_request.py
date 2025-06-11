#!/usr/bin/env python3
"""
Script para testar o endpoint de chat e reproduzir o erro 422
"""
import requests
import json
from datetime import datetime

def test_chat_endpoint():
    """Testa o endpoint de chat com diferentes payloads"""
    
    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/api/chat"
    
    print(f"🧪 Testando endpoint: {endpoint}")
    print(f"⏰ Timestamp: {datetime.now()}")
    print("-" * 50)
    
    # Teste 1: Payload que estava causando erro
    test_cases = [
        {
            "name": "Payload Original (string user_id)",
            "payload": {
                "user_id": "123", 
                "message": "Lumi, como está minha agenda hoje?",
                "context": {}
            }
        },
        {
            "name": "Payload com user_id como int",
            "payload": {
                "user_id": 123,
                "message": "Lumi, como está minha agenda hoje?", 
                "context": {}
            }
        },
        {
            "name": "Payload sem context",
            "payload": {
                "user_id": 123,
                "message": "Oi Lumi!"
            }
        },
        {
            "name": "Payload com context como string (formato antigo)",
            "payload": {
                "user_id": 123,
                "message": "Como estou indo hoje?",
                "context": "agenda_today"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Teste {i}: {test_case['name']}")
        print(f"📤 Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            response = requests.post(
                endpoint,
                json=test_case['payload'],
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'TestClient/1.0'
                },
                timeout=30
            )
            
            print(f"📈 Status Code: {response.status_code}")
            print(f"📋 Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Sucesso!")
                response_data = response.json()
                print(f"📝 Response: {json.dumps(response_data, indent=2)}")
            else:
                print(f"❌ Erro {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"📝 Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"📝 Raw Response: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"🔥 Erro de conexão: {e}")
        except Exception as e:
            print(f"🔥 Erro inesperado: {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_chat_endpoint()

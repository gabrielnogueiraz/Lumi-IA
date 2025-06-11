#!/usr/bin/env python3
"""
Teste específico para identificar o problema do frontend
"""
import requests
import json

def test_frontend_issue():
    """Testa especificamente o problema que o frontend está enfrentando"""
    
    url = "http://localhost:5000/api/chat"
    
    # Teste que deve funcionar
    valid_payload = {
        "user_id": 123,  # Como número
        "message": "Oi Lumi!"
    }
    
    print("🧪 Testando com user_id válido como número:")
    print(f"📤 Payload: {json.dumps(valid_payload, indent=2)}")
    
    try:
        response = requests.post(url, json=valid_payload, timeout=10)
        print(f"📈 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Sucesso!")
            print(f"📝 Resposta: {data['response'][:100]}...")
        else:
            print(f"❌ Erro {response.status_code}")
            try:
                error = response.json()
                print(f"📝 Erro: {json.dumps(error, indent=2)}")
            except:
                print(f"📝 Raw: {response.text}")
                
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")

if __name__ == "__main__":
    test_frontend_issue()

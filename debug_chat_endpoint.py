#!/usr/bin/env python3
"""
Script para debugar o endpoint /api/chat da Lumi API
"""

import requests
import json

# Configuração
API_BASE = "http://localhost:5000"
CHAT_ENDPOINT = f"{API_BASE}/api/chat"

def test_chat_endpoint():
    """Testa diferentes variações de payload para identificar o problema"""
    
    print("🔍 DEBUGANDO ENDPOINT /api/chat")
    print("=" * 50)
    
    # Teste 1: Payload mínimo válido
    print("\n📋 Teste 1: Payload mínimo válido")
    payload1 = {
        "userId": "test_user_123",
        "message": "Olá Lumi!"
    }
    
    test_request(payload1, "Payload mínimo")
    
    # Teste 2: Payload completo como esperado pelo PomodoroTasks
    print("\n📋 Teste 2: Payload completo PomodoroTasks")
    payload2 = {
        "userId": "user_456", 
        "message": "Como está meu jardim hoje?",
        "context": {
            "currentTasks": [],
            "recentPomodoros": 0,
            "flowersEarned": {"green": 2, "orange": 1, "red": 0, "purple": 0}
        },
        "action": "chat",
        "session_id": "session_789"
    }
    
    test_request(payload2, "Payload completo")
    
    # Teste 3: Payload com campos faltando
    print("\n📋 Teste 3: Payload sem userId (deve dar erro 400)")
    payload3 = {
        "message": "Teste sem userId"
    }
    
    test_request(payload3, "Sem userId")
    
    # Teste 4: Payload com message vazia
    print("\n📋 Teste 4: Payload com message vazia (deve dar erro 400)")
    payload4 = {
        "userId": "user_test",
        "message": ""
    }
    
    test_request(payload4, "Message vazia")
    
    # Teste 5: Payload com tipos incorretos
    print("\n📋 Teste 5: Payload com tipos incorretos")
    payload5 = {
        "userId": 123,  # Número ao invés de string
        "message": "Teste com tipos incorretos"
    }
    
    test_request(payload5, "Tipos incorretos")


def test_request(payload, description):
    """Executa uma requisição de teste"""
    print(f"\n🧪 {description}:")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            CHAT_ENDPOINT,
            json=payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"   Response: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   Response Text: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERRO: Não foi possível conectar ao servidor")
        print("   💡 Certifique-se de que a API está rodando em http://localhost:5001")
    except requests.exceptions.Timeout:
        print("   ❌ ERRO: Timeout na requisição")
    except Exception as e:
        print(f"   ❌ ERRO: {e}")


def check_server_status():
    """Verifica se o servidor está rodando"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        print(f"✅ Servidor rodando - Status: {response.status_code}")
        return True
    except:
        print("❌ Servidor não está rodando ou não responde")
        return False


if __name__ == "__main__":
    print("🚀 Iniciando debug do endpoint /api/chat")
    
    # Verifica se servidor está ativo
    if not check_server_status():
        print("\n💡 Para iniciar o servidor:")
        print("   cd c:\\Users\\Indica\\Documents\\workstation\\lumi-AI\\src")
        print("   python lumi_api.py")
        exit(1)
    
    # Executa testes
    test_chat_endpoint()
    
    print("\n" + "=" * 50)
    print("🏁 Debug concluído!")

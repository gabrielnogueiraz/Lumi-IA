#!/usr/bin/env python3
"""
Script para testar correção do erro 'dict object is not callable'
"""
import requests
import json
from datetime import datetime

def test_error_handling():
    """Testa os error handlers corrigidos"""
    
    base_url = "http://localhost:5000"
    endpoint = f"{base_url}/api/chat"
    
    print(f"🧪 Testando Error Handlers Corrigidos")
    print(f"⏰ Timestamp: {datetime.now()}")
    print("-" * 60)
    
    # Casos de teste para diferentes tipos de erro
    test_cases = [
        {
            "name": "user_id como 'None' (string)",
            "payload": {
                "user_id": "None",
                "message": "Olá Lumi"
            },
            "expected_status": 400,
            "expected_error": "user_id é obrigatório"
        },
        {
            "name": "user_id como string vazia",
            "payload": {
                "user_id": "",
                "message": "Olá Lumi"
            },
            "expected_status": 400,
            "expected_error": "user_id é obrigatório"
        },
        {
            "name": "user_id como 'null'",
            "payload": {
                "user_id": "null",
                "message": "Olá Lumi"
            },
            "expected_status": 400,
            "expected_error": "user_id é obrigatório"
        },
        {
            "name": "user_id como 'undefined'",
            "payload": {
                "user_id": "undefined",
                "message": "Olá Lumi"
            },
            "expected_status": 400,
            "expected_error": "user_id é obrigatório"
        },
        {
            "name": "user_id como número negativo",
            "payload": {
                "user_id": "-1",
                "message": "Olá Lumi"
            },
            "expected_status": 400,
            "expected_error": "número positivo"
        },
        {
            "name": "user_id como zero",
            "payload": {
                "user_id": "0",
                "message": "Olá Lumi"
            },
            "expected_status": 400,
            "expected_error": "número positivo"
        },
        {
            "name": "user_id válido",
            "payload": {
                "user_id": "123",
                "message": "Olá Lumi"
            },
            "expected_status": 200,
            "expected_error": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Teste {i}: {test_case['name']}")
        print(f"📤 Payload: {json.dumps(test_case['payload'], indent=2)}")
        print(f"📋 Status esperado: {test_case['expected_status']}")
        
        try:
            response = requests.post(
                endpoint,
                json=test_case['payload'],
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'ErrorTestClient/1.0'
                },
                timeout=10
            )
            
            print(f"📈 Status recebido: {response.status_code}")
            
            # Verificar se o status está correto
            if response.status_code == test_case['expected_status']:
                print("✅ Status correto!")
            else:
                print(f"❌ Status incorreto! Esperado {test_case['expected_status']}, recebido {response.status_code}")
            
            # Verificar se a resposta é JSON válido (não mais 'dict object is not callable')
            try:
                response_data = response.json()
                print("✅ Resposta JSON válida (error handler funcionando)")
                
                # Se é um erro esperado, verificar conteúdo
                if test_case['expected_status'] >= 400 and test_case['expected_error']:
                    error_message = response_data.get("error", {}).get("message", "")
                    if test_case['expected_error'] in error_message:
                        print(f"✅ Mensagem de erro correta: {error_message}")
                    else:
                        print(f"❌ Mensagem de erro incorreta: {error_message}")
                
                # Se é sucesso, mostrar resposta
                elif test_case['expected_status'] == 200:
                    print(f"✅ Resposta de sucesso: {response_data.get('response', 'N/A')[:50]}...")
                
            except json.JSONDecodeError:
                print("❌ Resposta não é JSON válido!")
                print(f"📝 Raw Response: {response.text[:200]}...")
                
        except requests.exceptions.RequestException as e:
            print(f"🔥 Erro de conexão: {e}")
        except Exception as e:
            print(f"🔥 Erro inesperado: {e}")
        
        print("-" * 60)

    print(f"\n🎯 Teste concluído!")

if __name__ == "__main__":
    test_error_handling()

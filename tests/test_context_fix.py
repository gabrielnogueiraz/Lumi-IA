#!/usr/bin/env python3
"""
Teste específico para validar a correção do erro 422 com context
"""
import requests
import json

def test_context_formats():
    """Testa diferentes formatos de context"""
    
    endpoint = "http://localhost:5000/api/chat"
    
    print("🧪 Testando correção do erro 422 - Context Formats")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Context como string (formato antigo) - CORRIGIDO",
            "payload": {
                "user_id": 123,
                "message": "Como estou indo hoje?",
                "context": "agenda_today"
            },
            "expected_status": 200
        },
        {
            "name": "Context como dict vazio",
            "payload": {
                "user_id": 123,
                "message": "Oi Lumi!",
                "context": {}
            },
            "expected_status": 200
        },
        {
            "name": "Context como dict com dados",
            "payload": {
                "user_id": 123,
                "message": "Preciso de ajuda",
                "context": {"page": "dashboard", "last_action": "view_tasks"}
            },
            "expected_status": 200
        },
        {
            "name": "Context como null/None",
            "payload": {
                "user_id": 123,
                "message": "Olá!",
                "context": None
            },
            "expected_status": 200
        },
        {
            "name": "Sem campo context",
            "payload": {
                "user_id": 123,
                "message": "Testando sem context"
            },
            "expected_status": 200
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Teste {i}: {test_case['name']}")
        print(f"📤 Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            response = requests.post(
                endpoint,
                json=test_case['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            actual_status = response.status_code
            expected_status = test_case['expected_status']
            
            print(f"📈 Status: {actual_status} (esperado: {expected_status})")
            
            if actual_status == expected_status:
                print("✅ PASSOU!")
                success_count += 1
                
                if actual_status == 200:
                    response_data = response.json()
                    print(f"📝 Response: {response_data.get('response', 'N/A')[:100]}...")
            else:
                print(f"❌ FALHOU! Status {actual_status} != {expected_status}")
                if actual_status != 200:
                    try:
                        error_data = response.json()
                        print(f"📝 Error: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"📝 Raw Response: {response.text}")
                        
        except Exception as e:
            print(f"🔥 Erro na requisição: {e}")
        
        print("-" * 50)
    
    print(f"\n📊 RESUMO: {success_count}/{len(test_cases)} testes passaram")
    
    if success_count == len(test_cases):
        print("🎉 TODOS OS TESTES PASSARAM! Erro 422 corrigido!")
    else:
        print("⚠️  Alguns testes falharam. Verificar logs acima.")

if __name__ == "__main__":
    test_context_formats()

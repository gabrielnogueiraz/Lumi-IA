#!/usr/bin/env python3
"""
🧪 TESTE AVANÇADO DA LUMI - VERIFICAÇÃO COMPLETA
Testa criação de tarefas, memória de conversa e inteligência adaptativa
"""
import requests
import json
import time
from datetime import datetime

def test_conversation_memory_and_task_creation():
    """Teste completo de memória e criação de tarefas"""
    
    print("🧪 TESTE COMPLETO DA LUMI - VERSÃO MELHORADA")
    print("=" * 70)
    print(f"Timestamp: {datetime.now()}")
    print("=" * 70)
    
    base_url = "http://localhost:5000"
    user_id = "550e8400-e29b-41d4-a716-446655440000"  # UUID válido para teste
    
    # Aguardar servidor inicializar
    print("⏳ Aguardando servidor inicializar...")
    time.sleep(3)
    
    # Teste 1: Apresentação e nome do usuário
    print("\n🧪 Teste 1: Apresentação e captura de nome")
    print("=" * 50)
    
    response1 = make_chat_request(base_url, user_id, "Olá! Meu nome é João e estou começando a usar o sistema")
    print(f"✅ Resposta 1: {response1.get('content', 'Erro')[:100]}...")
    
    # Aguardar um pouco entre requisições
    time.sleep(1)
    
    # Teste 2: Criação de tarefa com horário específico
    print("\n🧪 Teste 2: Criação de tarefa inteligente")
    print("=" * 50)
    
    response2 = make_chat_request(base_url, user_id, "Preciso estudar Python hoje às 18:30")
    print(f"✅ Resposta 2: {response2.get('content', 'Erro')[:100]}...")
    
    # Verificar se tarefa foi criada
    task_created = "tarefa" in response2.get('content', '').lower() and "python" in response2.get('content', '').lower()
    print(f"📋 Tarefa criada: {'✅ SIM' if task_created else '❌ NÃO'}")
    
    # Aguardar um pouco
    time.sleep(1)
    
    # Teste 3: Verificação de memória de nome
    print("\n🧪 Teste 3: Teste de memória de nome")
    print("=" * 50)
    
    response3 = make_chat_request(base_url, user_id, "Você lembra qual é o meu nome?")
    print(f"✅ Resposta 3: {response3.get('content', 'Erro')[:150]}...")
    
    # Verificar se a Lumi lembrou do nome
    remembers_name = "joão" in response3.get('content', '').lower()
    print(f"🧠 Lembrou do nome: {'✅ SIM' if remembers_name else '❌ NÃO'}")
    
    # Aguardar um pouco
    time.sleep(1)
    
    # Teste 4: Consulta de agenda
    print("\n🧪 Teste 4: Consulta de agenda/tarefas")
    print("=" * 50)
    
    response4 = make_chat_request(base_url, user_id, "Como está minha agenda para hoje?")
    print(f"✅ Resposta 4: {response4.get('content', 'Erro')[:150]}...")
    
    # Verificar se menciona a tarefa criada
    mentions_python_task = "python" in response4.get('content', '').lower()
    print(f"📅 Menciona tarefa Python: {'✅ SIM' if mentions_python_task else '❌ NÃO'}")
    
    # Teste 5: Inteligência contextual
    print("\n🧪 Teste 5: Inteligência contextual")
    print("=" * 50)
    
    response5 = make_chat_request(base_url, user_id, "Como você me ajudaria a ser mais produtivo?")
    print(f"✅ Resposta 5: {response5.get('content', 'Erro')[:150]}...")
    
    # Verificar se a resposta é personalizada e não robótica
    is_personalized = len(response5.get('content', '')) > 50 and not response5.get('content', '').startswith("Olá!")
    print(f"🤖 Resposta personalizada: {'✅ SIM' if is_personalized else '❌ NÃO'}")
    
    # Relatório final
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 30)
    
    results = {
        'memory_capture': remembers_name,
        'task_creation': task_created,
        'agenda_awareness': mentions_python_task,
        'personalized_response': is_personalized
    }
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 EXCELENTE! Lumi está funcionando perfeitamente!")
    elif passed_tests >= total_tests * 0.75:
        print("👍 BOM! Lumi está funcionando bem, com pequenas melhorias necessárias.")
    elif passed_tests >= total_tests * 0.5:
        print("⚠️  RAZOÁVEL. Lumi precisa de mais ajustes.")
    else:
        print("❌ CRÍTICO. Lumi precisa de correções importantes.")
    
    return results

def make_chat_request(base_url, user_id, message):
    """Faz uma requisição para o chat da Lumi"""
    try:
        payload = {
            "user_id": user_id,
            "message": message
        }
        
        print(f"📤 Enviando: {message}")
        
        response = requests.post(
            f"{base_url}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📋 Status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro HTTP {response.status_code}: {response.text}")
            return {"content": f"Erro HTTP {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        print("🔥 Erro de conexão: Servidor não está rodando")
        return {"content": "Erro de conexão"}
    except requests.exceptions.Timeout:
        print("⏰ Timeout: Servidor demorou para responder")
        return {"content": "Timeout"}
    except Exception as e:
        print(f"🔥 Erro inesperado: {e}")
        return {"content": f"Erro: {str(e)}"}

if __name__ == "__main__":
    test_conversation_memory_and_task_creation()

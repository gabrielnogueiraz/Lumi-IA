#!/usr/bin/env python3
"""
Teste específico para criação de tarefas
"""
import asyncio
import requests
import json
from datetime import datetime

# Teste de criação de tarefa via chat
def test_task_creation_via_chat():
    """Testa criação de tarefa através da conversa com Lumi"""
    
    base_url = "http://localhost:5000"
    
    # Teste 1: Criação simples de tarefa
    print("🧪 Teste 1: Criação de tarefa via conversa")
    print("=" * 50)
    
    payload = {
        "user_id": "123",
        "message": "Preciso estudar python hoje as 18:30"
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resposta da Lumi: {data.get('content', 'N/A')[:100]}...")
            
            # Verificar se tem ações de criação de tarefa
            actions = data.get('actions', [])
            task_created = any(action.get('type') == 'task_created' for action in actions)
            
            if task_created:
                task_data = next((action.get('data') for action in actions if action.get('type') == 'task_created'), {})
                print(f"✅ Tarefa criada com ID: {task_data.get('task_id', 'N/A')}")
                
                # Verificar se a tarefa realmente existe no banco
                return test_task_exists_in_db(task_data.get('task_id'))
            else:
                print("❌ Nenhuma ação de criação de tarefa encontrada")
                print(f"Actions disponíveis: {[a.get('type') for a in actions]}")
                return False
        else:
            print(f"❌ Erro: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_task_exists_in_db(task_id):
    """Verifica se a tarefa foi realmente criada no banco"""
    if not task_id:
        return False
        
    print(f"\n🔍 Verificando se tarefa {task_id} existe no banco...")
    
    # Como não temos acesso direto ao banco aqui, vamos tentar consultar via API
    # Se existir um endpoint para listar tarefas
    
    payload = {
        "user_id": "123",
        "message": "Quais são minhas tarefas?"
    }
    
    try:
        response = requests.post("http://localhost:5000/api/chat", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            content = data.get('content', '').lower()
            
            # Se a resposta mencionar tarefas específicas, é um bom sinal
            if 'python' in content and 'estudar' in content:
                print("✅ Tarefa aparece nas consultas subsequentes")
                return True
            elif 'não tem nenhuma tarefa' in content or 'você está livre' in content:
                print("❌ Tarefa não aparece nas consultas - não foi salva no banco")
                return False
            else:
                print(f"🤔 Resposta ambígua: {content[:150]}...")
                return False
        
    except Exception as e:
        print(f"❌ Erro ao verificar existência: {e}")
        return False

def test_conversation_memory():
    """Testa se a Lumi tem memória de conversas anteriores"""
    print("\n🧪 Teste 2: Memória de conversa")
    print("=" * 50)
    
    user_id = "123"
    
    # Primeira mensagem
    print("Mensagem 1: Apresentação")
    payload1 = {
        "user_id": user_id,
        "message": "Oi, meu nome é João e eu trabalho como desenvolvedor"
    }
    
    try:
        response1 = requests.post("http://localhost:5000/api/chat", json=payload1, timeout=10)
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ Resposta 1: {data1.get('content', '')[:100]}...")
        
        # Aguardar um pouco
        import time
        time.sleep(1)
        
        # Segunda mensagem (para testar memória)
        print("\nMensagem 2: Teste de memória")
        payload2 = {
            "user_id": user_id,
            "message": "Você se lembra do meu nome?"
        }
        
        response2 = requests.post("http://localhost:5000/api/chat", json=payload2, timeout=10)
        if response2.status_code == 200:
            data2 = response2.json()
            content2 = data2.get('content', '').lower()
            print(f"✅ Resposta 2: {data2.get('content', '')}")
            
            # Verificar se lembra do nome
            if 'joão' in content2:
                print("✅ Lumi lembrou do nome!")
                return True
            else:
                print("❌ Lumi não lembrou do nome")
                return False
        
    except Exception as e:
        print(f"❌ Erro no teste de memória: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE COMPLETO DA LUMI - FUNCIONALIDADES AVANÇADAS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    results = {
        'task_creation': False,
        'conversation_memory': False
    }
    
    # Teste 1: Criação de tarefas
    results['task_creation'] = test_task_creation_via_chat()
    
    # Teste 2: Memória de conversa
    results['conversation_memory'] = test_conversation_memory()
    
    # Relatório final
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 30)
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 Resultado: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print("🎉 Todos os testes passaram! Lumi está funcionando perfeitamente!")
    else:
        print("⚠️  Alguns testes falharam. Lumi precisa de melhorias.")

if __name__ == "__main__":
    main()

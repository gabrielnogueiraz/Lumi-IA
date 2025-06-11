#!/usr/bin/env python3
"""
🧪 TESTE COMPLETO: LUMI MEMORY + TASK CREATION
Testa as funcionalidades melhoradas da Lumi AI
"""
import requests
import json
import time
from datetime import datetime

def test_lumi_enhanced_features():
    """Testa as funcionalidades melhoradas da Lumi"""
    base_url = "http://localhost:5000"
    
    print("🧪 TESTE COMPLETO: LUMI MEMORY + TASK CREATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now()}")
    print("=" * 60)
    
    results = {}
    
    # 🧪 Teste 1: Apresentação e memória inicial
    print("\n🧪 Teste 1: Apresentação e memória inicial")
    print("=" * 50)
    
    try:
        payload1 = {
            "user_id": "123",
            "message": "Olá! Meu nome é João e estou começando a usar a Lumi hoje."
        }
        
        print(f"📤 Enviando: {payload1['message']}")
        response1 = requests.post(f"{base_url}/api/chat", json=payload1, timeout=30)
        print(f"📋 Status: {response1.status_code}")
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"✅ Resposta da Lumi: {data1['response'][:100]}...")
            results['memory_initial'] = "✅ PASSOU"
        else:
            print(f"❌ Erro: {response1.text}")
            results['memory_initial'] = "❌ FALHOU"
            
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")
        results['memory_initial'] = "❌ FALHOU"
    
    time.sleep(2)
    
    # 🧪 Teste 2: Criação de tarefa com horário
    print("\n🧪 Teste 2: Criação de tarefa com horário")
    print("=" * 50)
    
    try:
        payload2 = {
            "user_id": "123",
            "message": "Preciso estudar Python hoje às 18:30"
        }
        
        print(f"📤 Enviando: {payload2['message']}")
        response2 = requests.post(f"{base_url}/api/chat", json=payload2, timeout=30)
        print(f"📋 Status: {response2.status_code}")
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"✅ Resposta da Lumi: {data2['response'][:100]}...")
            
            # Verificar se a tarefa foi criada
            task_created = any("criei" in data2['response'].lower() or "tarefa" in data2['response'].lower())
            has_actions = len(data2.get('actions', [])) > 0
            
            if task_created:
                print(f"✅ Tarefa detectada e criada!")
                results['task_creation'] = "✅ PASSOU"
            else:
                print(f"❌ Tarefa não foi criada")
                results['task_creation'] = "❌ FALHOU"
                
        else:
            print(f"❌ Erro: {response2.text}")
            results['task_creation'] = "❌ FALHOU"
            
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")
        results['task_creation'] = "❌ FALHOU"
    
    time.sleep(2)
    
    # 🧪 Teste 3: Memória de conversa - Lumi deve lembrar do nome
    print("\n🧪 Teste 3: Memória de conversa")
    print("=" * 50)
    
    try:
        payload3 = {
            "user_id": "123",
            "message": "Como você me chama mesmo?"
        }
        
        print(f"📤 Enviando: {payload3['message']}")
        response3 = requests.post(f"{base_url}/api/chat", json=payload3, timeout=30)
        print(f"📋 Status: {response3.status_code}")
        
        if response3.status_code == 200:
            data3 = response3.json()
            print(f"✅ Resposta da Lumi: {data3['response'][:100]}...")
            
            # Verificar se lembrou do nome
            remembers_name = "joão" in data3['response'].lower()
            
            if remembers_name:
                print(f"✅ Lumi lembrou do nome!")
                results['conversation_memory'] = "✅ PASSOU"
            else:
                print(f"❌ Lumi não lembrou do nome")
                results['conversation_memory'] = "❌ FALHOU"
                
        else:
            print(f"❌ Erro: {response3.text}")
            results['conversation_memory'] = "❌ FALHOU"
            
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")
        results['conversation_memory'] = "❌ FALHOU"
    
    time.sleep(2)
    
    # 🧪 Teste 4: Consulta de agenda
    print("\n🧪 Teste 4: Consulta de agenda")
    print("=" * 50)
    
    try:
        payload4 = {
            "user_id": "123",
            "message": "Quais são minhas tarefas para hoje?"
        }
        
        print(f"📤 Enviando: {payload4['message']}")
        response4 = requests.post(f"{base_url}/api/chat", json=payload4, timeout=30)
        print(f"📋 Status: {response4.status_code}")
        
        if response4.status_code == 200:
            data4 = response4.json()
            print(f"✅ Resposta da Lumi: {data4['response'][:150]}...")
            
            # Verificar se mencionou a tarefa de Python
            mentions_python = "python" in data4['response'].lower()
            has_task_info = any(word in data4['response'].lower() for word in ['tarefa', 'estudar', 'python', '18:30'])
            
            if mentions_python or has_task_info:
                print(f"✅ Lumi mostrou a tarefa criada!")
                results['agenda_query'] = "✅ PASSOU"
            else:
                print(f"❌ Lumi não mostrou a tarefa criada")
                results['agenda_query'] = "❌ FALHOU"
                
        else:
            print(f"❌ Erro: {response4.text}")
            results['agenda_query'] = "❌ FALHOU"
            
    except Exception as e:
        print(f"🔥 Erro de conexão: {e}")
        results['agenda_query'] = "❌ FALHOU"
    
    # 📊 Relatório Final
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 30)
    
    passed_tests = sum(1 for result in results.values() if "✅" in result)
    total_tests = len(results)
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    print(f"\n🎯 Resultado: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 Todos os testes passaram! Lumi está funcionando perfeitamente!")
    elif passed_tests >= total_tests // 2:
        print("⚠️  A maioria dos testes passou. Algumas melhorias necessárias.")
    else:
        print("❌ Vários testes falharam. Lumi precisa de correções importantes.")
    
    return results

if __name__ == "__main__":
    test_lumi_enhanced_features()

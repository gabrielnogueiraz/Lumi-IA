#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste específico das funcionalidades que estavam com problema na Lumi AI
"""

import requests
import json

API_URL = "http://localhost:5000/api/chat"

def test_functionality(test_name, payload):
    """Testa uma funcionalidade específica"""
    print(f"\n🧪 {test_name}")
    print("=" * 50)
    
    try:
        response = requests.post(API_URL, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Resposta: {data.get('response', 'N/A')[:100]}...")
            print(f"   Humor: {data.get('mood', 'N/A')}")
            print(f"   Sugestões: {len(data.get('suggestions', []))}")
            print(f"   Ações: {len(data.get('actions', []))}")
            print(f"   Insights: {len(data.get('insights', []))}")
            
            # Mostra informações do jardim se disponível
            if 'garden_status' in data:
                garden = data['garden_status']
                print(f"   🌸 Jardim: {garden.get('flowers', 0)} flores - {garden.get('message', 'N/A')}")
            
            # Mostra estatísticas do usuário se disponível
            if 'user_stats' in data:
                stats = data['user_stats']
                print(f"   📊 Stats: Modo {stats.get('system_mode', 'N/A')}")
                
        else:
            print(f"   Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

def main():
    print("🚀 TESTANDO FUNCIONALIDADES CORRIGIDAS DA LUMI AI")
    print("=" * 60)
    
    # Teste 1: Comando para criar tarefa
    test_functionality(
        "Criar uma tarefa",
        {
            "userId": "test_user_tasks",
            "message": "Criar uma tarefa: Estudar Python por 2 horas",
            "context": {"task_count": 3},
            "action": "task_create"
        }
    )
    
    # Teste 2: Comando para completar tarefa
    test_functionality(
        "Completar uma tarefa",
        {
            "userId": "test_user_tasks",
            "message": "Completar a tarefa de estudos",
            "context": {"task_count": 5},
            "action": "task_complete"
        }
    )
    
    # Teste 3: Pergunta sobre pomodoro
    test_functionality(
        "Pergunta sobre pomodoro",
        {
            "userId": "test_user_pomodoro",
            "message": "Como funciona a técnica pomodoro?",
            "context": {"recentPomodoros": 2},
            "action": "chat"
        }
    )
    
    # Teste 4: Pergunta sobre jardim
    test_functionality(
        "Status do jardim",
        {
            "userId": "test_user_garden",
            "message": "Como está meu jardim hoje?",
            "context": {
                "task_count": 7,
                "flowersEarned": {"green": 5, "orange": 2, "red": 1, "purple": 0}
            },
            "action": "garden_status"
        }
    )
    
    # Teste 5: Comando de apagar tarefa
    test_functionality(
        "Apagar uma tarefa",
        {
            "userId": "test_user_delete",
            "message": "Remover a tarefa de reunião",
            "context": {"task_count": 8},
            "action": "task_delete"
        }
    )
    
    # Teste 6: Teste com muitas tarefas (deve sugerir priorização)
    test_functionality(
        "Usuário com muitas tarefas",
        {
            "userId": "test_user_busy",
            "message": "Estou muito ocupado hoje",
            "context": {"task_count": 12},
            "action": "chat"
        }
    )
    
    # Teste 7: Usuário sem tarefas (jardim vazio)
    test_functionality(
        "Usuário sem tarefas",
        {
            "userId": "test_user_empty",
            "message": "O que posso fazer hoje?",
            "context": {"task_count": 0},
            "action": "chat"
        }
    )
    
    print("\n🏁 Testes concluídos!")
    print("\n💡 Verifique se:")
    print("   - Lumi entende comandos de criar/apagar/editar tarefas")
    print("   - Lumi compreende perguntas sobre pomodoros")
    print("   - Jardim mostra informações corretas (não '0 flores')")
    print("   - Sistema integra com dados reais do PomodoroTasks")

if __name__ == "__main__":
    main()

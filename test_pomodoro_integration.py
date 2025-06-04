#!/usr/bin/env python3
"""
Teste específico para simular requisições do frontend PomodoroTasks
"""

import requests
import json
from datetime import datetime

def test_pomodoro_tasks_integration():
    """Simula requisições reais do PomodoroTasks"""
    
    API_BASE = "http://localhost:5000"
    
    print("🔄 TESTANDO INTEGRAÇÃO COM POMODORO TASKS")
    print("=" * 60)
    
    # Teste 1: Início de sessão
    print("\n📱 Teste 1: Início de sessão do usuário")
    payload = {
        "userId": "user_12345",
        "message": "Bom dia Lumi! Como está meu progresso?",
        "context": {
            "currentSession": {
                "startTime": datetime.now().isoformat(),
                "tasksCompleted": 0,
                "pomodorosCompleted": 0
            },
            "userStats": {
                "totalTasks": 15,
                "completedTasks": 12,
                "totalPomodoros": 8,
                "streak": 3
            },
            "garden": {
                "flowers": {
                    "green": 5,
                    "orange": 3,
                    "red": 2,
                    "purple": 1
                },
                "totalFlowers": 11
            }
        },
        "action": "start_session"
    }
    
    response = make_request(f"{API_BASE}/api/chat", payload)
    
    # Teste 2: Criação de tarefa
    print("\n📝 Teste 2: Criação de nova tarefa")
    payload = {
        "userId": "user_12345", 
        "message": "Quero criar uma tarefa: Estudar Python por 2 horas",
        "context": {
            "task": {
                "title": "Estudar Python por 2 horas",
                "priority": "high",
                "estimatedPomodoros": 4,
                "deadline": "2024-12-10"
            }
        },
        "action": "task_created"
    }
    
    response = make_request(f"{API_BASE}/api/chat", payload)
    
    # Teste 3: Completar pomodoro
    print("\n🍅 Teste 3: Pomodoro completado")
    payload = {
        "userId": "user_12345",
        "message": "Acabei de completar um pomodoro de estudo!",
        "context": {
            "pomodoro": {
                "taskId": "task_789",
                "duration": 25,
                "completed": True,
                "interruptions": 0
            },
            "flower": {
                "type": "orange",
                "earned": True,
                "reason": "task_completion"
            }
        },
        "action": "pomodoro_completed"
    }
    
    response = make_request(f"{API_BASE}/api/chat", payload)
    
    # Teste 4: Consultar estatísticas
    print("\n📊 Teste 4: Consultar estatísticas do jardim")
    payload = {
        "userId": "user_12345",
        "message": "Como está meu jardim virtual?",
        "context": {
            "request_type": "garden_status",
            "period": "week"
        },
        "action": "garden_view"
    }
    
    response = make_request(f"{API_BASE}/api/chat", payload)
    
    # Teste 5: Mensagem de apoio em dificuldade
    print("\n😰 Teste 5: Usuário relatando dificuldades")
    payload = {
        "userId": "user_12345",
        "message": "Estou com dificuldade para me concentrar hoje...",
        "context": {
            "mood": "struggling",
            "recent_performance": {
                "interrupted_pomodoros": 3,
                "completed_pomodoros": 1
            }
        },
        "action": "support_request"
    }
    
    response = make_request(f"{API_BASE}/api/chat", payload)
    
    print("\n" + "=" * 60)
    print("✅ Testes de integração PomodoroTasks concluídos!")


def make_request(url, payload):
    """Faz uma requisição e mostra o resultado"""
    print(f"\n🔗 URL: {url}")
    print(f"📦 Payload:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=15,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📬 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"🌟 Resposta da Lumi:")
            print(f"   💬 Texto: {data.get('response', '')[:100]}...")
            print(f"   😊 Humor: {data.get('mood', 'N/A')}")
            print(f"   💡 Sugestões: {len(data.get('suggestions', []))}")
            print(f"   ⚡ Ações: {len(data.get('actions', []))}")
            print(f"   🔍 Insights: {len(data.get('insights', []))}")
        else:
            print(f"❌ Erro: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   Detalhes: {error_data}")
            else:
                print(f"   Texto: {response.text[:200]}")
                
    except Exception as e:
        print(f"❌ Exceção: {e}")
    
    return response


if __name__ == "__main__":
    # Verifica se servidor está ativo
    try:
        status_response = requests.get("http://localhost:5000/", timeout=5)
        if status_response.status_code == 200:
            print("✅ Servidor Lumi está rodando!")
            test_pomodoro_tasks_integration()
        else:
            print("❌ Servidor não responde corretamente")
    except:
        print("❌ Servidor não está rodando")
        print("💡 Inicie o servidor com: cd src && python lumi_api.py")

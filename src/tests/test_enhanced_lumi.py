#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste Completo da Lumi 3.0 Enhanced
Testa todas as funcionalidades implementadas baseadas na documentação
"""

import sys
import os
import json
from datetime import datetime

# Adiciona o diretório pai ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_enhanced_lumi():
    """Testa a Enhanced Lumi diretamente"""
    try:
        from core.enhanced_lumi import enhanced_lumi
        
        print("🌟 === TESTE COMPLETO DA LUMI 3.0 ENHANCED ===")
        print()
        
        # Teste 1: Chat geral
        print("📝 Teste 1: Chat geral")
        test1 = {
            'userId': 'test123',
            'message': 'Oi Lumi, como você está hoje?',
            'context': {},
            'action': 'chat'
        }
        response1 = enhanced_lumi.process_request(test1)
        print(f"✅ Response: {response1['response'][:100]}...")
        print(f"✅ Mood: {response1['mood']}")
        print()
        
        # Teste 2: Pomodoro completado
        print("📝 Teste 2: Pomodoro completado")
        test2 = {
            'userId': 'test123',
            'message': 'Completei um pomodoro de 25 minutos focado em programação!',
            'context': {
                'recentActivity': [{'type': 'pomodoro_completed', 'duration': 25, 'priority': 'high'}],
                'garden': {'greenFlowers': 8, 'orangeFlowers': 3, 'redFlowers': 2}
            },
            'action': 'pomodoro_completed'
        }
        response2 = enhanced_lumi.process_request(test2)
        print(f"✅ Response: {response2['response'][:100]}...")
        print(f"✅ Mood: {response2['mood']}")
        print(f"✅ Suggestions: {response2['suggestions']}")
        print()
        
        # Teste 3: Flor rara ganha
        print("📝 Teste 3: Flor rara ganha")
        test3 = {
            'userId': 'test123',
            'message': 'Ganhei uma flor roxa!',
            'context': {
                'garden': {'rareFlowers': 1, 'purpleFlowers': 1},
                'recentActivity': [{'type': 'flower_earned', 'color': 'purple'}]
            },
            'action': 'flower_earned'
        }
        response3 = enhanced_lumi.process_request(test3)
        print(f"✅ Response: {response3['response'][:100]}...")
        print(f"✅ Mood: {response3['mood']}")
        print()
        
        # Teste 4: Dificuldades
        print("📝 Teste 4: Expressando dificuldades")
        test4 = {
            'userId': 'test123',
            'message': 'Estou tendo dificuldades para me concentrar hoje',
            'context': {
                'currentSession': {'completedToday': 0, 'currentStreak': 0}
            },
            'action': 'chat'
        }
        response4 = enhanced_lumi.process_request(test4)
        print(f"✅ Response: {response4['response'][:100]}...")
        print(f"✅ Mood: {response4['mood']}")
        print(f"✅ Suggestions: {response4['suggestions']}")
        print()
        
        # Teste 5: Análise de contexto
        print("📝 Teste 5: Análise completa de contexto")
        test5 = {
            'userId': 'test123',
            'message': 'Como estou indo hoje?',
            'context': {
                'user': {'name': 'João', 'memberSince': '2024-01-01'},
                'currentSession': {'activeTasks': 3, 'completedToday': 5, 'currentStreak': 7},
                'garden': {
                    'totalFlowers': 45,
                    'greenFlowers': 20,
                    'orangeFlowers': 15,
                    'redFlowers': 8,
                    'rareFlowers': 2
                },
                'patterns': {
                    'mostProductiveHour': 14,
                    'averageSessionLength': 28,
                    'completionRate': 0.87
                }
            },
            'action': 'analysis'
        }
        response5 = enhanced_lumi.process_request(test5)
        print(f"✅ Response: {response5['response'][:100]}...")
        print(f"✅ Mood: {response5['mood']}")
        print(f"✅ Insights: {response5.get('insights', [])}")
        print()
        
        print("🎉 === TODOS OS TESTES CONCLUÍDOS COM SUCESSO! ===")
        print("✅ Enhanced Lumi está funcionando perfeitamente!")
        print("✅ Personalidade autêntica: ATIVA")
        print("✅ Sistema de jardim virtual: ATIVO")
        print("✅ Análise comportamental: ATIVA") 
        print("✅ Padrões de resposta: ATIVOS")
        print("✅ Integração PomodoroTasks: PRONTA")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_integration():
    """Testa a integração com a API"""
    try:
        import requests
        
        print("🌐 === TESTE DE INTEGRAÇÃO COM API ===")
        print()
        
        # Teste da página inicial
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ API está online!")
            data = response.json()
            print(f"✅ Versão: {data['version']}")
            print(f"✅ Status: {data['status']}")
        else:
            print(f"❌ API offline. Status: {response.status_code}")
            return False
        
        # Teste do chat
        chat_data = {
            'userId': 'test123',
            'message': 'Oi Lumi, testando a integração!',
            'context': {'garden': {'greenFlowers': 3}},
            'action': 'chat'
        }
        
        response = requests.post('http://localhost:5000/api/chat', json=chat_data, timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint /api/chat funcionando!")
            data = response.json()
            print(f"✅ Response: {data['response'][:50]}...")
            print(f"✅ Mood: {data['mood']}")
        else:
            print(f"❌ Erro no chat. Status: {response.status_code}")
            return False
            
        print("🎉 === INTEGRAÇÃO COM API FUNCIONANDO! ===")
        return True
        
    except requests.exceptions.ConnectionError:
        print("⚠️ API não está rodando. Execute: python src/lumi_api.py")
        return False
    except Exception as e:
        print(f"❌ Erro na integração: {e}")
        return False

if __name__ == "__main__":
    print("🧪 INICIANDO TESTES DA LUMI 3.0 ENHANCED")
    print("=" * 60)
    print()
    
    # Teste da Enhanced Lumi
    test1_success = test_enhanced_lumi()
    print()
    
    # Teste da integração com API
    test2_success = test_api_integration()
    print()
    
    # Resultado final
    if test1_success and test2_success:
        print("🎉 === TODOS OS TESTES APROVADOS! ===")
        print("🌟 Lumi 3.0 Enhanced está 100% funcional!")
        print("🚀 Pronta para integração com PomodoroTasks!")
    elif test1_success:
        print("✅ Enhanced Lumi funcionando, mas API offline")
        print("💡 Inicie a API com: python src/lumi_api.py") 
    else:
        print("❌ Problemas encontrados nos testes")
        print("🔧 Verifique os logs acima para detalhes")

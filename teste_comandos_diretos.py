#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de detecção de comandos específicos da Lumi AI
"""

import requests
import json

def testar_comando(msg, desc, user_id):
    """Testa um comando específico"""
    print(f'🧪 {desc}')
    print(f'   Mensagem: "{msg}"')
    
    try:
        response = requests.post('http://localhost:5000/api/chat', 
            json={'message': msg, 'userId': user_id})
        
        if response.status_code == 200:
            data = response.json()
            actions = data.get('actions', [])
            suggestions = data.get('suggestions', [])
            mood = data.get('mood', 'N/A')
            
            print(f'   ✅ Status: OK | Humor: {mood}')
            print(f'   🎯 Ações detectadas: {len(actions)}')
            for action in actions:
                print(f'      - {action.get("type", "N/A")}: {action.get("description", "N/A")}')
            
            print(f'   💡 Sugestões: {len(suggestions)}')
            if suggestions:
                print(f'      - Primeira: {suggestions[0][:50]}...' if len(suggestions[0]) > 50 else f'      - {suggestions[0]}')
            print()
        else:
            print(f'   ❌ Erro: {response.status_code}')
            print(f'      {response.text}')
            print()
    except Exception as e:
        print(f'   ❌ Erro na requisição: {e}')
        print()

if __name__ == '__main__':
    print('🚀 TESTE DE DETECÇÃO DE COMANDOS ESPECÍFICOS')
    print('=' * 55)
    
    testes = [
        ('Adicionar tarefa: Estudar matemática', 'Comando direto - adicionar tarefa', 'user_1'),
        ('Iniciar pomodoro agora', 'Comando direto - iniciar pomodoro', 'user_2'),
        ('Como ganho flores no jardim?', 'Pergunta sobre sistema de flores', 'user_3'),
        ('Listar minhas tarefas', 'Comando - listar tarefas', 'user_4'),
        ('Remover tarefa de reunião', 'Comando - remover tarefa', 'user_5'),
        ('Como funciona a técnica pomodoro?', 'Pergunta sobre pomodoro', 'user_6'),
        ('Completar tarefa de estudos', 'Comando - completar tarefa', 'user_7'),
        ('Preciso focar mais', 'Pedido de ajuda para foco', 'user_8')
    ]
    
    for msg, desc, user_id in testes:
        testar_comando(msg, desc, user_id)
    
    print('🏁 Testes de comandos concluídos!')

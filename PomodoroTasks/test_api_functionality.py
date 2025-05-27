#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar a funcionalidade da Lumi 2.0
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ai_assistant import LumiAssistant
from task_manager import TaskManager

def main():
    print("🔥 TESTE FINAL - LUMI 2.0 API FUNCIONALIDADE")
    print("=" * 50)
    
    # Inicializar componentes
    try:
        task_manager = TaskManager()
        lumi = LumiAssistant(task_manager)
        print("✅ Componentes inicializados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return
    
    # Teste 1: Saudação
    print("\n📝 Teste 1: Saudação")
    response = lumi.process_message("Olá Lumi!")
    print(f"Resposta: {response}")
    
    # Teste 2: Adicionar tarefa
    print("\n📝 Teste 2: Adicionar tarefa")
    response = lumi.process_message("adicionar tarefa: Testar API da Lumi")
    print(f"Resposta: {response}")
    
    # Teste 3: Listar tarefas
    print("\n📝 Teste 3: Listar tarefas")
    response = lumi.process_message("listar tarefas")
    print(f"Resposta: {response}")
    
    # Teste 4: Status do sistema
    print("\n📝 Teste 4: Status")
    response = lumi.process_message("como estão as tarefas?")
    print(f"Resposta: {response}")
    
    print("\n🎯 Teste concluído!")

if __name__ == "__main__":
    main()

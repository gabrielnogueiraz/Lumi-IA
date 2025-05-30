#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste para verificar se a correção da agenda está funcionando
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from ai_assistant import LumiAssistant
from task_manager import TaskManager
from reports_generator import ReportsGenerator


def test_agenda_queries():
    """Testa as consultas de agenda"""
    print("🔥 TESTE - CORREÇÃO DA AGENDA DA LUMI")
    print("=" * 50)

    # Inicializar componentes
    try:
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        print("✅ Componentes inicializados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao inicializar: {e}")
        return

    # Teste 1: Verificar agenda vazia
    print("\n📝 Teste 1: Verificar agenda vazia")
    response = lumi.process_message("Tenho tarefas para hoje?")
    print(f"Resposta: {response}")

    # Teste 2: Adicionar uma tarefa
    print("\n📝 Teste 2: Adicionar tarefa")
    response = lumi.process_message("Adicionar tarefa: Estudar Python")
    print(f"Resposta: {response}")

    # Teste 3: Verificar agenda com tarefas
    print("\n📝 Teste 3: Verificar agenda com tarefas")
    response = lumi.process_message("Como está minha agenda?")
    print(f"Resposta: {response}")

    # Teste 4: Outra consulta de agenda
    print("\n📝 Teste 4: Tenho alguma tarefa?")
    response = lumi.process_message("Tenho alguma tarefa na minha agenda?")
    print(f"Resposta: {response}")

    print("\n🎯 Teste concluído!")


if __name__ == "__main__":
    test_agenda_queries()

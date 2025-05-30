#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste para verificar as correções das tarefas
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from core.task_handler import TaskHandler
from task_manager import TaskManager
from core.personality import Personality


def test_task_extraction():
    """Testa a extração corrigida de tarefas"""
    print("🔧 TESTE - CORREÇÕES DE TAREFAS")
    print("=" * 50)

    # Setup
    task_manager = TaskManager()
    personality = Personality()
    handler = TaskHandler(task_manager, personality)

    # Teste 1: Tarefa única simples
    print("\n📝 Teste 1: Tarefa única")
    message = "Preciso estudar minecraft hoje as 15:00, adicione na minha agenda"
    task_info = handler._extract_single_task_improved(message)
    print(f"Entrada: {message}")
    print(f"Resultado: {task_info}")

    expected_title = "Estudar minecraft"
    if task_info and task_info.get("title") == expected_title:
        print("✅ SUCESSO: Título extraído corretamente")
    else:
        print(
            f"❌ FALHA: Esperado '{expected_title}', obteve '{task_info.get('title') if task_info else None}'"
        )

    # Teste 2: Múltiplas tarefas
    print("\n📝 Teste 2: Múltiplas tarefas")
    message = "Preciso adicionar algumas tarefas hoje, que são: 1. Tenho levar meu celular para arrumar hoje as 14:30, 2. Preciso estudar automações com Python hoje as 16:00, 3. Preciso ir para casa da minha namorada hoje as 17:00"
    tasks = handler._extract_multiple_tasks_improved(message)
    print(f"Entrada: {message}")
    print(f"Tarefas encontradas: {len(tasks)}")

    expected_titles = [
        "Levar meu celular para arrumar",
        "Estudar automações com Python",
        "Ir para casa da minha namorada",
    ]

    for i, task in enumerate(tasks):
        print(f"  {i+1}. {task.get('title')} às {task.get('time')}")
        if i < len(expected_titles) and task.get("title") == expected_titles[i]:
            print(f"    ✅ Título {i+1} correto")
        else:
            print(f"    ❌ Título {i+1} incorreto")

    # Teste 3: Validação de títulos
    print("\n📝 Teste 3: Validação de títulos")
    invalid_titles = ["minha agenda", "na agenda", "que são", "tarefas"]
    for title in invalid_titles:
        is_valid = handler._is_valid_task_title(title)
        print(f"  '{title}' -> {'❌ Inválido' if not is_valid else '✅ Válido'}")

    valid_titles = ["Estudar Python", "Ir ao mercado", "Fazer exercícios"]
    for title in valid_titles:
        is_valid = handler._is_valid_task_title(title)
        print(f"  '{title}' -> {'✅ Válido' if is_valid else '❌ Inválido'}")

    print("\n🎯 Teste de correções concluído!")


if __name__ == "__main__":
    test_task_extraction()

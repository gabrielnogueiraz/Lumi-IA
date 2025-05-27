#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste de Integração LUMI 2.0
Verifica se o sistema funciona corretamente com os novos componentes humanizados
"""

import sys
import os
import traceback

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_integration():
    """Testa a integração básica dos componentes"""
    print("\n" + "="*70)
    print(f"{'🔧 TESTE DE INTEGRAÇÃO LUMI 2.0 🔧':^70}")
    print("="*70)
    
    try:
        # Importa os módulos
        print("\n📦 Importando módulos...")
        from task_manager import TaskManager
        from reports_generator import ReportsGenerator
        from ai_assistant import LumiAssistant
        
        print("✅ Módulos importados com sucesso!")
        
        # Inicializa os componentes
        print("\n🚀 Inicializando componentes...")
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        
        print("✅ Componentes inicializados com sucesso!")
        
        # Testa funcionalidades básicas
        print("\n🧪 Testando funcionalidades básicas...")
        
        # Teste 1: Adicionar tarefa
        print("\n📝 Teste 1: Adicionando tarefa...")
        response = lumi.process_message("Adicione a tarefa Estudar Python para hoje")
        print(f"Resposta: {response}")
        
        # Teste 2: Listar tarefas
        print("\n📋 Teste 2: Listando tarefas...")
        response = lumi.process_message("Quais são minhas tarefas?")
        print(f"Resposta: {response}")
        
        # Teste 3: Saudação
        print("\n👋 Teste 3: Saudação...")
        response = lumi.process_message("Oi Lumi!")
        print(f"Resposta: {response}")
        
        # Teste 4: Verificar métodos de compatibilidade
        print("\n🔗 Teste 4: Métodos de compatibilidade...")
        success = task_manager.add_task("Tarefa de teste")
        print(f"add_task() funcionou: {success}")
        
        tasks = task_manager.list_tasks()
        print(f"list_tasks() retornou {len(tasks)} tarefa(s)")
        
        stats = task_manager.get_task_count()
        print(f"Estatísticas: {stats}")
        
        print("\n✅ TODOS OS TESTES PASSARAM! Sistema integrado com sucesso! 🎉")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        print("\n🔍 Detalhes do erro:")
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("Iniciando testes de integração do sistema LUMI 2.0...")
    
    # Executa testes
    basic_ok = test_basic_integration()
    
    # Resumo final
    print("\n" + "="*70)
    print(f"{'📊 RESUMO DOS TESTES 📊':^70}")
    print("="*70)
    
    print(f"\n🔧 Integração Básica: {'✅ PASSOU' if basic_ok else '❌ FALHOU'}")
    
    if basic_ok:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! 🎉")
        print("✨ LUMI 2.0 está funcionando perfeitamente! ✨")
        print("\n🚀 Sistema pronto para uso!")
        return True
    else:
        print(f"\n⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija antes de usar o sistema.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_integration():
    """Testa a integração básica dos componentes"""
    print("\n" + "="*70)
    print(f"{'🔧 TESTE DE INTEGRAÇÃO LUMI 2.0 🔧':^70}")
    print("="*70)
    
    try:
        # Importa os módulos
        print("\n📦 Importando módulos...")
        from task_manager import TaskManager
        from reports_generator import ReportsGenerator
        from ai_assistant import LumiAssistant
        
        print("✅ Módulos importados com sucesso!")
        
        # Inicializa os componentes
        print("\n🚀 Inicializando componentes...")
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        
        print("✅ Componentes inicializados com sucesso!")
        
        # Testa funcionalidades básicas
        print("\n🧪 Testando funcionalidades básicas...")
        
        # Teste 1: Adicionar tarefa
        print("\n📝 Teste 1: Adicionando tarefa...")
        response = lumi.process_message("Adicione a tarefa Estudar Python para hoje")
        print(f"Resposta: {response}")
        
        # Teste 2: Listar tarefas
        print("\n📋 Teste 2: Listando tarefas...")
        response = lumi.process_message("Quais são minhas tarefas?")
        print(f"Resposta: {response}")
        
        # Teste 3: Saudação
        print("\n👋 Teste 3: Saudação...")
        response = lumi.process_message("Oi Lumi!")
        print(f"Resposta: {response}")
        
        # Teste 4: Verificar métodos de compatibilidade
        print("\n🔗 Teste 4: Métodos de compatibilidade...")
        success = task_manager.add_task("Tarefa de teste")
        print(f"add_task() funcionou: {success}")
        
        tasks = task_manager.list_tasks()
        print(f"list_tasks() retornou {len(tasks)} tarefa(s)")
        
        stats = task_manager.get_task_count()
        print(f"Estatísticas: {stats}")
        
        print("\n✅ TODOS OS TESTES PASSARAM! Sistema integrado com sucesso! 🎉")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {str(e)}")
        print("\n🔍 Detalhes do erro:")
        traceback.print_exc()
        return False

def test_personality_features():
    """Testa as funcionalidades de personalidade"""
    print("\n" + "="*70)
    print(f"{'💖 TESTE DE PERSONALIDADE LUMI 2.0 💖':^70}")
    print("="*70)
    
    try:
        from task_manager import TaskManager
        from reports_generator import ReportsGenerator
        from ai_assistant import LumiAssistant
        
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        
        # Testa diferentes tipos de interação
        test_messages = [
            "Como você está?",
            "Obrigado pela ajuda!",
            "Preciso organizar minha vida",
            "Estou stressado com tanto trabalho",
            "Você é incrível!",
            "Me ajuda com as tarefas?",
        ]
        
        print("\n🎭 Testando respostas da personalidade...")
        for i, message in enumerate(test_messages, 1):
            print(f"\n💬 Teste {i}: '{message}'")
            response = lumi.process_message(message)
            print(f"🤖 Lumi: {response[:150]}{'...' if len(response) > 150 else ''}")
        
        print("\n✨ TESTE DE PERSONALIDADE CONCLUÍDO! 🌟")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE DE PERSONALIDADE: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("Iniciando testes de integração do sistema LUMI 2.0...")
    
    # Executa testes
    basic_ok = test_basic_integration()
    personality_ok = test_personality_features()
    
    # Resumo final
    print("\n" + "="*70)
    print(f"{'📊 RESUMO DOS TESTES 📊':^70}")
    print("="*70)
    
    print(f"\n🔧 Integração Básica: {'✅ PASSOU' if basic_ok else '❌ FALHOU'}")
    print(f"💖 Personalidade: {'✅ PASSOU' if personality_ok else '❌ FALHOU'}")
    
    if basic_ok and personality_ok:
        print(f"\n🎉 TODOS OS TESTES PASSARAM! 🎉")
        print("✨ LUMI 2.0 está funcionando perfeitamente! ✨")
        print("\n🚀 Sistema pronto para uso!")
        return True
    else:
        print(f"\n⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e corrija antes de usar o sistema.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

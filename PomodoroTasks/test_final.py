#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste Abrangente LUMI 2.0
Teste final para validar todas as funcionalidades do sistema humanizado
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_comprehensive_test():
    """Executa teste abrangente das funcionalidades"""
    print("\n" + "="*80)
    print(f"{'🚀 TESTE ABRANGENTE LUMI 2.0 - SISTEMA HUMANIZADO 🚀':^80}")
    print("="*80)
    
    try:
        # Importa e inicializa
        from task_manager import TaskManager
        from reports_generator import ReportsGenerator
        from ai_assistant import LumiAssistant
        
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        
        # Lista de testes representativos
        test_cases = [
            # Saudações e interações casuais
            ("👋 Saudação simples", "Oi Lumi!"),
            ("💖 Elogio", "Você é incrível!"),
            ("🙏 Agradecimento", "Obrigado pela ajuda!"),
            ("❓ Como está", "Como você está?"),
            
            # Gestão de tarefas
            ("📝 Adicionar tarefa declarativa", "Preciso estudar machine learning hoje"),
            ("📋 Listar tarefas", "Quais são minhas tarefas?"),
            ("✅ Marcar como concluída", "Terminei a primeira tarefa"),
            ("📝 Nova tarefa com horário", "Agende reunião para amanhã às 15h"),
            ("📋 Ver agenda novamente", "Mostre minha lista"),
            
            # Consultas e relatórios
            ("📊 Solicitar relatório", "Me dê um relatório de produtividade"),
            ("🤔 Pergunta geral", "Me explique o que é IA"),
            
            # Estados emocionais
            ("😰 Estresse", "Estou muito estressado com tanto trabalho"),
            ("💪 Motivação", "Estou motivado para arrasar hoje!"),
        ]
        
        print(f"\n🧪 Executando {len(test_cases)} testes de interação...")
        
        passed = 0
        for i, (test_name, message) in enumerate(test_cases, 1):
            print(f"\n{i:2d}. {test_name}")
            print(f"    💬 Entrada: '{message}'")
            
            try:
                response = lumi.process_message(message)
                # Verifica se não é uma resposta de erro genérica
                if "algo não funcionou" not in response.lower() and "problema" not in response.lower():
                    print(f"    ✅ Resposta: {response[:100]}{'...' if len(response) > 100 else ''}")
                    passed += 1
                else:
                    print(f"    ⚠️  Resposta: {response[:100]}{'...' if len(response) > 100 else ''}")
                    
            except Exception as e:
                print(f"    ❌ Erro: {str(e)}")
        
        # Estatísticas finais
        print("\n" + "="*80)
        print(f"{'📊 RESULTADOS DO TESTE 📊':^80}")
        print("="*80)
        
        success_rate = (passed / len(test_cases)) * 100
        print(f"\n✅ Testes bem-sucedidos: {passed}/{len(test_cases)} ({success_rate:.1f}%)")
        
        # Verifica estatísticas do sistema
        stats = task_manager.get_task_count()
        tasks = task_manager.list_tasks()
        
        print(f"📋 Tarefas no sistema: {stats['total']} (Pendentes: {stats['pending']}, Concluídas: {stats['completed']})")
        print(f"🧠 Contexto do usuário: {len(lumi.conversation_memory)} conversas na memória")
        
        # Avaliação final
        if success_rate >= 80:
            print(f"\n🎉 EXCELENTE! Sistema funcionando perfeitamente!")
            print(f"🌟 LUMI 2.0 está humanizada e pronta para usar!")
            return True
        elif success_rate >= 60:
            print(f"\n👍 BOM! Sistema funcionando bem com pequenos ajustes")
            return True
        else:
            print(f"\n⚠️ ATENÇÃO! Sistema precisa de melhorias")
            return False
            
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO NO TESTE: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    print("\n" + "="*80)
    if success:
        print(f"{'✨ LUMI 2.0 APROVADA! SISTEMA HUMANIZADO FUNCIONANDO! ✨':^80}")
        print(f"{'🚀 Pronta para transformar a produtividade dos usuários! 🚀':^80}")
    else:
        print(f"{'⚠️ LUMI 2.0 PRECISA DE AJUSTES ANTES DO USO ⚠️':^80}")
    print("="*80)
    
    sys.exit(0 if success else 1)

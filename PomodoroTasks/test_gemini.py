#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste para verificar se o Google Gemini está funcionando na Lumi
"""
import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importações
try:
    import google.generativeai as genai
    print("✅ Google Generative AI importado com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar Google Generative AI: {e}")
    print("Execute: pip install google-generativeai")
    sys.exit(1)

# Importa os módulos da Lumi
try:
    from ai_assistant import LumiAssistant
    from task_manager import TaskManager
    from reports_generator import ReportsGenerator
    print("✅ Módulos da Lumi importados com sucesso!")
except ImportError as e:
    print(f"❌ Erro ao importar módulos da Lumi: {e}")
    sys.exit(1)

def test_google_gemini_direct():
    """Testa o Google Gemini diretamente"""
    print("\n🧪 Testando Google Gemini diretamente...")
    
    try:
        # Configurar API
        api_key = "AIzaSyAButmMFCGLI48y2BeU1kAdOkL1rggdujA"
        genai.configure(api_key=api_key)
        
        # Criar modelo
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Teste simples
        response = model.generate_content("Explique em uma frase o que é inteligência artificial")
        
        print(f"✅ Resposta do Gemini: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste direto do Gemini: {e}")
        return False

def test_lumi_with_gemini():
    """Testa a Lumi com Google Gemini"""
    print("\n🤖 Testando Lumi com Google Gemini...")
    
    try:
        # Inicializa componentes
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        
        # Verifica se o Gemini foi inicializado
        if lumi.genai_client:
            print("✅ Google Gemini inicializado na Lumi!")
            print(f"📝 Modelo configurado: {lumi.GEMINI_MODEL}")
        else:
            print("❌ Google Gemini NÃO foi inicializado na Lumi!")
            return False
        
        # Teste de pergunta educacional
        test_message = "Me explique o que é machine learning"
        print(f"\n📨 Enviando pergunta: '{test_message}'")
        
        response = lumi.process_message(test_message)
        print(f"\n💬 Resposta da Lumi:\n{response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste da Lumi: {e}")
        return False

def test_task_functionality():
    """Testa funcionalidades básicas de tarefas"""
    print("\n📋 Testando funcionalidades de tarefas...")
    
    try:
        # Inicializa componentes
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        lumi = LumiAssistant(task_manager, reports_generator)
        
        # Teste de adicionar tarefa
        print("➕ Testando adição de tarefa...")
        response1 = lumi.process_message("Adicionar estudar Python hoje às 20:00")
        print(f"Resposta: {response1}")
        
        # Teste de listar tarefas
        print("\n📋 Testando listagem de tarefas...")
        response2 = lumi.process_message("Quais tarefas tenho?")
        print(f"Resposta: {response2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de tarefas: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🚀 TESTE DE FUNCIONAMENTO DO GOOGLE GEMINI NA LUMI")
    print("=" * 60)
    
    # Testes
    gemini_ok = test_google_gemini_direct()
    lumi_ok = test_lumi_with_gemini()
    tasks_ok = test_task_functionality()
    
    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES:")
    print(f"🔹 Google Gemini Direto: {'✅ OK' if gemini_ok else '❌ FALHOU'}")
    print(f"🔹 Lumi com Gemini: {'✅ OK' if lumi_ok else '❌ FALHOU'}")
    print(f"🔹 Funcionalidades de Tarefas: {'✅ OK' if tasks_ok else '❌ FALHOU'}")
    
    if all([gemini_ok, lumi_ok, tasks_ok]):
        print("\n🎉 TODOS OS TESTES PASSARAM! A Lumi está funcionando com Google Gemini!")
        print("💡 Para confirmar que está usando Gemini, observe as mensagens:")
        print("   ✅ Google Gemini inicializado com sucesso!")
        print("   ✅ Resposta gerada pelo gemini-1.5-pro")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique os erros acima.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

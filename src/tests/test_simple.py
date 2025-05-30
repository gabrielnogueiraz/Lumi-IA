#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Teste simples para verificar o Google Gemini
"""

print("🧪 Testando Google Gemini...")

try:
    import google.generativeai as genai

    print("✅ Google Generative AI importado!")

    # Configurar API
    genai.configure(api_key="AIzaSyAButmMFCGLI48y2BeU1kAdOkL1rggdujA")
    print("✅ API key configurada!")

    # Criar modelo
    model = genai.GenerativeModel("gemma-3-1b-it")
    print("✅ Modelo criado!")

    # Teste simples
    response = model.generate_content("Responda apenas: 'Google Gemini funcionando!'")
    print(f"✅ Resposta: {response.text}")

except Exception as e:
    print(f"❌ Erro: {e}")

print("\n🤖 Testando Lumi...")

try:
    from task_manager import TaskManager
    from reports_generator import ReportsGenerator
    from ai_assistant import LumiAssistant

    print("✅ Módulos importados!")

    task_manager = TaskManager()
    reports_generator = ReportsGenerator(task_manager)
    lumi = LumiAssistant(task_manager, reports_generator)
    print("✅ Lumi inicializada!")

    if lumi.genai_client:
        print(f"✅ Google Gemini ativo no modelo: {lumi.GEMINI_MODEL}")
    else:
        print("❌ Google Gemini não inicializado na Lumi")

    # Teste de resposta educacional
    response = lumi.process_message("Explique brevemente o que é IA")
    print(f"💬 Resposta da Lumi: {response[:100]}...")

except Exception as e:
    print(f"❌ Erro na Lumi: {e}")
    import traceback

    traceback.print_exc()

print("\n🎯 Teste finalizado!")

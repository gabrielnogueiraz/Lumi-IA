#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste Simples da Lumi 3.0 Enhanced
"""

print("🌟 Iniciando teste da Lumi 3.0...")

# Teste direto da Enhanced Lumi
try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    
    from core.enhanced_lumi import enhanced_lumi
    
    print("✅ Enhanced Lumi importada com sucesso!")
    
    # Teste básico
    test_request = {
        'userId': 'test123',
        'message': 'Oi Lumi, como você está?',
        'context': {},
        'action': 'chat'
    }
    
    response = enhanced_lumi.process_request(test_request)
    
    print("✅ Teste de resposta básica:")
    print(f"Response: {response['response']}")
    print(f"Mood: {response['mood']}")
    print(f"Suggestions: {response.get('suggestions', [])}")
    
    print("\n🎉 Enhanced Lumi está funcionando perfeitamente!")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()

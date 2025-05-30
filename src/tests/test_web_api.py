#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Teste específico para verificar se a API web está usando o Google Gemini
"""

import requests
import json

def test_lumi_web_api():
    """Testa a API web da Lumi para verificar se está usando Gemini"""
    
    url = "http://localhost:5000/api/chat"
    
    # Teste 1: Pergunta simples
    print("🧪 Teste 1: Pergunta simples")
    data = {
        "message": "Explique o que é inteligência artificial"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Resposta recebida:")
            print(result.get("response", "Sem resposta"))
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando. Execute 'python lumi_api.py' primeiro.")
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    print("\n" + "="*50)
    
    # Teste 2: Pergunta sobre produtividade
    print("🧪 Teste 2: Pergunta sobre produtividade")
    data = {
        "message": "Como posso ser mais produtivo nos estudos?"
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Resposta recebida:")
            print(result.get("response", "Sem resposta"))
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando. Execute 'python lumi_api.py' primeiro.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🚀 Testando API Web da Lumi com Google Gemini")
    print("="*50)
    test_lumi_web_api()

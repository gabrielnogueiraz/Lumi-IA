#!/usr/bin/env python3
"""
Script de teste para verificar problemas da Lumi AI
"""

import asyncio
import json
from pydantic import BaseModel, Field, ValidationError
from typing import Optional, Dict, Any, Union

# Simular o modelo exato usado na API
class ChatRequest(BaseModel):
    user_id: Union[str, int] = Field(..., description="ID do usuário")
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    context: Optional[Dict[str, Any]] = Field(None, description="Contexto adicional")

def test_validation():
    """Testa diferentes cenários de validação"""
    
    test_cases = [
        # Caso 1: Dados corretos
        {
            "name": "Dados corretos",
            "data": {"user_id": "123", "message": "Olá Lumi"},
            "should_pass": True
        },
        # Caso 2: user_id como int
        {
            "name": "user_id como int", 
            "data": {"user_id": 123, "message": "Olá Lumi"},
            "should_pass": True
        },
        # Caso 3: Sem user_id
        {
            "name": "Sem user_id",
            "data": {"message": "Olá Lumi"},
            "should_pass": False
        },
        # Caso 4: Sem message
        {
            "name": "Sem message",
            "data": {"user_id": "123"},
            "should_pass": False
        },
        # Caso 5: Message vazia
        {
            "name": "Message vazia",
            "data": {"user_id": "123", "message": ""},
            "should_pass": False
        },
        # Caso 6: Com context
        {
            "name": "Com context",
            "data": {"user_id": "123", "message": "Olá", "context": {"energy": 0.8}},
            "should_pass": True
        },
        # Caso 7: Context como string (inválido)
        {
            "name": "Context como string",
            "data": {"user_id": "123", "message": "Olá", "context": "invalid"},
            "should_pass": False
        }
    ]
    
    print("🧪 Testando validação do ChatRequest\n")
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            request = ChatRequest(**test_case["data"])
            result = "✅ PASSOU"
            details = f"user_id={request.user_id}, message='{request.message[:20]}...'"
            
            if not test_case["should_pass"]:
                result = "❌ DEVERIA FALHAR (mas passou)"
                
        except ValidationError as e:
            if test_case["should_pass"]:
                result = "❌ FALHOU"
                details = f"Erros: {[error['msg'] for error in e.errors()]}"
            else:
                result = "✅ FALHOU CORRETAMENTE"
                details = f"Erros esperados: {[error['msg'] for error in e.errors()]}"
        except Exception as e:
            result = "💥 ERRO INESPERADO"
            details = str(e)
        
        print(f"Teste {i}: {test_case['name']}")
        print(f"  Status: {result}")
        print(f"  Dados: {test_case['data']}")
        print(f"  Detalhes: {details}")
        print()

def test_typical_frontend_data():
    """Testa dados típicos que um frontend React enviaria"""
    
    print("🖥️ Testando dados típicos de frontend\n")
    
    # Dados que um React app normalmente enviaria
    typical_requests = [
        {
            "name": "React com useState",
            "data": {
                "user_id": 1,  # React useState normalmente usa number
                "message": "Lumi, como está minha agenda hoje?"
            }
        },
        {
            "name": "Com context object",
            "data": {
                "user_id": 1,
                "message": "Preciso de ajuda",
                "context": {
                    "currentTime": "21:42:04",
                    "energyLevel": 0.7,
                    "platform": "web"
                }
            }
        },
        {
            "name": "Vazio (erro comum)",
            "data": {}
        },
        {
            "name": "user_id null",
            "data": {
                "user_id": None,
                "message": "Teste"
            }
        }
    ]
    
    for req in typical_requests:
        print(f"📝 {req['name']}:")
        print(f"   Dados enviados: {json.dumps(req['data'], indent=2)}")
        
        try:
            chat_req = ChatRequest(**req["data"])
            print(f"   ✅ Validação OK")
            print(f"   📄 Resultado: user_id='{chat_req.user_id}' (tipo: {type(chat_req.user_id)})")
        except ValidationError as e:
            print(f"   ❌ Erro de validação:")
            for error in e.errors():
                print(f"      - {error['loc']}: {error['msg']}")
        except Exception as e:
            print(f"   💥 Erro inesperado: {e}")
        
        print()

if __name__ == "__main__":
    print("🤖 Lumi AI - Diagnóstico de Problemas\n")
    
    test_validation()
    test_typical_frontend_data()
    
    print("🎯 Conclusão:")
    print("Se os testes passaram, o problema pode estar em:")
    print("1. Dados enviados pelo frontend")
    print("2. Middleware ou CORS")
    print("3. Serialização JSON")
    print("4. Headers HTTP")
    print("5. Problemas de rede/conectividade")

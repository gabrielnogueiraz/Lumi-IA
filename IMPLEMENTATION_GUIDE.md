# Lumi AI Assistant - Implementation Guide

## Visão Geral

Este guia fornece instruções detalhadas para desenvolvedores que desejam estender, modificar ou integrar o Lumi AI Assistant 2.0. Inclui padrões de código, exemplos práticos e best practices.

---

## Arquitetura de Extensão

### Padrões de Design Implementados

#### 1. Module Pattern
Cada funcionalidade é encapsulada em módulos independentes:

```python
# Estrutura de módulo padrão
class NovoModulo:
    def __init__(self, dependencies=None):
        """Inicializar com dependências injetadas"""
        self.dependencies = dependencies or {}
        self._initialize()
    
    def _initialize(self):
        """Setup interno do módulo"""
        pass
    
    def public_method(self, params):
        """Método público da API"""
        return self._process(params)
    
    def _process(self, params):
        """Lógica interna"""
        pass
```

#### 2. Strategy Pattern
Para diferentes tipos de resposta e processamento:

```python
class ResponseStrategy:
    def generate_response(self, context, message):
        raise NotImplementedError

class TaskResponseStrategy(ResponseStrategy):
    def generate_response(self, context, message):
        # Implementação específica para tarefas
        pass

class EducationalResponseStrategy(ResponseStrategy):
    def generate_response(self, context, message):
        # Implementação específica para educação
        pass
```

#### 3. Observer Pattern
Para atualizações de estado:

```python
class StateObserver:
    def update(self, event, data):
        raise NotImplementedError

class PersonalityObserver(StateObserver):
    def update(self, event, data):
        if event == "task_completed":
            self.personality.update_context("celebration", data)
```

---

## Adicionando Novos Módulos

### 1. Criar Módulo Core

#### Estrutura Base

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Novo Módulo Core para Lumi Assistant

Descrição da funcionalidade do módulo
"""

from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class NovoModulo:
    """
    Descrição do módulo e sua responsabilidade
    """
    
    def __init__(self, config=None):
        """
        Inicializar módulo
        
        Args:
            config (dict): Configurações específicas do módulo
        """
        self.config = config or {}
        self.state = {}
        self._initialize()
        logger.info("NovoModulo inicializado")
    
    def _initialize(self):
        """Setup interno do módulo"""
        # Configuração inicial
        self.state = {
            "initialized_at": datetime.now(),
            "active": True
        }
    
    def process(self, data):
        """
        Método principal de processamento
        
        Args:
            data: Dados de entrada
            
        Returns:
            Resultado processado
            
        Raises:
            Exception: Quando processamento falha
        """
        try:
            logger.debug(f"Processando: {data}")
            result = self._internal_process(data)
            logger.debug(f"Resultado: {result}")
            return result
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            raise
    
    def _internal_process(self, data):
        """Lógica interna de processamento"""
        # Implementar lógica específica
        return data
    
    def get_status(self):
        """
        Obter status atual do módulo
        
        Returns:
            dict: Status do módulo
        """
        return {
            "active": self.state.get("active", False),
            "initialized_at": self.state.get("initialized_at"),
            "config": self.config
        }
```

#### Integrar no Core

1. **Adicionar ao `src/core/__init__.py`**:
```python
from .novo_modulo import NovoModulo

__all__ = [..., "NovoModulo"]
```

2. **Integrar no `src/core/assistant.py`**:
```python
def _initialize_modules(self):
    """Initialize all modular components"""
    try:
        # ... módulos existentes
        
        # Novo módulo
        self.novo_modulo = NovoModulo(config=self._get_module_config('novo_modulo'))
        
        logger.info("✅ Todos os módulos carregados com sucesso!")
    except Exception as e:
        logger.error(f"⚠️ Erro ao inicializar módulos: {e}")
```

3. **Adicionar uso no `process_message`**:
```python
def process_message(self, message):
    """Process message with modular intelligence"""
    try:
        # ... lógica existente
        
        # Verificar se precisa do novo módulo
        if self._should_use_novo_modulo(message):
            return self.novo_modulo.process(message)
            
        # ... resto da lógica
    except Exception as e:
        return f"🤖 Ops! Algo inesperado aconteceu: {str(e)}"

def _should_use_novo_modulo(self, message):
    """Verificar se deve usar o novo módulo"""
    keywords = ["palavra-chave", "trigger", "ativador"]
    return any(keyword in message.lower() for keyword in keywords)
```

### 2. Criar Módulo Utilitário

#### Estrutura para Utils

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Nova Utilidade para Lumi Assistant

Funcionalidade de apoio para outros módulos
"""

class NovaUtilidade:
    """
    Utilidade para funcionalidade específica
    """
    
    def __init__(self):
        """Inicializar utilidade"""
        self.cache = {}
    
    def util_method(self, input_data):
        """
        Método utilitário principal
        
        Args:
            input_data: Dados de entrada
            
        Returns:
            Dados processados
        """
        # Verificar cache
        cache_key = self._generate_cache_key(input_data)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Processar
        result = self._process_util(input_data)
        
        # Armazenar em cache
        self.cache[cache_key] = result
        return result
    
    def _process_util(self, data):
        """Lógica de processamento"""
        return data
    
    def _generate_cache_key(self, data):
        """Gerar chave de cache"""
        return hash(str(data))
```

#### Integrar Utils

1. **Adicionar ao `src/utils/__init__.py`**:
```python
from .nova_utilidade import NovaUtilidade

__all__ = [..., "NovaUtilidade"]
```

2. **Usar em módulos core**:
```python
from ..utils.nova_utilidade import NovaUtilidade

class AlgumModulo:
    def __init__(self):
        self.util = NovaUtilidade()
    
    def process(self, data):
        processed = self.util.util_method(data)
        return processed
```

---

## Estendendo Funcionalidades Existentes

### 1. Adicionando Novos Padrões de Detecção

#### Estender PatternDetector

```python
# Em src/utils/patterns.py

class PatternDetector:
    def __init__(self):
        # ... vocabulário existente
        
        # Adicionar novos padrões
        self.vocabulario.update({
            "nova_acao": [
                "nova", "acao", "keyword1", "keyword2"
            ],
            "outro_comando": [
                "comando", "especial", "trigger"
            ]
        })
        
        # Padrões regex específicos
        self.custom_patterns = {
            "nova_acao": [
                r"\b(?:fazer|executar)\s+nova\s+acao\s+(.+)",
                r"^nova\s+acao:\s*(.+)"
            ]
        }
    
    def detect_action(self, message):
        """Detecção estendida com novos padrões"""
        # Verificar padrões customizados primeiro
        for action, patterns in self.custom_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message.lower()):
                    return action
        
        # Continuar com lógica existente
        return self._detect_standard_action(message)
    
    def detect_custom_intent(self, message):
        """Novo método para intenção específica"""
        custom_keywords = ["custom", "especial", "novo"]
        return any(keyword in message.lower() for keyword in custom_keywords)
```

### 2. Expandindo Sistema de Personalidade

#### Adicionando Novos Traços

```python
# Em src/core/personality.py

class Personality:
    def __init__(self):
        # ... configuração existente
        
        # Novos traços de personalidade
        self.personality_traits.update({
            "expertise_level": "intermediate",    # beginner, intermediate, expert
            "response_length": "medium",          # short, medium, long
            "formality_level": "casual",          # formal, casual, friendly
            "emoji_usage": "moderate"             # none, minimal, moderate, high
        })
        
        # Novos contextos de usuário
        self.user_context.update({
            "expertise_area": None,
            "preferred_communication": "casual",
            "learning_style": "practical"
        })
    
    def get_expertise_response(self, topic, user_level="beginner"):
        """
        Resposta baseada no nível de expertise
        
        Args:
            topic (str): Tópico da consulta
            user_level (str): Nível do usuário
            
        Returns:
            str: Resposta adequada ao nível
        """
        if user_level == "beginner":
            return f"🌱 Vou explicar {topic} de forma bem simples..."
        elif user_level == "intermediate":
            return f"🚀 Sobre {topic}, você já sabe o básico, então..."
        else:
            return f"🎯 Para {topic} em nível avançado..."
    
    def adapt_communication_style(self, message_context):
        """
        Adaptar estilo de comunicação baseado no contexto
        
        Args:
            message_context (dict): Contexto da mensagem
        """
        if message_context.get("urgency_level", 0) > 2:
            self.personality_traits["response_length"] = "short"
            self.personality_traits["emoji_usage"] = "minimal"
        else:
            self.personality_traits["response_length"] = "medium"
            self.personality_traits["emoji_usage"] = "moderate"
```

### 3. Melhorando AI Engine

#### Adicionando Novos Providers

```python
# Em src/core/ai_engine.py

class AIEngine:
    def __init__(self):
        # ... configuração existente
        
        # Novos providers
        self.providers = {
            "gemini": self._call_gemini_api,
            "openrouter": self._call_openrouter_api,
            "custom_api": self._call_custom_api,      # Novo provider
            "local_model": self._call_local_model     # Modelo local
        }
        
        # Ordem de fallback configurável
        self.fallback_order = ["gemini", "openrouter", "custom_api", "local_model"]
    
    def _call_custom_api(self, messages):
        """
        Implementar nova API de IA
        
        Args:
            messages (list): Lista de mensagens
            
        Returns:
            str: Resposta da API
        """
        try:
            # Implementar chamada para nova API
            url = "https://nova-api.com/v1/chat"
            headers = {
                "Authorization": f"Bearer {os.getenv('CUSTOM_API_KEY')}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": messages,
                "model": "custom-model",
                "temperature": 0.7
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
            
        except Exception as e:
            logger.error(f"Erro na Custom API: {e}")
            raise
    
    def _call_local_model(self, messages):
        """
        Implementar modelo local (ex: Ollama)
        
        Args:
            messages (list): Lista de mensagens
            
        Returns:
            str: Resposta do modelo local
        """
        try:
            # Exemplo com Ollama
            import ollama
            
            response = ollama.chat(
                model="llama3.1",
                messages=messages
            )
            
            return response["message"]["content"]
            
        except Exception as e:
            logger.error(f"Erro no modelo local: {e}")
            raise
    
    def add_provider(self, name, handler_function):
        """
        Adicionar novo provider dinamicamente
        
        Args:
            name (str): Nome do provider
            handler_function (callable): Função que processa mensagens
        """
        self.providers[name] = handler_function
        logger.info(f"Provider '{name}' adicionado")
```

---

## Criando Plugins

### 1. Sistema de Plugin Base

```python
# src/plugins/base_plugin.py

from abc import ABC, abstractmethod

class BasePlugin(ABC):
    """
    Classe base para todos os plugins
    """
    
    def __init__(self, name, version="1.0.0"):
        """
        Inicializar plugin base
        
        Args:
            name (str): Nome do plugin
            version (str): Versão do plugin
        """
        self.name = name
        self.version = version
        self.enabled = True
        self.dependencies = []
    
    @abstractmethod
    def initialize(self, assistant_context):
        """
        Inicializar plugin com contexto do assistente
        
        Args:
            assistant_context: Contexto do assistente principal
        """
        pass
    
    @abstractmethod
    def process(self, message, context):
        """
        Processar mensagem se aplicável
        
        Args:
            message (str): Mensagem do usuário
            context (dict): Contexto da conversação
            
        Returns:
            str or None: Resposta do plugin ou None se não aplicável
        """
        pass
    
    @abstractmethod
    def can_handle(self, message, context):
        """
        Verificar se plugin pode processar a mensagem
        
        Args:
            message (str): Mensagem do usuário
            context (dict): Contexto da conversação
            
        Returns:
            bool: True se pode processar
        """
        pass
    
    def get_info(self):
        """
        Obter informações do plugin
        
        Returns:
            dict: Informações do plugin
        """
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "dependencies": self.dependencies
        }
```

### 2. Plugin de Exemplo: Weather

```python
# src/plugins/weather_plugin.py

import requests
from .base_plugin import BasePlugin

class WeatherPlugin(BasePlugin):
    """
    Plugin para consultas meteorológicas
    """
    
    def __init__(self):
        super().__init__("Weather", "1.0.0")
        self.api_key = None
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    def initialize(self, assistant_context):
        """Inicializar plugin com API key"""
        import os
        self.api_key = os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            self.enabled = False
            print("⚠️ Weather plugin desabilitado: API key não encontrada")
    
    def can_handle(self, message, context):
        """Verificar se é consulta meteorológica"""
        weather_keywords = [
            "tempo", "weather", "clima", "temperatura", 
            "chuva", "sol", "previsão"
        ]
        return any(keyword in message.lower() for keyword in weather_keywords)
    
    def process(self, message, context):
        """Processar consulta meteorológica"""
        if not self.enabled:
            return "⛅ Serviço meteorológico temporariamente indisponível"
        
        try:
            # Extrair cidade da mensagem
            city = self._extract_city(message)
            if not city:
                city = "São Paulo"  # Cidade padrão
            
            # Buscar dados do tempo
            weather_data = self._get_weather(city)
            
            # Formatar resposta
            return self._format_weather_response(weather_data, city)
            
        except Exception as e:
            return f"🌦️ Não consegui obter informações meteorológicas: {str(e)}"
    
    def _extract_city(self, message):
        """Extrair nome da cidade da mensagem"""
        # Implementar extração de cidade
        import re
        
        patterns = [
            r"tempo em (.+)",
            r"clima de (.+)",
            r"previsão para (.+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message.lower())
            if match:
                return match.group(1).strip()
        
        return None
    
    def _get_weather(self, city):
        """Obter dados meteorológicos da API"""
        url = f"{self.base_url}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": "pt_br"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        return response.json()
    
    def _format_weather_response(self, data, city):
        """Formatar resposta meteorológica"""
        temp = data["main"]["temp"]
        description = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        return f"""🌤️ **Tempo em {city}**
        
📊 **Temperatura**: {temp}°C
🌥️ **Condição**: {description.title()}
💧 **Umidade**: {humidity}%

Que tal aproveitar o tempo para ser produtivo? 🚀"""
```

### 3. Sistema de Gerenciamento de Plugins

```python
# src/plugins/plugin_manager.py

import os
import importlib
from typing import List, Dict, Any

class PluginManager:
    """
    Gerenciador de plugins para Lumi
    """
    
    def __init__(self):
        """Inicializar gerenciador"""
        self.plugins = {}
        self.plugin_order = []
        self.assistant_context = None
    
    def initialize(self, assistant_context):
        """
        Inicializar com contexto do assistente
        
        Args:
            assistant_context: Contexto do assistente principal
        """
        self.assistant_context = assistant_context
        self.load_plugins()
    
    def load_plugins(self):
        """Carregar todos os plugins disponíveis"""
        plugin_dir = os.path.join(os.path.dirname(__file__))
        
        for filename in os.listdir(plugin_dir):
            if filename.endswith("_plugin.py") and filename != "base_plugin.py":
                plugin_name = filename[:-3]  # Remove .py
                
                try:
                    self._load_plugin(plugin_name)
                except Exception as e:
                    print(f"⚠️ Erro ao carregar plugin {plugin_name}: {e}")
    
    def _load_plugin(self, plugin_name):
        """Carregar plugin específico"""
        module = importlib.import_module(f".{plugin_name}", package="plugins")
        
        # Encontrar classe do plugin
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                hasattr(attr, "initialize") and 
                attr_name.endswith("Plugin")):
                
                # Instanciar plugin
                plugin_instance = attr()
                plugin_instance.initialize(self.assistant_context)
                
                # Registrar plugin
                self.plugins[plugin_instance.name] = plugin_instance
                self.plugin_order.append(plugin_instance.name)
                
                print(f"✅ Plugin '{plugin_instance.name}' carregado")
                break
    
    def process_message(self, message, context):
        """
        Processar mensagem através dos plugins
        
        Args:
            message (str): Mensagem do usuário
            context (dict): Contexto da conversação
            
        Returns:
            str or None: Resposta do plugin ou None
        """
        for plugin_name in self.plugin_order:
            plugin = self.plugins[plugin_name]
            
            if plugin.enabled and plugin.can_handle(message, context):
                try:
                    response = plugin.process(message, context)
                    if response:
                        return response
                except Exception as e:
                    print(f"⚠️ Erro no plugin {plugin_name}: {e}")
                    continue
        
        return None
    
    def get_plugin_info(self):
        """Obter informações de todos os plugins"""
        return {
            name: plugin.get_info() 
            for name, plugin in self.plugins.items()
        }
    
    def enable_plugin(self, plugin_name):
        """Habilitar plugin específico"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_name):
        """Desabilitar plugin específico"""
        if plugin_name in self.plugins:
            self.plugins[plugin_name].enabled = False
            return True
        return False
```

### 4. Integração com Assistant

```python
# Em src/core/assistant.py

class LumiAssistant:
    def __init__(self, task_manager, reports_generator):
        # ... inicialização existente
        
        # Inicializar sistema de plugins
        from plugins.plugin_manager import PluginManager
        self.plugin_manager = PluginManager()
        self.plugin_manager.initialize(self)
    
    def process_message(self, message):
        """Process message with plugin support"""
        try:
            # ... análise de contexto existente
            
            # Verificar plugins primeiro
            plugin_response = self.plugin_manager.process_message(message, context)
            if plugin_response:
                return plugin_response
            
            # Continuar com lógica existente
            action = self.pattern_detector.detect_action(message)
            # ... resto da lógica
            
        except Exception as e:
            return f"🤖 Ops! Algo inesperado aconteceu: {str(e)}"
```

---

## Testes e Qualidade

### 1. Estrutura de Testes

```python
# tests/test_novo_modulo.py

import unittest
from unittest.mock import Mock, patch
from core.novo_modulo import NovoModulo

class TestNovoModulo(unittest.TestCase):
    """Testes para NovoModulo"""
    
    def setUp(self):
        """Setup para cada teste"""
        self.config = {"test": True}
        self.modulo = NovoModulo(self.config)
    
    def test_initialization(self):
        """Testar inicialização"""
        self.assertIsNotNone(self.modulo)
        self.assertEqual(self.modulo.config, self.config)
        self.assertTrue(self.modulo.state["active"])
    
    def test_process_valid_data(self):
        """Testar processamento com dados válidos"""
        data = {"test": "data"}
        result = self.modulo.process(data)
        self.assertIsNotNone(result)
    
    def test_process_invalid_data(self):
        """Testar processamento com dados inválidos"""
        with self.assertRaises(ValueError):
            self.modulo.process(None)
    
    @patch('core.novo_modulo.external_service')
    def test_external_dependency(self, mock_service):
        """Testar com dependência externa mockada"""
        mock_service.return_value = "mocked_result"
        
        result = self.modulo.process({"external": True})
        self.assertEqual(result, "mocked_result")
        mock_service.assert_called_once()
    
    def test_get_status(self):
        """Testar obtenção de status"""
        status = self.modulo.get_status()
        self.assertIn("active", status)
        self.assertIn("initialized_at", status)
        self.assertIn("config", status)

class TestNovoModuloIntegration(unittest.TestCase):
    """Testes de integração"""
    
    def setUp(self):
        """Setup para testes de integração"""
        from task_manager import TaskManager
        from reports_generator import ReportsGenerator
        from core.assistant import LumiAssistant
        
        self.task_manager = TaskManager()
        self.reports = ReportsGenerator(self.task_manager)
        self.assistant = LumiAssistant(self.task_manager, self.reports)
    
    def test_module_integration(self):
        """Testar integração com assistente"""
        # Verificar se módulo foi carregado
        self.assertIsNotNone(self.assistant.novo_modulo)
        
        # Testar uso através do assistente
        response = self.assistant.process_message("trigger para novo modulo")
        self.assertIsInstance(response, str)

# Executar testes
if __name__ == "__main__":
    unittest.main()
```

### 2. Testes de Performance

```python
# tests/test_performance.py

import time
import unittest
import memory_profiler
from core.ai_engine import AIEngine

class TestPerformance(unittest.TestCase):
    """Testes de performance"""
    
    def setUp(self):
        self.ai_engine = AIEngine()
    
    def test_response_time(self):
        """Testar tempo de resposta"""
        messages = [{"role": "user", "content": "Teste rápido"}]
        
        start_time = time.time()
        response = self.ai_engine.call_ai_api(messages)
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 5.0, "Resposta muito lenta")
    
    @memory_profiler.profile
    def test_memory_usage(self):
        """Testar uso de memória"""
        # Criar muitas instâncias
        engines = [AIEngine() for _ in range(100)]
        
        # Fazer muitas chamadas
        for engine in engines[:10]:
            engine.call_ai_api([{"role": "user", "content": "test"}])
        
        # Verificar se memória é liberada
        del engines
    
    def test_concurrent_requests(self):
        """Testar requisições concorrentes"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def worker():
            response = self.ai_engine.call_ai_api([
                {"role": "user", "content": "Teste concorrente"}
            ])
            results.put(response)
        
        # Criar threads
        threads = [threading.Thread(target=worker) for _ in range(5)]
        
        # Executar
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Verificar resultados
        self.assertEqual(results.qsize(), 5)
        self.assertLess(end_time - start_time, 10.0)
```

### 3. Code Quality

```python
# setup.cfg para flake8
[flake8]
max-line-length = 88
ignore = E203, W503
exclude = .git,__pycache__,.venv

# pyproject.toml para black
[tool.black]
line-length = 88
target-version = ['py37']
include = '\.pyi?$'

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.942
    hooks:
      - id: mypy
```

---

## Deployment e Distribuição

### 1. Docker Configuration

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY src/ ./src/
COPY scripts/ ./scripts/

# Criar diretório de dados
RUN mkdir -p src/data

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app/src
ENV FLASK_APP=src/lumi_api.py

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "src/lumi_api.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  lumi-assistant:
    build: .
    ports:
      - "5000:5000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./data:/app/src/data
    restart: unless-stopped
    
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### 2. CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov flake8 black
    
    - name: Lint with flake8
      run: |
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
    
    - name: Format check with black
      run: |
        black --check src/
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=src/ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      run: |
        # Adicionar script de deploy
        echo "Deploying to production..."
```

### 3. Package Distribution

```python
# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lumi-ai-assistant",
    version="2.0.0",
    author="Lumi AI Team",
    author_email="team@lumi-ai.com",
    description="Modular AI Assistant for Productivity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lumi-ai/lumi-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1",
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
        "psutil>=5.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "plugins": [
            "ollama>=0.1.0",
            "opencv-python>=4.5.0",
            "speechrecognition>=3.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "lumi=main:main",
            "lumi-api=lumi_api:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yml", "*.yaml"],
    },
)
```

---

## Best Practices

### 1. Código Limpo

#### Nomenclatura
```python
# ✅ Bom
def extract_task_title_from_message(message: str) -> str:
    """Extract clean task title from user message"""
    pass

# ❌ Ruim
def eTtFm(msg):
    pass
```

#### Funções Pequenas
```python
# ✅ Bom - Função com responsabilidade única
def validate_task_title(title: str) -> bool:
    """Validate if task title is meaningful"""
    if not title or len(title.strip()) < 3:
        return False
    
    return not _is_only_connectors(title)

def _is_only_connectors(title: str) -> bool:
    """Check if title contains only connector words"""
    connectors = ["e", "ou", "de", "para", "com", "em"]
    words = title.lower().split()
    return all(word in connectors for word in words)

# ❌ Ruim - Função fazendo muitas coisas
def process_user_input(message):
    # 50 linhas de código fazendo várias coisas
    pass
```

#### Documentação
```python
def analyze_mood_context(message: str, history: List[Dict]) -> Dict:
    """
    Analyze user mood and emotional context from message.
    
    This function examines the user's message for emotional indicators,
    urgency markers, and politeness level to provide personalized responses.
    
    Args:
        message (str): The user's input message to analyze
        history (List[Dict]): Previous conversation history for context
        
    Returns:
        Dict: Analysis results containing:
            - mood (str): Detected mood ('stressed', 'motivated', 'neutral')
            - urgency_level (int): Number of urgency indicators found
            - politeness_level (int): Politeness score (0-1)
            - trend (str): Recent mood trend from history
            
    Example:
        >>> analyze_mood_context("Preciso urgente terminar isso!", [])
        {
            'mood': 'stressed',
            'urgency_level': 1,
            'politeness_level': 0,
            'trend': 'neutral'
        }
        
    Note:
        This function maintains conversation history limited to last 10 entries
        for performance and privacy considerations.
    """
```

### 2. Error Handling

#### Specific Exceptions
```python
class LumiException(Exception):
    """Base exception for Lumi Assistant"""
    pass

class AIEngineError(LumiException):
    """Raised when AI engine encounters an error"""
    pass

class TaskValidationError(LumiException):
    """Raised when task validation fails"""
    pass

# Uso
def add_task(title: str) -> bool:
    try:
        if not self._validate_title(title):
            raise TaskValidationError(f"Invalid task title: {title}")
        
        return self._save_task(title)
        
    except TaskValidationError:
        logger.warning(f"Task validation failed for: {title}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding task: {e}")
        raise LumiException(f"Failed to add task: {str(e)}") from e
```

#### Graceful Degradation
```python
def get_ai_response(message: str) -> str:
    """Get AI response with fallback to static responses"""
    try:
        # Tentar AI principal
        return self.ai_engine.call_ai_api(message)
        
    except AIEngineError:
        logger.warning("AI engine failed, using fallback")
        
        # Fallback para respostas estáticas
        return self._get_static_response(message)
        
    except Exception as e:
        logger.error(f"Complete AI failure: {e}")
        
        # Última opção
        return "🤖 Estou temporariamente indisponível, mas suas tarefas estão seguras!"
```

### 3. Performance

#### Caching
```python
from functools import lru_cache
import hashlib

class PatternDetector:
    def __init__(self):
        self._pattern_cache = {}
    
    @lru_cache(maxsize=100)
    def detect_action(self, message: str) -> str:
        """Cached action detection"""
        return self._internal_detect_action(message)
    
    def detect_with_custom_cache(self, message: str) -> str:
        """Custom caching implementation"""
        cache_key = hashlib.md5(message.encode()).hexdigest()
        
        if cache_key in self._pattern_cache:
            return self._pattern_cache[cache_key]
        
        result = self._internal_detect_action(message)
        
        # Limitar tamanho do cache
        if len(self._pattern_cache) > 1000:
            oldest_key = next(iter(self._pattern_cache))
            del self._pattern_cache[oldest_key]
        
        self._pattern_cache[cache_key] = result
        return result
```

#### Lazy Loading
```python
class LumiAssistant:
    def __init__(self):
        self._ai_engine = None
        self._personality = None
        
    @property
    def ai_engine(self):
        """Lazy load AI engine"""
        if self._ai_engine is None:
            self._ai_engine = AIEngine()
        return self._ai_engine
    
    @property
    def personality(self):
        """Lazy load personality module"""
        if self._personality is None:
            self._personality = Personality()
        return self._personality
```

### 4. Security

#### Input Validation
```python
import re
from typing import Optional

def sanitize_user_input(message: str) -> Optional[str]:
    """
    Sanitize user input for security
    
    Args:
        message (str): Raw user input
        
    Returns:
        Optional[str]: Sanitized message or None if invalid
    """
    if not message or not isinstance(message, str):
        return None
    
    # Remover caracteres perigosos
    message = re.sub(r'[<>"\']', '', message)
    
    # Limitar tamanho
    if len(message) > 1000:
        message = message[:1000]
    
    # Verificar se ainda é válido
    if len(message.strip()) < 1:
        return None
    
    return message.strip()

def validate_api_key(key: str) -> bool:
    """Validate API key format"""
    if not key or not isinstance(key, str):
        return False
    
    # Verificar formato básico (exemplo)
    pattern = r'^[a-zA-Z0-9\-_]{20,}$'
    return re.match(pattern, key) is not None
```

#### Rate Limiting
```python
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int = 60, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed for identifier"""
        now = time.time()
        
        # Limpar requests antigos
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        # Verificar limite
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        # Adicionar request atual
        self.requests[identifier].append(now)
        return True

# Uso na API
rate_limiter = RateLimiter()

@app.route('/message', methods=['POST'])
def process_message():
    client_ip = request.remote_addr
    
    if not rate_limiter.is_allowed(client_ip):
        return jsonify({"error": "Rate limit exceeded"}), 429
    
    # Processar normalmente
    pass
```

---

## Conclusão

Este guia de implementação fornece uma base sólida para estender e melhorar o Lumi AI Assistant. Seguindo estes padrões e práticas, você pode:

1. **Criar novos módulos** que se integram naturalmente ao sistema
2. **Desenvolver plugins** para funcionalidades específicas
3. **Manter código limpo** e bem documentado
4. **Implementar testes** abrangentes e confiáveis
5. **Deploying safely** com CI/CD automatizado

### Próximos Passos Recomendados

1. **Configurar ambiente de desenvolvimento** com pre-commit hooks
2. **Implementar logging estruturado** para melhor debugging
3. **Adicionar métricas de performance** para monitoramento
4. **Criar documentação de API** automatizada
5. **Estabelecer processo de review** de código

### Recursos Adicionais

- **Código fonte**: GitHub repository
- **Documentação**: Technical docs e API reference
- **Comunidade**: Discord/Slack para desenvolvedores
- **Issues**: GitHub issues para bugs e features

---

**Lumi AI Assistant 2.0** - Implementation Guide for Developers

*Versão 1.0 - Guia de Implementação Completo*

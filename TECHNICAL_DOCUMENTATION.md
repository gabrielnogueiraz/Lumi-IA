# Lumi AI Assistant - Documentação Técnica Completa

## Índice

1. [Visão Geral do Sistema](#visão-geral-do-sistema)
2. [Arquitetura Modular](#arquitetura-modular)
3. [Módulos do Core](#módulos-do-core)
4. [Módulos Utilitários](#módulos-utilitários)
5. [Integração de IA](#integração-de-ia)
6. [Gerenciamento de Tarefas](#gerenciamento-de-tarefas)
7. [Sistema de Personalidade](#sistema-de-personalidade)
8. [Detecção de Padrões](#detecção-de-padrões)
9. [Análise de Humor](#análise-de-humor)
10. [API REST](#api-rest)
11. [Sistema de Fallback](#sistema-de-fallback)
12. [Implantação e Configuração](#implantação-e-configuração)
13. [Guia do Desenvolvedor](#guia-do-desenvolvedor)
14. [Exemplos de Uso](#exemplos-de-uso)
15. [Solução de Problemas](#solução-de-problemas)

---

## Visão Geral do Sistema

### Descrição Geral

Lumi é um assistente de IA modular e inteligente projetado para gerenciamento de produtividade. O sistema foi refatorado de uma arquitetura monolítica para uma arquitetura modular avançada, mantendo total compatibilidade com versões anteriores.

### Principais Características

- **Arquitetura Modular**: Sistema organizado em módulos especializados
- **IA Dual**: Google Gemini como principal, OpenRouter como fallback
- **Consciência Contextual**: Sistema de memória e análise de contexto
- **Processamento Múltiplo**: Capacidade de processar múltiplas tarefas simultaneamente
- **Personalidade Adaptativa**: Respostas personalizadas baseadas no humor do usuário
- **Compatibilidade Reversa**: Mantém compatibilidade total com versões anteriores

### Versões

- **Versão Atual**: 2.0.0
- **Arquitetura**: Modular com Fallback Automático
- **Linguagem**: Python 3.7+
- **Dependências**: Requests, Flask, PSUtil

---

## Arquitetura Modular

### Estrutura de Diretórios

```
lumi-AI/
├── src/
│   ├── core/                    # Módulos principais
│   │   ├── __init__.py         # Exportações do core
│   │   ├── ai_engine.py        # Engine de IA (Gemini/OpenRouter)
│   │   ├── assistant.py        # Assistente modular principal
│   │   ├── education.py        # Módulo educacional
│   │   ├── personality.py      # Sistema de personalidade
│   │   └── task_handler.py     # Manipulador de tarefas
│   ├── utils/                   # Módulos utilitários
│   │   ├── __init__.py         # Exportações dos utils
│   │   ├── mood_analyzer.py    # Analisador de humor
│   │   └── patterns.py         # Detector de padrões
│   ├── ai_assistant.py         # Wrapper de compatibilidade
│   ├── lumi_api.py            # API REST Flask
│   ├── task_manager.py        # Gerenciador de dados
│   └── main.py                # Ponto de entrada principal
├── requirements.txt           # Dependências Python
└── README.md                 # Documentação básica
```

### Fluxo de Importação

O sistema implementa um mecanismo de importação híbrido:

```python
# Tentativa de importação relativa
try:
    from .ai_engine import AIEngine
    from ..utils.patterns import PatternDetector
except ImportError:
    # Fallback para importação absoluta
    from core.ai_engine import AIEngine
    from utils.patterns import PatternDetector
```

### Padrão de Design

- **Modular**: Cada funcionalidade em módulo separado
- **Dependency Injection**: Dependências injetadas na inicialização
- **Wrapper Pattern**: Mantém compatibilidade com API anterior
- **Fallback Pattern**: Sistema de emergência para falhas

---

## Módulos do Core

### 1. AIEngine (`core/ai_engine.py`)

**Responsabilidade**: Gerenciar comunicação com APIs de IA.

#### Características Principais

- **IA Primária**: Google Gemini (gemini-1.5-flash)
- **IA Secundária**: OpenRouter com múltiplos modelos
- **Fallback Automático**: Troca automática em caso de falha
- **Tipos de Resposta**: Especializadas por contexto

#### Métodos Principais

```python
class AIEngine:
    def __init__(self):
        """Inicializa engine com configuração dual"""
        
    def call_ai_api(self, messages):
        """Chama API de IA com fallback automático"""
        
    def generate_task_response(self, context, message, task_info=None):
        """Gera respostas específicas para tarefas"""
        
    def generate_educational_explanation(self, topic, message):
        """Gera explicações educacionais"""
        
    def generate_general_response(self, message):
        """Gera respostas gerais"""
```

#### Configuração de IA

```python
# Google Gemini (Primário)
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

# OpenRouter (Fallback)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
FALLBACK_MODELS = [
    "anthropic/claude-3.5-sonnet",
    "openai/gpt-4o-mini",
    "meta-llama/llama-3.1-8b-instruct:free"
]
```

### 2. Assistant (`core/assistant.py`)

**Responsabilidade**: Orquestração principal do sistema modular.

#### Características Principais

- **Inicialização Modular**: Carrega todos os módulos
- **Processamento Inteligente**: Detecta intenções e roteia ações
- **Memória Conversacional**: Mantém contexto das interações
- **Integração Completa**: Conecta todos os módulos

#### Fluxo de Processamento

```python
def process_message(self, message):
    """
    1. Analisa contexto e humor
    2. Atualiza memória conversacional
    3. Detecta ação via patterns
    4. Verifica se é consulta educacional
    5. Processa ação específica
    6. Retorna resposta personalizada
    """
```

#### Métodos de Inicialização

```python
def _initialize_modules(self):
    """
    Inicializa todos os módulos:
    - AIEngine: Comunicação com IA
    - Personality: Sistema de personalidade
    - Education: Módulo educacional
    - PatternDetector: Detecção de padrões
    - MoodAnalyzer: Análise de humor
    - TaskHandler: Manipulação de tarefas
    """
```

### 3. TaskHandler (`core/task_handler.py`)

**Responsabilidade**: Gerenciar operações de tarefas com IA.

#### Características Principais

- **Extração Inteligente**: Parsing avançado de tarefas
- **Processamento Múltiplo**: Suporte a listas numeradas
- **Validação**: Verificação de títulos válidos
- **Consciência**: Atualização de contexto após ações

#### Métodos de Processamento

```python
class TaskHandler:
    def process_add_task(self, message):
        """Adiciona tarefas com parsing inteligente"""
        
    def process_list_tasks(self, message):
        """Lista tarefas com respostas personalizadas"""
        
    def process_complete_task(self, message):
        """Completa tarefas com confirmação"""
        
    def process_remove_task(self, message):
        """Remove tarefas ou todas (mass removal)"""
```

#### Extração de Tarefas

```python
def _extract_single_task_improved(self, message):
    """
    Extração inteligente melhorada:
    1. Remove comandos conhecidos
    2. Limpa conectores desnecessários
    3. Valida título resultante
    4. Retorna tarefa estruturada
    """
```

### 4. Personality (`core/personality.py`)

**Responsabilidade**: Gerenciar personalidade e estilo de resposta.

#### Características Principais

- **Traços de Personalidade**: Estado emocional configurável
- **Memória Conversacional**: Histórico de interações
- **Respostas Contextuais**: Baseadas em ações e sucesso
- **Análise de Tendências**: Padrões de humor do usuário

#### Sistema de Personalidade

```python
personality_traits = {
    "emotional_state": "enthusiastic",
    "energy_level": 0.8,
    "conversation_style": "friendly_professional",
    "humor_level": 0.6,
    "motivation_mode": "encouraging"
}
```

#### Tipos de Resposta

```python
def get_personality_response_style(self, action_type, success=True):
    """
    Estilos disponíveis:
    - task_added: Resposta para tarefa adicionada
    - task_completed: Resposta para tarefa concluída
    - task_removed: Resposta para tarefa removida
    - tasks_listed: Resposta para listagem
    - casual: Interações casuais
    """
```

### 5. Education (`core/education.py`)

**Responsabilidade**: Processar consultas educacionais com IA.

#### Características Principais

- **Detecção Educacional**: Identifica perguntas de aprendizado
- **Explicações Especializadas**: Respostas didáticas
- **Dicas de Estudo**: Sugestões motivacionais
- **Integração com IA**: Respostas geradas dinamicamente

#### Detecção de Intenção

```python
def detect_educational_intent(self, message):
    """
    Detecta perguntas educacionais por:
    - Palavras interrogativas
    - Verbos de aprendizado
    - Solicitações de explicação
    - Contexto acadêmico
    """
```

---

## Módulos Utilitários

### 1. PatternDetector (`utils/patterns.py`)

**Responsabilidade**: Detectar padrões e intenções em mensagens.

#### Vocabulário Expandido

```python
vocabulario = {
    "adicionar": ["adicionar", "criar", "nova", "preciso", "tenho que", ...],
    "listar": ["listar", "mostrar", "ver", "quais", "minhas tarefas", ...],
    "concluir": ["concluir", "terminei", "pronto", "finalizar", ...],
    "remover": ["remover", "deletar", "excluir", "cancelar", ...],
    "relatório": ["relatório", "resumo", "estatística", "progresso", ...],
    "editar": ["editar", "alterar", "modificar", "mudar", ...]
}
```

#### Algoritmo de Detecção

```python
def detect_action(self, message):
    """
    1. Verifica padrões regex específicos
    2. Analisa palavras-chave com pontuação
    3. Detecta contexto educacional
    4. Identifica verbos de ação
    5. Retorna ação mais provável
    """
```

### 2. MoodAnalyzer (`utils/mood_analyzer.py`)

**Responsabilidade**: Analisar humor e contexto emocional.

#### Indicadores de Humor

```python
stress_indicators = ["estressado", "cansado", "difícil", "complicado"]
motivation_indicators = ["motivado", "animado", "pronto", "vamos"]
urgency_indicators = ["urgente", "rápido", "importante", "prioridade"]
```

#### Análise Contextual

```python
def analyze_context_and_mood(self, message):
    """
    Retorna:
    - mood: stressed/motivated/neutral
    - urgency_level: 0-N baseado em indicadores
    - politeness_level: 0-1 baseado em cortesia
    - mood_trend: tendência recente
    """
```

---

## Integração de IA

### Configuração Dual

O sistema utiliza duas APIs de IA com fallback automático:

#### Google Gemini (Primário)

```python
# Configuração
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-1.5-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

# Parâmetros de geração
generation_config = {
    "temperature": 0.7,
    "maxOutputTokens": 1000,
    "topP": 0.95
}
```

#### OpenRouter (Fallback)

```python
# Modelos de fallback
FALLBACK_MODELS = [
    "anthropic/claude-3.5-sonnet",      # Mais capaz
    "openai/gpt-4o-mini",               # Rápido e eficiente
    "meta-llama/llama-3.1-8b-instruct:free"  # Gratuito
]
```

### Tipos de Prompts

#### Para Tarefas

```python
system_content = f"""Você é Lumi, uma assistente de produtividade carismática.
O usuário acabou de {context} a tarefa: "{task_title}"
Responda de forma entusiasmada, motivacional e personalizada.
Máximo 100 palavras."""
```

#### Para Educação

```python
system_content = f"""Você é Lumi, uma assistente educacional didática.
Explique sobre {topic} de forma clara, simples e motivadora.
Inclua sempre uma sugestão para criar uma tarefa de estudo.
Máximo 200 palavras."""
```

---

## Gerenciamento de Tarefas

### Estrutura de Dados

```python
# Tarefa individual
task = {
    "id": unique_id,
    "title": "Título da tarefa",
    "completed": False,
    "created_at": datetime.now(),
    "completed_at": None,
    "priority": "normal",  # low, normal, high
    "category": "general"
}
```

### Operações Principais

#### Adição de Tarefas

```python
def add_task(self, title, priority="normal", category="general"):
    """
    1. Valida título
    2. Cria objeto tarefa
    3. Salva em arquivo JSON
    4. Retorna confirmação
    """
```

#### Processamento Múltiplo

```python
def _extract_multiple_tasks_improved(self, message):
    """
    Detecta listas numeradas:
    1. Primeira tarefa
    2. Segunda tarefa
    3. Terceira tarefa
    
    Retorna array de tarefas válidas
    """
```

### Validação de Títulos

```python
def _is_valid_task_title(self, title):
    """
    Verifica:
    - Comprimento mínimo (3 caracteres)
    - Não é apenas conectores
    - Não contém apenas números
    - Possui substantivos ou verbos
    """
```

---

## Sistema de Personalidade

### Traços Configuráveis

```python
personality_traits = {
    "emotional_state": "enthusiastic",     # enthusiastic, supportive, focused
    "energy_level": 0.8,                   # 0.0 to 1.0
    "conversation_style": "friendly_professional",
    "humor_level": 0.6,                    # Sutil, não exagerado
    "motivation_mode": "encouraging"
}
```

### Contexto do Usuário

```python
user_context = {
    "current_focus": None,
    "productivity_patterns": [],
    "preferences": {},
    "interaction_count": 0,
    "last_task_added": None,
    "mood_indicators": [],
    "last_action": None,
    "last_action_details": None,
    "last_action_success": None
}
```

### Respostas Contextuais

O sistema gera respostas baseadas em:

- **Tipo de ação**: Adicionar, completar, remover, listar
- **Sucesso da operação**: True/False
- **Humor detectado**: Stress, motivação, neutro
- **Histórico de interações**: Padrões de uso

### Memória Conversacional

```python
def update_conversation_memory(self, message, context):
    """
    Mantém histórico de 20 interações:
    - Timestamp da mensagem
    - Conteúdo da mensagem
    - Contexto detectado
    - Incrementa contador de interações
    """
```

---

## Detecção de Padrões

### Algoritmo Inteligente

O `PatternDetector` utiliza um algoritmo em camadas:

#### 1. Padrões Regex

```python
action_patterns = {
    "adicionar": [
        r"\b(?:adicionar|criar|nova?)\s+(?:tarefa)?\s*[:\-]?\s*(.+)",
        r"\b(?:preciso|tenho que|vou)\s+(.+)",
        r"^(?:fazer|estudar|comprar)\s+(.+)"
    ]
}
```

#### 2. Análise de Palavras-chave

```python
def detect_action(self, message):
    """
    1. Verifica padrões específicos (score alto)
    2. Analisa palavras-chave (score baseado em relevância)
    3. Considera comprimento das palavras
    4. Retorna ação com maior pontuação
    """
```

#### 3. Detecção Contextual

- **Educacional**: Perguntas, explicações, conceitos
- **Casual**: Saudações, agradecimentos, despedidas
- **Urgência**: Indicadores de prioridade temporal

### Remoção em Massa

```python
def detect_mass_removal(self, message):
    """
    Detecta solicitações como:
    - "remover todas as tarefas"
    - "limpar lista"
    - "deletar tudo"
    """
```

---

## Análise de Humor

### Indicadores Emocionais

O `MoodAnalyzer` identifica:

#### Estados de Humor

- **Stressed**: "estressado", "cansado", "difícil", "problema"
- **Motivated**: "motivado", "animado", "pronto", "vamos"
- **Neutral**: Estado padrão sem indicadores específicos

#### Nível de Urgência

Baseado em palavras como:
- "urgente", "rápido", "importante", "prioridade", "hoje"

#### Nível de Cortesia

Detecta:
- "por favor", "obrigado", "obrigada", "please", "thanks"

### Histórico de Humor

```python
mood_history = [
    {
        "timestamp": datetime.now(),
        "mood": "motivated",
        "urgency": 1,
        "message_length": 25
    }
]
```

### Sugestões Baseadas em Humor

```python
def get_mood_based_suggestion(self, context):
    """
    Stressed: "Respirar fundo e focar numa tarefa de cada vez"
    Urgent: "Detectei que é importante! Que tal começar por essa?"
    Motivated: "Adorei sua energia! Vamos canalizar isso"
    """
```

---

## API REST

### Estrutura da API (`lumi_api.py`)

#### Configuração Flask

```python
app = Flask(__name__)
CORS(app)  # Permite CORS para frontend

# Inicialização global
task_manager = TaskManager()
reports_generator = ReportsGenerator(task_manager)
lumi = LumiAssistant(task_manager, reports_generator)
```

#### Endpoints Principais

##### POST /message
```python
@app.route('/message', methods=['POST'])
def process_message():
    """
    Processa mensagem do usuário
    
    Body: {"message": "sua mensagem aqui"}
    Response: {"response": "resposta da Lumi"}
    """
```

##### GET /tasks
```python
@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Retorna lista de tarefas
    
    Response: {"tasks": [...]}
    """
```

##### POST /tasks
```python
@app.route('/tasks', methods=['POST'])
def add_task():
    """
    Adiciona nova tarefa
    
    Body: {"title": "título da tarefa"}
    Response: {"message": "confirmação"}
    """
```

##### PUT /tasks/:id/complete
```python
@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    """
    Marca tarefa como concluída
    
    Response: {"message": "confirmação"}
    """
```

#### Tratamento de Erros

```python
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erro interno do servidor"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint não encontrado"}), 404
```

### Configuração CORS

```python
CORS(app, origins=["http://localhost:3000", "http://localhost:8080"])
```

---

## Sistema de Fallback

### Wrapper de Compatibilidade

O arquivo `ai_assistant.py` funciona como wrapper que:

#### 1. Tentativa Modular

```python
try:
    from core.assistant import LumiAssistant as ModularLumiAssistant
    modular_available = True
except ImportError:
    modular_available = False
```

#### 2. Inicialização Híbrida

```python
def __init__(self, task_manager, reports_generator):
    if modular_available:
        try:
            self._modular_assistant = ModularLumiAssistant(task_manager, reports_generator)
            self._use_modular = True
        except Exception:
            self._use_modular = False
            self._init_fallback()
```

#### 3. Delegação de Métodos

```python
def process_message(self, message):
    if self._use_modular and self._modular_assistant:
        try:
            return self._modular_assistant.process_message(message)
        except Exception:
            # Fallback automático
            pass
    
    # Sistema de emergência
    return self._legacy_assistant.process_message(message)
```

### Vantagens do Sistema

- **Compatibilidade Total**: Código antigo funciona sem modificações
- **Degradação Graceful**: Falha de módulos não quebra o sistema
- **Transição Suave**: Permite migração gradual
- **Robustez**: Múltiplas camadas de proteção

---

## Implantação e Configuração

### Requisitos do Sistema

#### Python
- **Versão**: Python 3.7 ou superior
- **Recomendado**: Python 3.9+

#### Dependências
```
requests>=2.25.1    # Comunicação HTTP
psutil>=5.8.0       # Monitoramento do sistema
flask>=2.0.0        # API REST
flask-cors>=3.0.0   # CORS para frontend
```

### Instalação

#### 1. Clone do Repositório
```bash
git clone https://github.com/usuario/lumi-AI.git
cd lumi-AI
```

#### 2. Ambiente Virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

#### 3. Instalação de Dependências
```bash
pip install -r requirements.txt
```

#### 4. Configuração de Variáveis

Crie arquivo `.env`:
```
GEMINI_API_KEY=sua_chave_gemini_aqui
OPENROUTER_API_KEY=sua_chave_openrouter_aqui
```

### Execução

#### Modo Console
```bash
python src/main.py
```

#### Modo API
```bash
python src/lumi_api.py
```

#### Com Script (Windows)
```bash
run.bat
```

### Configuração de Produção

#### Usando Gunicorn
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 src.lumi_api:app
```

#### Docker (Opcional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
EXPOSE 5000
CMD ["python", "src/lumi_api.py"]
```

---

## Guia do Desenvolvedor

### Arquitetura de Módulos

#### Criando Novo Módulo Core

1. **Criar arquivo** em `src/core/novo_modulo.py`:
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Novo Módulo para Lumi Assistant
"""

class NovoModulo:
    def __init__(self):
        """Inicializar módulo"""
        pass
    
    def funcionalidade_principal(self, dados):
        """Implementar funcionalidade"""
        return resultado
```

2. **Adicionar ao** `src/core/__init__.py`:
```python
from .novo_modulo import NovoModulo
__all__ = [..., "NovoModulo"]
```

3. **Integrar no assistente** em `src/core/assistant.py`:
```python
def _initialize_modules(self):
    # ... outros módulos
    self.novo_modulo = NovoModulo()
```

#### Criando Módulo Utilitário

1. **Criar em** `src/utils/nova_util.py`
2. **Seguir mesmo padrão** de importação e integração

### Padrões de Código

#### Documentação
```python
def metodo_exemplo(self, parametro):
    """
    Descrição breve do método
    
    Args:
        parametro (tipo): Descrição do parâmetro
        
    Returns:
        tipo: Descrição do retorno
        
    Raises:
        Exception: Quando ocorre erro específico
    """
```

#### Tratamento de Erros
```python
try:
    resultado = operacao_arriscada()
    return resultado
except Exception as e:
    logger.error(f"Erro em operacao: {e}")
    return valor_fallback
```

#### Logging
```python
import logging

logger = logging.getLogger(__name__)

def funcao():
    logger.info("Operação iniciada")
    logger.debug("Detalhes de debug")
    logger.warning("Aviso importante")
    logger.error("Erro ocorrido")
```

### Testes

#### Estrutura de Testes
```
src/tests/
├── test_ai_engine.py
├── test_personality.py
├── test_task_handler.py
└── test_patterns.py
```

#### Exemplo de Teste
```python
import unittest
from core.ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        self.ai_engine = AIEngine()
    
    def test_api_call(self):
        response = self.ai_engine.call_ai_api([
            {"role": "user", "content": "Teste"}
        ])
        self.assertIsNotNone(response)
```

### Debugging

#### Modo Debug
```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)

# No assistant.py
print(f"🔍 Ação detectada: {action}")
print(f"🔍 Contexto: {context}")
```

#### Verificação de Módulos
```python
def _get_module_status(self):
    return {
        "ai_engine": self.ai_engine is not None,
        "personality": self.personality is not None,
        # ... outros módulos
    }
```

---

## Exemplos de Uso

### Uso Programático

#### Inicialização Básica
```python
from task_manager import TaskManager
from reports_generator import ReportsGenerator
from ai_assistant import LumiAssistant

# Configuração
task_manager = TaskManager()
reports_generator = ReportsGenerator(task_manager)
lumi = LumiAssistant(task_manager, reports_generator)

# Uso
response = lumi.process_message("Adicionar tarefa: estudar Python")
print(response)
```

#### Uso Avançado
```python
# Verificar status dos módulos
stats = lumi.get_user_stats()
print(f"Módulos carregados: {stats}")

# Operações diretas
lumi.add_task("Nova tarefa")
tasks = lumi.list_tasks()
lumi.complete_task(1)
```

### Uso via API

#### Enviar Mensagem
```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Adicionar tarefa: comprar livro"}'
```

#### Listar Tarefas
```bash
curl http://localhost:5000/tasks
```

#### Completar Tarefa
```bash
curl -X PUT http://localhost:5000/tasks/1/complete
```

### Exemplos de Interação

#### Adição de Tarefas
```
Usuário: "Preciso estudar matemática"
Lumi: "✨ Perfeito! Adicionei 'estudar matemática' às suas tarefas. Você está construindo algo incrível!"

Usuário: "Adicionar: 1. Estudar Python 2. Fazer exercícios 3. Revisar código"
Lumi: "🚀 Fantástico! Acabei de adicionar 3 tarefas à sua agenda produtiva. Bora conquistar!"
```

#### Consultas Educacionais
```
Usuário: "O que são algoritmos?"
Lumi: "🤓 Algoritmos são sequências de instruções lógicas para resolver problemas! Como receitas de cozinha, mas para computadores. Quer criar uma tarefa para estudar mais sobre isso?"
```

#### Interações Casuais
```
Usuário: "Oi Lumi!"
Lumi: "✨ Oi! Como posso turbinar sua produtividade hoje?"

Usuário: "Obrigado pela ajuda"
Lumi: "🌟 De nada! Estou sempre aqui para te ajudar!"
```

---

## Solução de Problemas

### Problemas Comuns

#### 1. Módulos Não Carregam
**Erro**: `ImportError: No module named 'core'`

**Solução**:
```python
# Verificar estrutura de diretórios
# Garantir que __init__.py existe
# Verificar PYTHONPATH
import sys
sys.path.append('/caminho/para/lumi-AI/src')
```

#### 2. IA Não Responde
**Erro**: "Sistema de IA temporariamente indisponível"

**Solução**:
```bash
# Verificar chaves de API
echo $GEMINI_API_KEY
echo $OPENROUTER_API_KEY

# Testar conectividade
curl -s https://generativelanguage.googleapis.com/
```

#### 3. Dados Não Persistem
**Erro**: Tarefas desaparecem após reiniciar

**Solução**:
```python
# Verificar permissões de escrita
# Verificar se diretório data/ existe
import os
os.makedirs('src/data', exist_ok=True)
```

#### 4. API CORS Error
**Erro**: "Access-Control-Allow-Origin"

**Solução**:
```python
# Em lumi_api.py
from flask_cors import CORS
CORS(app, origins=["*"])  # Para desenvolvimento
```

### Logs de Debug

#### Ativar Logging Detalhado
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Verificar Estado do Sistema
```python
# Adicionar ao assistant.py
def debug_status(self):
    return {
        "modules_loaded": self._get_module_status(),
        "ai_engine_active": self.ai_engine is not None,
        "memory_usage": len(self.personality.conversation_memory),
        "mood_history": len(self.mood_analyzer.mood_history)
    }
```

### Performance

#### Otimização de Memória
```python
# Limitar histórico
MAX_CONVERSATION_MEMORY = 20
MAX_MOOD_HISTORY = 10

# Limpar caches periodicamente
def cleanup_memory(self):
    if len(self.conversation_memory) > MAX_CONVERSATION_MEMORY:
        self.conversation_memory = self.conversation_memory[-MAX_CONVERSATION_MEMORY:]
```

#### Otimização de API
```python
# Cache de respostas
response_cache = {}

def cached_ai_call(self, message_hash, messages):
    if message_hash in response_cache:
        return response_cache[message_hash]
    
    result = self.call_ai_api(messages)
    response_cache[message_hash] = result
    return result
```

---

## Conclusão

O Lumi AI Assistant 2.0 representa uma evolução significativa em termos de arquitetura, funcionalidade e maintibilidade. Com sua arquitetura modular, integração dual de IA, sistema de personalidade avançado e compatibilidade total com versões anteriores, o sistema oferece uma base sólida para desenvolvimento futuro e expansão de funcionalidades.

### Próximos Passos Sugeridos

1. **Interface Gráfica**: Desenvolvimento de UI web ou desktop
2. **Análise Avançada**: Machine learning para padrões de produtividade
3. **Integrações**: Conectores com calendários e ferramentas externas
4. **Mobile**: Aplicativo móvel para acesso em movimento
5. **Colaboração**: Recursos para trabalho em equipe

### Contribuindo

Para contribuir com o projeto:

1. Fork o repositório
2. Crie branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Crie Pull Request

---

**Lumi AI Assistant 2.0** - Assistente de IA Modular para Produtividade

*Documentação Técnica Completa - Versão 1.0*

*Última atualização: $(date)*

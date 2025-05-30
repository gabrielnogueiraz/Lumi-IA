# Lumi AI Assistant - API Reference

## Sumário Executivo

Esta documentação fornece uma referência completa da API interna e externa do Lumi AI Assistant 2.0, incluindo todos os módulos, métodos, parâmetros e exemplos de uso.

---

## Core API Reference

### AIEngine Class

**Localização**: `src/core/ai_engine.py`

```python
class AIEngine:
    """Manages AI API calls with Google Gemini as primary and OpenRouter as fallback"""
```

#### Métodos Públicos

##### `__init__()`
```python
def __init__(self):
    """Initialize AI engine with dual API configuration"""
```

##### `call_ai_api(messages)`
```python
def call_ai_api(self, messages):
    """
    Call AI API with automatic fallback
    
    Args:
        messages (list): List of message objects with 'role' and 'content'
                        [{"role": "user", "content": "Hello"}]
    
    Returns:
        str: AI response text
        
    Raises:
        Exception: When all AI services fail
    """
```

**Exemplo de uso**:
```python
ai_engine = AIEngine()
response = ai_engine.call_ai_api([
    {"role": "system", "content": "You are a helpful assistant"},
    {"role": "user", "content": "Hello world"}
])
```

##### `generate_task_response(context, message, task_info=None)`
```python
def generate_task_response(self, context, message, task_info=None):
    """
    Generate specialized responses for task operations
    
    Args:
        context (str): Operation context ("adicionar", "concluir", etc.)
        message (str): Original user message
        task_info (dict, optional): Task information dict
    
    Returns:
        str: Personalized AI response
    """
```

##### `generate_educational_explanation(topic, message)`
```python
def generate_educational_explanation(self, topic, message):
    """
    Generate educational explanations
    
    Args:
        topic (str): Educational topic extracted from message
        message (str): Original user question
    
    Returns:
        str: Educational explanation with study suggestion
    """
```

##### `generate_general_response(message)`
```python
def generate_general_response(self, message):
    """
    Generate general conversational responses
    
    Args:
        message (str): User message
    
    Returns:
        str: General AI response
    """
```

#### Métodos Privados

##### `_call_gemini_api(messages)`
```python
def _call_gemini_api(self, messages):
    """Call Google Gemini API (primary)"""
```

##### `_call_openrouter_api(messages)`
```python
def _call_openrouter_api(self, messages):
    """Call OpenRouter API (fallback)"""
```

---

### LumiAssistant Class (Core)

**Localização**: `src/core/assistant.py`

```python
class LumiAssistant:
    """LUMI 2.0 - Modular AI Assistant for Productivity"""
```

#### Inicialização

```python
def __init__(self, task_manager, reports_generator):
    """
    Initialize modular Lumi with all subsystems
    
    Args:
        task_manager: TaskManager instance for data operations
        reports_generator: ReportsGenerator instance for analytics
    """
```

#### Métodos Principais

##### `process_message(message)`
```python
def process_message(self, message):
    """
    Process user message with full AI intelligence
    
    Args:
        message (str): User input message
    
    Returns:
        str: AI-generated response
        
    Flow:
        1. Analyze mood and context
        2. Update conversation memory
        3. Detect action pattern
        4. Check educational intent
        5. Route to appropriate handler
        6. Return personalized response
    """
```

#### Módulos Integrados

A classe inicializa e integra os seguintes módulos:

- `self.ai_engine`: AIEngine instance
- `self.personality`: Personality instance
- `self.education`: Education instance
- `self.pattern_detector`: PatternDetector instance
- `self.mood_analyzer`: MoodAnalyzer instance
- `self.task_handler`: TaskHandler instance

#### Métodos de Compatibilidade

```python
def add_task(self, title): 
    """Direct task addition"""

def list_tasks(): 
    """Direct task listing"""

def complete_task(identifier): 
    """Direct task completion"""

def remove_task(identifier): 
    """Direct task removal"""

def get_task_count(): 
    """Get task statistics"""

def get_user_stats(): 
    """Get user interaction statistics"""
```

---

### TaskHandler Class

**Localização**: `src/core/task_handler.py`

```python
class TaskHandler:
    """Handles task management operations with AI-powered responses"""
```

#### Inicialização

```python
def __init__(self, task_manager, personality):
    """
    Initialize task handler
    
    Args:
        task_manager: TaskManager instance
        personality: Personality instance for context updates
    """
```

#### Métodos de Processamento

##### `process_add_task(message)`
```python
def process_add_task(self, message):
    """
    Process task addition with intelligent parsing
    
    Args:
        message (str): User message containing task(s)
    
    Returns:
        str: AI-generated confirmation response
        
    Features:
        - Single task extraction
        - Multiple numbered tasks support
        - Title validation
        - Context awareness updates
    """
```

##### `process_list_tasks(message)`
```python
def process_list_tasks(self, message):
    """
    Process task listing with personalized responses
    
    Args:
        message (str): User request message
    
    Returns:
        str: Formatted task list with AI commentary
    """
```

##### `process_complete_task(message)`
```python
def process_complete_task(self, message):
    """
    Process task completion with intelligent identification
    
    Args:
        message (str): User message with task identifier
    
    Returns:
        str: AI-generated completion celebration
    """
```

##### `process_remove_task(message)`
```python
def process_remove_task(self, message):
    """
    Process task removal (single or mass)
    
    Args:
        message (str): User message with removal request
    
    Returns:
        str: AI-generated removal confirmation
        
    Features:
        - Single task removal by ID or name
        - Mass removal detection ("todas as tarefas")
        - Confirmation responses
    """
```

#### Métodos Utilitários

##### `_extract_single_task_improved(message)`
```python
def _extract_single_task_improved(self, message):
    """
    Extract single task with enhanced intelligence
    
    Args:
        message (str): Raw user message
    
    Returns:
        dict: {"title": str, "date": str, "time": str}
              or None if no valid task found
    """
```

##### `_extract_multiple_tasks_improved(message)`
```python
def _extract_multiple_tasks_improved(self, message):
    """
    Extract multiple tasks from numbered lists
    
    Args:
        message (str): Message with numbered list
    
    Returns:
        list: Array of task dicts [{"title": str}, ...]
    """
```

##### `_is_valid_task_title(title)`
```python
def _is_valid_task_title(self, title):
    """
    Validate task title quality
    
    Args:
        title (str): Proposed task title
    
    Returns:
        bool: True if title is valid and meaningful
    """
```

---

### Personality Class

**Localização**: `src/core/personality.py`

```python
class Personality:
    """Manages Lumi's personality traits and response styles"""
```

#### Configuração de Personalidade

```python
personality_traits = {
    "emotional_state": "enthusiastic",        # Current emotional state
    "energy_level": 0.8,                     # Energy from 0.0 to 1.0
    "conversation_style": "friendly_professional", # Communication style
    "humor_level": 0.6,                      # Humor intensity
    "motivation_mode": "encouraging"         # Motivational approach
}
```

#### Métodos Principais

##### `get_personality_response_style(action_type, success=True)`
```python
def get_personality_response_style(self, action_type, success=True):
    """
    Get personality-based response style
    
    Args:
        action_type (str): Type of action performed
                          ("task_added", "task_completed", etc.)
        success (bool): Whether operation was successful
    
    Returns:
        str: Randomly selected personalized response
    """
```

**Action Types Disponíveis**:
- `"task_added"`: Task addition responses
- `"task_completed"`: Task completion celebrations
- `"task_removed"`: Task removal confirmations
- `"tasks_listed"`: Task listing introductions
- `"casual"`: Casual conversation responses

##### `analyze_context_and_mood(message)`
```python
def analyze_context_and_mood(self, message):
    """
    Analyze message context and user mood
    
    Args:
        message (str): User message to analyze
    
    Returns:
        dict: {
            "mood": str,           # "stressed", "motivated", "neutral"
            "urgency_level": int,  # 0-N urgency indicators
            "message_length": int, # Message length
            "politeness_level": int # 0-1 politeness score
        }
    """
```

##### `get_casual_response(message_lower)`
```python
def get_casual_response(self, message_lower):
    """
    Handle casual conversations
    
    Args:
        message_lower (str): Lowercase user message
    
    Returns:
        str: Appropriate casual response
    """
```

#### Gerenciamento de Memória

##### `update_conversation_memory(message, context)`
```python
def update_conversation_memory(self, message, context):
    """
    Update conversation memory with new interaction
    
    Args:
        message (str): User message
        context (dict): Analyzed context from mood analyzer
    
    Side Effects:
        - Adds to conversation_memory (max 20 entries)
        - Increments interaction_count
        - Updates mood indicators
    """
```

##### `get_user_stats()`
```python
def get_user_stats(self):
    """
    Return user interaction statistics
    
    Returns:
        dict: {
            "interaction_count": int,
            "mood_trend": str,
            "productivity_level": str
        }
    """
```

---

### Education Class

**Localização**: `src/core/education.py`

```python
class Education:
    """Handles educational queries and provides AI-powered explanations"""
```

#### Métodos Principais

##### `detect_educational_intent(message)`
```python
def detect_educational_intent(self, message):
    """
    Detect if message is an educational question
    
    Args:
        message (str): User message to analyze
    
    Returns:
        bool: True if message contains educational intent
        
    Detection Criteria:
        - Question words: "o que", "como", "por que"
        - Learning verbs: "explique", "ensine", "aprenda"
        - Academic terms: "conceito", "definição", "teoria"
    """
```

##### `process_educational_query(message)`
```python
def process_educational_query(self, message):
    """
    Process educational questions with AI
    
    Args:
        message (str): Educational question
    
    Returns:
        str: AI-generated educational explanation
        
    Features:
        - Topic extraction
        - Specialized educational prompts
        - Study tip integration
        - Task creation suggestions
    """
```

#### Métodos Especializados

##### `_extract_educational_topic(message)`
```python
def _extract_educational_topic(self, message):
    """Extract main topic from educational question"""
```

##### `_explain_key_concepts(topic)`
```python
def _explain_key_concepts(self, topic):
    """Explain key concepts about specific topic"""
```

##### `_provide_study_tips(subject=None)`
```python
def _provide_study_tips(self, subject=None):
    """Provide subject-specific or general study tips"""
```

---

## Utility API Reference

### PatternDetector Class

**Localização**: `src/utils/patterns.py`

```python
class PatternDetector:
    """Detects patterns in user messages to determine actions and intents"""
```

#### Vocabulário de Ações

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

#### Métodos Principais

##### `detect_action(message)`
```python
def detect_action(self, message):
    """
    Intelligent action detection with context analysis
    
    Args:
        message (str): User message to analyze
    
    Returns:
        str: Detected action ("adicionar", "listar", "concluir", etc.)
             or "consulta" for general queries
    
    Algorithm:
        1. Check specific regex patterns (high score)
        2. Analyze keywords with relevance scoring
        3. Detect educational context
        4. Identify action verbs in declarative sentences
        5. Return highest-scoring action
    """
```

##### `detect_mass_removal(message)`
```python
def detect_mass_removal(self, message):
    """
    Detect mass removal requests
    
    Args:
        message (str): User message
    
    Returns:
        bool: True if requesting to remove all tasks
    """
```

##### `detect_educational_intent(message)`
```python
def detect_educational_intent(self, message):
    """
    Detect educational questions
    
    Args:
        message (str): User message
    
    Returns:
        bool: True if message has educational intent
    """
```

##### `detect_casual_patterns(message)`
```python
def detect_casual_patterns(self, message):
    """
    Detect casual conversation patterns
    
    Args:
        message (str): User message
    
    Returns:
        bool: True if message is casual conversation
    """
```

#### Métodos de Extração

##### `extract_urgency_indicators(message)`
```python
def extract_urgency_indicators(self, message):
    """
    Extract urgency level from message
    
    Args:
        message (str): User message
    
    Returns:
        int: Urgency level (0-N based on indicators)
    """
```

##### `extract_emotional_indicators(message)`
```python
def extract_emotional_indicators(self, message):
    """
    Extract emotional state from message
    
    Args:
        message (str): User message
    
    Returns:
        str: Emotional state ("stressed", "motivated", "neutral")
    """
```

##### `extract_politeness_level(message)`
```python
def extract_politeness_level(self, message):
    """
    Extract politeness level from message
    
    Args:
        message (str): User message
    
    Returns:
        int: Politeness score (0-1)
    """
```

---

### MoodAnalyzer Class

**Localização**: `src/utils/mood_analyzer.py`

```python
class MoodAnalyzer:
    """Analyzes user mood and emotional context for personalized interactions"""
```

#### Métodos Principais

##### `analyze_context_and_mood(message)`
```python
def analyze_context_and_mood(self, message):
    """
    Comprehensive mood and context analysis
    
    Args:
        message (str): User message to analyze
    
    Returns:
        dict: {
            "mood": str,              # Current mood state
            "urgency_level": int,     # Urgency indicators count
            "message_length": int,    # Message length
            "politeness_level": int,  # Politeness score
            "mood_trend": str         # Recent mood trend
        }
    
    Side Effects:
        - Updates mood_history (max 10 entries)
        - Stores analysis timestamp
    """
```

##### `get_mood_based_suggestion(context)`
```python
def get_mood_based_suggestion(self, context):
    """
    Get personalized suggestions based on mood
    
    Args:
        context (dict): Mood analysis context
    
    Returns:
        str: Personalized suggestion message
    """
```

##### `get_current_mood_state()`
```python
def get_current_mood_state(self):
    """
    Get current mood state summary
    
    Returns:
        dict: {
            "current_mood": str,    # Latest mood
            "trend": str,           # Mood trend
            "energy": str           # Energy level
        }
    """
```

#### Análise de Tendências

##### `_analyze_mood_trend()`
```python
def _analyze_mood_trend(self):
    """
    Analyze mood trend from recent interactions
    
    Returns:
        str: "stressed_trend", "motivated_trend", or "balanced"
    """
```

##### `_calculate_politeness(message_lower)`
```python
def _calculate_politeness(self, message_lower):
    """
    Calculate politeness score
    
    Args:
        message_lower (str): Lowercase message
    
    Returns:
        int: 0 or 1 politeness score
    """
```

---

## REST API Reference

### Base Configuration

**Base URL**: `http://localhost:5000`
**Content-Type**: `application/json`
**CORS**: Enabled for development

### Authentication

Currently no authentication required (development mode).

---

### Endpoints

#### POST /message

Process user message through Lumi AI.

**Request**:
```json
{
    "message": "Adicionar tarefa: estudar Python"
}
```

**Response**:
```json
{
    "response": "✨ Perfeito! Adicionei 'estudar Python' às suas tarefas. Você está construindo algo incrível!"
}
```

**Error Response**:
```json
{
    "error": "Mensagem é obrigatória"
}
```

**Status Codes**:
- `200`: Success
- `400`: Bad Request (missing message)
- `500`: Internal Server Error

---

#### GET /tasks

Retrieve all tasks.

**Response**:
```json
{
    "tasks": [
        {
            "id": 1,
            "title": "estudar Python",
            "completed": false,
            "created_at": "2024-01-15T10:30:00",
            "priority": "normal"
        }
    ]
}
```

---

#### POST /tasks

Add new task directly.

**Request**:
```json
{
    "title": "Nova tarefa"
}
```

**Response**:
```json
{
    "message": "Tarefa adicionada com sucesso",
    "task_id": 2
}
```

---

#### PUT /tasks/:id/complete

Mark task as completed.

**Response**:
```json
{
    "message": "Tarefa concluída com sucesso"
}
```

**Error Response**:
```json
{
    "error": "Tarefa não encontrada"
}
```

---

#### DELETE /tasks/:id

Remove specific task.

**Response**:
```json
{
    "message": "Tarefa removida com sucesso"
}
```

---

#### GET /health

Health check endpoint.

**Response**:
```json
{
    "status": "healthy",
    "modules": {
        "ai_engine": true,
        "task_manager": true,
        "personality": true
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Data Models

### Task Model

```python
{
    "id": int,                    # Unique identifier
    "title": str,                 # Task title
    "completed": bool,            # Completion status
    "created_at": str,            # ISO timestamp
    "completed_at": str,          # ISO timestamp (nullable)
    "priority": str,              # "low", "normal", "high"
    "category": str,              # Task category
    "description": str            # Optional description
}
```

### Context Model

```python
{
    "mood": str,                  # "stressed", "motivated", "neutral"
    "urgency_level": int,         # 0-N urgency indicators
    "message_length": int,        # Character count
    "politeness_level": int,      # 0-1 politeness score
    "mood_trend": str            # Recent mood pattern
}
```

### User Stats Model

```python
{
    "interaction_count": int,     # Total interactions
    "mood_state": {
        "current_mood": str,      # Current mood
        "trend": str,             # Mood trend
        "energy": str             # Energy level
    },
    "ai_engine_active": bool,     # AI availability
    "system_mode": str           # "modular" or "fallback"
}
```

---

## Error Handling

### Exception Types

#### AIEngineError
```python
class AIEngineError(Exception):
    """Raised when AI engine fails"""
    pass
```

#### TaskNotFoundError
```python
class TaskNotFoundError(Exception):
    """Raised when task is not found"""
    pass
```

#### InvalidTaskError
```python
class InvalidTaskError(Exception):
    """Raised when task data is invalid"""
    pass
```

### Error Response Format

```json
{
    "error": "Error description",
    "code": "ERROR_CODE",
    "details": {
        "module": "module_name",
        "function": "function_name",
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

---

## Configuration

### Environment Variables

```bash
# AI Configuration
GEMINI_API_KEY=your_gemini_api_key
OPENROUTER_API_KEY=your_openrouter_api_key

# API Configuration
FLASK_PORT=5000
FLASK_DEBUG=true

# Data Configuration
DATA_PATH=src/data
BACKUP_ENABLED=true
```

### Module Configuration

```python
# In src/config.py
AI_CONFIG = {
    "primary_provider": "gemini",
    "fallback_provider": "openrouter",
    "timeout": 30,
    "max_retries": 3
}

PERSONALITY_CONFIG = {
    "energy_level": 0.8,
    "humor_level": 0.6,
    "motivation_mode": "encouraging"
}
```

---

## Testing API

### Unit Test Example

```python
import unittest
from core.ai_engine import AIEngine

class TestAIEngine(unittest.TestCase):
    def setUp(self):
        self.ai_engine = AIEngine()
    
    def test_generate_task_response(self):
        response = self.ai_engine.generate_task_response(
            "adicionar", 
            "Nova tarefa",
            {"title": "test"}
        )
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
```

### Integration Test Example

```python
import requests

def test_api_message():
    response = requests.post(
        "http://localhost:5000/message",
        json={"message": "Oi Lumi!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
```

---

## Performance Considerations

### Caching

```python
# Response caching for repeated queries
response_cache = {}

def cached_ai_call(message_hash, messages):
    if message_hash in response_cache:
        return response_cache[message_hash]
    
    result = ai_engine.call_ai_api(messages)
    response_cache[message_hash] = result
    return result
```

### Memory Management

```python
# Automatic cleanup of conversation memory
MAX_CONVERSATION_MEMORY = 20
MAX_MOOD_HISTORY = 10

def cleanup_memory():
    """Clean up memory usage periodically"""
    conversation_memory = conversation_memory[-MAX_CONVERSATION_MEMORY:]
    mood_history = mood_history[-MAX_MOOD_HISTORY:]
```

### API Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/message', methods=['POST'])
@limiter.limit("10 per minute")
def process_message():
    # Implementation
```

---

**Lumi AI Assistant 2.0** - Complete API Reference

*Version 1.0 - Technical Documentation*

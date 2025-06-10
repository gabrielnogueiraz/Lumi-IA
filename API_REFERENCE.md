# 📡 API Reference - Lumi AI

## 📋 Índice

1. [Visão Geral da API](#-visão-geral-da-api)
2. [Autenticação](#-autenticação)
3. [Endpoints de Chat](#-endpoints-de-chat)
4. [Endpoints de Analytics](#-endpoints-de-analytics)
5. [Endpoints de Health](#-endpoints-de-health)
6. [Modelos de Dados](#-modelos-de-dados)
7. [Códigos de Erro](#-códigos-de-erro)
8. [Exemplos de Uso](#-exemplos-de-uso)
9. [Rate Limiting](#-rate-limiting)
10. [Webhooks](#-webhooks)

---

## 🌐 Visão Geral da API

### Base URL
```
Production:  https://api.lumi-ai.com/v1
Development: http://localhost:5000
```

### Características Principais
- ✅ **REST API** com JSON
- ✅ **Documentação OpenAPI** automática
- ✅ **Validação** com Pydantic
- ✅ **Rate Limiting** inteligente
- ✅ **Versionamento** da API
- ✅ **CORS** configurado

### Formatos de Resposta
```json
{
  "success": true,
  "data": {...},
  "message": "Operação realizada com sucesso",
  "timestamp": "2024-01-10T15:30:00Z",
  "request_id": "uuid-4"
}
```

---

## 🔐 Autenticação

### API Key Authentication
```http
Authorization: Bearer YOUR_API_KEY
```

### Headers Obrigatórios
```http
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
X-User-ID: 12345
```

### Obter API Key
```bash
curl -X POST "https://api.lumi-ai.com/v1/auth/api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 12345,
    "app_name": "Toivo App",
    "permissions": ["chat", "analytics", "insights"]
  }'
```

---

## 💬 Endpoints de Chat

### POST `/chat`

Inicia uma conversação com a Lumi AI.

#### Request Body
```json
{
  "user_id": 12345,
  "message": "Como está minha produtividade esta semana?",
  "context": {
    "current_time": "14:30",
    "energy_level": 0.8,
    "current_task_id": 456,
    "session_type": "work"
  },
  "conversation_id": "optional-uuid",
  "metadata": {
    "platform": "web",
    "timezone": "America/Sao_Paulo"
  }
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "response": "Sua produtividade esta semana está excelente! 🎯 Você completou 15 tarefas de 18 planejadas (83% de conclusão). Seus horários de pico foram entre 9h-11h e 14h-16h.",
    "mood_detected": "motivated",
    "confidence": 0.87,
    "conversation_id": "conv-uuid-123",
    "suggestions": [
      {
        "type": "task_optimization",
        "title": "Otimizar agenda de amanhã",
        "action": "schedule_deep_work",
        "description": "Agendar tarefa complexa para 9h-11h"
      },
      {
        "type": "analytics",
        "title": "Ver relatório detalhado",
        "action": "view_weekly_report",
        "description": "Análise completa da semana"
      }
    ],
    "personality_state": "motivated",
    "context_updated": true,
    "follow_up_questions": [
      "Gostaria de ver quais tarefas faltaram?",
      "Quer ajuda para planejar a próxima semana?"
    ]
  },
  "message": "Resposta gerada com sucesso",
  "timestamp": "2024-01-10T15:30:00Z",
  "processing_time_ms": 1250
}
```

#### Parâmetros de Query
- `include_suggestions` (boolean): Incluir sugestões de ação
- `conversation_mode` (string): "casual" | "focused" | "detailed"
- `max_response_length` (integer): Máximo de caracteres na resposta

#### Códigos de Status
- `200` - Sucesso
- `400` - Parâmetros inválidos
- `429` - Rate limit excedido
- `500` - Erro interno

---

### GET `/chat/{conversation_id}/history`

Recupera histórico de uma conversação.

#### Response
```json
{
  "success": true,
  "data": {
    "conversation_id": "conv-uuid-123",
    "messages": [
      {
        "id": "msg-1",
        "type": "user",
        "content": "Como está minha produtividade?",
        "timestamp": "2024-01-10T15:30:00Z",
        "context": {...}
      },
      {
        "id": "msg-2", 
        "type": "assistant",
        "content": "Sua produtividade está ótima!",
        "mood_detected": "motivated",
        "confidence": 0.87,
        "timestamp": "2024-01-10T15:30:15Z"
      }
    ],
    "total_messages": 2,
    "conversation_started": "2024-01-10T15:30:00Z",
    "last_interaction": "2024-01-10T15:30:15Z"
  }
}
```

---

### POST `/chat/context/update`

Atualiza contexto do usuário para melhorar respostas.

#### Request Body
```json
{
  "user_id": 12345,
  "context_updates": {
    "current_energy": 0.6,
    "mood_override": "struggling",
    "active_tasks": [456, 789],
    "environment": "home_office",
    "interruptions_today": 3
  }
}
```

---

## 📊 Endpoints de Analytics

### GET `/analytics/{user_id}/insights`

Obtém insights personalizados de produtividade.

#### Parâmetros de Query
- `period` (string): "day" | "week" | "month" | "quarter"
- `metrics` (array): ["productivity", "mood", "tasks", "time"]
- `include_predictions` (boolean): Incluir predições futuras

#### Response
```json
{
  "success": true,
  "data": {
    "user_id": 12345,
    "period": "week",
    "productivity_score": 0.83,
    "insights": [
      {
        "type": "performance_insight",
        "title": "Pico de Produtividade Identificado",
        "description": "Você é 40% mais produtivo entre 9h-11h",
        "confidence": 0.91,
        "suggested_actions": [
          "Agendar tarefas complexas para manhã",
          "Evitar reuniões no horário de pico"
        ],
        "impact_score": 0.8
      },
      {
        "type": "mood_insight",
        "title": "Padrão de Humor Estável",
        "description": "Seu humor tem se mantido consistentemente positivo",
        "confidence": 0.76,
        "trend": "stable",
        "mood_distribution": {
          "motivated": 0.4,
          "focused": 0.35,
          "celebrating": 0.15,
          "struggling": 0.1
        }
      }
    ],
    "metrics": {
      "tasks_completed": 15,
      "total_focus_time": 18.5,
      "avg_session_length": 47,
      "interruption_rate": 0.12,
      "energy_consistency": 0.73
    },
    "predictions": {
      "next_week_score": 0.85,
      "recommended_goals": {
        "tasks_target": 16,
        "focus_time_target": 20
      }
    },
    "generated_at": "2024-01-10T15:30:00Z"
  }
}
```

---

### GET `/analytics/{user_id}/productivity-score`

Calcula score detalhado de produtividade.

#### Response
```json
{
  "success": true,
  "data": {
    "overall_score": 0.83,
    "components": {
      "task_completion": {
        "score": 0.85,
        "weight": 0.30,
        "details": {
          "completed": 15,
          "planned": 18,
          "rate": 0.83
        }
      },
      "focus_quality": {
        "score": 0.78,
        "weight": 0.25,
        "details": {
          "avg_session_length": 47,
          "interruption_rate": 0.12,
          "deep_work_sessions": 8
        }
      },
      "time_efficiency": {
        "score": 0.81,
        "weight": 0.20,
        "details": {
          "planned_vs_actual": 0.95,
          "context_switching": 0.15,
          "procrastination_score": 0.1
        }
      },
      "consistency": {
        "score": 0.89,
        "weight": 0.15,
        "details": {
          "daily_variance": 0.11,
          "streak_length": 12,
          "habit_strength": 0.89
        }
      },
      "goal_achievement": {
        "score": 0.92,
        "weight": 0.10,
        "details": {
          "weekly_goals_met": 0.9,
          "milestone_progress": 0.75
        }
      }
    },
    "trend": {
      "direction": "improving",
      "change_percentage": 8.5,
      "period_comparison": "vs_last_week"
    },
    "percentile": 78
  }
}
```

---

### GET `/analytics/{user_id}/patterns`

Identifica padrões comportamentais.

#### Response
```json
{
  "success": true,
  "data": {
    "temporal_patterns": {
      "peak_hours": [
        {"start": "09:00", "end": "11:00", "efficiency": 0.91},
        {"start": "14:00", "end": "16:00", "efficiency": 0.84}
      ],
      "best_days": ["tuesday", "wednesday", "thursday"],
      "energy_cycles": {
        "type": "bimodal",
        "morning_peak": "09:30",
        "afternoon_peak": "15:00",
        "low_point": "13:00"
      }
    },
    "task_patterns": {
      "preferred_sequence": ["planning", "deep_work", "communication", "review"],
      "optimal_batch_size": 3,
      "context_switching_tolerance": "low",
      "complexity_preference": {
        "morning": "high",
        "afternoon": "medium",
        "evening": "low"
      }
    },
    "mood_patterns": {
      "mood_triggers": {
        "motivated": ["task_completion", "achievement_unlock"],
        "focused": ["morning_routine", "minimal_interruptions"],
        "struggling": ["high_complexity", "multiple_deadlines"]
      },
      "recovery_patterns": {
        "from_struggling": {
          "avg_time": "2.5 hours",
          "best_activities": ["small_wins", "break", "physical_activity"]
        }
      }
    },
    "prediction_accuracy": 0.87,
    "confidence_level": 0.83
  }
}
```

---

### POST `/analytics/{user_id}/goals`

Define e acompanha metas personalizadas.

#### Request Body
```json
{
  "goals": [
    {
      "type": "productivity_score",
      "target": 0.9,
      "timeframe": "week",
      "priority": "high"
    },
    {
      "type": "focus_time",
      "target": 25,
      "unit": "hours",
      "timeframe": "week",
      "priority": "medium"
    },
    {
      "type": "task_completion",
      "target": 20,
      "unit": "tasks",
      "timeframe": "week",
      "priority": "medium"
    }
  ],
  "auto_adjust": true,
  "notification_preferences": {
    "progress_updates": "daily",
    "milestone_alerts": true,
    "course_correction": true
  }
}
```

---

## 🏥 Endpoints de Health

### GET `/health`

Health check básico do sistema.

#### Response
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2024-01-10T15:30:00Z",
    "uptime": "72h 15m 30s",
    "version": "1.2.3",
    "environment": "production"
  }
}
```

---

### GET `/health/detailed`

Health check detalhado com métricas do sistema.

#### Response
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "components": {
      "database": {
        "status": "healthy",
        "response_time_ms": 45,
        "pool_status": {
          "total_connections": 20,
          "active_connections": 8,
          "idle_connections": 12
        },
        "last_check": "2024-01-10T15:30:00Z"
      },
      "ai_service": {
        "status": "healthy",
        "response_time_ms": 1200,
        "requests_per_minute": 45,
        "success_rate": 0.98,
        "last_check": "2024-01-10T15:29:55Z"
      },
      "cache": {
        "status": "healthy",
        "hit_rate": 0.85,
        "memory_usage": "67%",
        "eviction_rate": 0.02
      }
    },
    "metrics": {
      "requests_per_second": 12.5,
      "avg_response_time": 850,
      "error_rate": 0.001,
      "memory_usage": "512MB",
      "cpu_usage": "23%"
    }
  }
}
```

---

## 📋 Modelos de Dados

### User Model
```python
class User(BaseModel):
    id: int
    username: str
    email: Optional[str]
    created_at: datetime
    last_active: datetime
    preferences: Dict[str, Any] = {}
    current_mood: str = "focused"
    total_flowers: int = 0
    current_streak: int = 0
```

### Task Model
```python
class Task(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(ge=1, le=5, default=3)
    complexity: TaskComplexity = TaskComplexity.MEDIUM
    estimated_duration: int = 25  # minutes
    actual_duration: Optional[int]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
    tags: List[str] = []
    parent_task_id: Optional[int]
    subtasks: List['Task'] = []
```

### Chat Request/Response Models
```python
class ChatRequest(BaseModel):
    user_id: int = Field(..., ge=1)
    message: str = Field(..., min_length=1, max_length=2000)
    context: Dict[str, Any] = Field(default_factory=dict)
    conversation_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    response: str
    mood_detected: str
    confidence: float = Field(ge=0.0, le=1.0)
    conversation_id: str
    suggestions: List[ActionSuggestion] = []
    personality_state: str
    context_updated: bool = False
    follow_up_questions: List[str] = []
    processing_time_ms: int
```

### Analytics Models
```python
class ProductivityMetrics(BaseModel):
    productivity_score: float = Field(ge=0.0, le=1.0)
    tasks_completed: int
    total_focus_time: float  # hours
    avg_session_length: float  # minutes
    interruption_rate: float = Field(ge=0.0, le=1.0)
    energy_consistency: float = Field(ge=0.0, le=1.0)
    mood_stability: float = Field(ge=0.0, le=1.0)

class PersonalizedInsight(BaseModel):
    type: InsightType
    title: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    impact_score: float = Field(ge=0.0, le=1.0)
    suggested_actions: List[str] = []
    created_at: datetime
    expires_at: Optional[datetime]
```

### Error Models
```python
class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str
    suggested_action: Optional[str] = None

class ValidationError(BaseModel):
    field: str
    message: str
    invalid_value: Any
    constraint: str
```

---

## ⚠️ Códigos de Erro

### Códigos de Sistema

| Código | Descrição | Ação Sugerida |
|--------|-----------|---------------|
| `LUMI_1001` | Erro da API de IA | Tentar novamente |
| `LUMI_1002` | Rate limit da IA | Aguardar e tentar novamente |
| `LUMI_1003` | Modelo indisponível | Usar modelo alternativo |
| `LUMI_2001` | Erro de conexão DB | Verificar conectividade |
| `LUMI_2002` | Query timeout | Otimizar consulta |
| `LUMI_2003` | Pool esgotado | Aguardar conexão disponível |
| `LUMI_3001` | Dados inválidos | Corrigir entrada |
| `LUMI_3002` | Usuário não encontrado | Verificar user_id |
| `LUMI_3003` | Permissão negada | Verificar autenticação |
| `LUMI_4001` | Rate limit excedido | Implementar backoff |
| `LUMI_4002` | Quota excedida | Aguardar reset |
| `LUMI_5001` | Contexto inválido | Reenviar com contexto correto |

### Exemplos de Respostas de Erro

#### 400 - Bad Request
```json
{
  "success": false,
  "error": {
    "code": "LUMI_3001",
    "message": "Dados de entrada inválidos",
    "details": {
      "validation_errors": [
        {
          "field": "user_id",
          "message": "deve ser maior que 0",
          "invalid_value": -1
        },
        {
          "field": "message", 
          "message": "não pode estar vazio",
          "invalid_value": ""
        }
      ]
    },
    "timestamp": "2024-01-10T15:30:00Z",
    "request_id": "req-uuid-123"
  }
}
```

#### 429 - Rate Limit
```json
{
  "success": false,
  "error": {
    "code": "LUMI_4001",
    "message": "Rate limit excedido",
    "details": {
      "limit": 60,
      "remaining": 0,
      "reset_at": "2024-01-10T15:31:00Z"
    },
    "suggested_action": "retry_after_delay"
  }
}
```

#### 500 - Internal Server Error
```json
{
  "success": false,
  "error": {
    "code": "LUMI_1001",
    "message": "Erro interno do servidor",
    "details": {
      "component": "ai_engine",
      "recoverable": true
    },
    "suggested_action": "retry_with_backoff",
    "timestamp": "2024-01-10T15:30:00Z",
    "request_id": "req-uuid-123"
  }
}
```

---

## 💡 Exemplos de Uso

### Chat Simples
```bash
curl -X POST "https://api.lumi-ai.com/v1/chat" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 12345" \
  -d '{
    "user_id": 12345,
    "message": "Preciso de ajuda para organizar meu dia"
  }'
```

### Chat com Contexto
```bash
curl -X POST "https://api.lumi-ai.com/v1/chat" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 12345" \
  -d '{
    "user_id": 12345,
    "message": "Estou me sentindo sobrecarregado com as tarefas",
    "context": {
      "energy_level": 0.3,
      "pending_tasks": 15,
      "deadline_pressure": "high",
      "interruptions_today": 8
    }
  }'
```

### Analytics Detalhado
```bash
curl -X GET "https://api.lumi-ai.com/v1/analytics/12345/insights?period=week&include_predictions=true" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "X-User-ID: 12345"
```

### Python SDK
```python
from lumi_ai import LumiClient

client = LumiClient(api_key="YOUR_API_KEY")

# Chat simples
response = await client.chat(
    user_id=12345,
    message="Como posso melhorar minha produtividade?"
)

# Analytics
insights = await client.get_insights(
    user_id=12345,
    period="week",
    include_predictions=True
)

# Padrões comportamentais
patterns = await client.get_patterns(user_id=12345)
```

### JavaScript/TypeScript
```javascript
import { LumiAI } from '@lumi-ai/sdk';

const lumi = new LumiAI({
  apiKey: 'YOUR_API_KEY',
  baseURL: 'https://api.lumi-ai.com/v1'
});

// Chat
const response = await lumi.chat({
  userId: 12345,
  message: "Estou tendo dificuldades para focar",
  context: {
    energyLevel: 0.4,
    environment: "home_office"
  }
});

// Analytics
const analytics = await lumi.getAnalytics(12345, {
  period: 'week',
  metrics: ['productivity', 'mood', 'patterns']
});
```

---

## 🚦 Rate Limiting

### Limites por Endpoint

| Endpoint | Limite | Janela | Reset |
|----------|--------|--------|-------|
| `/chat` | 60 req | 1 min | Rolling |
| `/analytics/*` | 120 req | 1 min | Rolling |
| `/health` | 1000 req | 1 min | Rolling |
| Global | 1000 req | 1 hora | Fixed |

### Headers de Rate Limit
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641825600
X-RateLimit-Window: 60
```

### Estratégias de Backoff
```python
import time
import random

def exponential_backoff(attempt: int, base_delay: float = 1.0) -> float:
    """Calcula delay para retry com jitter"""
    delay = base_delay * (2 ** attempt)
    jitter = random.uniform(0.1, 0.3) * delay
    return delay + jitter

# Uso
for attempt in range(3):
    try:
        response = await api_call()
        break
    except RateLimitError:
        if attempt < 2:
            delay = exponential_backoff(attempt)
            await asyncio.sleep(delay)
```

---

## 🔄 Webhooks

### Configuração
```bash
curl -X POST "https://api.lumi-ai.com/v1/webhooks" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/lumi",
    "events": ["insight_generated", "goal_achieved", "mood_changed"],
    "secret": "your-webhook-secret"
  }'
```

### Eventos Disponíveis

#### `insight_generated`
```json
{
  "event": "insight_generated",
  "data": {
    "user_id": 12345,
    "insight": {
      "type": "productivity_improvement",
      "title": "Novo padrão identificado",
      "confidence": 0.89,
      "impact_score": 0.75
    }
  },
  "timestamp": "2024-01-10T15:30:00Z"
}
```

#### `goal_achieved`
```json
{
  "event": "goal_achieved",
  "data": {
    "user_id": 12345,
    "goal": {
      "type": "weekly_productivity",
      "target": 0.85,
      "achieved": 0.87,
      "streak_days": 14
    }
  },
  "timestamp": "2024-01-10T15:30:00Z"
}
```

#### `mood_changed`
```json
{
  "event": "mood_changed",
  "data": {
    "user_id": 12345,
    "previous_mood": "focused",
    "new_mood": "overwhelmed",
    "confidence": 0.82,
    "triggers": ["high_task_load", "interruption_spike"]
  },
  "timestamp": "2024-01-10T15:30:00Z"
}
```

### Verificação de Assinatura
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verifica assinatura do webhook"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected}", signature)
```

---

## 🔧 SDK e Bibliotecas

### Python SDK
```bash
pip install lumi-ai-sdk
```

```python
from lumi_ai import LumiClient, ChatContext

client = LumiClient(
    api_key="YOUR_API_KEY",
    base_url="https://api.lumi-ai.com/v1"
)

# Configurar contexto padrão
context = ChatContext(
    timezone="America/Sao_Paulo",
    language="pt-br",
    platform="toivo_app"
)

# Chat com contexto automático
async with client.session(user_id=12345, context=context) as session:
    response = await session.chat("Como está minha semana?")
    analytics = await session.get_analytics(period="week")
```

### JavaScript SDK
```bash
npm install @lumi-ai/sdk
```

```typescript
import { LumiAI, ChatOptions } from '@lumi-ai/sdk';

const lumi = new LumiAI({
  apiKey: process.env.LUMI_API_KEY,
  timeout: 30000,
  retries: 3
});

// Chat tipado
const response = await lumi.chat({
  userId: 12345,
  message: "Preciso de uma pausa?",
  context: {
    energyLevel: 0.3,
    sessionsToday: 6,
    lastBreak: "2 hours ago"
  }
});

// Analytics tipado
const insights = await lumi.analytics.getInsights(12345, {
  period: 'week',
  includePatterns: true,
  includePredictions: true
});
```

---

## 📚 Documentação Adicional

### Links Úteis
- **Swagger UI**: `https://api.lumi-ai.com/docs`
- **ReDoc**: `https://api.lumi-ai.com/redoc`
- **Status Page**: `https://status.lumi-ai.com`
- **Changelog**: `https://docs.lumi-ai.com/changelog`

### Suporte
- **Email**: api-support@lumi-ai.com
- **Discord**: [Lumi Developers](https://discord.gg/lumi-dev)
- **GitHub**: [lumi-ai/api-issues](https://github.com/lumi-ai/api-issues)

### Rate Limits e Quotas
- **Desenvolvimento**: 1,000 requests/hora
- **Produção Basic**: 10,000 requests/hora  
- **Produção Pro**: 100,000 requests/hora
- **Enterprise**: Ilimitado

---

Esta documentação da API fornece todos os detalhes necessários para integrar com a Lumi AI. Para implementação prática, consulte também o [Implementation Guide](IMPLEMENTATION_GUIDE.md) e a [Technical Documentation](TECHNICAL_DOCUMENTATION.md).

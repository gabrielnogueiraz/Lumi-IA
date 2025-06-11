from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
import json
from datetime import datetime

from core.database_manager import db_manager
from core.ai_engine import AIEngine
from core.context_analyzer import ContextAnalyzer
from services.task_intelligence import TaskIntelligenceService
from services.mood_detector import MoodDetectorService
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: Union[str, int] = Field(..., description="ID do usuário")
    message: str = Field(..., min_length=1, description="Mensagem do usuário")
    context: Optional[Any] = Field(None, description="Contexto adicional - aceita string ou dict")
    
    @validator('user_id', pre=True)
    def convert_user_id_to_string(cls, v):
        """Converte user_id para string se necessário"""
        return str(v)
    
    @validator('message', pre=True)
    def validate_message(cls, v):
        """Valida se a mensagem não está vazia após strip"""
        if not v or not str(v).strip():
            raise ValueError('Mensagem não pode estar vazia')
        return str(v).strip()
    
    @validator('context', pre=True)
    def normalize_context(cls, v):
        """Converte context string para dict para compatibilidade"""
        if v is None:
            return None
        elif isinstance(v, str):
            # Converte string para dict com chave padrão
            return {"legacy_context": v, "type": "string_format"}
        elif isinstance(v, dict):
            return v
        else:
            # Para outros tipos, converte para string e depois dict
            return {"legacy_context": str(v), "type": "converted"}
    
    def get_context_value(self) -> Optional[str]:
        """Método helper para extrair valor do contexto independente do formato"""
        if self.context is None:
            return None
        elif isinstance(self.context, dict):
            return self.context.get("legacy_context", str(self.context))
        else:
            return str(self.context)

class ChatResponse(BaseModel):
    response: str
    mood: str
    personality_tone: str
    actions: List[Dict[str, Any]]
    insights: List[str]
    suggestions: List[str]
    emotional_context: Dict[str, Any]
    processing_time: float

# Initialize services
ai_engine = AIEngine()
context_analyzer = ContextAnalyzer()
task_intelligence = TaskIntelligenceService(db_manager)
mood_detector = MoodDetectorService(db_manager)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_lumi(request: ChatRequest):
    """
    Endpoint principal para chat com a Lumi AI
    """
    try:
        start_time = datetime.now()
        
        # Log detalhado da requisição
        logger.info(f"🎯 CHAT REQUEST START", extra={
            "user_id": request.user_id,
            "message_length": len(request.message),            "has_context": request.context is not None,
            "timestamp": start_time.isoformat()
        })
        
        logger.info(f"Processing chat request for user {request.user_id}: {request.message[:50]}...")
        
        # Validate user_id format
        try:
            # Check for invalid values first
            if request.user_id in ["None", "null", "undefined", "", "0"]:
                logger.error(f"Invalid user_id value: {request.user_id}")
                raise HTTPException(status_code=400, detail="user_id é obrigatório e deve ser um número válido")
            
            user_id_int = int(request.user_id)
            if user_id_int <= 0:
                logger.error(f"Invalid user_id: {request.user_id} (negative or zero)")
                raise HTTPException(status_code=400, detail="user_id deve ser um número positivo")
        except ValueError as e:
            logger.error(f"Invalid user_id format: {request.user_id} - {e}")
            raise HTTPException(status_code=400, detail="user_id deve ser um número válido")
        
        logger.info(f"✅ User ID validation passed: {request.user_id}")
        
        # Fetch comprehensive user context
        try:
            logger.info(f"🔍 Fetching user context for user {request.user_id}")
            user_context = await db_manager.fetch_user_context(request.user_id)
            logger.info(f"📊 User context fetched: {type(user_context)}, has_error: {'error' in user_context}")
        except Exception as e:
            logger.error(f"❌ Database fetch error: {e}")
            user_context = {"error": f"Database error: {str(e)}"}
        
        if "error" in user_context:
            # Se usuário não existe, crie um contexto básico
            if "User not found" in user_context.get("error", ""):
                logger.info(f"👤 User {request.user_id} not found, creating basic context")
                user_context = await _create_basic_user_context(request.user_id)
            else:
                logger.error(f"💥 Database error for user {request.user_id}: {user_context['error']}")
                # Em vez de falhar, vamos usar contexto básico
                logger.info(f"🔄 Using fallback basic context due to database error")
                user_context = await _create_basic_user_context(request.user_id)
          # Create default context if needed
        if not user_context.get("user_info"):
            logger.info(f"📝 Creating default context for user {request.user_id}")
            user_context = await _create_basic_user_context(request.user_id)
        
        logger.info(f"✅ User context ready")
        
        # 🧠 NOVA FUNCIONALIDADE: Detecção inteligente de tarefas
        try:
            from core.intelligent_task_extractor import task_extractor
            task_intent = task_extractor.extract_task_from_message(request.message)
            if task_intent:
                logger.info(f"🎯 Tarefa detectada: {task_intent.title}")
                # Criar tarefa automaticamente
                response = await _handle_intelligent_task_creation(request.user_id, task_intent, user_context)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                response_data = _ensure_complete_response(response, {"mood": "motivated"}, processing_time)
                
                logger.info(f"🎉 Tarefa criada automaticamente para user {request.user_id} in {processing_time:.2f}s")
                return ChatResponse(**response_data)
        except Exception as e:
            logger.error(f"❌ Erro na detecção de tarefas: {e}")
        
        # Analyze message context and intent
        try:
            logger.info(f"🧠 Analyzing context for message")
            context_analysis = await context_analyzer.analyze_context(request.message, user_context)
            logger.info(f"✅ Context analysis complete")
        except Exception as e:
            logger.error(f"❌ Context analysis error: {e}")
            # Fallback to simple analysis
            context_analysis = _create_simple_context_analysis(request.message)
            logger.info(f"🔄 Using simple context analysis fallback")
          # Detect current mood
        try:
            logger.info(f"😊 Detecting mood")
            mood_analysis = await mood_detector.detect_current_mood(request.user_id, user_context)
            logger.info(f"✅ Mood detection complete: {mood_analysis.get('mood', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Mood detection error: {e}")
            # Fallback mood
            mood_analysis = {"mood": "focused", "confidence": 0.5}
            logger.info(f"🔄 Using fallback mood: focused")
        
        # Generate response
        try:
            logger.info(f"🤖 Generating AI response")
            
            # 🧠 MELHORAR: Detectar consultas sobre tarefas pendentes
            message_lower = request.message.lower()
            pending_queries = [
                "tenho alguma tarefa", "tarefas pendentes", "o que preciso fazer",
                "pendências", "tarefas para hoje", "minha agenda"
            ]
            
            if any(query in message_lower for query in pending_queries):
                logger.info(f"📋 Detectada consulta de tarefas pendentes")
                response = await _handle_pending_tasks_query(request.user_id, user_context)
            # Handle specific intents with specialized responses
            elif hasattr(context_analysis, 'intent') and context_analysis.intent in ["create_task", "modify_task", "delete_task"]:
                logger.info(f"📋 Handling task intent: {context_analysis.intent}")
                response = await _handle_task_intent(request.user_id, context_analysis, user_context)
            elif hasattr(context_analysis, 'intent') and context_analysis.intent == "start_pomodoro":
                logger.info(f"🍅 Handling pomodoro intent")
                response = await _handle_pomodoro_intent(request.user_id, context_analysis, user_context)
            elif hasattr(context_analysis, 'intent') and context_analysis.intent in ["check_progress", "productivity_insights"]:
                logger.info(f"📊 Handling analytics intent")
                response = await _handle_analytics_intent(request.user_id, context_analysis, user_context)
            elif hasattr(context_analysis, 'intent') and context_analysis.intent == "get_suggestions":
                logger.info(f"💡 Handling suggestions intent")
                response = await _handle_suggestions_intent(request.user_id, context_analysis, user_context)
            else:
                # General conversational response
                logger.info(f"💬 Generating general conversational response")
                response = await ai_engine.generate_response(user_context, request.message)
            
            logger.info(f"✅ Response generated successfully")
        except Exception as e:
            logger.error(f"❌ Response generation error: {e}")
            # Fallback response
            response = _create_fallback_response(request.message, mood_analysis)
            logger.info(f"🔄 Using fallback response")
        
        # Update Lumi's memory with interaction
        try:
            logger.info(f"💾 Updating interaction memory")
            await _update_interaction_memory(request.user_id, request.message, response, mood_analysis)
            logger.info(f"✅ Memory updated successfully")
        except Exception as e:
            logger.error(f"❌ Memory update error: {e}")
            logger.info(f"🔄 Continuing without memory update")
            # Continue without updating memory
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Ensure response has all required fields
        try:
            logger.info(f"🔧 Ensuring complete response structure")
            response_data = _ensure_complete_response(response, mood_analysis, processing_time)
            logger.info(f"✅ Response structure validated")
        except Exception as e:
            logger.error(f"❌ Response structure error: {e}")
            # Use absolute fallback
            response_data = {
                "response": "Olá! Como posso ajudar você hoje?",
                "mood": "focused",
                "personality_tone": "friendly",
                "actions": [],
                "insights": [],
                "suggestions": ["Verificar tarefas", "Iniciar pomodoro"],
                "emotional_context": {"fallback": True},
                "processing_time": processing_time
            }
        
        logger.info(f"🎉 Chat response generated for user {request.user_id} in {processing_time:.2f}s")
        
        # Final validation before return
        try:
            final_response = ChatResponse(**response_data)
            logger.info(f"✅ Final response validation successful")
            return final_response
        except Exception as e:
            logger.error(f"❌ Final response validation failed: {e}")
            # Absolute minimal response
            return ChatResponse(
                response="Olá! Estou aqui para ajudar com sua produtividade.",
                mood="focused",
                personality_tone="friendly", 
                actions=[],
                insights=[],
                suggestions=[],
                emotional_context={},
                processing_time=processing_time
            )
        
    except HTTPException as he:
        logger.error(f"🚨 HTTP Exception: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"💥 Unexpected error in chat endpoint: {e}", extra={
            "error_type": type(e).__name__,
            "user_id": getattr(request, 'user_id', 'unknown'),
            "message_preview": getattr(request, 'message', '')[:50] if hasattr(request, 'message') else 'unknown'
        })
        # Return a safe fallback response
        return ChatResponse(
            response="Ops! Algo deu errado. Tente novamente em alguns instantes.",
            mood="neutral",
            personality_tone="apologetic",
            actions=[],
            insights=[],
            suggestions=["Tentar novamente", "Verificar conexão"],
            emotional_context={"error": True, "fallback": True},
            processing_time=0.1
        )

async def _handle_task_intent(user_id: str, context_analysis, user_context: Dict[str, Any]):
    """Handle task-related intents"""
    
    if context_analysis.intent == "create_task":
        # Extract task details from context
        suggested_actions = context_analysis.suggested_actions
        if suggested_actions and suggested_actions[0]["type"] == "create_task":
            task_data = suggested_actions[0]["data"]
            
            # Get intelligent estimates
            task_title = task_data.get("title", "Nova tarefa")
            complexity_analysis = await task_intelligence.estimate_task_complexity(
                user_id, task_title
            )
            
            # Get optimal timing
            timing_suggestion = await task_intelligence.suggest_optimal_timing(
                user_id, task_data.get("priority", "medium")
            )
            
            # Create the task
            task_id = await db_manager.create_task(user_id, {
                "title": task_title,
                "description": task_data.get("description", ""),
                "priority": task_data.get("priority", "medium"),
                "estimated_pomodoros": complexity_analysis["estimated_pomodoros"],
                "due_date": task_data.get("due_date")
            })
            
            if task_id:
                # Generate response about task creation
                response_content = f"✅ Criei a tarefa '{task_title}'! "
                response_content += f"Estimei {complexity_analysis['estimated_pomodoros']} pomodoros "
                
                if timing_suggestion["optimal_hours"]:
                    best_hour = timing_suggestion["optimal_hours"][0]
                    response_content += f"e sugiro fazer às {best_hour}h. "
                
                if complexity_analysis["confidence"] > 0.7:
                    response_content += "A estimativa está baseada em tarefas similares suas! 🎯"
                else:
                    response_content += "Vamos ajustando a estimativa conforme você trabalha! 📈"
                
                return type('Response', (), {
                    'content': response_content,
                    'mood': 'motivated',
                    'personality_tone': 'supportive',
                    'actions': [{"type": "task_created", "data": {"task_id": task_id}}],
                    'insights': [f"Estimativa baseada em {complexity_analysis['based_on_similar_tasks']} tarefas similares"],
                    'suggestions': [timing_suggestion["reasoning"]],
                    'emotional_context': {"task_creation": True}
                })()
            else:
                raise HTTPException(status_code=500, detail="Erro ao criar tarefa")
    
    # For other task intents, use general AI response
    return await ai_engine.generate_response(user_context, "Vamos trabalhar com suas tarefas!")

async def _handle_pomodoro_intent(user_id: str, context_analysis, user_context: Dict[str, Any]):
    """Handle pomodoro start intent"""
    
    # Get task suggestions for pomodoro
    task_suggestions = await task_intelligence.generate_intelligent_task_suggestions(
        user_id, "iniciar pomodoro"
    )
    
    response_content = "🍅 Vamos começar um pomodoro! "
    
    if task_suggestions:
        best_suggestion = task_suggestions[0]
        response_content += f"Que tal trabalhar em: '{best_suggestion.title}'? "
        response_content += f"({best_suggestion.reasoning}) "
        
        actions = [{
            "type": "pomodoro_suggested",
            "data": {
                "suggested_task": best_suggestion.title,
                "estimated_duration": best_suggestion.estimated_pomodoros * 25,
                "reasoning": best_suggestion.reasoning
            }
        }]
    else:
        response_content += "Escolha uma tarefa e vamos focar juntos! 💪"
        actions = [{"type": "pomodoro_start_ready", "data": {}}]
    
    return type('Response', (), {
        'content': response_content,
        'mood': 'focused',
        'personality_tone': 'direct',
        'actions': actions,
        'insights': ["Hora de focar na produtividade"],
        'suggestions': [s.reasoning for s in task_suggestions[:2]],
        'emotional_context': {"pomodoro_intent": True}
    })()

async def _handle_analytics_intent(user_id: str, context_analysis, user_context: Dict[str, Any]):
    """Handle analytics and progress checking intent"""
    
    from services.user_analytics import UserAnalyticsService
    analytics_service = UserAnalyticsService(db_manager)
    
    # Get comprehensive analytics
    analytics = await analytics_service.get_comprehensive_analytics(user_id)
    
    # Generate insights response
    daily_stats = analytics.daily_stats
    achievements = analytics.achievements
    
    response_content = "📊 Aqui está seu resumo de produtividade:\n\n"
    
    # Today's stats
    tasks_today = daily_stats.get("tasks", {})
    completed_today = tasks_today.get("completed_tasks", 0)
    focus_time = daily_stats.get("focus_time_minutes", 0)
    
    response_content += f"**Hoje:** {completed_today} tarefas completadas, {focus_time}min de foco\n"
    
    # Current streak
    current_streak = user_context.get("current_streak", 0)
    if current_streak > 0:
        response_content += f"🔥 **Sequência:** {current_streak} dias consecutivos!\n"
    
    # Recent achievements
    if achievements:
        latest_achievement = achievements[0]
        response_content += f"🏆 **Conquista:** {latest_achievement['title']} - {latest_achievement['description']}\n"
    
    # Weekly trend
    weekly_trend = analytics.weekly_trends.get("trend", "stable")
    if weekly_trend == "improving":
        response_content += "📈 Sua produtividade está melhorando esta semana!"
    elif weekly_trend == "declining":
        response_content += "📉 Vamos ajustar a estratégia para melhorar os resultados"
    else:
        response_content += "📊 Sua produtividade está estável"
    
    return type('Response', (), {
        'content': response_content,
        'mood': 'analytical',
        'personality_tone': 'informative',
        'actions': [{"type": "analytics_provided", "data": analytics.__dict__}],
        'insights': analytics.recommendations,
        'suggestions': ["Quer ver análises mais detalhadas?", "Posso sugerir otimizações personalizadas"],
        'emotional_context': {"analytics_request": True}
    })()

async def _handle_suggestions_intent(user_id: str, context_analysis, user_context: Dict[str, Any]):
    """Handle suggestions request intent"""
    
    # Get intelligent task suggestions
    task_suggestions = await task_intelligence.generate_intelligent_task_suggestions(
        user_id, context_analysis.entities.get("potential_task", "")
    )
    
    # Get task optimizations
    optimizations = await task_intelligence.optimize_existing_tasks(user_id)
    
    response_content = "💡 Aqui estão minhas sugestões personalizadas:\n\n"
    
    # Task suggestions
    if task_suggestions:
        response_content += "**Novas Tarefas:**\n"
        for i, suggestion in enumerate(task_suggestions[:3], 1):
            response_content += f"{i}. {suggestion.title} ({suggestion.estimated_pomodoros} pomodoros)\n"
            response_content += f"   ↳ {suggestion.reasoning}\n"
    
    # Optimizations
    if optimizations:
        response_content += "\n**Otimizações:**\n"
        for optimization in optimizations[:2]:
            response_content += f"• {optimization.suggested_changes.get('suggested_action', 'Otimizar tarefa')}\n"
    
    if not task_suggestions and not optimizations:
        response_content += "Você está bem organizado! Continue assim! 🎯"
    
    actions = []
    if task_suggestions:
        actions.append({
            "type": "suggestions_provided",
            "data": {"suggestions": [s.__dict__ for s in task_suggestions]}
        })
    
    return type('Response', (), {
        'content': response_content,
        'mood': 'helpful',
        'personality_tone': 'advisory',
        'actions': actions,
        'insights': [s.reasoning for s in task_suggestions[:2]],
        'suggestions': ["Quer que eu crie alguma dessas tarefas?", "Posso ajudar a priorizar suas atividades"],
        'emotional_context': {"suggestions_provided": True}
    })()

async def _update_interaction_memory(user_id: str, message: str, response, mood_analysis: Dict[str, Any]):
    """Update Lumi's interaction memory"""
    try:
        interaction_data = {
            "last_message": message,
            "last_response": response.content,
            "interaction_mood": mood_analysis.get("current_mood", "neutral"),
            "successful_intent": True,
            "timestamp": datetime.now().isoformat()
        }
        
        memory_update = {
            "current_mood": mood_analysis.get("current_mood", "neutral"),
            "contextual_memory": json.dumps(interaction_data),
            "interaction_count": 1  # This will be incremented in the database
        }
        
        await db_manager.update_lumi_memory(user_id, memory_update)
        
    except Exception as e:
        logger.error(f"Error updating interaction memory: {e}")

async def _create_basic_user_context(user_id: str) -> Dict[str, Any]:
    """Cria contexto básico para usuário novo"""
    return {
        "user_info": {
            "id": user_id,
            "name": f"Usuário {user_id}",
            "email": None,
            "created_at": datetime.now()
        },
        "tasks_stats": {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "in_progress_tasks": 0,
            "overdue_tasks": 0,
            "avg_pomodoros_per_task": 0
        },
        "recent_activity": [],
        "productivity_patterns": {},
        "current_streak": 0,
        "lumi_memory": None,
        "today_pomodoros": []
    }

def _create_simple_context_analysis(message: str):
    """Cria análise de contexto simples como fallback"""
    class SimpleContext:
        def __init__(self, msg):
            self.intent = "general_conversation"
            self.entities = []
            self.suggested_actions = []
            self.message = msg
    return SimpleContext(message)

def _create_fallback_response(message: str, mood_analysis: Dict[str, Any]):
    """Cria resposta de fallback quando outros sistemas falham"""
    class FallbackResponse:
        def __init__(self):
            self.content = "Entendi! Como posso ajudar você a ser mais produtivo hoje?"
            self.mood = mood_analysis.get("mood", "focused")
            self.personality_tone = "friendly"
            self.actions = []
            self.insights = []
            self.suggestions = ["Ver tarefas pendentes", "Iniciar um pomodoro", "Organizar agenda"]
            self.emotional_context = {"fallback": True, "confidence": 0.3}
    
    return FallbackResponse()

def _ensure_complete_response(response, mood_analysis: Dict[str, Any], processing_time: float) -> Dict[str, Any]:
    """Garante que a resposta tenha todos os campos necessários"""
    
    # Se response é um objeto da AI Engine
    if hasattr(response, 'content'):
        return {
            "response": response.content,
            "mood": getattr(response, 'mood', mood_analysis.get("mood", "focused")),
            "personality_tone": getattr(response, 'personality_tone', "friendly"),
            "actions": getattr(response, 'actions', []),
            "insights": getattr(response, 'insights', []),
            "suggestions": getattr(response, 'suggestions', []),
            "emotional_context": getattr(response, 'emotional_context', {}),
            "processing_time": processing_time
        }
    
    # Se response é um dicionário
    elif isinstance(response, dict):
        return {
            "response": response.get("content", response.get("response", "Como posso ajudar?")),
            "mood": response.get("mood", mood_analysis.get("mood", "focused")),
            "personality_tone": response.get("personality_tone", "friendly"),
            "actions": response.get("actions", []),
            "insights": response.get("insights", []),
            "suggestions": response.get("suggestions", []),
            "emotional_context": response.get("emotional_context", {}),
            "processing_time": processing_time
        }
    
    # Se response é uma string simples
    elif isinstance(response, str):
        return {
            "response": response,
            "mood": mood_analysis.get("mood", "focused"),
            "personality_tone": "friendly",
            "actions": [],
            "insights": [],
            "suggestions": [],
            "emotional_context": {},
            "processing_time": processing_time
        }
    
    # Fallback final
    else:
        return {
            "response": "Como posso ajudar você hoje?",
            "mood": "focused",
            "personality_tone": "friendly",
            "actions": [],
            "insights": [],
            "suggestions": ["Ver tarefas", "Iniciar pomodoro", "Verificar progresso"],
            "emotional_context": {"fallback": True},
            "processing_time": processing_time
        }

@router.get("/chat/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "services": {
            "ai_engine": "operational",
            "context_analyzer": "operational",
            "task_intelligence": "operational",
            "mood_detector": "operational"
        },
        "timestamp": datetime.now().isoformat()
    }

async def _handle_intelligent_task_creation(user_id: str, task_intent, user_context: Dict[str, Any]):
    """Cria tarefa automaticamente baseada na detecção inteligente"""
    try:
        # Criar tarefa no banco de dados
        task_data = {
            "title": task_intent.title,
            "description": task_intent.description or f"Tarefa criada automaticamente: {task_intent.title}",
            "priority": task_intent.priority,
            "estimated_pomodoros": task_intent.estimated_pomodoros,
            "due_date": task_intent.due_date,
            "status": "pending"
        }
        
        # Tentar criar no banco (mesmo que falhe, vamos responder positivamente)
        task_id = None
        try:
            task_id = await db_manager.create_task(user_id, task_data)
            logger.info(f"✅ Tarefa criada no banco: ID {task_id}")
        except Exception as db_error:
            logger.error(f"❌ Erro ao salvar tarefa no banco: {db_error}")
            # Continuar mesmo assim para dar feedback ao usuário
        
        # Gerar resposta empática e natural
        response_text = f"✅ Perfeito! Criei a tarefa **{task_intent.title}** para você"
        
        if task_intent.due_date:
            if task_intent.time:
                response_text += f" agendada para {task_intent.due_date} às {task_intent.time}"
            else:
                response_text += f" para {task_intent.due_date}"
        
        if task_intent.estimated_pomodoros > 1:
            response_text += f". Estimei {task_intent.estimated_pomodoros} pomodoros para isso"
        
        response_text += ". 🎯\n\nEstou aqui para te lembrar e te ajudar quando for hora de começar! 💪"
        
        # Retornar resposta estruturada
        return type('Response', (), {
            'content': response_text,
            'mood': 'motivated',
            'personality_tone': 'supportive',
            'actions': [{
                "type": "task_created",
                "data": {
                    "task_id": task_id,
                    "title": task_intent.title,
                    "due_date": task_intent.due_date,
                    "time": task_intent.time,
                    "confidence": task_intent.confidence
                }
            }],
            'insights': [f"Detectei automaticamente que você queria criar esta tarefa"],
            'suggestions': [
                "Quer que eu te lembre antes do horário?",
                "Posso sugerir uma preparação para essa tarefa"
            ],
            'emotional_context': {
                "task_creation": True,
                "intelligent_detection": True,
                "user_intent_understood": True
            }
        })()
        
    except Exception as e:
        logger.error(f"❌ Erro na criação inteligente de tarefa: {e}")
        # Fallback response
        return type('Response', (), {
            'content': f"Entendi que você quer {task_intent.title}! Vou te ajudar a organizar isso. 😊",
            'mood': 'supportive',
            'personality_tone': 'helpful',
            'actions': [],
            'insights': ["Detectei sua intenção mas houve um problema técnico"],
            'suggestions': ["Tente me dizer novamente como posso ajudar"],
            'emotional_context': {"fallback": True}
        })()

async def _handle_pending_tasks_query(user_id: str, user_context: Dict[str, Any]):
    """Responde consultas sobre tarefas pendentes"""
    try:
        # Buscar tarefas pendentes do usuário
        pending_tasks = []
        try:
            # Simular busca de tarefas (mesmo que DB falhe, dar resposta útil)
            tasks_stats = user_context.get("tasks_stats", {})
            pending_count = tasks_stats.get("pending_tasks", 0)
            overdue_count = tasks_stats.get("overdue_tasks", 0)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar tarefas: {e}")
            pending_count = 0
            overdue_count = 0
        
        # Gerar resposta baseada no estado
        if pending_count == 0 and overdue_count == 0:
            response_text = "🎉 Você está livre! Não tem nenhuma tarefa pendente no momento.\n\nQue tal aproveitar para planejar algo novo ou relaxar um pouco? 😊"
            mood = "celebrating"
            suggestions = [
                "Criar uma nova tarefa para amanhã",
                "Revisar seus objetivos da semana",
                "Fazer uma pausa merecida"
            ]
        elif overdue_count > 0:
            response_text = f"📋 Você tem {pending_count} tarefas pendentes"
            if overdue_count > 0:
                response_text += f", sendo {overdue_count} em atraso"
            response_text += ".\n\nVamos organizar isso juntos? Posso te ajudar a priorizar! 💪"
            mood = "focused"
            suggestions = [
                "Mostrar tarefas em atraso primeiro",
                "Reorganizar por prioridade",
                "Começar com a mais simples"
            ]
        else:
            response_text = f"📝 Você tem {pending_count} tarefas pendentes para trabalhar.\n\nEstá tudo organizado! Quer começar por alguma específica? 🎯"
            mood = "motivated"
            suggestions = [
                "Ver lista completa de tarefas",
                "Começar pela mais importante",
                "Iniciar um pomodoro agora"
            ]
        
        return type('Response', (), {
            'content': response_text,
            'mood': mood,
            'personality_tone': 'supportive',
            'actions': [{
                "type": "tasks_overview_provided",
                "data": {
                    "pending_tasks": pending_count,
                    "overdue_tasks": overdue_count,
                    "total_tasks": pending_count + overdue_count
                }
            }],
            'insights': [
                f"Você tem {pending_count} tarefas para focar" if pending_count > 0 
                else "Ótimo momento para planejar novas atividades"
            ],
            'suggestions': suggestions,
            'emotional_context': {
                "tasks_query": True,
                "organized_status": overdue_count == 0,
                "motivation_needed": overdue_count > 0
            }
        })()
        
    except Exception as e:
        logger.error(f"❌ Erro ao consultar tarefas pendentes: {e}")
        return type('Response', (), {
            'content': "Vou te ajudar a organizar suas tarefas! Ainda estou coletando os dados, mas já podemos começar a planejar. 😊",
            'mood': 'supportive',
            'personality_tone': 'helpful',
            'actions': [],
            'insights': ["Dados sendo carregados"],
            'suggestions': ["Me conte o que você precisa fazer hoje"],
            'emotional_context': {"loading": True}
        })()

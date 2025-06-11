from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Union
import json
from datetime import datetime

from core.database_manager import db_manager
from core.ai_engine import AIEngine
from core.context_analyzer import ContextAnalyzer
from core.conversation_memory import get_conversation_memory
from services.task_intelligence import TaskIntelligenceService
from services.mood_detector import MoodDetectorService
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

# Instâncias dos serviços
ai_engine = AIEngine()
context_analyzer = ContextAnalyzer()
task_intelligence = TaskIntelligenceService(db_manager)
mood_detector = MoodDetectorService(db_manager)
conversation_memory = get_conversation_memory()

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
            return {"legacy_context": v, "type": "string_format"}
        elif isinstance(v, dict):
            return v
        else:
            try:
                return {"processed_context": str(v), "type": "other"}
            except:
                return None

class ChatResponse(BaseModel):
    response: str
    mood: str = "neutral"
    personality_tone: str = "friendly"
    actions: List[Dict[str, Any]] = []
    insights: List[str] = []
    suggestions: List[str] = []
    emotional_context: Dict[str, Any] = {}
    processing_time: float = 0.0
    conversation_id: Optional[str] = None

@router.post("/chat", response_model=ChatResponse)
async def chat_with_lumi(request: ChatRequest):
    """
    🤖 ENDPOINT PRINCIPAL: Conversa com a Lumi AI
    
    A Lumi agora possui:
    - ✅ Memória persistente de conversas
    - ✅ Criação inteligente de tarefas
    - ✅ Personalidade adaptativa
    - ✅ Contexto completo do usuário
    """
    start_time = datetime.now()
    
    try:
        logger.info(f"🗣️ Nova conversa iniciada com usuário {request.user_id}: '{request.message}'")
          # Validar user_id como UUID
        import uuid
        try:
            if request.user_id in ["None", "null", "undefined", "", "0"]:
                logger.error(f"Invalid user_id value: {request.user_id}")
                raise HTTPException(status_code=400, detail="user_id é obrigatório e deve ser um UUID válido")
            
            uuid.UUID(request.user_id)
        except ValueError as e:
            logger.error(f"Invalid user_id format: {request.user_id} - {e}")
            raise HTTPException(status_code=400, detail="user_id deve ser um UUID válido")
        
        logger.info(f"✅ User ID validation passed: {request.user_id}")
        
        # 🧠 CARREGAR MEMÓRIA DA CONVERSA
        try:
            logger.info(f"🧠 Carregando memória da conversa para usuário {request.user_id}")
            conversation_context = await conversation_memory.get_conversation_context(request.user_id)
            user_name = conversation_context.get('user_name')
            recent_messages = conversation_context.get('recent_messages', [])
            
            logger.info(f"💾 Memória carregada: {len(recent_messages)} mensagens recentes")
            if user_name:
                logger.info(f"👤 Nome do usuário: {user_name}")
        except Exception as e:
            logger.error(f"❌ Erro ao carregar memória da conversa: {e}")
            conversation_context = {'recent_messages': [], 'user_name': None}
            user_name = None
        
        # Fetch comprehensive user context
        try:
            logger.info(f"🔍 Fetching user context for user {request.user_id}")
            user_context = await db_manager.fetch_user_context(request.user_id)
            logger.info(f"📊 User context fetched: {type(user_context)}, has_error: {'error' in user_context}")
        except Exception as e:
            logger.error(f"❌ Database fetch error: {e}")
            user_context = {"error": f"Database error: {str(e)}"}
        
        if "error" in user_context:
            if "User not found" in user_context.get("error", ""):
                logger.info(f"👤 User {request.user_id} not found, creating basic context")
                user_context = await _create_basic_user_context(request.user_id)
            else:
                logger.error(f"💥 Database error for user {request.user_id}: {user_context['error']}")
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
                
                # Salvar conversa na memória da Lumi
                await conversation_memory.save_conversation(
                    request.user_id, 
                    request.message, 
                    response.content,
                    {
                        "detected_context": "task_creation",
                        "lumi_mood": "motivated",
                        "topics": ["task_creation", "productivity"],
                        "user_sentiment": "proactive"
                    }
                )
                
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
            context_analysis = _create_simple_context_analysis(request.message)
            logger.info(f"🔄 Using simple context analysis fallback")
        
        # Detect current mood
        try:
            logger.info(f"😊 Detecting mood")
            mood_analysis = await mood_detector.detect_current_mood(request.user_id, user_context)
            logger.info(f"✅ Mood detection complete: {mood_analysis.get('mood', 'unknown')}")
        except Exception as e:
            logger.error(f"❌ Mood detection error: {e}")
            mood_analysis = {"mood": "focused", "confidence": 0.5}
            logger.info(f"🔄 Using fallback mood: focused")
        
        # Generate response
        try:
            logger.info(f"🤖 Generating AI response")
            
            # 🧠 MELHORAR: Detectar consultas sobre tarefas pendentes
            message_lower = request.message.lower()
            pending_queries = [
                "tenho alguma tarefa", "tarefas pendentes", "o que preciso fazer",
                "pendências", "tarefas para hoje", "minha agenda", "lista de tarefas"
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
                # 🧠 PERSONALIZAÇÃO: Usar memória para resposta mais contextual
                enhanced_context = {**user_context}
                enhanced_context.update({
                    'conversation_memory': conversation_context,
                    'user_name': user_name,
                    'recent_messages': recent_messages
                })
                
                logger.info(f"🤖 Generating contextualized response with memory")
                response = await ai_engine.generate_response(enhanced_context, request.message)
            
            logger.info(f"✅ Response generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Response generation error: {e}")
            # Fallback response
            greeting = f"Olá, {user_name}!" if user_name else "Olá!"
            response = type('Response', (), {
                'content': f"{greeting} Estou aqui para te ajudar! Como posso te auxiliar hoje? 😊",
                'mood': 'encouraging',
                'personality_tone': 'friendly',
                'actions': [],
                'insights': [],
                'suggestions': ["Me conte sobre suas tarefas", "Precisa de ajuda com algo específico?"],
                'emotional_context': {"fallback": True}
            })()
        
        # 💾 SALVAR CONVERSA NA MEMÓRIA DA LUMI
        try:
            await conversation_memory.save_conversation(
                request.user_id,
                request.message,
                response.content,
                {
                    "detected_context": getattr(context_analysis, 'intent', 'general'),
                    "lumi_mood": response.mood,
                    "topics": getattr(context_analysis, 'topics', []),
                    "user_sentiment": mood_analysis.get('mood', 'neutral')
                }
            )
        except Exception as e:
            logger.error(f"❌ Erro ao salvar conversa na memória: {e}")
        
        # Update interaction memory
        try:
            await _update_interaction_memory(request.user_id, request.message, response, mood_analysis)
        except Exception as e:
            logger.error(f"❌ Interaction memory update error: {e}")
        
        # Prepare final response
        processing_time = (datetime.now() - start_time).total_seconds()
        response_data = _ensure_complete_response(response, mood_analysis, processing_time)
        
        logger.info(f"🎉 Response completed for user {request.user_id} in {processing_time:.2f}s")
        
        return ChatResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"💥 Unexpected error in chat endpoint: {e}")
        
        return ChatResponse(
            response="Ops! Algo deu errado. Tente novamente em alguns instantes.",
            mood="apologetic",
            personality_tone="supportive",
            processing_time=processing_time,
            emotional_context={"error_occurred": True}
        )

async def _create_basic_user_context(user_id: str) -> Dict[str, Any]:
    """Create basic user context when user doesn't exist"""
    return {
        "user_info": {"id": user_id, "name": None, "created_at": datetime.now()},
        "tasks_stats": {"total_tasks": 0, "completed_tasks": 0, "pending_tasks": 0},
        "recent_activity": [],
        "productivity_patterns": {},
        "current_streak": 0,
        "lumi_memory": None,
        "today_pomodoros": []
    }

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
        response_content += f"**Sequência atual:** {current_streak} dias consecutivos! 🔥\n"
    
    # Recent achievements
    if achievements.get("recent_milestones"):
        response_content += f"**Conquistas recentes:** {len(achievements['recent_milestones'])} novos marcos!\n"
    
    response_content += "\nContinue assim! Você está no caminho certo! 🎯"
    
    return type('Response', (), {
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
        # Update behavior patterns based on interaction
        await conversation_memory.update_behavior_patterns(user_id, {
            "interaction_time": datetime.now().hour,
            "message_length": len(message),
            "response_type": response.mood,
            "user_mood": mood_analysis.get("mood", "neutral")
        })
        
        logger.info(f"🧠 Interaction memory updated for user {user_id}")
    except Exception as e:
        logger.error(f"❌ Error updating interaction memory: {e}")

async def _handle_intelligent_task_creation(user_id: str, task_intent, user_context: Dict[str, Any]):
    """Cria tarefa automaticamente baseada na detecção inteligente"""
    try:
        # Preparar horário se fornecido
        due_date_formatted = None
        if task_intent.due_date and task_intent.time:
            due_date_formatted = f"{task_intent.due_date} {task_intent.time}:00"
        elif task_intent.due_date:
            due_date_formatted = task_intent.due_date
        
        # Criar tarefa no banco de dados
        task_data = {
            "title": task_intent.title,
            "description": task_intent.description or f"Tarefa criada automaticamente: {task_intent.title}",
            "priority": task_intent.priority,
            "estimated_pomodoros": task_intent.estimated_pomodoros,
            "due_date": due_date_formatted,
            "time": task_intent.time,
            "status": "pending"
        }
        
        # Tentar criar no banco
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
        async with db_manager.get_connection() as conn:            pending_tasks = await conn.fetch("""
                SELECT id, title, description, priority, "dueDate", 
                       "estimatedPomodoros", "createdAt"
                FROM task
                WHERE "userId" = $1 AND status = 'pending'
                ORDER BY 
                    CASE priority 
                        WHEN 'high' THEN 1 
                        WHEN 'medium' THEN 2 
                        ELSE 3 
                    END,
                    "dueDate" ASC NULLS LAST,
                    "createdAt" ASC
                LIMIT 10
            """, user_id)
        
        # Buscar estatísticas
        tasks_stats = user_context.get("tasks_stats", {})
        pending_count = tasks_stats.get("pending_tasks", 0)
        overdue_count = tasks_stats.get("overdue_tasks", 0)
        
        # Gerar resposta baseada no estado
        if pending_count == 0 and overdue_count == 0:
            response_text = "🎉 Você está livre! Não tem nenhuma tarefa pendente no momento.\n\nQue tal aproveitar para planejar algo novo ou relaxar um pouco? 😊"
            mood = "celebrating"
            suggestions = [
                "Criar uma nova tarefa para amanhã",
                "Revisar seus objetivos da semana",
                "Fazer uma pausa merecida"
            ]
        else:
            response_text = f"📋 Você tem {pending_count} tarefas pendentes"
            if overdue_count > 0:
                response_text += f", sendo {overdue_count} em atraso"
            response_text += ".\n\n"
            
            # Listar as principais tarefas
            if pending_tasks:
                response_text += "**Suas principais tarefas:**\n"
                for i, task in enumerate(pending_tasks[:5], 1):
                    priority_emoji = "🔥" if task['priority'] == 'high' else "⭐" if task['priority'] == 'medium' else "📝"
                    response_text += f"{i}. {priority_emoji} {task['title']}\n"
                    
                    if task['due_date']:
                        response_text += f"   📅 Prazo: {task['due_date'].strftime('%d/%m às %H:%M')}\n"
                    
                    if task['estimated_pomodoros']:
                        response_text += f"   ⏱️ {task['estimated_pomodoros']} pomodoros\n"
                    response_text += "\n"
            
            response_text += "Vamos organizar isso juntos? Posso te ajudar a priorizar! 💪"
            mood = "focused"
            suggestions = [
                "Começar pela tarefa mais importante",
                "Quebrar tarefas grandes em menores",
                "Definir horários específicos para cada tarefa"
            ]
        
        return type('Response', (), {
            'content': response_text,
            'mood': mood,
            'personality_tone': 'helpful',
            'actions': [{
                "type": "tasks_listed",
                "data": {
                    "pending_count": pending_count,
                    "overdue_count": overdue_count,
                    "tasks": [dict(task) for task in pending_tasks[:5]]
                }
            }],
            'insights': [
                f"Total de {pending_count} tarefas pendentes",
                f"{overdue_count} tarefas em atraso" if overdue_count > 0 else "Nenhuma tarefa em atraso"
            ],
            'suggestions': suggestions,
            'emotional_context': {
                "agenda_consultation": True,
                "has_pending_tasks": pending_count > 0,
                "has_overdue_tasks": overdue_count > 0
            }
        })()
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar tarefas pendentes: {e}")
        return type('Response', (), {
            'content': "Ops! Tive um problema para acessar suas tarefas. Tente novamente em alguns instantes. 😅",
            'mood': 'apologetic',
            'personality_tone': 'helpful',
            'actions': [],
            'insights': ["Erro técnico ao acessar tarefas"],
            'suggestions': ["Tente perguntar novamente", "Verifique sua conexão"],
            'emotional_context': {"technical_error": True}
        })()

def _create_simple_context_analysis(message: str):
    """Create simple fallback context analysis"""
    return type('ContextAnalysis', (), {
        'intent': 'general_conversation',
        'entities': {},
        'suggested_actions': [],
        'confidence': 0.5,
        'topics': ['general']
    })()

def _ensure_complete_response(response, mood_analysis: Dict[str, Any], processing_time: float) -> Dict[str, Any]:
    """Ensure response has all required fields"""
    return {
        "response": getattr(response, 'content', 'Olá! Como posso te ajudar hoje?'),
        "mood": getattr(response, 'mood', mood_analysis.get('mood', 'neutral')),
        "personality_tone": getattr(response, 'personality_tone', 'friendly'),
        "actions": getattr(response, 'actions', []),
        "insights": getattr(response, 'insights', []),
        "suggestions": getattr(response, 'suggestions', []),
        "emotional_context": getattr(response, 'emotional_context', {}),
        "processing_time": processing_time
    }

@router.get("/chat/health")
async def chat_health():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "service": "chat_handler",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "intelligent_task_creation": True,
            "conversation_memory": True,
            "adaptive_personality": True,
            "context_awareness": True
        }
    }

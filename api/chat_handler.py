from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
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
    user_id: str = Field(..., description="ID do usuário")
    message: str = Field(..., description="Mensagem do usuário")
    context: Optional[str] = Field(None, description="Contexto adicional")

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
        
        # Fetch comprehensive user context
        user_context = await db_manager.fetch_user_context(request.user_id)
        if "error" in user_context:
            raise HTTPException(status_code=404, detail=f"Usuário não encontrado: {user_context['error']}")
        
        # Analyze message context and intent
        context_analysis = await context_analyzer.analyze_context(request.message, user_context)
        
        # Detect current mood
        mood_analysis = await mood_detector.detect_current_mood(request.user_id, user_context)
        
        # Handle specific intents with specialized responses
        if context_analysis.intent in ["create_task", "modify_task", "delete_task"]:
            response = await _handle_task_intent(request.user_id, context_analysis, user_context)
        elif context_analysis.intent == "start_pomodoro":
            response = await _handle_pomodoro_intent(request.user_id, context_analysis, user_context)
        elif context_analysis.intent in ["check_progress", "productivity_insights"]:
            response = await _handle_analytics_intent(request.user_id, context_analysis, user_context)
        elif context_analysis.intent == "get_suggestions":
            response = await _handle_suggestions_intent(request.user_id, context_analysis, user_context)
        else:
            # General conversational response
            response = await ai_engine.generate_response(user_context, request.message)
        
        # Update Lumi's memory with interaction
        await _update_interaction_memory(request.user_id, request.message, response, mood_analysis)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ChatResponse(
            response=response.content,
            mood=response.mood,
            personality_tone=response.personality_tone,
            actions=response.actions,
            insights=response.insights,
            suggestions=response.suggestions,
            emotional_context=response.emotional_context,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

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

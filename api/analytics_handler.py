from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

from core.database_manager import db_manager
from services.user_analytics import UserAnalyticsService
from services.mood_detector import MoodDetectorService
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

class AnalyticsResponse(BaseModel):
    daily_stats: Dict[str, Any]
    weekly_trends: Dict[str, Any]
    monthly_overview: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    achievements: List[Dict[str, Any]]
    recommendations: List[str]

class InsightsResponse(BaseModel):
    productivity_metrics: Dict[str, Any]
    mood_analysis: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]
    predictive_insights: List[str]

class MoodHistoryResponse(BaseModel):
    period_days: int
    mood_patterns: Dict[str, Any]
    mood_triggers: Dict[str, Any]
    stability_score: float
    recommendations: List[str]

# Initialize services
analytics_service = UserAnalyticsService(db_manager)
mood_detector = MoodDetectorService(db_manager)

@router.get("/user/{user_id}/analytics", response_model=AnalyticsResponse)
async def get_user_analytics(
    user_id: str,
    period: str = Query("30_days", description="Período de análise: 7_days, 30_days, 90_days")
):
    """
    Obtém análises completas de produtividade do usuário
    """
    try:
        # Validate period
        if period not in ["7_days", "30_days", "90_days"]:
            raise HTTPException(status_code=400, detail="Período inválido")
        
        # Get comprehensive analytics
        analytics = await analytics_service.get_comprehensive_analytics(user_id, period)
        
        return AnalyticsResponse(
            daily_stats=analytics.daily_stats,
            weekly_trends=analytics.weekly_trends,
            monthly_overview=analytics.monthly_overview,
            behavioral_patterns=analytics.behavioral_patterns,
            achievements=analytics.achievements,
            recommendations=analytics.recommendations
        )
        
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter análises")

@router.get("/user/{user_id}/insights", response_model=InsightsResponse)
async def get_user_insights(
    user_id: str,
    include_predictions: bool = Query(True, description="Incluir insights preditivos")
):
    """
    Obtém insights avançados de produtividade e comportamento
    """
    try:
        # Get user context
        user_context = await db_manager.fetch_user_context(user_id)
        if "error" in user_context:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Get productivity insights
        productivity_insights = await db_manager.get_productivity_insights(user_id)
        
        # Get mood analysis
        mood_analysis = await mood_detector.detect_current_mood(user_id, user_context)
        
        # Get optimization suggestions
        from services.task_intelligence import TaskIntelligenceService
        task_intelligence = TaskIntelligenceService(db_manager)
        optimizations = await task_intelligence.optimize_existing_tasks(user_id)
        
        optimization_suggestions = [
            {
                "task_id": opt.task_id,
                "type": opt.optimization_type,
                "suggestion": opt.suggested_changes.get("suggested_action", ""),
                "expected_improvement": opt.expected_improvement
            }
            for opt in optimizations
        ]
        
        # Generate predictive insights
        predictive_insights = []
        if include_predictions:
            predictions = await mood_detector.predict_mood_changes(user_id, user_context)
            
            risk_level = predictions.get("overall_risk_level", "low")
            if risk_level == "high":
                predictive_insights.append("Alto risco de queda na produtividade nos próximos dias")
            elif risk_level == "medium":
                predictive_insights.append("Monitore sua energia para manter o ritmo atual")
            else:
                predictive_insights.append("Tendência positiva de manutenção da produtividade")
            
            # Add specific predictions
            risk_factors = predictions.get("risk_factors", [])
            if risk_factors:
                predictive_insights.extend(risk_factors[:2])
        
        return InsightsResponse(
            productivity_metrics=productivity_insights,
            mood_analysis=mood_analysis,
            optimization_suggestions=optimization_suggestions,
            predictive_insights=predictive_insights
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user insights: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter insights")

@router.get("/user/{user_id}/mood-history", response_model=MoodHistoryResponse)
async def get_mood_history(
    user_id: str,
    days: int = Query(30, description="Número de dias para análise", ge=7, le=90)
):
    """
    Obtém histórico e análise de padrões de humor do usuário
    """
    try:
        # Get mood history analysis
        mood_history = await mood_detector.analyze_mood_history(user_id, days)
        
        if "error" in mood_history:
            raise HTTPException(status_code=404, detail=mood_history["error"])
        
        return MoodHistoryResponse(
            period_days=mood_history["period_days"],
            mood_patterns=mood_history["mood_patterns"],
            mood_triggers=mood_history["mood_triggers"],
            stability_score=mood_history["stability_score"],
            recommendations=mood_history["recommendations"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mood history: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter histórico de humor")

@router.post("/user/{user_id}/feedback")
async def submit_feedback(
    user_id: str,
    feedback: Dict[str, Any]
):
    """
    Submete feedback sobre a experiência com a Lumi
    """
    try:
        # Validate feedback structure
        required_fields = ["rating", "interaction_id"]
        if not all(field in feedback for field in required_fields):
            raise HTTPException(status_code=400, detail="Campos obrigatórios: rating, interaction_id")
        
        # Store feedback in database
        feedback_data = {
            "user_id": user_id,
            "rating": feedback["rating"],
            "interaction_id": feedback["interaction_id"],
            "comments": feedback.get("comments", ""),
            "suggestions": feedback.get("suggestions", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Update Lumi's learning from feedback
        await _process_feedback_learning(user_id, feedback_data)
        
        return {
            "status": "success",
            "message": "Feedback recebido com sucesso",
            "feedback_id": feedback["interaction_id"]  # In a real system, generate unique ID
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(status_code=500, detail="Erro ao enviar feedback")

@router.get("/user/{user_id}/summary")
async def get_user_summary(user_id: str):
    """
    Obtém resumo executivo do usuário para dashboard
    """
    try:
        # Get basic user context
        user_context = await db_manager.fetch_user_context(user_id)
        if "error" in user_context:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Get current mood
        mood_analysis = await mood_detector.detect_current_mood(user_id, user_context)
        
        # Compile summary
        tasks_stats = user_context.get("tasks_stats", {})
        current_streak = user_context.get("current_streak", 0)
        today_pomodoros = len(user_context.get("today_pomodoros", []))
        
        return {
            "user_info": user_context.get("user_info", {}),
            "current_mood": mood_analysis.get("current_mood", "neutral"),
            "mood_confidence": mood_analysis.get("confidence", 0.5),
            "today_summary": {
                "pomodoros_completed": today_pomodoros,
                "tasks_pending": tasks_stats.get("pending_tasks", 0),
                "tasks_completed": tasks_stats.get("completed_tasks", 0)
            },
            "streak_days": current_streak,
            "quick_insights": mood_analysis.get("insights", [])[:2],
            "recommendations": mood_analysis.get("recommendations", [])[:2]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user summary: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter resumo")

@router.get("/user/{user_id}/task-suggestions")
async def get_task_suggestions(
    user_id: str,
    context: Optional[str] = Query(None, description="Contexto para sugestões")
):
    """
    Obtém sugestões inteligentes de tarefas
    """
    try:
        from services.task_intelligence import TaskIntelligenceService
        task_intelligence = TaskIntelligenceService(db_manager)
        
        # Get intelligent task suggestions
        suggestions = await task_intelligence.generate_intelligent_task_suggestions(
            user_id, context or ""
        )
        
        return {
            "suggestions": [
                {
                    "title": s.title,
                    "description": s.description,
                    "priority": s.priority,
                    "estimated_pomodoros": s.estimated_pomodoros,
                    "reasoning": s.reasoning,
                    "confidence": s.confidence
                }
                for s in suggestions
            ],
            "context_used": context or "general",
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting task suggestions: {e}")
        raise HTTPException(status_code=500, detail="Erro ao obter sugestões de tarefas")

async def _process_feedback_learning(user_id: str, feedback_data: Dict[str, Any]):
    """Process feedback for machine learning improvements"""
    try:
        # In a real system, this would update ML models
        # For now, store the feedback for future analysis
        
        learning_data = {
            "personality_profile": json.dumps({
                "feedback_history": [feedback_data],
                "user_satisfaction": feedback_data["rating"],
                "improvement_areas": feedback_data.get("suggestions", "")
            }),
            "behavior_patterns": json.dumps({
                "feedback_frequency": 1,
                "avg_rating": feedback_data["rating"]
            })
        }
        
        await db_manager.update_lumi_memory(user_id, learning_data)
        logger.info(f"Processed feedback learning for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error processing feedback learning: {e}")

@router.get("/analytics/health")
async def analytics_health():
    """Health check for analytics services"""
    return {
        "status": "healthy",
        "services": {
            "user_analytics": "operational",
            "mood_detector": "operational",
            "database": "connected"
        },
        "timestamp": datetime.now().isoformat()
    }

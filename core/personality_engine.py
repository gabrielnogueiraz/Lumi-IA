import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from config.personality_config import MOOD_STATES, PERSONALITY_TRAITS, COMMUNICATION_PATTERNS, MOOD_DETECTION_RULES
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class MoodAnalysis:
    detected_mood: str
    confidence: float
    personality_tone: str
    adaptation_applied: bool
    contributing_factors: List[str]
    recommendations: List[str]

class PersonalityEngine:
    def __init__(self):
        self.mood_cache = {}
        self.personality_cache = {}
    
    async def analyze_user_mood(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user mood based on behavioral data"""
        try:
            user_id = user_context.get("user_info", {}).get("id")
            if not user_id:
                return self._get_default_mood()
            
            # Check cache first (valid for 30 minutes)
            cache_key = f"{user_id}_{datetime.now().strftime('%H_%M')}"
            if cache_key in self.mood_cache:
                cached_result = self.mood_cache[cache_key]
                if (datetime.now() - cached_result["timestamp"]).seconds < 1800:
                    return cached_result["mood_analysis"]
            
            # Analyze mood based on multiple factors
            mood_scores = await self._calculate_mood_scores(user_context)
            
            # Determine primary mood
            primary_mood = max(mood_scores.items(), key=lambda x: x[1])
            mood_name, confidence = primary_mood
            
            # Get personality adaptation
            personality_tone = self._get_personality_tone(mood_name, confidence)
            
            # Generate contributing factors and recommendations
            contributing_factors = self._get_contributing_factors(mood_name, user_context)
            recommendations = self._get_mood_recommendations(mood_name, user_context)
            
            mood_analysis = {
                "detected_mood": mood_name,
                "confidence": confidence,
                "personality_tone": personality_tone,
                "adaptation_applied": True,
                "contributing_factors": contributing_factors,
                "recommendations": recommendations,
                "mood_scores": mood_scores
            }
            
            # Cache result
            self.mood_cache[cache_key] = {
                "mood_analysis": mood_analysis,
                "timestamp": datetime.now()
            }
            
            logger.info(f"Mood analyzed for user {user_id}: {mood_name} ({confidence:.2f})")
            
            return mood_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing user mood: {e}")
            return self._get_default_mood()
    
    async def _calculate_mood_scores(self, user_context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate mood scores based on behavioral indicators"""
        mood_scores = {mood: 0.0 for mood in MOOD_STATES.keys()}
        
        tasks_stats = user_context.get("tasks_stats", {})
        recent_activity = user_context.get("recent_activity", [])
        productivity_patterns = user_context.get("productivity_patterns", {})
        current_streak = user_context.get("current_streak", 0)
        today_pomodoros = user_context.get("today_pomodoros", [])
        lumi_memory = user_context.get("lumi_memory", {})
        
        # Calculate individual mood scores
        mood_scores["motivated"] = self._calculate_motivated_score(
            tasks_stats, recent_activity, current_streak, today_pomodoros
        )
        
        mood_scores["struggling"] = self._calculate_struggling_score(
            tasks_stats, recent_activity, current_streak, lumi_memory
        )
        
        mood_scores["focused"] = self._calculate_focused_score(
            today_pomodoros, productivity_patterns, tasks_stats
        )
        
        mood_scores["overwhelmed"] = self._calculate_overwhelmed_score(
            tasks_stats, recent_activity, today_pomodoros
        )
        
        mood_scores["celebrating"] = self._calculate_celebrating_score(
            current_streak, tasks_stats, recent_activity, lumi_memory
        )
        
        mood_scores["returning"] = self._calculate_returning_score(
            recent_activity, lumi_memory, current_streak
        )
        
        # Normalize scores to 0-1 range
        max_score = max(mood_scores.values()) if mood_scores.values() else 1.0
        if max_score > 0:
            mood_scores = {mood: score / max_score for mood, score in mood_scores.items()}
        
        return mood_scores
    
    def _calculate_motivated_score(self, tasks_stats: Dict, recent_activity: List, 
                                 current_streak: int, today_pomodoros: List) -> float:
        """Calculate motivated mood score"""
        score = 0.0
        
        # Recent completions
        today_completions = len([p for p in today_pomodoros if p.get("status") == "completed"])
        if today_completions >= 3:
            score += 0.3
        
        # Current streak
        if current_streak >= 2:
            score += 0.2 + min(current_streak * 0.05, 0.3)
        
        # Completion rate
        total_tasks = tasks_stats.get("total_tasks", 0)
        completed_tasks = tasks_stats.get("completed_tasks", 0)
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            if completion_rate > 0.7:
                score += 0.2
        
        # Recent activity trend
        if len(recent_activity) >= 2:
            recent_trend = recent_activity[0].get("tasks_completed", 0) - recent_activity[1].get("tasks_completed", 0)
            if recent_trend > 0:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_struggling_score(self, tasks_stats: Dict, recent_activity: List,
                                  current_streak: int, lumi_memory: Dict) -> float:
        """Calculate struggling mood score"""
        score = 0.0
        
        # Overdue tasks
        overdue_tasks = tasks_stats.get("overdue_tasks", 0)
        if overdue_tasks >= 2:
            score += 0.3 + min(overdue_tasks * 0.1, 0.2)
        
        # Low completion rate
        total_tasks = tasks_stats.get("total_tasks", 0)
        completed_tasks = tasks_stats.get("completed_tasks", 0)
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            if completion_rate < 0.3:
                score += 0.3
        
        # Broken streak
        if current_streak == 0:
            score += 0.2
        
        # Declining activity
        if len(recent_activity) >= 3:
            recent_completions = [day.get("tasks_completed", 0) for day in recent_activity[:3]]
            if all(recent_completions[i] >= recent_completions[i+1] for i in range(len(recent_completions)-1)):
                score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_focused_score(self, today_pomodoros: List, productivity_patterns: Dict,
                               tasks_stats: Dict) -> float:
        """Calculate focused mood score"""
        score = 0.0
        
        # Long pomodoro sessions
        completed_pomodoros = [p for p in today_pomodoros if p.get("status") == "completed"]
        if completed_pomodoros:
            avg_duration = sum(p.get("duration", 0) for p in completed_pomodoros) / len(completed_pomodoros)
            if avg_duration >= 20:
                score += 0.3
        
        # Consecutive sessions
        consecutive_count = 0
        for i, pomodoro in enumerate(today_pomodoros):
            if pomodoro.get("status") == "completed":
                consecutive_count += 1
            else:
                break
        
        if consecutive_count >= 3:
            score += 0.2
        
        # Current focus time
        current_time = datetime.now().hour
        peak_hour = productivity_patterns.get("peak_hour")
        if peak_hour and abs(current_time - peak_hour) <= 1:
            score += 0.2
        
        # Task switching (low switching = high focus)
        if len(set(p.get("title", "") for p in today_pomodoros)) <= 2 and len(today_pomodoros) >= 3:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_overwhelmed_score(self, tasks_stats: Dict, recent_activity: List,
                                   today_pomodoros: List) -> float:
        """Calculate overwhelmed mood score"""
        score = 0.0
        
        # Too many pending tasks
        pending_tasks = tasks_stats.get("pending_tasks", 0)
        if pending_tasks >= 10:
            score += 0.4
        elif pending_tasks >= 5:
            score += 0.2
        
        # Poor task creation vs completion ratio
        if recent_activity:
            recent_created = sum(day.get("tasks_created", 0) for day in recent_activity[:3])
            recent_completed = sum(day.get("tasks_completed", 0) for day in recent_activity[:3])
            if recent_created > 0 and recent_completed / recent_created < 0.4:
                score += 0.3
        
        # Many high priority pending tasks
        # This would need additional query, for now use heuristic
        if pending_tasks >= 5:
            score += 0.2
        
        # Many started but not completed pomodoros today
        incomplete_pomodoros = len([p for p in today_pomodoros if p.get("status") != "completed"])
        if incomplete_pomodoros >= 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_celebrating_score(self, current_streak: int, tasks_stats: Dict,
                                   recent_activity: List, lumi_memory: Dict) -> float:
        """Calculate celebrating mood score"""
        score = 0.0
        
        # Long streak
        if current_streak >= 7:
            score += 0.4 + min((current_streak - 7) * 0.05, 0.2)
        
        # High completion rate
        total_tasks = tasks_stats.get("total_tasks", 0)
        completed_tasks = tasks_stats.get("completed_tasks", 0)
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            if completion_rate >= 0.8:
                score += 0.3
        
        # Recent achievement (checking if today's completion is above average)
        if recent_activity:
            today_completed = recent_activity[0].get("tasks_completed", 0)
            if len(recent_activity) > 1:
                avg_completion = sum(day.get("tasks_completed", 0) for day in recent_activity[1:]) / (len(recent_activity) - 1)
                if today_completed > avg_completion * 1.5:
                    score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_returning_score(self, recent_activity: List, lumi_memory: Dict,
                                 current_streak: int) -> float:
        """Calculate returning mood score"""
        score = 0.0
        
        # Days since last activity
        if len(recent_activity) == 0:
            # No recent activity but user is here now
            score += 0.5
        elif len(recent_activity) < 3:
            # Sparse activity
            score += 0.3
        
        # Previous streak was good but broken
        if current_streak == 0 and lumi_memory:
            # This would need to check historical streak data
            # For now, use heuristic
            interaction_count = lumi_memory.get("interaction_count", 0)
            if interaction_count > 10:
                score += 0.3
        
        # User has history but low recent activity
        total_tasks = sum(day.get("tasks_completed", 0) for day in recent_activity) if recent_activity else 0
        if lumi_memory and lumi_memory.get("interaction_count", 0) > 5 and total_tasks < 3:
            score += 0.2
        
        return min(score, 1.0)
    
    def _get_personality_tone(self, mood: str, confidence: float) -> str:
        """Get personality tone based on mood and confidence"""
        mood_config = MOOD_STATES.get(mood, MOOD_STATES["motivated"])
        base_tone = mood_config["tone"]
        
        # Adjust tone based on confidence
        if confidence < 0.5:
            # Low confidence, use more neutral tone
            return "supportive"
        
        return base_tone
    
    def _get_contributing_factors(self, mood: str, user_context: Dict[str, Any]) -> List[str]:
        """Get factors that contributed to the detected mood"""
        factors = []
        
        tasks_stats = user_context.get("tasks_stats", {})
        current_streak = user_context.get("current_streak", 0)
        today_pomodoros = user_context.get("today_pomodoros", [])
        
        if mood == "motivated":
            if current_streak >= 2:
                factors.append(f"Sequência de {current_streak} dias ativa")
            if len(today_pomodoros) >= 3:
                factors.append("Múltiplos pomodoros completados hoje")
                
        elif mood == "struggling":
            overdue = tasks_stats.get("overdue_tasks", 0)
            if overdue > 0:
                factors.append(f"{overdue} tarefas em atraso")
            if current_streak == 0:
                factors.append("Sequência interrompida")
                
        elif mood == "focused":
            if today_pomodoros:
                factors.append("Sessões de foco consistentes hoje")
                
        elif mood == "overwhelmed":
            pending = tasks_stats.get("pending_tasks", 0)
            if pending >= 5:
                factors.append(f"{pending} tarefas pendentes")
                
        elif mood == "celebrating":
            if current_streak >= 7:
                factors.append(f"Sequência impressionante de {current_streak} dias")
                
        return factors[:3]
    
    def _get_mood_recommendations(self, mood: str, user_context: Dict[str, Any]) -> List[str]:
        """Get recommendations based on detected mood"""
        recommendations = []
        
        if mood == "motivated":
            recommendations.extend([
                "Aproveite essa energia para tacklear tarefas desafiadoras",
                "Considere aumentar sua meta diária"
            ])
            
        elif mood == "struggling":
            recommendations.extend([
                "Comece com tarefas pequenas e fáceis",
                "Considere reduzir o escopo das tarefas grandes"
            ])
            
        elif mood == "focused":
            recommendations.extend([
                "Continue no seu ritmo atual",
                "Evite distrações durante esse período produtivo"
            ])
            
        elif mood == "overwhelmed":
            recommendations.extend([
                "Priorize apenas 3 tarefas para hoje",
                "Divida tarefas grandes em partes menores"
            ])
            
        elif mood == "celebrating":
            recommendations.extend([
                "Defina a próxima meta desafiadora",
                "Compartilhe seu sucesso para manter a motivação"
            ])
            
        elif mood == "returning":
            recommendations.extend([
                "Comece devagar com tarefas simples",
                "Reestabeleça uma rotina consistente"
            ])
        
        return recommendations[:2]
    
    def _get_default_mood(self) -> Dict[str, Any]:
        """Get default mood analysis when unable to analyze"""
        return {
            "detected_mood": "neutral",
            "confidence": 0.5,
            "personality_tone": "friendly",
            "adaptation_applied": False,
            "contributing_factors": ["Análise inicial"],
            "recommendations": ["Continue usando o sistema para análises mais precisas"],
            "mood_scores": {}
        }
    
    async def update_personality_memory(self, user_id: str, mood_analysis: Dict[str, Any], 
                                      interaction_feedback: Optional[Dict[str, Any]] = None) -> bool:
        """Update personality memory based on interaction"""
        try:
            # This would update the database with personality learning
            # For now, just update cache
            self.personality_cache[user_id] = {
                "last_mood": mood_analysis["detected_mood"],
                "confidence_history": mood_analysis["confidence"],
                "successful_adaptations": [],
                "interaction_preferences": interaction_feedback or {},
                "updated_at": datetime.now()
            }
            
            return True
        except Exception as e:
            logger.error(f"Error updating personality memory: {e}")
            return False

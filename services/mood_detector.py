import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from config.personality_config import MOOD_DETECTION_RULES
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class MoodIndicator:
    indicator_type: str
    value: Any
    weight: float
    description: str

@dataclass
class MoodTransition:
    from_mood: str
    to_mood: str
    timestamp: datetime
    trigger_factors: List[str]
    confidence: float

class MoodDetectorService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.mood_history_cache = {}
        
    async def detect_current_mood(self, user_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect user's current mood based on behavioral indicators"""
        try:
            # Calculate mood indicators
            mood_indicators = await self._calculate_mood_indicators(user_id, user_context)
            
            # Apply detection rules
            mood_scores = await self._apply_detection_rules(mood_indicators)
            
            # Determine primary mood
            primary_mood, confidence = self._determine_primary_mood(mood_scores)
            
            # Analyze mood transitions
            mood_transition = await self._analyze_mood_transition(user_id, primary_mood)
            
            # Generate mood insights
            insights = self._generate_mood_insights(primary_mood, mood_indicators, mood_transition)
            
            # Update mood history
            await self._update_mood_history(user_id, primary_mood, confidence, mood_indicators)
            
            return {
                "current_mood": primary_mood,
                "confidence": confidence,
                "mood_scores": mood_scores,
                "indicators": [indicator.__dict__ for indicator in mood_indicators],
                "transition": mood_transition.__dict__ if mood_transition else None,
                "insights": insights,
                "recommendations": self._generate_mood_recommendations(primary_mood, mood_indicators)
            }
            
        except Exception as e:
            logger.error(f"Error detecting mood: {e}")
            return self._get_default_mood_detection()
    
    async def analyze_mood_history(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze user's mood patterns over time"""
        try:
            async with self.db_manager.get_connection() as conn:
                # Get mood history from lumi_memory table
                mood_history = await conn.fetch("""
                    SELECT current_mood, updated_at, behavior_patterns
                    FROM lumi_memory 
                    WHERE user_id = $1 AND updated_at >= NOW() - INTERVAL '%s days'
                    ORDER BY updated_at DESC
                """, user_id, days)
                
                if not mood_history:
                    return {"error": "Insufficient mood history data"}
                
                # Analyze patterns
                mood_patterns = self._analyze_mood_patterns([dict(row) for row in mood_history])
                
                # Identify triggers
                mood_triggers = await self._identify_mood_triggers(user_id, days)
                
                # Calculate mood stability
                stability_score = self._calculate_mood_stability(mood_history)
                
                return {
                    "period_days": days,
                    "mood_patterns": mood_patterns,
                    "mood_triggers": mood_triggers,
                    "stability_score": stability_score,
                    "recommendations": self._generate_pattern_recommendations(mood_patterns)
                }
                
        except Exception as e:
            logger.error(f"Error analyzing mood history: {e}")
            return {"error": str(e)}
    
    async def predict_mood_changes(self, user_id: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Predict potential mood changes based on patterns and current state"""
        try:
            # Get current mood state
            current_mood_data = await self.detect_current_mood(user_id, user_context)
            current_mood = current_mood_data["current_mood"]
            
            # Analyze risk factors for mood decline
            risk_factors = await self._analyze_mood_risk_factors(user_id, user_context)
            
            # Predict likely transitions
            likely_transitions = self._predict_mood_transitions(current_mood, risk_factors)
            
            # Generate preventive recommendations
            preventive_actions = self._generate_preventive_actions(risk_factors, likely_transitions)
            
            return {
                "current_mood": current_mood,
                "risk_factors": risk_factors,
                "likely_transitions": likely_transitions,
                "preventive_actions": preventive_actions,
                "overall_risk_level": self._calculate_overall_risk(risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Error predicting mood changes: {e}")
            return {"error": str(e)}
    
    async def _calculate_mood_indicators(self, user_id: str, user_context: Dict[str, Any]) -> List[MoodIndicator]:
        """Calculate specific mood indicators from user data"""
        indicators = []
        
        tasks_stats = user_context.get("tasks_stats", {})
        recent_activity = user_context.get("recent_activity", [])
        current_streak = user_context.get("current_streak", 0)
        today_pomodoros = user_context.get("today_pomodoros", [])
        productivity_patterns = user_context.get("productivity_patterns", {})
        
        # Task completion indicators
        total_tasks = tasks_stats.get("total_tasks", 0)
        completed_tasks = tasks_stats.get("completed_tasks", 0)
        overdue_tasks = tasks_stats.get("overdue_tasks", 0)
        pending_tasks = tasks_stats.get("pending_tasks", 0)
        
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            indicators.append(MoodIndicator(
                indicator_type="completion_rate",
                value=completion_rate,
                weight=0.8,
                description=f"Taxa de conclusão: {completion_rate:.1%}"
            ))
        
        # Overdue tasks indicator
        if overdue_tasks > 0:
            indicators.append(MoodIndicator(
                indicator_type="overdue_tasks",
                value=overdue_tasks,
                weight=0.9,
                description=f"{overdue_tasks} tarefas em atraso"
            ))
        
        # Streak indicator
        indicators.append(MoodIndicator(
            indicator_type="current_streak",
            value=current_streak,
            weight=0.7,
            description=f"Sequência de {current_streak} dias"
        ))
        
        # Daily activity indicator
        today_completed_pomodoros = len([p for p in today_pomodoros if p.get("status") == "completed"])
        indicators.append(MoodIndicator(
            indicator_type="today_pomodoros",
            value=today_completed_pomodoros,
            weight=0.6,
            description=f"{today_completed_pomodoros} pomodoros hoje"
        ))
        
        # Recent activity trend
        if len(recent_activity) >= 2:
            recent_trend = (recent_activity[0].get("tasks_completed", 0) - 
                          recent_activity[1].get("tasks_completed", 0))
            indicators.append(MoodIndicator(
                indicator_type="activity_trend",
                value=recent_trend,
                weight=0.5,
                description=f"Tendência de atividade: {'+' if recent_trend >= 0 else ''}{recent_trend}"
            ))
        
        # Focus quality indicator
        if today_pomodoros:
            avg_duration = sum(p.get("duration", 0) for p in today_pomodoros if p.get("status") == "completed")
            if today_completed_pomodoros > 0:
                avg_duration = avg_duration / today_completed_pomodoros
                indicators.append(MoodIndicator(
                    indicator_type="focus_quality",
                    value=avg_duration,
                    weight=0.4,
                    description=f"Duração média de foco: {avg_duration:.1f}min"
                ))
        
        # Overwhelm indicator
        if pending_tasks > 0:
            overwhelm_score = min(pending_tasks / 10.0, 1.0)
            indicators.append(MoodIndicator(
                indicator_type="overwhelm_level",
                value=overwhelm_score,
                weight=0.6,
                description=f"Nível de sobrecarga: {overwhelm_score:.1%}"
            ))
        
        # Productivity timing indicator
        current_hour = datetime.now().hour
        peak_hour = productivity_patterns.get("peak_hour")
        if peak_hour:
            time_alignment = 1.0 - abs(current_hour - peak_hour) / 12.0
            indicators.append(MoodIndicator(
                indicator_type="timing_alignment",
                value=time_alignment,
                weight=0.3,
                description=f"Alinhamento com horário de pico: {time_alignment:.1%}"
            ))
        
        return indicators
    
    async def _apply_detection_rules(self, indicators: List[MoodIndicator]) -> Dict[str, float]:
        """Apply mood detection rules to calculate mood scores"""
        mood_scores = {mood: 0.0 for mood in MOOD_DETECTION_RULES.keys()}
        
        # Create indicator lookup
        indicator_values = {ind.indicator_type: ind.value for ind in indicators}
        
        for mood, rules in MOOD_DETECTION_RULES.items():
            score = 0.0
            total_weight = 0.0
            
            for rule_key, rule_condition in rules.items():
                if rule_key in indicator_values:
                    value = indicator_values[rule_key]
                    weight = next((ind.weight for ind in indicators if ind.indicator_type == rule_key), 1.0)
                    
                    # Apply rule conditions
                    if isinstance(rule_condition, dict):
                        if "min" in rule_condition and value >= rule_condition["min"]:
                            score += weight
                        if "max" in rule_condition and value <= rule_condition["max"]:
                            score += weight
                        if "ratio" in rule_condition:
                            # Special handling for ratio comparisons
                            pass
                    elif rule_condition is True:
                        score += weight
                    
                    total_weight += weight
            
            # Special logic for specific moods
            if mood == "motivated":
                score += self._calculate_motivated_bonus(indicator_values)
            elif mood == "struggling":
                score += self._calculate_struggling_bonus(indicator_values)
            elif mood == "focused":
                score += self._calculate_focused_bonus(indicator_values)
            elif mood == "overwhelmed":
                score += self._calculate_overwhelmed_bonus(indicator_values)
            elif mood == "celebrating":
                score += self._calculate_celebrating_bonus(indicator_values)
            elif mood == "returning":
                score += self._calculate_returning_bonus(indicator_values)
            
            # Normalize score
            mood_scores[mood] = score / max(total_weight, 1.0) if total_weight > 0 else 0.0
        
        return mood_scores
    
    def _calculate_motivated_bonus(self, indicators: Dict[str, Any]) -> float:
        """Calculate bonus score for motivated mood"""
        bonus = 0.0
        
        if indicators.get("completion_rate", 0) > 0.7:
            bonus += 0.3
        if indicators.get("current_streak", 0) >= 3:
            bonus += 0.2
        if indicators.get("today_pomodoros", 0) >= 3:
            bonus += 0.2
        if indicators.get("activity_trend", 0) > 0:
            bonus += 0.1
        
        return bonus
    
    def _calculate_struggling_bonus(self, indicators: Dict[str, Any]) -> float:
        """Calculate bonus score for struggling mood"""
        bonus = 0.0
        
        if indicators.get("overdue_tasks", 0) >= 2:
            bonus += 0.4
        if indicators.get("completion_rate", 0) < 0.3:
            bonus += 0.3
        if indicators.get("current_streak", 0) == 0:
            bonus += 0.2
        if indicators.get("today_pomodoros", 0) == 0:
            bonus += 0.2
        
        return bonus
    
    def _calculate_focused_bonus(self, indicators: Dict[str, Any]) -> float:
        """Calculate bonus score for focused mood"""
        bonus = 0.0
        
        focus_quality = indicators.get("focus_quality", 0)
        if focus_quality >= 20:
            bonus += 0.3
        
        if indicators.get("today_pomodoros", 0) >= 3:
            bonus += 0.2
        
        timing_alignment = indicators.get("timing_alignment", 0)
        if timing_alignment > 0.8:
            bonus += 0.2
        
        return bonus
    
    def _calculate_overwhelmed_bonus(self, indicators: Dict[str, Any]) -> float:
        """Calculate bonus score for overwhelmed mood"""
        bonus = 0.0
        
        overwhelm_level = indicators.get("overwhelm_level", 0)
        if overwhelm_level > 0.7:
            bonus += 0.4
        
        if indicators.get("overdue_tasks", 0) >= 3:
            bonus += 0.3
        
        completion_rate = indicators.get("completion_rate", 0)
        if completion_rate < 0.4:
            bonus += 0.2
        
        return bonus
    
    def _calculate_celebrating_bonus(self, indicators: Dict[str, Any]) -> float:
        """Calculate bonus score for celebrating mood"""
        bonus = 0.0
        
        if indicators.get("current_streak", 0) >= 7:
            bonus += 0.4
        if indicators.get("completion_rate", 0) >= 0.8:
            bonus += 0.3
        if indicators.get("activity_trend", 0) > 1:
            bonus += 0.2
        
        return bonus
    
    def _calculate_returning_bonus(self, indicators: Dict[str, Any]) -> float:
        """Calculate bonus score for returning mood"""
        # This would require historical data about user absence
        # For now, use simple heuristics
        bonus = 0.0
        
        if indicators.get("current_streak", 0) == 0:
            bonus += 0.2
        if indicators.get("today_pomodoros", 0) == 0:
            bonus += 0.1
        
        return bonus
    
    def _determine_primary_mood(self, mood_scores: Dict[str, float]) -> Tuple[str, float]:
        """Determine primary mood from scores"""
        if not mood_scores or all(score == 0 for score in mood_scores.values()):
            return "neutral", 0.5
        
        # Find the mood with highest score
        primary_mood = max(mood_scores.items(), key=lambda x: x[1])
        mood_name, confidence = primary_mood
        
        # Ensure minimum confidence threshold
        if confidence < 0.3:
            return "neutral", confidence
        
        return mood_name, min(confidence, 1.0)
    
    async def _analyze_mood_transition(self, user_id: str, current_mood: str) -> Optional[MoodTransition]:
        """Analyze mood transition from previous state"""
        try:
            async with self.db_manager.get_connection() as conn:
                # Get previous mood from memory
                previous_mood_data = await conn.fetchrow("""
                    SELECT current_mood, updated_at
                    FROM lumi_memory
                    WHERE user_id = $1
                    ORDER BY updated_at DESC
                    LIMIT 1
                """, user_id)
                
                if previous_mood_data:
                    previous_mood = previous_mood_data["current_mood"]
                    previous_timestamp = previous_mood_data["updated_at"]
                    
                    if previous_mood != current_mood:
                        # Analyze what caused the transition
                        trigger_factors = self._identify_transition_triggers(previous_mood, current_mood)
                        
                        return MoodTransition(
                            from_mood=previous_mood,
                            to_mood=current_mood,
                            timestamp=datetime.now(),
                            trigger_factors=trigger_factors,
                            confidence=0.7
                        )
                
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing mood transition: {e}")
            return None
    
    def _identify_transition_triggers(self, from_mood: str, to_mood: str) -> List[str]:
        """Identify likely triggers for mood transition"""
        triggers = []
        
        # Common transition patterns
        if from_mood == "motivated" and to_mood == "overwhelmed":
            triggers.append("Aumento na carga de trabalho")
        elif from_mood == "struggling" and to_mood == "motivated":
            triggers.append("Conclusão de tarefas pendentes")
        elif from_mood == "focused" and to_mood == "celebrating":
            triggers.append("Atingimento de objetivos")
        elif to_mood == "returning":
            triggers.append("Retorno após período de inatividade")
        
        return triggers
    
    def _generate_mood_insights(self, mood: str, indicators: List[MoodIndicator], 
                              transition: Optional[MoodTransition]) -> List[str]:
        """Generate insights about the detected mood"""
        insights = []
        
        # Primary mood insights
        if mood == "motivated":
            insights.append("Você está em um excelente momento de produtividade!")
        elif mood == "struggling":
            insights.append("Detectei alguns desafios em sua rotina")
        elif mood == "focused":
            insights.append("Seu foco está em alta qualidade")
        elif mood == "overwhelmed":
            insights.append("Há sinais de sobrecarga em suas atividades")
        elif mood == "celebrating":
            insights.append("Parabéns pelos resultados conquistados!")
        elif mood == "returning":
            insights.append("Bem-vindo de volta à sua rotina produtiva")
        
        # Indicator-based insights
        high_weight_indicators = [ind for ind in indicators if ind.weight >= 0.7]
        for indicator in high_weight_indicators[:2]:
            insights.append(indicator.description)
        
        # Transition insights
        if transition:
            insights.append(f"Transição de {transition.from_mood} para {transition.to_mood}")
        
        return insights
    
    def _generate_mood_recommendations(self, mood: str, indicators: List[MoodIndicator]) -> List[str]:
        """Generate recommendations based on detected mood"""
        recommendations = []
        
        if mood == "motivated":
            recommendations.extend([
                "Aproveite esse momento para tackle tarefas desafiadoras",
                "Considere aumentar suas metas diárias"
            ])
        elif mood == "struggling":
            recommendations.extend([
                "Comece com tarefas pequenas para reconstruir momentum",
                "Considere reduzir temporariamente suas expectativas"
            ])
        elif mood == "focused":
            recommendations.extend([
                "Continue no ritmo atual para maximizar a produtividade",
                "Evite interrupções durante este período de foco"
            ])
        elif mood == "overwhelmed":
            recommendations.extend([
                "Priorize apenas 3 tarefas mais importantes",
                "Considere delegar ou adiar tarefas menos críticas"
            ])
        elif mood == "celebrating":
            recommendations.extend([
                "Defina novas metas desafiadoras",
                "Compartilhe seus sucessos para manter motivação"
            ])
        elif mood == "returning":
            recommendations.extend([
                "Comece gradualmente com tarefas simples",
                "Foque em reestabelecer sua rotina"
            ])
        
        return recommendations[:3]
    
    async def _update_mood_history(self, user_id: str, mood: str, confidence: float, 
                                 indicators: List[MoodIndicator]) -> bool:
        """Update mood history in database"""
        try:
            # Store mood in lumi_memory table
            mood_data = {
                "current_mood": mood,
                "confidence": confidence,
                "indicators": [ind.__dict__ for ind in indicators],
                "timestamp": datetime.now().isoformat()
            }
            
            await self.db_manager.update_lumi_memory(user_id, {
                "current_mood": mood,
                "contextual_memory": json.dumps(mood_data)
            })
            
            return True
        except Exception as e:
            logger.error(f"Error updating mood history: {e}")
            return False
    
    def _get_default_mood_detection(self) -> Dict[str, Any]:
        """Get default mood detection result"""
        return {
            "current_mood": "neutral",
            "confidence": 0.5,
            "mood_scores": {},
            "indicators": [],
            "transition": None,
            "insights": ["Analisando seus padrões..."],
            "recommendations": ["Continue usando o sistema para análises mais precisas"]
        }

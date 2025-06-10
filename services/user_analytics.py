import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class ProductivityMetrics:
    completion_rate: float
    avg_pomodoros_per_task: float
    peak_productivity_hours: List[int]
    productive_days: List[str]
    focus_score: float
    consistency_score: float
    efficiency_trend: str

@dataclass
class UserAnalytics:
    daily_stats: Dict[str, Any]
    weekly_trends: Dict[str, Any]
    monthly_overview: Dict[str, Any]
    behavioral_patterns: Dict[str, Any]
    achievements: List[Dict[str, Any]]
    recommendations: List[str]

class UserAnalyticsService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    async def get_comprehensive_analytics(self, user_id: str, period: str = "30_days") -> UserAnalytics:
        """Get comprehensive user analytics"""
        try:
            # Get base user context
            user_context = await self.db_manager.fetch_user_context(user_id)
            
            # Calculate productivity metrics
            productivity_metrics = await self._calculate_productivity_metrics(user_id, period)
            
            # Generate daily statistics
            daily_stats = await self._generate_daily_stats(user_id)
            
            # Analyze weekly trends
            weekly_trends = await self._analyze_weekly_trends(user_id)
            
            # Create monthly overview
            monthly_overview = await self._create_monthly_overview(user_id)
            
            # Detect behavioral patterns
            behavioral_patterns = await self._detect_behavioral_patterns(user_id, period)
            
            # Calculate achievements
            achievements = await self._calculate_achievements(user_id, user_context)
            
            # Generate personalized recommendations
            recommendations = await self._generate_recommendations(user_id, productivity_metrics, behavioral_patterns)
            
            return UserAnalytics(
                daily_stats=daily_stats,
                weekly_trends=weekly_trends,
                monthly_overview=monthly_overview,
                behavioral_patterns=behavioral_patterns,
                achievements=achievements,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error generating user analytics: {e}")
            return self._get_default_analytics()
    
    async def _calculate_productivity_metrics(self, user_id: str, period: str) -> ProductivityMetrics:
        """Calculate detailed productivity metrics"""
        
        # Convert period to days
        days = {"7_days": 7, "30_days": 30, "90_days": 90}.get(period, 30)
        
        async with self.db_manager.get_connection() as conn:
            # Completion rate
            completion_data = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks
                FROM tasks 
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
            """, user_id, days)
            
            total_tasks = completion_data["total_tasks"] or 0
            completed_tasks = completion_data["completed_tasks"] or 0
            completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0.0
            
            # Average pomodoros per task
            avg_pomodoros = await conn.fetchval("""
                SELECT AVG(completed_pomodoros)
                FROM tasks 
                WHERE user_id = $1 AND status = 'completed' 
                    AND updated_at >= NOW() - INTERVAL '%s days'
            """, user_id, days) or 0.0
            
            # Peak productivity hours
            peak_hours_data = await conn.fetch("""
                SELECT 
                    EXTRACT(hour FROM started_at) as hour,
                    COUNT(*) as pomodoro_count
                FROM pomodoros p
                JOIN tasks t ON p.task_id = t.id
                WHERE t.user_id = $1 AND p.status = 'completed'
                    AND p.started_at >= NOW() - INTERVAL '%s days'
                GROUP BY EXTRACT(hour FROM started_at)
                ORDER BY pomodoro_count DESC
                LIMIT 3
            """, user_id, days)
            
            peak_hours = [int(row["hour"]) for row in peak_hours_data]
            
            # Productive days
            productive_days_data = await conn.fetch("""
                SELECT 
                    EXTRACT(dow FROM updated_at) as day_of_week,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_count
                FROM tasks
                WHERE user_id = $1 AND updated_at >= NOW() - INTERVAL '%s days'
                GROUP BY EXTRACT(dow FROM updated_at)
                HAVING COUNT(*) FILTER (WHERE status = 'completed') > 0
                ORDER BY completed_count DESC
            """, user_id, days)
            
            day_names = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
            productive_days = [day_names[int(row["day_of_week"])] for row in productive_days_data[:3]]
            
            # Focus score (based on pomodoro completion rate and duration)
            focus_data = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_pomodoros,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_pomodoros,
                    AVG(duration) FILTER (WHERE status = 'completed') as avg_duration
                FROM pomodoros p
                JOIN tasks t ON p.task_id = t.id
                WHERE t.user_id = $1 AND p.started_at >= NOW() - INTERVAL '%s days'
            """, user_id, days)
            
            total_pomodoros = focus_data["total_pomodoros"] or 0
            completed_pomodoros = focus_data["completed_pomodoros"] or 0
            avg_duration = focus_data["avg_duration"] or 0
            
            focus_score = 0.0
            if total_pomodoros > 0:
                completion_ratio = completed_pomodoros / total_pomodoros
                duration_score = min(avg_duration / 25.0, 1.0) if avg_duration > 0 else 0.0
                focus_score = (completion_ratio * 0.7 + duration_score * 0.3)
            
            # Consistency score (based on daily activity)
            consistency_data = await conn.fetchval("""
                SELECT COUNT(DISTINCT DATE(updated_at))
                FROM tasks
                WHERE user_id = $1 AND status = 'completed'
                    AND updated_at >= NOW() - INTERVAL '%s days'
            """, user_id, days)
            
            consistency_score = (consistency_data or 0) / days
            
            # Efficiency trend (comparing recent vs earlier performance)
            efficiency_trend = await self._calculate_efficiency_trend(user_id, days, conn)
            
            return ProductivityMetrics(
                completion_rate=completion_rate,
                avg_pomodoros_per_task=float(avg_pomodoros),
                peak_productivity_hours=peak_hours,
                productive_days=productive_days,
                focus_score=focus_score,
                consistency_score=consistency_score,
                efficiency_trend=efficiency_trend
            )
    
    async def _calculate_efficiency_trend(self, user_id: str, days: int, conn) -> str:
        """Calculate efficiency trend over time"""
        
        # Split period in half and compare
        half_period = days // 2
        
        recent_completion = await conn.fetchval("""
            SELECT COUNT(*) FILTER (WHERE status = 'completed')::float / 
                   NULLIF(COUNT(*), 0)
            FROM tasks
            WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
        """, user_id, half_period) or 0.0
        
        earlier_completion = await conn.fetchval("""
            SELECT COUNT(*) FILTER (WHERE status = 'completed')::float / 
                   NULLIF(COUNT(*), 0)
            FROM tasks
            WHERE user_id = $1 
                AND created_at >= NOW() - INTERVAL '%s days'
                AND created_at < NOW() - INTERVAL '%s days'
        """, user_id, days, half_period) or 0.0
        
        if recent_completion > earlier_completion * 1.1:
            return "improving"
        elif recent_completion < earlier_completion * 0.9:
            return "declining"
        else:
            return "stable"
    
    async def _generate_daily_stats(self, user_id: str) -> Dict[str, Any]:
        """Generate today's statistics"""
        
        async with self.db_manager.get_connection() as conn:
            today_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
                    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress_tasks,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending_tasks
                FROM tasks
                WHERE user_id = $1 AND DATE(created_at) = CURRENT_DATE
            """, user_id)
            
            today_pomodoros = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_pomodoros,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_pomodoros,
                    SUM(duration) FILTER (WHERE status = 'completed') as total_focus_time
                FROM pomodoros p
                JOIN tasks t ON p.task_id = t.id
                WHERE t.user_id = $1 AND DATE(p.started_at) = CURRENT_DATE
            """, user_id)
            
            return {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tasks": dict(today_stats) if today_stats else {},
                "pomodoros": dict(today_pomodoros) if today_pomodoros else {},
                "focus_time_minutes": (today_pomodoros["total_focus_time"] or 0) if today_pomodoros else 0
            }
    
    async def _analyze_weekly_trends(self, user_id: str) -> Dict[str, Any]:
        """Analyze weekly productivity trends"""
        
        async with self.db_manager.get_connection() as conn:
            # Last 4 weeks comparison
            weekly_data = await conn.fetch("""
                SELECT 
                    DATE_TRUNC('week', updated_at) as week_start,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
                    COUNT(*) as total_tasks,
                    SUM(completed_pomodoros) as total_pomodoros
                FROM tasks
                WHERE user_id = $1 AND updated_at >= NOW() - INTERVAL '28 days'
                GROUP BY DATE_TRUNC('week', updated_at)
                ORDER BY week_start DESC
            """, user_id)
            
            # Daily patterns within the week
            daily_patterns = await conn.fetch("""
                SELECT 
                    EXTRACT(dow FROM updated_at) as day_of_week,
                    AVG(CASE WHEN status = 'completed' THEN 1.0 ELSE 0.0 END) as avg_completion_rate,
                    COUNT(*) as total_tasks
                FROM tasks
                WHERE user_id = $1 AND updated_at >= NOW() - INTERVAL '28 days'
                GROUP BY EXTRACT(dow FROM updated_at)
                ORDER BY day_of_week
            """, user_id)
            
            return {
                "weekly_progression": [dict(row) for row in weekly_data],
                "daily_patterns": [dict(row) for row in daily_patterns],
                "trend": self._calculate_weekly_trend(weekly_data)
            }
    
    def _calculate_weekly_trend(self, weekly_data: List) -> str:
        """Calculate overall weekly trend"""
        if len(weekly_data) < 2:
            return "insufficient_data"
        
        completion_rates = []
        for week in weekly_data:
            total = week["total_tasks"] or 0
            completed = week["completed_tasks"] or 0
            rate = completed / total if total > 0 else 0
            completion_rates.append(rate)
        
        if len(completion_rates) >= 2:
            recent_avg = sum(completion_rates[:2]) / 2
            earlier_avg = sum(completion_rates[2:]) / len(completion_rates[2:]) if len(completion_rates) > 2 else completion_rates[-1]
            
            if recent_avg > earlier_avg * 1.1:
                return "improving"
            elif recent_avg < earlier_avg * 0.9:
                return "declining"
        
        return "stable"
    
    async def _create_monthly_overview(self, user_id: str) -> Dict[str, Any]:
        """Create monthly productivity overview"""
        
        async with self.db_manager.get_connection() as conn:
            monthly_stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_tasks,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed_tasks,
                    SUM(completed_pomodoros) as total_pomodoros,
                    AVG(completed_pomodoros) FILTER (WHERE status = 'completed') as avg_pomodoros_per_task
                FROM tasks
                WHERE user_id = $1 AND created_at >= DATE_TRUNC('month', CURRENT_DATE)
            """, user_id)
            
            # Monthly goals (would be defined by user, for now use estimates)
            monthly_goal_tasks = 50  # Could be retrieved from user preferences
            monthly_goal_pomodoros = 100
            
            completed_tasks = monthly_stats["completed_tasks"] or 0
            total_pomodoros = monthly_stats["total_pomodoros"] or 0
            
            return {
                "period": datetime.now().strftime("%Y-%m"),
                "statistics": dict(monthly_stats) if monthly_stats else {},
                "goals": {
                    "tasks": {
                        "target": monthly_goal_tasks,
                        "current": completed_tasks,
                        "progress": min(completed_tasks / monthly_goal_tasks, 1.0) if monthly_goal_tasks > 0 else 0
                    },
                    "pomodoros": {
                        "target": monthly_goal_pomodoros,
                        "current": total_pomodoros,
                        "progress": min(total_pomodoros / monthly_goal_pomodoros, 1.0) if monthly_goal_pomodoros > 0 else 0
                    }
                }
            }
    
    async def _detect_behavioral_patterns(self, user_id: str, period: str) -> Dict[str, Any]:
        """Detect user behavioral patterns"""
        
        days = {"7_days": 7, "30_days": 30, "90_days": 90}.get(period, 30)
        
        async with self.db_manager.get_connection() as conn:
            # Time-based patterns
            hourly_activity = await conn.fetch("""
                SELECT 
                    EXTRACT(hour FROM started_at) as hour,
                    COUNT(*) as activity_count,
                    AVG(duration) as avg_duration
                FROM pomodoros p
                JOIN tasks t ON p.task_id = t.id
                WHERE t.user_id = $1 AND p.started_at >= NOW() - INTERVAL '%s days'
                GROUP BY EXTRACT(hour FROM started_at)
                ORDER BY hour
            """, user_id, days)
            
            # Task complexity preferences
            complexity_patterns = await conn.fetchrow("""
                SELECT 
                    AVG(estimated_pomodoros) as preferred_task_size,
                    STDDEV(estimated_pomodoros) as task_size_variance,
                    COUNT(*) FILTER (WHERE estimated_pomodoros = 1) as quick_tasks,
                    COUNT(*) FILTER (WHERE estimated_pomodoros >= 4) as complex_tasks
                FROM tasks
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '%s days'
            """, user_id, days)
            
            # Break patterns
            break_patterns = await self._analyze_break_patterns(user_id, days, conn)
            
            # Procrastination indicators
            procrastination_score = await self._calculate_procrastination_score(user_id, days, conn)
            
            return {
                "activity_by_hour": [dict(row) for row in hourly_activity],
                "task_complexity": dict(complexity_patterns) if complexity_patterns else {},
                "break_patterns": break_patterns,
                "procrastination_score": procrastination_score,
                "optimal_session_length": self._find_optimal_session_length(hourly_activity)
            }
    
    async def _analyze_break_patterns(self, user_id: str, days: int, conn) -> Dict[str, Any]:
        """Analyze break patterns between pomodoros"""
        
        # This would require more complex analysis of time gaps between pomodoros
        # For now, provide a simplified version
        
        pomodoro_sessions = await conn.fetch("""
            SELECT DATE(started_at) as session_date, COUNT(*) as pomodoro_count
            FROM pomodoros p
            JOIN tasks t ON p.task_id = t.id
            WHERE t.user_id = $1 AND p.started_at >= NOW() - INTERVAL '%s days'
                AND p.status = 'completed'
            GROUP BY DATE(started_at)
            ORDER BY session_date DESC
        """, user_id, days)
        
        if session_sessions:
            avg_pomodoros_per_day = sum(s["pomodoro_count"] for s in pomodoro_sessions) / len(pomodoro_sessions)
            max_daily_pomodoros = max(s["pomodoro_count"] for s in pomodoro_sessions)
            
            return {
                "avg_pomodoros_per_day": avg_pomodoros_per_day,
                "max_daily_pomodoros": max_daily_pomodoros,
                "consistent_sessions": len([s for s in pomodoro_sessions if s["pomodoro_count"] >= avg_pomodoros_per_day * 0.8])
            }
        
        return {"avg_pomodoros_per_day": 0, "max_daily_pomodoros": 0, "consistent_sessions": 0}
    
    async def _calculate_procrastination_score(self, user_id: str, days: int, conn) -> float:
        """Calculate procrastination tendency score"""
        
        # Measure time between task creation and first pomodoro
        procrastination_data = await conn.fetchrow("""
            SELECT 
                AVG(EXTRACT(epoch FROM (
                    SELECT MIN(p.started_at) 
                    FROM pomodoros p 
                    WHERE p.task_id = t.id
                ) - t.created_at) / 3600) as avg_delay_hours,
                COUNT(*) FILTER (WHERE (
                    SELECT MIN(p.started_at) 
                    FROM pomodoros p 
                    WHERE p.task_id = t.id
                ) - t.created_at > INTERVAL '24 hours') as tasks_delayed_over_day
            FROM tasks t
            WHERE t.user_id = $1 AND t.created_at >= NOW() - INTERVAL '%s days'
                AND EXISTS (SELECT 1 FROM pomodoros p WHERE p.task_id = t.id)
        """, user_id, days)
        
        if procrastination_data and procrastination_data["avg_delay_hours"]:
            avg_delay = procrastination_data["avg_delay_hours"]
            delayed_tasks = procrastination_data["tasks_delayed_over_day"] or 0
            
            # Score from 0-1, where 1 is high procrastination
            delay_score = min(avg_delay / 24.0, 1.0)  # Normalize to 24 hours
            frequency_score = delayed_tasks / 10.0  # Normalize to 10 tasks
            
            return min((delay_score + frequency_score) / 2, 1.0)
        
        return 0.0
    
    def _find_optimal_session_length(self, hourly_activity: List) -> Dict[str, Any]:
        """Find optimal session length based on activity patterns"""
        if not hourly_activity:
            return {"recommended_length": 25, "confidence": "low"}
        
        # Simple heuristic: sessions with higher average duration tend to be more successful
        sorted_hours = sorted(hourly_activity, key=lambda x: x["avg_duration"] or 0, reverse=True)
        
        if sorted_hours and sorted_hours[0]["avg_duration"]:
            optimal_length = int(sorted_hours[0]["avg_duration"])
            return {
                "recommended_length": optimal_length,
                "confidence": "medium",
                "best_hour": int(sorted_hours[0]["hour"])
            }
        
        return {"recommended_length": 25, "confidence": "low"}
    
    async def _calculate_achievements(self, user_id: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate user achievements and milestones"""
        achievements = []
        
        tasks_stats = user_context.get("tasks_stats", {})
        current_streak = user_context.get("current_streak", 0)
        total_tasks = tasks_stats.get("total_tasks", 0)
        completed_tasks = tasks_stats.get("completed_tasks", 0)
        
        # Streak achievements
        if current_streak >= 30:
            achievements.append({
                "type": "streak",
                "title": "Consistência Diamante",
                "description": f"Sequência de {current_streak} dias!",
                "icon": "💎",
                "rarity": "legendary"
            })
        elif current_streak >= 14:
            achievements.append({
                "type": "streak",
                "title": "Duas Semanas Forte",
                "description": f"Sequência de {current_streak} dias!",
                "icon": "🔥",
                "rarity": "epic"
            })
        elif current_streak >= 7:
            achievements.append({
                "type": "streak",
                "title": "Uma Semana Completa",
                "description": f"Sequência de {current_streak} dias!",
                "icon": "⭐",
                "rarity": "rare"
            })
        
        # Completion achievements
        if completed_tasks >= 100:
            achievements.append({
                "type": "completion",
                "title": "Centurião",
                "description": f"{completed_tasks} tarefas completadas!",
                "icon": "🏆",
                "rarity": "epic"
            })
        elif completed_tasks >= 50:
            achievements.append({
                "type": "completion",
                "title": "Meio Centenário",
                "description": f"{completed_tasks} tarefas completadas!",
                "icon": "🥇",
                "rarity": "rare"
            })
        
        # Completion rate achievements
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            if completion_rate >= 0.9:
                achievements.append({
                    "type": "efficiency",
                    "title": "Eficiência Máxima",
                    "description": f"{completion_rate:.1%} de conclusão!",
                    "icon": "⚡",
                    "rarity": "legendary"
                })
        
        return achievements
    
    async def _generate_recommendations(self, user_id: str, productivity_metrics: ProductivityMetrics, 
                                      behavioral_patterns: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Based on completion rate
        if productivity_metrics.completion_rate < 0.5:
            recommendations.append("Tente criar tarefas menores e mais específicas para aumentar sua taxa de conclusão")
        
        # Based on focus score
        if productivity_metrics.focus_score < 0.6:
            recommendations.append("Considere sessões de pomodoro mais curtas para melhorar seu foco")
        
        # Based on consistency
        if productivity_metrics.consistency_score < 0.3:
            recommendations.append("Estabeleça um horário fixo diário para trabalhar nas suas tarefas")
        
        # Based on peak hours
        if productivity_metrics.peak_productivity_hours:
            peak_hour = productivity_metrics.peak_productivity_hours[0]
            recommendations.append(f"Suas {peak_hour}h são seu horário de pico - use para tarefas mais importantes")
        
        # Based on task complexity
        complexity = behavioral_patterns.get("task_complexity", {})
        preferred_size = complexity.get("preferred_task_size", 0)
        if preferred_size > 3:
            recommendations.append("Considere dividir tarefas grandes em subtarefas menores")
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_default_analytics(self) -> UserAnalytics:
        """Get default analytics for error cases"""
        return UserAnalytics(
            daily_stats={"date": datetime.now().strftime("%Y-%m-%d"), "tasks": {}, "pomodoros": {}},
            weekly_trends={"weekly_progression": [], "daily_patterns": [], "trend": "insufficient_data"},
            monthly_overview={"period": datetime.now().strftime("%Y-%m"), "statistics": {}, "goals": {}},
            behavioral_patterns={},
            achievements=[],
            recommendations=["Continue usando o sistema para gerar análises personalizadas"]
        )

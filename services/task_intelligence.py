import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class TaskSuggestion:
    title: str
    description: str
    priority: str
    estimated_pomodoros: int
    reasoning: str
    confidence: float

@dataclass
class TaskOptimization:
    task_id: str
    current_status: str
    suggested_changes: Dict[str, Any]
    optimization_type: str
    expected_improvement: str

class TaskIntelligenceService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        
    async def generate_intelligent_task_suggestions(self, user_id: str, context: str = "") -> List[TaskSuggestion]:
        """Generate intelligent task suggestions based on user patterns"""
        try:
            # Get user context and patterns
            user_context = await self.db_manager.fetch_user_context(user_id)
            behavioral_patterns = await self._analyze_task_patterns(user_id)
            
            # Generate suggestions based on different strategies
            suggestions = []
            
            # Pattern-based suggestions
            pattern_suggestions = await self._generate_pattern_based_suggestions(user_id, behavioral_patterns)
            suggestions.extend(pattern_suggestions)
            
            # Gap analysis suggestions
            gap_suggestions = await self._generate_gap_analysis_suggestions(user_id, user_context)
            suggestions.extend(gap_suggestions)
            
            # Context-aware suggestions
            if context:
                context_suggestions = await self._generate_context_suggestions(user_id, context, behavioral_patterns)
                suggestions.extend(context_suggestions)
            
            # Time-based suggestions
            time_suggestions = await self._generate_time_based_suggestions(user_id, user_context)
            suggestions.extend(time_suggestions)
            
            # Sort by confidence and return top suggestions
            suggestions.sort(key=lambda x: x.confidence, reverse=True)
            return suggestions[:5]
            
        except Exception as e:
            logger.error(f"Error generating task suggestions: {e}")
            return self._get_default_suggestions()
    
    async def optimize_existing_tasks(self, user_id: str) -> List[TaskOptimization]:
        """Analyze and optimize existing tasks"""
        try:
            optimizations = []
            
            # Get user's pending tasks
            async with self.db_manager.get_connection() as conn:
                pending_tasks = await conn.fetch("""
                    SELECT id, title, description, priority, estimated_pomodoros, 
                           completed_pomodoros, created_at, due_date
                    FROM tasks
                    WHERE user_id = $1 AND status IN ('pending', 'in_progress')
                    ORDER BY created_at DESC
                """, user_id)
                
                for task in pending_tasks:
                    task_dict = dict(task)
                    optimization = await self._analyze_task_optimization(user_id, task_dict)
                    if optimization:
                        optimizations.append(optimization)
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error optimizing tasks: {e}")
            return []
    
    async def estimate_task_complexity(self, user_id: str, task_description: str) -> Dict[str, Any]:
        """Estimate task complexity and duration based on user patterns"""
        try:
            # Get user's historical task data
            async with self.db_manager.get_connection() as conn:
                similar_tasks = await conn.fetch("""
                    SELECT title, estimated_pomodoros, completed_pomodoros
                    FROM tasks
                    WHERE user_id = $1 AND status = 'completed'
                        AND (
                            LOWER(title) SIMILAR TO LOWER($2) OR
                            LOWER(description) SIMILAR TO LOWER($2)
                        )
                    ORDER BY created_at DESC
                    LIMIT 10
                """, user_id, f"%{task_description.lower()}%")
                
                # Calculate average based on similar tasks
                if similar_tasks:
                    avg_estimated = sum(t["estimated_pomodoros"] for t in similar_tasks) / len(similar_tasks)
                    avg_actual = sum(t["completed_pomodoros"] for t in similar_tasks) / len(similar_tasks)
                    accuracy_ratio = avg_actual / avg_estimated if avg_estimated > 0 else 1.0
                else:
                    # Use default estimation logic
                    avg_estimated = self._estimate_from_description(task_description)
                    avg_actual = avg_estimated
                    accuracy_ratio = 1.0
                
                # Get user's general estimation accuracy
                user_accuracy = await self._get_user_estimation_accuracy(user_id, conn)
                
                # Apply user's accuracy pattern to the estimate
                suggested_estimate = max(1, int(avg_estimated * user_accuracy))
                
                return {
                    "estimated_pomodoros": suggested_estimate,
                    "confidence": min(len(similar_tasks) / 5, 1.0),
                    "based_on_similar_tasks": len(similar_tasks),
                    "user_accuracy_factor": user_accuracy,
                    "complexity_factors": self._analyze_complexity_factors(task_description)
                }
                
        except Exception as e:
            logger.error(f"Error estimating task complexity: {e}")
            return {"estimated_pomodoros": 1, "confidence": 0.3}
    
    async def suggest_optimal_timing(self, user_id: str, task_priority: str = "medium") -> Dict[str, Any]:
        """Suggest optimal timing for a task based on user patterns"""
        try:
            async with self.db_manager.get_connection() as conn:
                # Get user's productivity patterns
                hourly_patterns = await conn.fetch("""
                    SELECT 
                        EXTRACT(hour FROM started_at) as hour,
                        COUNT(*) as session_count,
                        AVG(duration) as avg_duration,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed_count
                    FROM pomodoros p
                    JOIN tasks t ON p.task_id = t.id
                    WHERE t.user_id = $1 AND p.started_at >= NOW() - INTERVAL '30 days'
                    GROUP BY EXTRACT(hour FROM started_at)
                    ORDER BY completed_count DESC, avg_duration DESC
                """, user_id)
                
                # Get daily patterns
                daily_patterns = await conn.fetch("""
                    SELECT 
                        EXTRACT(dow FROM started_at) as day_of_week,
                        COUNT(*) as session_count,
                        AVG(duration) as avg_duration
                    FROM pomodoros p
                    JOIN tasks t ON p.task_id = t.id
                    WHERE t.user_id = $1 AND p.started_at >= NOW() - INTERVAL '30 days'
                        AND p.status = 'completed'
                    GROUP BY EXTRACT(dow FROM started_at)
                    ORDER BY session_count DESC
                """, user_id)
                
                # Determine optimal time slots
                optimal_hours = []
                if hourly_patterns:
                    # For high priority tasks, suggest top 2 hours
                    # For medium priority, suggest top 3-5 hours
                    # For low priority, suggest any productive hour
                    
                    if task_priority == "high":
                        optimal_hours = [int(h["hour"]) for h in hourly_patterns[:2]]
                    elif task_priority == "medium":
                        optimal_hours = [int(h["hour"]) for h in hourly_patterns[2:5]]
                    else:
                        optimal_hours = [int(h["hour"]) for h in hourly_patterns[5:]]
                
                # Get best days
                day_names = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
                optimal_days = []
                if daily_patterns:
                    optimal_days = [day_names[int(d["day_of_week"])] for d in daily_patterns[:3]]
                
                # Generate specific recommendations
                next_optimal_slots = self._generate_next_optimal_slots(optimal_hours, optimal_days)
                
                return {
                    "optimal_hours": optimal_hours,
                    "optimal_days": optimal_days,
                    "next_available_slots": next_optimal_slots,
                    "reasoning": self._generate_timing_reasoning(task_priority, optimal_hours, optimal_days)
                }
                
        except Exception as e:
            logger.error(f"Error suggesting optimal timing: {e}")
            return {"optimal_hours": [9, 14], "optimal_days": ["Segunda", "Terça"], "next_available_slots": []}
    
    async def _analyze_task_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's task creation and completion patterns"""
        
        async with self.db_manager.get_connection() as conn:
            # Task type analysis
            task_types = await conn.fetch("""
                SELECT 
                    CASE 
                        WHEN LOWER(title) LIKE '%estud%' THEN 'estudo'
                        WHEN LOWER(title) LIKE '%trabalh%' THEN 'trabalho'
                        WHEN LOWER(title) LIKE '%exerc%' THEN 'exercicio'
                        WHEN LOWER(title) LIKE '%leitura%' OR LOWER(title) LIKE '%ler%' THEN 'leitura'
                        WHEN LOWER(title) LIKE '%codigo%' OR LOWER(title) LIKE '%program%' THEN 'programacao'
                        ELSE 'outros'
                    END as task_type,
                    COUNT(*) as count,
                    AVG(completed_pomodoros) as avg_pomodoros,
                    AVG(CASE WHEN status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM tasks
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY task_type
                ORDER BY count DESC
            """, user_id)
            
            # Size preferences
            size_patterns = await conn.fetchrow("""
                SELECT 
                    AVG(estimated_pomodoros) as avg_task_size,
                    MODE() WITHIN GROUP (ORDER BY estimated_pomodoros) as preferred_size,
                    COUNT(*) FILTER (WHERE estimated_pomodoros = 1) as quick_tasks,
                    COUNT(*) FILTER (WHERE estimated_pomodoros >= 4) as large_tasks
                FROM tasks
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '30 days'
            """, user_id)
            
            # Creation timing patterns
            creation_patterns = await conn.fetch("""
                SELECT 
                    EXTRACT(hour FROM created_at) as hour,
                    COUNT(*) as creation_count
                FROM tasks
                WHERE user_id = $1 AND created_at >= NOW() - INTERVAL '30 days'
                GROUP BY EXTRACT(hour FROM created_at)
                ORDER BY creation_count DESC
            """, user_id)
            
            return {
                "task_types": [dict(row) for row in task_types],
                "size_patterns": dict(size_patterns) if size_patterns else {},
                "creation_patterns": [dict(row) for row in creation_patterns]
            }
    
    async def _generate_pattern_based_suggestions(self, user_id: str, patterns: Dict[str, Any]) -> List[TaskSuggestion]:
        """Generate suggestions based on user patterns"""
        suggestions = []
        
        task_types = patterns.get("task_types", [])
        size_patterns = patterns.get("size_patterns", {})
        
        # Suggest tasks based on successful types
        successful_types = [t for t in task_types if t["completion_rate"] > 0.7 and t["count"] >= 3]
        
        for task_type in successful_types[:2]:  # Top 2 successful types
            if task_type["task_type"] == "estudo":
                suggestions.append(TaskSuggestion(
                    title="Sessão de Estudo",
                    description="Aproveite sua boa performance em estudos",
                    priority="medium",
                    estimated_pomodoros=int(task_type["avg_pomodoros"]) or 2,
                    reasoning=f"Você tem {task_type['completion_rate']:.0%} de sucesso em tarefas de estudo",
                    confidence=0.8
                ))
            elif task_type["task_type"] == "programacao":
                suggestions.append(TaskSuggestion(
                    title="Sessão de Programação",
                    description="Continue seus projetos de código",
                    priority="medium",
                    estimated_pomodoros=int(task_type["avg_pomodoros"]) or 3,
                    reasoning=f"Suas tarefas de programação têm alta taxa de conclusão",
                    confidence=0.8
                ))
        
        return suggestions
    
    async def _generate_gap_analysis_suggestions(self, user_id: str, user_context: Dict[str, Any]) -> List[TaskSuggestion]:
        """Generate suggestions based on gaps in productivity"""
        suggestions = []
        
        tasks_stats = user_context.get("tasks_stats", {})
        current_streak = user_context.get("current_streak", 0)
        
        # If user has overdue tasks
        overdue_tasks = tasks_stats.get("overdue_tasks", 0)
        if overdue_tasks > 0:
            suggestions.append(TaskSuggestion(
                title="Recuperar Tarefas em Atraso",
                description="Foque em uma tarefa que está esperando",
                priority="high",
                estimated_pomodoros=1,
                reasoning=f"Você tem {overdue_tasks} tarefas em atraso",
                confidence=0.9
            ))
        
        # If streak is broken, suggest streak recovery
        if current_streak == 0:
            suggestions.append(TaskSuggestion(
                title="Reiniciar Sequência",
                description="Uma tarefa simples para começar nova sequência",
                priority="medium",
                estimated_pomodoros=1,
                reasoning="Reconstruir sua consistência diária",
                confidence=0.7
            ))
        
        # If user is inactive today
        today_pomodoros = user_context.get("today_pomodoros", [])
        if len(today_pomodoros) == 0:
            current_hour = datetime.now().hour
            if 9 <= current_hour <= 18:  # Work hours
                suggestions.append(TaskSuggestion(
                    title="Primeira Tarefa do Dia",
                    description="Comece o dia com uma vitória rápida",
                    priority="medium",
                    estimated_pomodoros=1,
                    reasoning="Ainda não iniciou atividades hoje",
                    confidence=0.8
                ))
        
        return suggestions
    
    async def _generate_context_suggestions(self, user_id: str, context: str, patterns: Dict[str, Any]) -> List[TaskSuggestion]:
        """Generate context-aware suggestions"""
        suggestions = []
        context_lower = context.lower()
        
        # Context-based task suggestions
        if "estudo" in context_lower or "estudar" in context_lower:
            suggestions.append(TaskSuggestion(
                title="Sessão de Estudo Focada",
                description="Baseado no seu interesse atual em estudos",
                priority="medium",
                estimated_pomodoros=2,
                reasoning="Detectei interesse em estudos na nossa conversa",
                confidence=0.7
            ))
        
        if "projeto" in context_lower or "trabalho" in context_lower:
            suggestions.append(TaskSuggestion(
                title="Avançar no Projeto",
                description="Continue o projeto que você mencionou",
                priority="high",
                estimated_pomodoros=3,
                reasoning="Você mencionou um projeto em andamento",
                confidence=0.8
            ))
        
        if "exercicio" in context_lower or "treino" in context_lower:
            suggestions.append(TaskSuggestion(
                title="Sessão de Exercícios",
                description="Mantenha sua rotina de atividade física",
                priority="medium",
                estimated_pomodoros=1,
                reasoning="Você está interessado em manter exercícios",
                confidence=0.6
            ))
        
        return suggestions
    
    async def _generate_time_based_suggestions(self, user_id: str, user_context: Dict[str, Any]) -> List[TaskSuggestion]:
        """Generate time-sensitive suggestions"""
        suggestions = []
        current_hour = datetime.now().hour
        current_weekday = datetime.now().weekday()  # 0 = Monday
        
        # Morning suggestions
        if 6 <= current_hour <= 10:
            suggestions.append(TaskSuggestion(
                title="Planejamento do Dia",
                description="Organize suas prioridades para hoje",
                priority="medium",
                estimated_pomodoros=1,
                reasoning="Manhãs são ideais para planejamento",
                confidence=0.6
            ))
        
        # Afternoon energy boost
        elif 13 <= current_hour <= 15:
            suggestions.append(TaskSuggestion(
                title="Tarefa Desafiadora",
                description="Aproveite o pico de energia da tarde",
                priority="high",
                estimated_pomodoros=2,
                reasoning="Tarde é seu momento de maior produtividade",
                confidence=0.7
            ))
        
        # Evening reflection
        elif 18 <= current_hour <= 21:
            suggestions.append(TaskSuggestion(
                title="Revisão e Reflexão",
                description="Reflita sobre o progresso do dia",
                priority="low",
                estimated_pomodoros=1,
                reasoning="Final do dia é ideal para reflexão",
                confidence=0.5
            ))
        
        # Weekend suggestions
        if current_weekday >= 5:  # Saturday or Sunday
            suggestions.append(TaskSuggestion(
                title="Projeto Pessoal",
                description="Trabalhe em algo que você gosta",
                priority="medium",
                estimated_pomodoros=2,
                reasoning="Fins de semana são perfeitos para projetos pessoais",
                confidence=0.6
            ))
        
        return suggestions
    
    async def _analyze_task_optimization(self, user_id: str, task: Dict[str, Any]) -> Optional[TaskOptimization]:
        """Analyze a specific task for optimization opportunities"""
        
        optimizations = []
        task_id = task["id"]
        created_at = task["created_at"]
        estimated_pomodoros = task["estimated_pomodoros"]
        
        # Check if task is too old (potential procrastination)
        days_old = (datetime.now() - created_at).days
        if days_old > 7:
            optimizations.append({
                "type": "break_down",
                "reason": f"Tarefa criada há {days_old} dias - pode estar muito complexa",
                "suggested_action": "Dividir em subtarefas menores"
            })
        
        # Check if task is too large
        if estimated_pomodoros > 4:
            optimizations.append({
                "type": "simplify",
                "reason": "Tarefa muito grande pode ser desencorajante",
                "suggested_action": f"Dividir {estimated_pomodoros} pomodoros em tarefas de 1-2 pomodoros"
            })
        
        # Check priority alignment with due date
        if task.get("due_date"):
            due_date = task["due_date"]
            days_until_due = (due_date - datetime.now().date()).days
            
            if days_until_due <= 1 and task["priority"] != "high":
                optimizations.append({
                    "type": "prioritize",
                    "reason": f"Vence em {days_until_due} dias",
                    "suggested_action": "Aumentar prioridade para alta"
                })
        
        if optimizations:
            return TaskOptimization(
                task_id=str(task_id),
                current_status=task.get("status", "pending"),
                suggested_changes=optimizations[0],  # Most important optimization
                optimization_type=optimizations[0]["type"],
                expected_improvement="Maior probabilidade de conclusão"
            )
        
        return None
    
    def _estimate_from_description(self, description: str) -> int:
        """Estimate pomodoros from task description"""
        description_lower = description.lower()
        
        # Simple heuristic based on keywords
        if any(word in description_lower for word in ["rápido", "quick", "simples", "revisar"]):
            return 1
        elif any(word in description_lower for word in ["estudar", "ler", "pesquisar"]):
            return 2
        elif any(word in description_lower for word in ["projeto", "criar", "desenvolver"]):
            return 3
        elif any(word in description_lower for word in ["complexo", "difícil", "grande"]):
            return 4
        else:
            return 2  # Default
    
    async def _get_user_estimation_accuracy(self, user_id: str, conn) -> float:
        """Get user's historical estimation accuracy"""
        
        accuracy_data = await conn.fetchrow("""
            SELECT 
                AVG(completed_pomodoros::float / NULLIF(estimated_pomodoros, 0)) as avg_ratio
            FROM tasks
            WHERE user_id = $1 AND status = 'completed' 
                AND estimated_pomodoros > 0 AND completed_pomodoros > 0
                AND created_at >= NOW() - INTERVAL '60 days'
        """, user_id)
        
        if accuracy_data and accuracy_data["avg_ratio"]:
            return min(max(accuracy_data["avg_ratio"], 0.5), 2.0)  # Clamp between 0.5 and 2.0
        
        return 1.0  # Default if no data
    
    def _analyze_complexity_factors(self, description: str) -> List[str]:
        """Analyze factors that affect task complexity"""
        factors = []
        description_lower = description.lower()
        
        if len(description) > 100:
            factors.append("Descrição longa indica complexidade")
        
        if any(word in description_lower for word in ["projeto", "sistema", "completo"]):
            factors.append("Envolve projeto amplo")
        
        if any(word in description_lower for word in ["aprender", "novo", "primeira vez"]):
            factors.append("Envolve aprendizado novo")
        
        if any(word in description_lower for word in ["research", "pesquisar", "investigar"]):
            factors.append("Requer pesquisa")
        
        return factors
    
    def _generate_next_optimal_slots(self, optimal_hours: List[int], optimal_days: List[str]) -> List[Dict[str, Any]]:
        """Generate next available optimal time slots"""
        slots = []
        
        if not optimal_hours:
            return slots
        
        current_time = datetime.now()
        
        # Find next available slots in the coming week
        for day_offset in range(7):
            check_date = current_time + timedelta(days=day_offset)
            day_name = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][check_date.weekday()]
            
            if day_name in optimal_days or not optimal_days:
                for hour in optimal_hours:
                    slot_time = check_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                    
                    # Only suggest future times
                    if slot_time > current_time:
                        slots.append({
                            "datetime": slot_time.strftime("%Y-%m-%d %H:%M"),
                            "day": day_name,
                            "hour": hour,
                            "relative": f"{'Hoje' if day_offset == 0 else f'Em {day_offset} dias'} às {hour}h"
                        })
                        
                        # Limit to 3 suggestions
                        if len(slots) >= 3:
                            return slots
        
        return slots
    
    def _generate_timing_reasoning(self, priority: str, optimal_hours: List[int], optimal_days: List[str]) -> str:
        """Generate reasoning for timing suggestions"""
        
        if not optimal_hours and not optimal_days:
            return "Baseado em padrões gerais de produtividade"
        
        reasoning_parts = []
        
        if optimal_hours:
            if len(optimal_hours) == 1:
                reasoning_parts.append(f"Suas {optimal_hours[0]}h são seu horário mais produtivo")
            else:
                reasoning_parts.append(f"Você rende melhor entre {min(optimal_hours)}h-{max(optimal_hours)}h")
        
        if optimal_days:
            if len(optimal_days) <= 2:
                reasoning_parts.append(f"{' e '.join(optimal_days)} são seus dias mais focados")
            else:
                reasoning_parts.append("Baseado nos seus dias mais produtivos")
        
        if priority == "high":
            reasoning_parts.append("Para alta prioridade, sugerindo seus melhores horários")
        
        return ". ".join(reasoning_parts) if reasoning_parts else "Baseado nos seus padrões de produtividade"
    
    def _get_default_suggestions(self) -> List[TaskSuggestion]:
        """Get default suggestions when unable to generate personalized ones"""
        return [
            TaskSuggestion(
                title="Começar uma Tarefa Simples",
                description="Inicie com algo pequeno para criar momentum",
                priority="medium",
                estimated_pomodoros=1,
                reasoning="Sugestão padrão para começar",
                confidence=0.5
            ),
            TaskSuggestion(
                title="Organizar Pendências",
                description="Revise e organize suas tarefas existentes",
                priority="low",
                estimated_pomodoros=1,
                reasoning="Sempre útil para manter organização",
                confidence=0.4
            )
        ]

"""
Serviço de insights de produtividade para o Lumi AI.
Gera análises avançadas e recomendações personalizadas de produtividade.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import statistics
from dataclasses import dataclass
from enum import Enum

from ..utils.pattern_detector import PatternDetector, Pattern, PatternType
from ..utils.time_analyzer import TimeAnalyzer, TimePattern, ProductivityPeriod

class InsightCategory(Enum):
    """Categorias de insights de produtividade."""
    TIME_MANAGEMENT = "time_management"
    TASK_OPTIMIZATION = "task_optimization"
    ENERGY_MANAGEMENT = "energy_management"
    HABIT_FORMATION = "habit_formation"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    WELLBEING = "wellbeing"

class InsightPriority(Enum):
    """Prioridades dos insights."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ProductivityInsight:
    """Insight de produtividade estruturado."""
    id: str
    category: InsightCategory
    priority: InsightPriority
    title: str
    description: str
    current_state: str
    target_state: str
    impact_score: float  # 0-10
    effort_required: float  # 0-10
    confidence: float  # 0-1
    recommendations: List[str]
    metrics_to_track: List[str]
    estimated_improvement: Dict[str, float]
    implementation_steps: List[str]
    timeframe: str
    related_patterns: List[str]

class ProductivityInsightsService:
    """Serviço avançado de insights de produtividade."""
    
    def __init__(self):
        self.pattern_detector = PatternDetector()
        self.time_analyzer = TimeAnalyzer()
        self.insight_cache = {}
        
    async def generate_comprehensive_insights(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gera insights abrangentes de produtividade.
        
        Args:
            user_data: Dados completos do usuário
            
        Returns:
            Análise completa com insights categorizados
        """
        # Detecta padrões comportamentais
        patterns = self.pattern_detector.detect_all_patterns(user_data)
        
        # Analisa padrões temporais
        time_patterns = self.time_analyzer.identify_peak_hours(user_data)
        
        # Gera insights categorizados
        insights = {
            "time_management": await self._generate_time_management_insights(user_data, time_patterns),
            "task_optimization": await self._generate_task_optimization_insights(user_data, patterns),
            "energy_management": await self._generate_energy_management_insights(user_data, patterns),
            "habit_formation": await self._generate_habit_formation_insights(user_data, patterns),
            "performance_analysis": await self._generate_performance_insights(user_data),
            "wellbeing": await self._generate_wellbeing_insights(user_data, patterns)
        }
        
        # Calcula métricas de resumo
        summary_metrics = await self._calculate_summary_metrics(user_data, patterns)
        
        # Identifica ações prioritárias
        priority_actions = await self._identify_priority_actions(insights)
        
        # Gera roadmap de melhoria
        improvement_roadmap = await self._generate_improvement_roadmap(insights, patterns)
        
        return {
            "insights": insights,
            "summary_metrics": summary_metrics,
            "priority_actions": priority_actions,
            "improvement_roadmap": improvement_roadmap,
            "patterns_detected": len(patterns),
            "confidence_score": self._calculate_overall_confidence(patterns),
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_time_management_insights(self, user_data: Dict, time_patterns: List[TimePattern]) -> List[ProductivityInsight]:
        """Gera insights de gestão de tempo."""
        insights = []
        
        # Análise de picos de produtividade
        if time_patterns:
            high_productivity_patterns = [p for p in time_patterns if p.productivity_level == ProductivityPeriod.HIGH]
            
            if high_productivity_patterns:
                best_pattern = max(high_productivity_patterns, key=lambda x: x.confidence_score)
                
                insight = ProductivityInsight(
                    id="time_mgmt_001",
                    category=InsightCategory.TIME_MANAGEMENT,
                    priority=InsightPriority.HIGH,
                    title="Otimize Seu Horário de Pico",
                    description=f"Você é mais produtivo entre {best_pattern.hour_start}h-{best_pattern.hour_end}h",
                    current_state=f"Produtividade variável ao longo do dia",
                    target_state=f"Concentrar trabalho importante no período {best_pattern.hour_start}h-{best_pattern.hour_end}h",
                    impact_score=8.5,
                    effort_required=3.0,
                    confidence=best_pattern.confidence_score,
                    recommendations=[
                        f"Agende reuniões importantes entre {best_pattern.hour_start}h-{best_pattern.hour_end}h",
                        f"Reserve este período para trabalho que requer foco profundo",
                        f"Evite tarefas administrativas durante seu pico de produtividade"
                    ],
                    metrics_to_track=["tasks_completed_peak_hours", "focus_duration", "task_quality"],
                    estimated_improvement={
                        "productivity": 25.0,
                        "task_completion_rate": 20.0,
                        "focus_quality": 30.0
                    },
                    implementation_steps=[
                        "Identifique suas 3 tarefas mais importantes do dia",
                        f"Bloqueie {best_pattern.hour_start}h-{best_pattern.hour_end}h no calendário",
                        "Configure notificações para minimizar interrupções",
                        "Monitore produtividade por 2 semanas"
                    ],
                    timeframe="2-3 semanas para estabelecer rotina",
                    related_patterns=["productivity_cycle"]
                )
                insights.append(insight)
        
        # Análise de fragmentação de tempo
        time_fragmentation = self._analyze_time_fragmentation(user_data)
        if time_fragmentation > 0.6:  # Alta fragmentação
            
            insight = ProductivityInsight(
                id="time_mgmt_002",
                category=InsightCategory.TIME_MANAGEMENT,
                priority=InsightPriority.MEDIUM,
                title="Reduza a Fragmentação do Tempo",
                description=f"Seu tempo está {time_fragmentation:.0%} fragmentado, impactando o foco",
                current_state="Frequentes mudanças de contexto e interrupções",
                target_state="Blocos contínuos de tempo para trabalho focado",
                impact_score=7.0,
                effort_required=5.0,
                confidence=0.8,
                recommendations=[
                    "Agrupe tarefas similares em blocos de tempo",
                    "Estabeleça períodos específicos para email e mensagens",
                    "Use técnica de time-blocking no calendário"
                ],
                metrics_to_track=["average_task_duration", "context_switches", "deep_work_blocks"],
                estimated_improvement={
                    "focus_duration": 40.0,
                    "task_efficiency": 25.0,
                    "stress_reduction": 20.0
                },
                implementation_steps=[
                    "Identifique principais fontes de interrupção",
                    "Defina 3 blocos de 90min para trabalho focado",
                    "Configure períodos específicos para comunicação",
                    "Use app bloqueador de distrações"
                ],
                timeframe="3-4 semanas para criar novos hábitos",
                related_patterns=["distraction", "task_clustering"]
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_task_optimization_insights(self, user_data: Dict, patterns: List[Pattern]) -> List[ProductivityInsight]:
        """Gera insights de otimização de tarefas."""
        insights = []
        
        # Análise de procrastinação
        procrastination_patterns = [p for p in patterns if p.type == PatternType.PROCRASTINATION]
        if procrastination_patterns:
            pattern = procrastination_patterns[0]
            
            insight = ProductivityInsight(
                id="task_opt_001",
                category=InsightCategory.TASK_OPTIMIZATION,
                priority=InsightPriority.CRITICAL,
                title="Estratégia Anti-Procrastinação",
                description=pattern.description,
                current_state=f"Procrastinação em {pattern.frequency:.0%} das tarefas",
                target_state="Reduzir procrastinação para menos de 10% das tarefas",
                impact_score=9.0,
                effort_required=6.0,
                confidence=pattern.confidence,
                recommendations=pattern.recommendations,
                metrics_to_track=["on_time_completion", "task_start_delay", "completion_rate"],
                estimated_improvement={
                    "task_completion": 50.0,
                    "stress_reduction": 35.0,
                    "time_efficiency": 30.0
                },
                implementation_steps=[
                    "Identifique tipos específicos de tarefas procrastinadas",
                    "Divida tarefas grandes em subtarefas de 25min",
                    "Use técnica dos 2 minutos para tarefas pequenas",
                    "Implemente sistema de recompensas"
                ],
                timeframe="4-6 semanas para mudança comportamental",
                related_patterns=["procrastination"]
            )
            insights.append(insight)
        
        # Análise de complexidade de tarefas
        task_complexity_insight = self._analyze_task_complexity_patterns(user_data)
        if task_complexity_insight:
            insights.append(task_complexity_insight)
        
        return insights
    
    async def _generate_energy_management_insights(self, user_data: Dict, patterns: List[Pattern]) -> List[ProductivityInsight]:
        """Gera insights de gestão de energia."""
        insights = []
        
        # Análise de padrões de energia
        energy_patterns = [p for p in patterns if p.type == PatternType.ENERGY_PATTERN]
        
        # Análise de pausas
        break_analysis = self.time_analyzer.analyze_break_patterns(user_data)
        
        if break_analysis['break_effectiveness'] < 0.7:
            insight = ProductivityInsight(
                id="energy_mgmt_001",
                category=InsightCategory.ENERGY_MANAGEMENT,
                priority=InsightPriority.HIGH,
                title="Otimize Suas Pausas",
                description=f"Suas pausas têm apenas {break_analysis['break_effectiveness']:.0%} de efetividade",
                current_state=f"Pausas de {break_analysis['average_break_duration']:.0f}min a cada {break_analysis['average_work_interval']:.0f}min",
                target_state=f"Pausas otimizadas de {break_analysis['recommended_break_duration']}min a cada {break_analysis['recommended_work_interval']}min",
                impact_score=7.5,
                effort_required=2.0,
                confidence=0.85,
                recommendations=[
                    f"Faça pausas de {break_analysis['recommended_break_duration']} minutos",
                    f"Trabalhe em blocos de {break_analysis['recommended_work_interval']} minutos",
                    "Inclua atividades físicas nas pausas"
                ],
                metrics_to_track=["energy_levels", "focus_after_break", "productivity_sustainability"],
                estimated_improvement={
                    "energy_sustainability": 40.0,
                    "afternoon_productivity": 35.0,
                    "overall_wellbeing": 25.0
                },
                implementation_steps=[
                    "Configure timer para pausas regulares",
                    "Prepare lista de atividades para pausas",
                    "Monitore níveis de energia antes/depois das pausas",
                    "Ajuste timing baseado na resposta pessoal"
                ],
                timeframe="2-3 semanas para estabelecer ritmo",
                related_patterns=["break_pattern", "energy_pattern"]
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_habit_formation_insights(self, user_data: Dict, patterns: List[Pattern]) -> List[ProductivityInsight]:
        """Gera insights de formação de hábitos."""
        insights = []
        
        # Identifica hábitos positivos a serem reforçados
        positive_patterns = [p for p in patterns if p.type in [PatternType.FLOW_STATE, PatternType.TASK_CLUSTERING]]
        
        for pattern in positive_patterns:
            if pattern.type == PatternType.FLOW_STATE:
                insight = ProductivityInsight(
                    id="habit_form_001",
                    category=InsightCategory.HABIT_FORMATION,
                    priority=InsightPriority.MEDIUM,
                    title="Cultive Estados de Fluxo",
                    description=f"Você entra em fluxo {pattern.frequency:.0%} do tempo - há potencial para mais",
                    current_state=f"Estados de fluxo esporádicos ({pattern.frequency:.0%})",
                    target_state="Estados de fluxo regulares (>50% do tempo produtivo)",
                    impact_score=8.0,
                    effort_required=4.0,
                    confidence=pattern.confidence,
                    recommendations=pattern.recommendations,
                    metrics_to_track=["flow_frequency", "flow_duration", "flow_quality"],
                    estimated_improvement={
                        "deep_work_quality": 60.0,
                        "job_satisfaction": 40.0,
                        "creative_output": 50.0
                    },
                    implementation_steps=[
                        "Identifique condições que favorecem o fluxo",
                        "Crie ambiente dedicado para trabalho profundo",
                        "Estabeleça rituais pré-fluxo",
                        "Pratique mindfulness para melhorar foco"
                    ],
                    timeframe="6-8 semanas para desenvolver hábito",
                    related_patterns=["flow_state"]
                )
                insights.append(insight)
        
        return insights
    
    async def _generate_performance_insights(self, user_data: Dict) -> List[ProductivityInsight]:
        """Gera insights de análise de performance."""
        insights = []
        
        # Análise de tendências de produtividade
        productivity_trend = self._calculate_productivity_trend(user_data)
        
        if productivity_trend['direction'] == 'decreasing' and productivity_trend['significance'] > 0.7:
            insight = ProductivityInsight(
                id="perf_001",
                category=InsightCategory.PERFORMANCE_ANALYSIS,
                priority=InsightPriority.HIGH,
                title="Tendência de Queda na Produtividade",
                description=f"Produtividade diminuindo {productivity_trend['rate']:.1f}% por semana",
                current_state="Declínio constante na produtividade",
                target_state="Reverter tendência e estabilizar performance",
                impact_score=8.5,
                effort_required=7.0,
                confidence=productivity_trend['significance'],
                recommendations=[
                    "Identifique fatores causando o declínio",
                    "Revise carga de trabalho e prioridades",
                    "Considere ajustes no ambiente de trabalho",
                    "Avalie necessidade de descanso ou férias"
                ],
                metrics_to_track=["weekly_productivity", "task_completion_rate", "quality_scores"],
                estimated_improvement={
                    "productivity_stabilization": 100.0,
                    "performance_recovery": 80.0
                },
                implementation_steps=[
                    "Análise detalhada dos últimos 30 dias",
                    "Identifique mudanças em rotina ou ambiente",
                    "Implemente mudanças uma de cada vez",
                    "Monitore impacto semanalmente"
                ],
                timeframe="4-6 semanas para recuperação",
                related_patterns=["productivity_cycle"]
            )
            insights.append(insight)
        
        return insights
    
    async def _generate_wellbeing_insights(self, user_data: Dict, patterns: List[Pattern]) -> List[ProductivityInsight]:
        """Gera insights de bem-estar."""
        insights = []
        
        # Análise de equilíbrio trabalho-vida
        work_life_balance = self._analyze_work_life_balance(user_data)
        
        if work_life_balance['score'] < 0.6:
            insight = ProductivityInsight(
                id="wellbeing_001",
                category=InsightCategory.WELLBEING,
                priority=InsightPriority.HIGH,
                title="Melhore o Equilíbrio Trabalho-Vida",
                description=f"Equilíbrio trabalho-vida em {work_life_balance['score']:.0%} - abaixo do ideal",
                current_state="Desequilíbrio entre trabalho e vida pessoal",
                target_state="Equilíbrio saudável (>70%) entre trabalho e vida pessoal",
                impact_score=9.0,
                effort_required=5.0,
                confidence=0.8,
                recommendations=[
                    "Estabeleça horários fixos para trabalho",
                    "Crie rituais de transição trabalho-casa",
                    "Reserve tempo para atividades pessoais",
                    "Pratique mindfulness e relaxamento"
                ],
                metrics_to_track=["work_hours", "personal_time", "stress_levels", "satisfaction"],
                estimated_improvement={
                    "life_satisfaction": 35.0,
                    "stress_reduction": 40.0,
                    "long_term_productivity": 25.0
                },
                implementation_steps=[
                    "Defina horários claros de início/fim do trabalho",
                    "Configure notificações para lembrar de pausas",
                    "Agende atividades pessoais como compromissos",
                    "Pratique técnicas de relaxamento"
                ],
                timeframe="6-8 semanas para estabelecer equilíbrio",
                related_patterns=["energy_pattern", "mood_cycle"]
            )
            insights.append(insight)
        
        return insights
    
    async def _calculate_summary_metrics(self, user_data: Dict, patterns: List[Pattern]) -> Dict[str, Any]:
        """Calcula métricas de resumo da análise."""
        return {
            "productivity_score": self._calculate_overall_productivity_score(user_data),
            "efficiency_score": self._calculate_efficiency_score(user_data),
            "consistency_score": self._calculate_consistency_score(patterns),
            "optimization_potential": self._calculate_optimization_potential(patterns),
            "wellbeing_score": self._calculate_wellbeing_score(user_data),
            "improvement_velocity": self._calculate_improvement_velocity(user_data)
        }
    
    async def _identify_priority_actions(self, insights: Dict[str, List[ProductivityInsight]]) -> List[Dict[str, Any]]:
        """Identifica ações prioritárias baseadas nos insights."""
        all_insights = []
        for category_insights in insights.values():
            all_insights.extend(category_insights)
        
        # Ordena por prioridade e impacto
        priority_insights = sorted(all_insights, key=lambda x: (
            x.priority.value,
            -x.impact_score,
            x.effort_required
        ))[:5]
        
        actions = []
        for insight in priority_insights:
            action = {
                "title": insight.title,
                "priority": insight.priority.value,
                "impact_score": insight.impact_score,
                "effort_required": insight.effort_required,
                "first_step": insight.implementation_steps[0] if insight.implementation_steps else "Revisar recomendações",
                "timeframe": insight.timeframe,
                "category": insight.category.value
            }
            actions.append(action)
        
        return actions
    
    async def _generate_improvement_roadmap(self, insights: Dict, patterns: List[Pattern]) -> Dict[str, Any]:
        """Gera roadmap de melhoria escalonado."""
        all_insights = []
        for category_insights in insights.values():
            all_insights.extend(category_insights)
        
        # Organiza por fases baseado no esforço e dependências
        phase_1 = [i for i in all_insights if i.effort_required <= 3.0]  # Quick wins
        phase_2 = [i for i in all_insights if 3.0 < i.effort_required <= 6.0]  # Medium effort
        phase_3 = [i for i in all_insights if i.effort_required > 6.0]  # High effort
        
        roadmap = {
            "phase_1_quick_wins": {
                "title": "Vitórias Rápidas (1-3 semanas)",
                "insights": [{"title": i.title, "impact": i.impact_score} for i in phase_1[:3]],
                "expected_impact": sum(i.impact_score for i in phase_1[:3]) / 3 if phase_1 else 0
            },
            "phase_2_foundation": {
                "title": "Construção da Base (1-2 meses)",
                "insights": [{"title": i.title, "impact": i.impact_score} for i in phase_2[:3]],
                "expected_impact": sum(i.impact_score for i in phase_2[:3]) / 3 if phase_2 else 0
            },
            "phase_3_optimization": {
                "title": "Otimização Avançada (2-3 meses)",
                "insights": [{"title": i.title, "impact": i.impact_score} for i in phase_3[:2]],
                "expected_impact": sum(i.impact_score for i in phase_3[:2]) / 2 if phase_3 else 0
            }
        }
        
        return roadmap
    
    # Métodos auxiliares de cálculo
    
    def _analyze_time_fragmentation(self, user_data: Dict) -> float:
        """Analisa fragmentação do tempo."""
        tasks = user_data.get('tasks', [])
        if len(tasks) < 5:
            return 0.3  # Baixa fragmentação assumida
        
        # Calcula variabilidade na duração das tarefas
        durations = [t.get('actual_duration', 60) for t in tasks]
        if len(durations) <= 1:
            return 0.3
            
        mean_duration = statistics.mean(durations)
        std_duration = statistics.stdev(durations)
        
        # Fragmentação = coeficiente de variação
        fragmentation = std_duration / mean_duration if mean_duration > 0 else 0.3
        return min(1.0, fragmentation)
    
    def _analyze_task_complexity_patterns(self, user_data: Dict) -> Optional[ProductivityInsight]:
        """Analisa padrões de complexidade de tarefas."""
        tasks = user_data.get('tasks', [])
        
        # Analisa distribuição de complexidade
        complexities = [t.get('complexity', 'medium') for t in tasks]
        complexity_dist = {
            'low': complexities.count('low') / len(complexities),
            'medium': complexities.count('medium') / len(complexities), 
            'high': complexities.count('high') / len(complexities)
        }
        
        # Se muitas tarefas de alta complexidade
        if complexity_dist['high'] > 0.4:
            return ProductivityInsight(
                id="task_opt_002",
                category=InsightCategory.TASK_OPTIMIZATION,
                priority=InsightPriority.MEDIUM,
                title="Balanceie a Complexidade das Tarefas",
                description=f"{complexity_dist['high']:.0%} das tarefas são de alta complexidade",
                current_state="Concentração excessiva em tarefas complexas",
                target_state="Mix balanceado: 20% alta, 50% média, 30% baixa complexidade",
                impact_score=6.5,
                effort_required=4.0,
                confidence=0.75,
                recommendations=[
                    "Intercale tarefas complexas com simples",
                    "Divida projetos grandes em subtarefas menores",
                    "Reserve energia para tarefas mais desafiadoras"
                ],
                metrics_to_track=["complexity_distribution", "completion_rate_by_complexity"],
                estimated_improvement={
                    "task_completion_rate": 20.0,
                    "mental_fatigue_reduction": 30.0
                },
                implementation_steps=[
                    "Classifique todas as tarefas por complexidade",
                    "Planeje dias com mix de complexidades",
                    "Use tarefas simples como 'aquecimento'",
                    "Monitore energia ao longo do dia"
                ],
                timeframe="3-4 semanas para ajustar fluxo",
                related_patterns=["task_clustering"]
            )
        
        return None
    
    def _calculate_productivity_trend(self, user_data: Dict) -> Dict[str, float]:
        """Calcula tendência de produtividade."""
        tasks = user_data.get('tasks', [])
        
        # Agrupa tarefas por semana e calcula produtividade semanal
        weekly_productivity = {}
        for task in tasks:
            # Simplificado - assume estrutura de data
            week = "2024-W1"  # Placeholder
            score = self._calculate_task_productivity_score(task)
            if week not in weekly_productivity:
                weekly_productivity[week] = []
            weekly_productivity[week].append(score)
        
        # Calcula médias semanais
        weekly_avgs = [statistics.mean(scores) for scores in weekly_productivity.values()]
        
        if len(weekly_avgs) < 3:
            return {"direction": "stable", "rate": 0.0, "significance": 0.0}
        
        # Calcula tendência linear simples
        trend_slope = (weekly_avgs[-1] - weekly_avgs[0]) / len(weekly_avgs)
        
        return {
            "direction": "increasing" if trend_slope > 0.01 else "decreasing" if trend_slope < -0.01 else "stable",
            "rate": abs(trend_slope) * 100,
            "significance": min(1.0, abs(trend_slope) * 10)
        }
    
    def _analyze_work_life_balance(self, user_data: Dict) -> Dict[str, float]:
        """Analisa equilíbrio trabalho-vida."""
        # Simplificado - baseado em horas trabalhadas
        tasks = user_data.get('tasks', [])
        total_work_hours = sum(t.get('actual_duration', 60) for t in tasks) / 60
        days_analyzed = len(set(t.get('date', '2024-01-01')[:10] for t in tasks))
        
        avg_daily_hours = total_work_hours / max(1, days_analyzed)
        
        # Score baseado em horas ideais (7-8h por dia)
        if avg_daily_hours <= 8:
            score = 1.0 - (8 - avg_daily_hours) * 0.1
        else:
            score = 1.0 - (avg_daily_hours - 8) * 0.15
        
        return {"score": max(0.0, min(1.0, score))}
    
    def _calculate_task_productivity_score(self, task: Dict) -> float:
        """Calcula score de produtividade de uma tarefa."""
        score = 0.5  # Base
        
        if task.get('status') == 'completed':
            score += 0.3
        
        # Eficiência temporal
        estimated = task.get('estimated_duration', 60)
        actual = task.get('actual_duration', 60)
        if estimated > 0:
            efficiency = min(1.0, estimated / actual)
            score += efficiency * 0.2
        
        return min(1.0, score)
    
    def _calculate_overall_productivity_score(self, user_data: Dict) -> float:
        """Calcula score geral de produtividade."""
        tasks = user_data.get('tasks', [])
        if not tasks:
            return 0.5
        
        scores = [self._calculate_task_productivity_score(t) for t in tasks]
        return statistics.mean(scores)
    
    def _calculate_efficiency_score(self, user_data: Dict) -> float:
        """Calcula score de eficiência."""
        tasks = user_data.get('tasks', [])
        efficiency_scores = []
        
        for task in tasks:
            estimated = task.get('estimated_duration')
            actual = task.get('actual_duration')
            if estimated and actual and estimated > 0:
                efficiency = min(1.0, estimated / actual)
                efficiency_scores.append(efficiency)
        
        return statistics.mean(efficiency_scores) if efficiency_scores else 0.5
    
    def _calculate_consistency_score(self, patterns: List[Pattern]) -> float:
        """Calcula score de consistência baseado nos padrões."""
        if not patterns:
            return 0.3
        
        strong_patterns = [p for p in patterns if p.confidence > 0.7]
        return min(1.0, len(strong_patterns) / 5)  # Normaliza para 5 padrões
    
    def _calculate_optimization_potential(self, patterns: List[Pattern]) -> float:
        """Calcula potencial de otimização."""
        # Baseado na presença de padrões problemáticos
        problematic_patterns = [p for p in patterns if p.type in [
            PatternType.PROCRASTINATION, 
            PatternType.DISTRACTION
        ]]
        
        # Mais padrões problemáticos = maior potencial de otimização
        return min(1.0, len(problematic_patterns) / 3)
    
    def _calculate_wellbeing_score(self, user_data: Dict) -> float:
        """Calcula score de bem-estar."""
        balance_score = self._analyze_work_life_balance(user_data)['score']
        
        # Combina com outros fatores de bem-estar
        stress_indicators = self._count_stress_indicators(user_data)
        stress_score = max(0.0, 1.0 - stress_indicators * 0.2)
        
        return (balance_score + stress_score) / 2
    
    def _calculate_improvement_velocity(self, user_data: Dict) -> float:
        """Calcula velocidade de melhoria."""
        # Simplificado - baseado em tendências recentes
        trend = self._calculate_productivity_trend(user_data)
        
        if trend['direction'] == 'increasing':
            return min(1.0, trend['rate'] / 10)
        else:
            return 0.3  # Velocidade base
    
    def _count_stress_indicators(self, user_data: Dict) -> int:
        """Conta indicadores de stress nos dados."""
        indicators = 0
        
        tasks = user_data.get('tasks', [])
        
        # Tarefas atrasadas
        delayed_tasks = sum(1 for t in tasks if self._is_task_delayed(t))
        if delayed_tasks > len(tasks) * 0.2:
            indicators += 1
        
        # Horas excessivas
        total_hours = sum(t.get('actual_duration', 60) for t in tasks) / 60
        days = len(set(t.get('date', '2024-01-01')[:10] for t in tasks))
        if total_hours / max(1, days) > 10:
            indicators += 1
        
        return indicators
    
    def _is_task_delayed(self, task: Dict) -> bool:
        """Verifica se tarefa foi atrasada."""
        # Simplificado
        return task.get('status') == 'overdue'
    
    def _calculate_overall_confidence(self, patterns: List[Pattern]) -> float:
        """Calcula confiança geral da análise."""
        if not patterns:
            return 0.3
        
        confidences = [p.confidence for p in patterns]
        return statistics.mean(confidences)

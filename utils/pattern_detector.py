"""
Módulo de detecção de padrões para o Lumi AI.
Identifica padrões comportamentais, tendências de produtividade e insights preditivos.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Set
import statistics
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter, defaultdict

class PatternType(Enum):
    """Tipos de padrões identificados."""
    PRODUCTIVITY_CYCLE = "productivity_cycle"
    TASK_CLUSTERING = "task_clustering" 
    BREAK_PATTERN = "break_pattern"
    MOOD_CYCLE = "mood_cycle"
    ENERGY_PATTERN = "energy_pattern"
    PROCRASTINATION = "procrastination"
    FLOW_STATE = "flow_state"
    DISTRACTION = "distraction"

class PatternStrength(Enum):
    """Força/confiabilidade do padrão."""
    WEAK = "weak"
    MODERATE = "moderate"
    STRONG = "strong"
    VERY_STRONG = "very_strong"

@dataclass
class Pattern:
    """Padrão comportamental identificado."""
    type: PatternType
    strength: PatternStrength
    description: str
    frequency: float  # 0-1
    confidence: float  # 0-1
    triggers: List[str]
    outcomes: List[str]
    recommendations: List[str]
    data_points: int
    time_range: Tuple[datetime, datetime]

@dataclass
class Trend:
    """Tendência temporal identificada."""
    metric: str
    direction: str  # "increasing", "decreasing", "stable"
    rate_of_change: float
    significance: float
    duration_days: int
    prediction: Optional[float]

class PatternDetector:
    """Detector avançado de padrões comportamentais e de produtividade."""
    
    def __init__(self):
        self.min_data_points = 5
        self.confidence_threshold = 0.6
        self.pattern_cache = {}
        
    def detect_all_patterns(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """
        Detecta todos os padrões disponíveis nos dados do usuário.
        
        Args:
            user_data: Dados completos do usuário
            
        Returns:
            Lista de padrões identificados ordenados por força
        """
        patterns = []
        
        # Detecta diferentes tipos de padrões
        patterns.extend(self.detect_productivity_cycles(user_data))
        patterns.extend(self.detect_task_clustering_patterns(user_data))
        patterns.extend(self.detect_break_patterns(user_data))
        patterns.extend(self.detect_mood_cycles(user_data))
        patterns.extend(self.detect_energy_patterns(user_data))
        patterns.extend(self.detect_procrastination_patterns(user_data))
        patterns.extend(self.detect_flow_states(user_data))
        patterns.extend(self.detect_distraction_patterns(user_data))
        
        # Filtra padrões por confiança mínima
        significant_patterns = [p for p in patterns if p.confidence >= self.confidence_threshold]
        
        # Ordena por força e confiança
        return sorted(significant_patterns, key=lambda x: (x.strength.value, x.confidence), reverse=True)
    
    def detect_productivity_cycles(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta ciclos de produtividade (diários, semanais, mensais)."""
        patterns = []
        tasks = user_data.get('tasks', [])
        
        if len(tasks) < self.min_data_points:
            return patterns
        
        # Análise de ciclos diários
        daily_pattern = self._analyze_daily_productivity_cycle(tasks)
        if daily_pattern:
            patterns.append(daily_pattern)
            
        # Análise de ciclos semanais
        weekly_pattern = self._analyze_weekly_productivity_cycle(tasks)
        if weekly_pattern:
            patterns.append(weekly_pattern)
            
        return patterns
    
    def detect_task_clustering_patterns(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta padrões de agrupamento de tarefas."""
        patterns = []
        tasks = user_data.get('tasks', [])
        
        # Detecta agrupamento por tipo
        type_clustering = self._analyze_task_type_clustering(tasks)
        if type_clustering:
            patterns.append(type_clustering)
            
        # Detecta agrupamento temporal
        temporal_clustering = self._analyze_temporal_task_clustering(tasks)
        if temporal_clustering:
            patterns.append(temporal_clustering)
            
        return patterns
    
    def detect_break_patterns(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta padrões de pausas e descansos."""
        breaks = user_data.get('breaks', [])
        tasks = user_data.get('tasks', [])
        
        if len(breaks) < self.min_data_points:
            return []
            
        return self._analyze_break_timing_patterns(breaks, tasks)
    
    def detect_mood_cycles(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta ciclos de humor e estado emocional."""
        mood_data = user_data.get('mood_history', [])
        
        if len(mood_data) < self.min_data_points:
            return []
            
        return self._analyze_mood_cycles(mood_data)
    
    def detect_energy_patterns(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta padrões de energia e fadiga."""
        energy_data = user_data.get('energy_levels', [])
        tasks = user_data.get('tasks', [])
        
        return self._analyze_energy_patterns(energy_data, tasks)
    
    def detect_procrastination_patterns(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta padrões de procrastinação."""
        tasks = user_data.get('tasks', [])
        
        if len(tasks) < self.min_data_points:
            return []
            
        return self._analyze_procrastination_patterns(tasks)
    
    def detect_flow_states(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta padrões de estados de fluxo/foco profundo."""
        tasks = user_data.get('tasks', [])
        focus_sessions = user_data.get('focus_sessions', [])
        
        return self._analyze_flow_state_patterns(tasks, focus_sessions)
    
    def detect_distraction_patterns(self, user_data: Dict[str, Any]) -> List[Pattern]:
        """Detecta padrões de distração e interrupção."""
        distractions = user_data.get('distractions', [])
        tasks = user_data.get('tasks', [])
        
        return self._analyze_distraction_patterns(distractions, tasks)
    
    def identify_trends(self, user_data: Dict[str, Any], metrics: List[str]) -> List[Trend]:
        """
        Identifica tendências temporais em métricas específicas.
        
        Args:
            user_data: Dados do usuário
            metrics: Lista de métricas para analisar tendências
            
        Returns:
            Lista de tendências identificadas
        """
        trends = []
        
        for metric in metrics:
            trend = self._analyze_metric_trend(user_data, metric)
            if trend:
                trends.append(trend)
                
        return sorted(trends, key=lambda x: x.significance, reverse=True)
    
    def predict_behavioral_changes(self, user_data: Dict[str, Any], patterns: List[Pattern]) -> Dict[str, Any]:
        """
        Prediz mudanças comportamentais baseadas nos padrões identificados.
        
        Args:
            user_data: Dados históricos do usuário
            patterns: Padrões identificados
            
        Returns:
            Predições e recomendações
        """
        predictions = {
            'productivity_forecast': self._predict_productivity_changes(patterns),
            'mood_forecast': self._predict_mood_changes(patterns),
            'energy_forecast': self._predict_energy_changes(patterns),
            'risk_factors': self._identify_risk_factors(patterns),
            'opportunities': self._identify_improvement_opportunities(patterns)
        }
        
        return predictions
    
    def generate_insights(self, patterns: List[Pattern]) -> List[Dict[str, Any]]:
        """
        Gera insights acionáveis baseados nos padrões detectados.
        
        Args:
            patterns: Lista de padrões identificados
            
        Returns:
            Lista de insights com recomendações
        """
        insights = []
        
        # Agrupa padrões por tipo
        pattern_groups = defaultdict(list)
        for pattern in patterns:
            pattern_groups[pattern.type].append(pattern)
        
        # Gera insights para cada grupo
        for pattern_type, type_patterns in pattern_groups.items():
            insight = self._generate_pattern_insight(pattern_type, type_patterns)
            if insight:
                insights.append(insight)
        
        # Insights combinados
        combined_insights = self._generate_combined_insights(patterns)
        insights.extend(combined_insights)
        
        return sorted(insights, key=lambda x: x.get('priority', 0), reverse=True)
    
    # Métodos auxiliares privados
    
    def _analyze_daily_productivity_cycle(self, tasks: List[Dict]) -> Optional[Pattern]:
        """Analisa ciclo de produtividade diário."""
        hourly_productivity = defaultdict(list)
        
        for task in tasks:
            start_time = task.get('start_time')
            if start_time:
                hour = self._extract_hour(start_time)
                if hour is not None:
                    productivity_score = self._calculate_task_productivity(task)
                    hourly_productivity[hour].append(productivity_score)
        
        if len(hourly_productivity) < 6:  # Necessita dados de pelo menos 6 horas
            return None
            
        # Calcula médias horárias
        avg_hourly = {hour: statistics.mean(scores) for hour, scores in hourly_productivity.items()}
        
        # Identifica picos e vales
        peak_hours = self._find_productivity_peaks(avg_hourly)
        low_hours = self._find_productivity_lows(avg_hourly)
        
        if not peak_hours and not low_hours:
            return None
            
        # Calcula força do padrão
        variance = statistics.variance(avg_hourly.values()) if len(avg_hourly) > 1 else 0
        strength = self._calculate_pattern_strength(variance, len(tasks))
        
        return Pattern(
            type=PatternType.PRODUCTIVITY_CYCLE,
            strength=strength,
            description=f"Maior produtividade entre {min(peak_hours)}-{max(peak_hours)}h, menor entre {min(low_hours)}-{max(low_hours)}h",
            frequency=self._calculate_pattern_frequency(hourly_productivity),
            confidence=min(0.9, len(tasks) / 50),
            triggers=[f"Horário: {h}h" for h in peak_hours],
            outcomes=["Alta produtividade", "Melhor foco"],
            recommendations=[
                f"Agende tarefas importantes entre {min(peak_hours)}-{max(peak_hours)}h",
                f"Use {min(low_hours)}-{max(low_hours)}h para tarefas administrativas"
            ],
            data_points=len(tasks),
            time_range=self._get_data_time_range(tasks)
        )
    
    def _analyze_weekly_productivity_cycle(self, tasks: List[Dict]) -> Optional[Pattern]:
        """Analisa ciclo de produtividade semanal."""
        weekly_productivity = defaultdict(list)
        
        for task in tasks:
            start_time = task.get('start_time')
            if start_time:
                weekday = self._extract_weekday(start_time)
                if weekday is not None:
                    productivity_score = self._calculate_task_productivity(task)
                    weekly_productivity[weekday].append(productivity_score)
        
        if len(weekly_productivity) < 5:  # Necessita dados de pelo menos 5 dias
            return None
            
        # Calcula médias por dia da semana
        avg_daily = {day: statistics.mean(scores) for day, scores in weekly_productivity.items()}
        
        best_days = sorted(avg_daily.keys(), key=lambda d: avg_daily[d], reverse=True)[:2]
        worst_days = sorted(avg_daily.keys(), key=lambda d: avg_daily[d])[:2]
        
        day_names = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        
        variance = statistics.variance(avg_daily.values()) if len(avg_daily) > 1 else 0
        strength = self._calculate_pattern_strength(variance, len(tasks))
        
        return Pattern(
            type=PatternType.PRODUCTIVITY_CYCLE,
            strength=strength,
            description=f"Maior produtividade: {', '.join([day_names[d] for d in best_days])}. Menor: {', '.join([day_names[d] for d in worst_days])}",
            frequency=self._calculate_pattern_frequency(weekly_productivity),
            confidence=min(0.9, len(tasks) / 30),
            triggers=[f"Dia da semana: {day_names[d]}" for d in best_days],
            outcomes=["Produtividade otimizada"],
            recommendations=[
                f"Concentre trabalho importante em {', '.join([day_names[d] for d in best_days])}",
                f"Use {', '.join([day_names[d] for d in worst_days])} para planejamento e tarefas leves"
            ],
            data_points=len(tasks),
            time_range=self._get_data_time_range(tasks)
        )
    
    def _analyze_task_type_clustering(self, tasks: List[Dict]) -> Optional[Pattern]:
        """Analisa padrões de agrupamento por tipo de tarefa."""
        if len(tasks) < self.min_data_points:
            return None
            
        task_sequences = self._extract_task_sequences(tasks)
        type_clusters = self._find_type_clusters(task_sequences)
        
        if not type_clusters:
            return None
            
        cluster_strength = self._calculate_clustering_strength(type_clusters)
        
        return Pattern(
            type=PatternType.TASK_CLUSTERING,
            strength=cluster_strength,
            description=f"Tendência a agrupar tarefas do tipo: {', '.join(type_clusters[:3])}",
            frequency=len(type_clusters) / len(set(t.get('type', 'unknown') for t in tasks)),
            confidence=min(0.85, cluster_strength.value * 0.3),
            triggers=["Início de tarefa do mesmo tipo"],
            outcomes=["Maior eficiência", "Melhor contexto"],
            recommendations=[
                "Continue agrupando tarefas similares",
                "Reserve blocos de tempo para cada tipo de tarefa"
            ],
            data_points=len(tasks),
            time_range=self._get_data_time_range(tasks)
        )
    
    def _analyze_temporal_task_clustering(self, tasks: List[Dict]) -> Optional[Pattern]:
        """Analisa padrões de agrupamento temporal."""
        if len(tasks) < self.min_data_points:
            return None
            
        time_gaps = self._calculate_time_gaps(tasks)
        cluster_threshold = statistics.median(time_gaps) if time_gaps else 30
        
        clusters = self._group_tasks_by_time_proximity(tasks, cluster_threshold)
        
        if len(clusters) < 2:
            return None
            
        avg_cluster_size = statistics.mean([len(cluster) for cluster in clusters])
        
        return Pattern(
            type=PatternType.TASK_CLUSTERING,
            strength=self._calculate_pattern_strength(avg_cluster_size, len(tasks)),
            description=f"Executa tarefas em grupos de ~{avg_cluster_size:.1f} com intervalos de {cluster_threshold:.0f}min",
            frequency=len(clusters) / len(tasks),
            confidence=min(0.8, len(clusters) / 10),
            triggers=[f"Intervalo < {cluster_threshold:.0f} minutos"],
            outcomes=["Produtividade em rajadas"],
            recommendations=[
                "Aproveite os períodos de agrupamento natural",
                "Planeje pausas entre clusters de tarefas"
            ],
            data_points=len(tasks),
            time_range=self._get_data_time_range(tasks)
        )
    
    def _analyze_break_timing_patterns(self, breaks: List[Dict], tasks: List[Dict]) -> List[Pattern]:
        """Analisa padrões de timing de pausas."""
        patterns = []
        
        # Analisa intervalos entre pausas
        break_intervals = self._calculate_break_intervals(breaks)
        if break_intervals:
            avg_interval = statistics.mean(break_intervals)
            interval_pattern = Pattern(
                type=PatternType.BREAK_PATTERN,
                strength=self._calculate_pattern_strength(statistics.stdev(break_intervals) if len(break_intervals) > 1 else 0, len(breaks)),
                description=f"Pausa a cada {avg_interval:.0f} minutos em média",
                frequency=len(breaks) / max(1, len(tasks)),
                confidence=min(0.8, len(breaks) / 20),
                triggers=[f"Trabalho contínuo por ~{avg_interval:.0f}min"],
                outcomes=["Recuperação de energia"],
                recommendations=[
                    f"Programe pausas a cada {avg_interval:.0f} minutos",
                    "Mantenha consistência nos intervalos"
                ],
                data_points=len(breaks),
                time_range=self._get_data_time_range(breaks)
            )
            patterns.append(interval_pattern)
        
        return patterns
    
    def _analyze_mood_cycles(self, mood_data: List[Dict]) -> List[Pattern]:
        """Analisa ciclos de humor."""
        patterns = []
        
        if len(mood_data) < self.min_data_points:
            return patterns
            
        # Analisa flutuações diárias de humor
        daily_moods = self._group_moods_by_day(mood_data)
        mood_variance = self._calculate_mood_variance(daily_moods)
        
        if mood_variance > 0.3:  # Threshold para variação significativa
            pattern = Pattern(
                type=PatternType.MOOD_CYCLE,
                strength=self._calculate_pattern_strength(mood_variance, len(mood_data)),
                description="Flutuações regulares de humor ao longo do dia",
                frequency=mood_variance,
                confidence=min(0.85, len(mood_data) / 30),
                triggers=self._identify_mood_triggers(mood_data),
                outcomes=["Variação de produtividade"],
                recommendations=[
                    "Monitore gatilhos de mudança de humor",
                    "Ajuste cronograma conforme ciclos de humor"
                ],
                data_points=len(mood_data),
                time_range=self._get_data_time_range(mood_data)
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_energy_patterns(self, energy_data: List[Dict], tasks: List[Dict]) -> List[Pattern]:
        """Analisa padrões de energia."""
        patterns = []
        
        if not energy_data:
            # Infere padrões de energia a partir das tarefas
            inferred_pattern = self._infer_energy_from_tasks(tasks)
            if inferred_pattern:
                patterns.append(inferred_pattern)
        else:
            # Analisa dados diretos de energia
            energy_pattern = self._analyze_direct_energy_data(energy_data)
            if energy_pattern:
                patterns.append(energy_pattern)
        
        return patterns
    
    def _analyze_procrastination_patterns(self, tasks: List[Dict]) -> List[Pattern]:
        """Analisa padrões de procrastinação."""
        patterns = []
        
        delayed_tasks = [t for t in tasks if self._is_task_delayed(t)]
        
        if len(delayed_tasks) < 3:
            return patterns
            
        # Analisa tipos de tarefas mais procrastinadas
        procrastinated_types = Counter([t.get('type', 'unknown') for t in delayed_tasks])
        most_procrastinated = procrastinated_types.most_common(2)
        
        procrastination_rate = len(delayed_tasks) / len(tasks)
        
        if procrastination_rate > 0.2:  # Mais de 20% das tarefas atrasadas
            pattern = Pattern(
                type=PatternType.PROCRASTINATION,
                strength=self._calculate_pattern_strength(procrastination_rate, len(tasks)),
                description=f"Procrastinação em {procrastination_rate:.0%} das tarefas, especialmente: {', '.join([t[0] for t in most_procrastinated])}",
                frequency=procrastination_rate,
                confidence=min(0.9, len(delayed_tasks) / 10),
                triggers=self._identify_procrastination_triggers(delayed_tasks),
                outcomes=["Atraso em entregas", "Stress"],
                recommendations=[
                    f"Divida tarefas do tipo '{most_procrastinated[0][0]}' em partes menores",
                    "Estabeleça deadlines intermediários",
                    "Use técnica Pomodoro para tarefas difíceis"
                ],
                data_points=len(tasks),
                time_range=self._get_data_time_range(tasks)
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_flow_state_patterns(self, tasks: List[Dict], focus_sessions: List[Dict]) -> List[Pattern]:
        """Analisa padrões de estado de fluxo."""
        patterns = []
        
        # Identifica sessões de foco prolongado
        long_focus_sessions = [t for t in tasks if t.get('actual_duration', 0) > 60 and t.get('interruptions', 0) == 0]
        
        if len(long_focus_sessions) < 3:
            return patterns
            
        # Analisa condições que levam ao flow
        flow_conditions = self._analyze_flow_conditions(long_focus_sessions)
        
        flow_frequency = len(long_focus_sessions) / len(tasks)
        
        pattern = Pattern(
            type=PatternType.FLOW_STATE,
            strength=self._calculate_pattern_strength(flow_frequency, len(tasks)),
            description=f"Estado de fluxo em {flow_frequency:.0%} das sessões, média de {statistics.mean([t.get('actual_duration', 0) for t in long_focus_sessions]):.0f}min",
            frequency=flow_frequency,
            confidence=min(0.85, len(long_focus_sessions) / 10),
            triggers=flow_conditions,
            outcomes=["Alta produtividade", "Satisfação"],
            recommendations=[
                "Reproduza condições que levam ao estado de fluxo",
                "Bloqueie distrações durante períodos de foco",
                "Reserve tempo contínuo para tarefas complexas"
            ],
            data_points=len(tasks),
            time_range=self._get_data_time_range(tasks)
        )
        patterns.append(pattern)
        
        return patterns
    
    def _analyze_distraction_patterns(self, distractions: List[Dict], tasks: List[Dict]) -> List[Pattern]:
        """Analisa padrões de distração."""
        patterns = []
        
        if not distractions:
            # Infere distrações a partir de interrupções nas tarefas
            interrupted_tasks = [t for t in tasks if t.get('interruptions', 0) > 0]
            if len(interrupted_tasks) >= 3:
                distraction_rate = len(interrupted_tasks) / len(tasks)
                avg_interruptions = statistics.mean([t.get('interruptions', 0) for t in interrupted_tasks])
                
                pattern = Pattern(
                    type=PatternType.DISTRACTION,
                    strength=self._calculate_pattern_strength(distraction_rate, len(tasks)),
                    description=f"Interrupções em {distraction_rate:.0%} das tarefas, média de {avg_interruptions:.1f} por tarefa",
                    frequency=distraction_rate,
                    confidence=min(0.8, len(interrupted_tasks) / 15),
                    triggers=self._identify_distraction_triggers(interrupted_tasks),
                    outcomes=["Redução de produtividade", "Stress"],
                    recommendations=[
                        "Identifique e elimine fontes de distração",
                        "Use bloqueadores de sites/apps durante foco",
                        "Estabeleça horários específicos para comunicação"
                    ],
                    data_points=len(tasks),
                    time_range=self._get_data_time_range(tasks)
                )
                patterns.append(pattern)
        
        return patterns
    
    # Métodos auxiliares para cálculos específicos
    
    def _extract_hour(self, time_str: str) -> Optional[int]:
        """Extrai hora de string de tempo."""
        try:
            if 'T' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.hour
            else:
                dt = datetime.strptime(time_str, '%H:%M')
                return dt.hour
        except:
            return None
    
    def _extract_weekday(self, time_str: str) -> Optional[int]:
        """Extrai dia da semana (0=segunda, 6=domingo)."""
        try:
            if 'T' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.weekday()
        except:
            return None
    
    def _calculate_task_productivity(self, task: Dict) -> float:
        """Calcula pontuação de produtividade de uma tarefa."""
        score = 0.5  # Base
        
        # Conclusão
        if task.get('status') == 'completed':
            score += 0.3
        
        # Eficiência (tempo real vs estimado)
        estimated = task.get('estimated_duration')
        actual = task.get('actual_duration')
        if estimated and actual:
            efficiency = min(1.0, estimated / actual)
            score += efficiency * 0.2
        
        # Qualidade (se disponível)
        quality = task.get('quality_score', 0.5)
        score += quality * 0.2
        
        return min(1.0, score)
    
    def _find_productivity_peaks(self, hourly_avg: Dict[int, float]) -> List[int]:
        """Encontra horários de pico de produtividade."""
        if not hourly_avg:
            return []
            
        avg_productivity = statistics.mean(hourly_avg.values())
        threshold = avg_productivity + statistics.stdev(hourly_avg.values()) * 0.5
        
        return [hour for hour, score in hourly_avg.items() if score > threshold]
    
    def _find_productivity_lows(self, hourly_avg: Dict[int, float]) -> List[int]:
        """Encontra horários de baixa produtividade."""
        if not hourly_avg:
            return []
            
        avg_productivity = statistics.mean(hourly_avg.values())
        threshold = avg_productivity - statistics.stdev(hourly_avg.values()) * 0.5
        
        return [hour for hour, score in hourly_avg.items() if score < threshold]
    
    def _calculate_pattern_strength(self, variance_or_score: float, data_points: int) -> PatternStrength:
        """Calcula força do padrão baseada na variância e quantidade de dados."""
        # Normaliza baseado na quantidade de dados
        confidence_factor = min(1.0, data_points / 20)
        strength_score = variance_or_score * confidence_factor
        
        if strength_score > 0.7:
            return PatternStrength.VERY_STRONG
        elif strength_score > 0.5:
            return PatternStrength.STRONG
        elif strength_score > 0.3:
            return PatternStrength.MODERATE
        else:
            return PatternStrength.WEAK
    
    def _calculate_pattern_frequency(self, data_groups: Dict) -> float:
        """Calcula frequência do padrão."""
        if not data_groups:
            return 0.0
        
        total_entries = sum(len(group) for group in data_groups.values())
        return min(1.0, total_entries / (len(data_groups) * 5))  # 5 como base esperada
    
    def _get_data_time_range(self, data: List[Dict]) -> Tuple[datetime, datetime]:
        """Obtém range temporal dos dados."""
        timestamps = []
        for item in data:
            for time_field in ['start_time', 'end_time', 'timestamp', 'created_at']:
                if time_field in item:
                    try:
                        if 'T' in str(item[time_field]):
                            dt = datetime.fromisoformat(str(item[time_field]).replace('Z', '+00:00'))
                            timestamps.append(dt)
                    except:
                        continue
        
        if timestamps:
            return min(timestamps), max(timestamps)
        else:
            now = datetime.now()
            return now - timedelta(days=30), now
    
    def _is_task_delayed(self, task: Dict) -> bool:
        """Verifica se uma tarefa foi atrasada."""
        due_date = task.get('due_date')
        completed_date = task.get('completed_date')
        
        if not due_date or not completed_date:
            return False
            
        try:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            completed = datetime.fromisoformat(completed_date.replace('Z', '+00:00'))
            return completed > due
        except:
            return False
    
    def _identify_procrastination_triggers(self, delayed_tasks: List[Dict]) -> List[str]:
        """Identifica gatilhos de procrastinação."""
        triggers = []
        
        # Analisa tipos de tarefa mais procrastinados
        task_types = Counter([t.get('type', 'unknown') for t in delayed_tasks])
        for task_type, count in task_types.most_common(3):
            if count >= 2:
                triggers.append(f"Tarefas do tipo '{task_type}'")
        
        # Analisa complexidade
        complexities = Counter([t.get('complexity', 'medium') for t in delayed_tasks])
        if complexities.get('high', 0) > len(delayed_tasks) * 0.4:
            triggers.append("Tarefas de alta complexidade")
        
        return triggers
    
    def _analyze_flow_conditions(self, flow_sessions: List[Dict]) -> List[str]:
        """Analisa condições que levam ao estado de fluxo."""
        conditions = []
        
        # Analisa horários
        hours = [self._extract_hour(t.get('start_time', '')) for t in flow_sessions]
        hours = [h for h in hours if h is not None]
        if hours:
            common_hours = Counter(hours).most_common(2)
            for hour, count in common_hours:
                if count >= 2:
                    conditions.append(f"Horário: {hour}h")
        
        # Analisa tipos de tarefa
        types = Counter([t.get('type', 'unknown') for t in flow_sessions])
        for task_type, count in types.most_common(2):
            if count >= 2:
                conditions.append(f"Tipo de tarefa: {task_type}")
        
        return conditions
    
    def _identify_distraction_triggers(self, interrupted_tasks: List[Dict]) -> List[str]:
        """Identifica gatilhos de distração."""
        triggers = []
        
        # Analisa horários com mais interrupções
        hours = [self._extract_hour(t.get('start_time', '')) for t in interrupted_tasks]
        hours = [h for h in hours if h is not None]
        if hours:
            common_hours = Counter(hours).most_common(2)
            for hour, count in common_hours:
                if count >= 2:
                    triggers.append(f"Horário de alta distração: {hour}h")
        
        return triggers
    
    def _analyze_metric_trend(self, user_data: Dict[str, Any], metric: str) -> Optional[Trend]:
        """Analisa tendência de uma métrica específica."""
        # Placeholder para análise de tendências
        # Implementação dependeria da estrutura específica dos dados
        return None
    
    def _predict_productivity_changes(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """Prediz mudanças na produtividade."""
        return {"forecast": "stable", "confidence": 0.7}
    
    def _predict_mood_changes(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """Prediz mudanças no humor."""
        return {"forecast": "stable", "confidence": 0.6}
    
    def _predict_energy_changes(self, patterns: List[Pattern]) -> Dict[str, Any]:
        """Prediz mudanças nos níveis de energia."""
        return {"forecast": "stable", "confidence": 0.65}
    
    def _identify_risk_factors(self, patterns: List[Pattern]) -> List[str]:
        """Identifica fatores de risco."""
        risks = []
        
        for pattern in patterns:
            if pattern.type == PatternType.PROCRASTINATION and pattern.strength in [PatternStrength.STRONG, PatternStrength.VERY_STRONG]:
                risks.append("Alto risco de procrastinação")
            elif pattern.type == PatternType.DISTRACTION and pattern.frequency > 0.5:
                risks.append("Frequentes distrações impactando produtividade")
        
        return risks
    
    def _identify_improvement_opportunities(self, patterns: List[Pattern]) -> List[str]:
        """Identifica oportunidades de melhoria."""
        opportunities = []
        
        for pattern in patterns:
            if pattern.type == PatternType.FLOW_STATE and pattern.frequency < 0.3:
                opportunities.append("Aumentar frequência de estados de fluxo")
            elif pattern.type == PatternType.PRODUCTIVITY_CYCLE and pattern.strength == PatternStrength.STRONG:
                opportunities.append("Otimizar cronograma baseado nos ciclos de produtividade")
        
        return opportunities
    
    def _generate_pattern_insight(self, pattern_type: PatternType, patterns: List[Pattern]) -> Optional[Dict[str, Any]]:
        """Gera insight para um tipo específico de padrão."""
        if not patterns:
            return None
            
        strongest_pattern = max(patterns, key=lambda p: p.confidence)
        
        insight = {
            "type": pattern_type.value,
            "title": f"Padrão {pattern_type.value.replace('_', ' ').title()} Identificado",
            "description": strongest_pattern.description,
            "strength": strongest_pattern.strength.value,
            "recommendations": strongest_pattern.recommendations,
            "priority": self._calculate_insight_priority(strongest_pattern)
        }
        
        return insight
    
    def _generate_combined_insights(self, patterns: List[Pattern]) -> List[Dict[str, Any]]:
        """Gera insights combinando múltiplos padrões."""
        insights = []
        
        # Exemplo: Combina padrões de produtividade e energia
        productivity_patterns = [p for p in patterns if p.type == PatternType.PRODUCTIVITY_CYCLE]
        energy_patterns = [p for p in patterns if p.type == PatternType.ENERGY_PATTERN]
        
        if productivity_patterns and energy_patterns:
            insight = {
                "type": "combined_optimization",
                "title": "Oportunidade de Otimização Combinada",
                "description": "Padrões de produtividade e energia podem ser sincronizados",
                "recommendations": [
                    "Alinhe tarefas de alta energia com picos de produtividade",
                    "Reserve períodos de baixa energia para tarefas administrativas"
                ],
                "priority": 8
            }
            insights.append(insight)
        
        return insights
    
    def _calculate_insight_priority(self, pattern: Pattern) -> int:
        """Calcula prioridade do insight (1-10)."""
        base_priority = {
            PatternType.PROCRASTINATION: 9,
            PatternType.DISTRACTION: 8,
            PatternType.PRODUCTIVITY_CYCLE: 7,
            PatternType.FLOW_STATE: 6,
            PatternType.ENERGY_PATTERN: 5,
            PatternType.MOOD_CYCLE: 4,
            PatternType.BREAK_PATTERN: 3,
            PatternType.TASK_CLUSTERING: 2
        }
        
        priority = base_priority.get(pattern.type, 5)
        
        # Ajusta baseado na força do padrão
        if pattern.strength == PatternStrength.VERY_STRONG:
            priority += 1
        elif pattern.strength == PatternStrength.WEAK:
            priority -= 1
            
        return max(1, min(10, priority))
    
    # Métodos auxiliares adicionais (simplificados para brevidade)
    
    def _extract_task_sequences(self, tasks: List[Dict]) -> List[List[str]]:
        """Extrai sequências de tipos de tarefa."""
        # Implementação simplificada
        return []
    
    def _find_type_clusters(self, sequences: List[List[str]]) -> List[str]:
        """Encontra clusters de tipos de tarefa."""
        # Implementação simplificada
        return []
    
    def _calculate_clustering_strength(self, clusters: List[str]) -> PatternStrength:
        """Calcula força do clustering."""
        return PatternStrength.MODERATE
    
    def _calculate_time_gaps(self, tasks: List[Dict]) -> List[float]:
        """Calcula intervalos de tempo entre tarefas."""
        # Implementação simplificada
        return [30.0, 45.0, 20.0]  # Placeholder
    
    def _group_tasks_by_time_proximity(self, tasks: List[Dict], threshold: float) -> List[List[Dict]]:
        """Agrupa tarefas por proximidade temporal."""
        # Implementação simplificada
        return [tasks[:3], tasks[3:6]] if len(tasks) >= 6 else [tasks]
    
    def _calculate_break_intervals(self, breaks: List[Dict]) -> List[float]:
        """Calcula intervalos entre pausas."""
        # Implementação simplificada
        return [45.0, 60.0, 40.0]  # Placeholder
    
    def _group_moods_by_day(self, mood_data: List[Dict]) -> Dict:
        """Agrupa dados de humor por dia."""
        # Implementação simplificada
        return {}
    
    def _calculate_mood_variance(self, daily_moods: Dict) -> float:
        """Calcula variância do humor."""
        # Implementação simplificada
        return 0.4
    
    def _identify_mood_triggers(self, mood_data: List[Dict]) -> List[str]:
        """Identifica gatilhos de mudança de humor."""
        return ["Stress no trabalho", "Falta de sono"]
    
    def _infer_energy_from_tasks(self, tasks: List[Dict]) -> Optional[Pattern]:
        """Infere padrões de energia a partir das tarefas."""
        # Implementação simplificada
        return None
    
    def _analyze_direct_energy_data(self, energy_data: List[Dict]) -> Optional[Pattern]:
        """Analisa dados diretos de energia."""
        # Implementação simplificada
        return None

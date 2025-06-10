"""
Módulo de análise temporal para o Lumi AI.
Analisa padrões de tempo, produtividade horária e otimização de cronogramas.
"""

from datetime import datetime, timedelta, time
from typing import Dict, List, Tuple, Optional, Any
import statistics
from dataclasses import dataclass
from enum import Enum

class ProductivityPeriod(Enum):
    """Períodos de produtividade."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"

@dataclass
class TimePattern:
    """Padrão temporal identificado."""
    hour_start: int
    hour_end: int
    productivity_level: ProductivityPeriod
    task_completion_rate: float
    average_focus_duration: float
    confidence_score: float

@dataclass
class TimeRecommendation:
    """Recomendação temporal para atividades."""
    activity_type: str
    recommended_time: time
    duration_minutes: int
    confidence: float
    reasoning: str

class TimeAnalyzer:
    """Analisador temporal avançado para otimização de produtividade."""
    
    def __init__(self):
        self.productivity_patterns: Dict[int, List[float]] = {}
        self.task_completion_times: Dict[str, List[Tuple[datetime, int]]] = {}
        self.focus_periods: List[Tuple[datetime, datetime]] = []
        
    def analyze_hourly_productivity(self, user_data: Dict[str, Any]) -> Dict[int, ProductivityPeriod]:
        """
        Analisa produtividade por hora do dia.
        
        Args:
            user_data: Dados do usuário com histórico de atividades
            
        Returns:
            Mapeamento hora -> nível de produtividade
        """
        hourly_scores = {}
        
        for hour in range(24):
            tasks_in_hour = self._get_tasks_by_hour(user_data.get('tasks', []), hour)
            
            if not tasks_in_hour:
                hourly_scores[hour] = ProductivityPeriod.VERY_LOW
                continue
                
            completion_rate = self._calculate_completion_rate(tasks_in_hour)
            focus_score = self._calculate_focus_score(tasks_in_hour)
            efficiency_score = self._calculate_efficiency_score(tasks_in_hour)
            
            # Pontuação composta
            composite_score = (completion_rate * 0.4 + focus_score * 0.3 + efficiency_score * 0.3)
            
            if composite_score >= 0.8:
                hourly_scores[hour] = ProductivityPeriod.HIGH
            elif composite_score >= 0.6:
                hourly_scores[hour] = ProductivityPeriod.MEDIUM
            elif composite_score >= 0.4:
                hourly_scores[hour] = ProductivityPeriod.LOW
            else:
                hourly_scores[hour] = ProductivityPeriod.VERY_LOW
                
        return hourly_scores
    
    def identify_peak_hours(self, user_data: Dict[str, Any]) -> List[TimePattern]:
        """
        Identifica os horários de pico de produtividade.
        
        Args:
            user_data: Dados históricos do usuário
            
        Returns:
            Lista de padrões temporais identificados
        """
        hourly_productivity = self.analyze_hourly_productivity(user_data)
        patterns = []
        
        # Agrupa horas consecutivas com alta produtividade
        current_pattern = None
        
        for hour in sorted(hourly_productivity.keys()):
            productivity = hourly_productivity[hour]
            
            if productivity in [ProductivityPeriod.HIGH, ProductivityPeriod.MEDIUM]:
                if current_pattern is None:
                    current_pattern = {
                        'start': hour,
                        'end': hour,
                        'levels': [productivity]
                    }
                else:
                    current_pattern['end'] = hour
                    current_pattern['levels'].append(productivity)
            else:
                if current_pattern and len(current_pattern['levels']) >= 2:
                    pattern = self._create_time_pattern(current_pattern, user_data)
                    patterns.append(pattern)
                current_pattern = None
        
        # Verifica se há um padrão no final
        if current_pattern and len(current_pattern['levels']) >= 2:
            pattern = self._create_time_pattern(current_pattern, user_data)
            patterns.append(pattern)
            
        return sorted(patterns, key=lambda x: x.confidence_score, reverse=True)
    
    def suggest_optimal_schedule(self, tasks: List[Dict], user_patterns: List[TimePattern]) -> List[Dict]:
        """
        Sugere um cronograma otimizado baseado nos padrões do usuário.
        
        Args:
            tasks: Lista de tarefas a serem agendadas
            user_patterns: Padrões temporais do usuário
            
        Returns:
            Lista de tarefas com horários sugeridos
        """
        if not user_patterns:
            return self._default_schedule(tasks)
            
        scheduled_tasks = []
        high_productivity_periods = [p for p in user_patterns if p.productivity_level == ProductivityPeriod.HIGH]
        
        # Ordena tarefas por prioridade e complexidade
        sorted_tasks = sorted(tasks, key=lambda t: (
            t.get('priority', 3),  # Prioridade (1=alta, 3=baixa)
            -t.get('estimated_duration', 30)  # Duração (tarefas mais longas primeiro)
        ))
        
        for task in sorted_tasks:
            best_time = self._find_best_time_slot(task, high_productivity_periods)
            
            scheduled_task = task.copy()
            scheduled_task['suggested_start_time'] = best_time.strftime('%H:%M')
            scheduled_task['reasoning'] = self._generate_time_reasoning(task, best_time, user_patterns)
            
            scheduled_tasks.append(scheduled_task)
            
        return scheduled_tasks
    
    def analyze_break_patterns(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa padrões de pausas e sugere intervalos otimizados.
        
        Args:
            user_data: Dados históricos do usuário
            
        Returns:
            Análise de padrões de pausas
        """
        break_data = user_data.get('breaks', [])
        
        if not break_data:
            return self._default_break_analysis()
            
        # Analisa duração média das pausas
        break_durations = [b.get('duration', 0) for b in break_data]
        avg_break_duration = statistics.mean(break_durations) if break_durations else 15
        
        # Analisa intervalos entre pausas
        work_intervals = self._calculate_work_intervals(break_data)
        avg_work_interval = statistics.mean(work_intervals) if work_intervals else 45
        
        # Analisa efetividade das pausas
        break_effectiveness = self._analyze_break_effectiveness(user_data)
        
        return {
            'average_break_duration': round(avg_break_duration, 1),
            'average_work_interval': round(avg_work_interval, 1),
            'break_effectiveness': break_effectiveness,
            'recommended_break_duration': self._recommend_break_duration(avg_break_duration, break_effectiveness),
            'recommended_work_interval': self._recommend_work_interval(avg_work_interval, break_effectiveness),
            'optimal_break_activities': self._suggest_break_activities(break_data)
        }
    
    def predict_task_duration(self, task: Dict, user_history: List[Dict]) -> Tuple[int, float]:
        """
        Prediz a duração de uma tarefa baseada no histórico do usuário.
        
        Args:
            task: Tarefa a ser analisada
            user_history: Histórico de tarefas similares
            
        Returns:
            Tuple (duração_estimada_minutos, confiança)
        """
        similar_tasks = self._find_similar_tasks(task, user_history)
        
        if not similar_tasks:
            # Estimativa padrão baseada na complexidade
            complexity = task.get('complexity', 'medium')
            base_durations = {'low': 30, 'medium': 60, 'high': 120}
            return base_durations.get(complexity, 60), 0.3
            
        durations = [t.get('actual_duration', t.get('estimated_duration', 60)) for t in similar_tasks]
        
        # Calcula estatísticas
        avg_duration = statistics.mean(durations)
        std_deviation = statistics.stdev(durations) if len(durations) > 1 else 0
        
        # Ajusta para fatores contextuais
        adjusted_duration = self._adjust_duration_for_context(avg_duration, task, similar_tasks)
        
        # Calcula confiança baseada na quantidade e variabilidade de dados
        confidence = min(0.9, len(similar_tasks) / 10) * max(0.1, 1 - (std_deviation / avg_duration))
        
        return round(adjusted_duration), round(confidence, 2)
    
    def generate_time_recommendations(self, user_data: Dict[str, Any]) -> List[TimeRecommendation]:
        """
        Gera recomendações temporais personalizadas.
        
        Args:
            user_data: Dados completos do usuário
            
        Returns:
            Lista de recomendações temporais
        """
        patterns = self.identify_peak_hours(user_data)
        recommendations = []
        
        # Recomendações para diferentes tipos de atividade
        activity_types = ['deep_work', 'meetings', 'creative_work', 'admin_tasks', 'learning']
        
        for activity in activity_types:
            best_time = self._find_optimal_time_for_activity(activity, patterns, user_data)
            duration = self._estimate_optimal_duration(activity, user_data)
            confidence = self._calculate_recommendation_confidence(activity, patterns)
            reasoning = self._generate_recommendation_reasoning(activity, best_time, patterns)
            
            recommendations.append(TimeRecommendation(
                activity_type=activity,
                recommended_time=best_time,
                duration_minutes=duration,
                confidence=confidence,
                reasoning=reasoning
            ))
            
        return sorted(recommendations, key=lambda x: x.confidence, reverse=True)
    
    # Métodos auxiliares privados
    
    def _get_tasks_by_hour(self, tasks: List[Dict], hour: int) -> List[Dict]:
        """Filtra tarefas por hora específica."""
        return [t for t in tasks if self._extract_hour(t.get('start_time')) == hour]
    
    def _extract_hour(self, time_str: Optional[str]) -> Optional[int]:
        """Extrai a hora de uma string de tempo."""
        if not time_str:
            return None
        try:
            if 'T' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(time_str, '%H:%M')
            return dt.hour
        except:
            return None
    
    def _calculate_completion_rate(self, tasks: List[Dict]) -> float:
        """Calcula taxa de conclusão de tarefas."""
        if not tasks:
            return 0.0
        completed = sum(1 for t in tasks if t.get('status') == 'completed')
        return completed / len(tasks)
    
    def _calculate_focus_score(self, tasks: List[Dict]) -> float:
        """Calcula pontuação de foco baseada na duração das tarefas."""
        if not tasks:
            return 0.0
        
        durations = [t.get('actual_duration', 0) for t in tasks if t.get('actual_duration')]
        if not durations:
            return 0.5
            
        avg_duration = statistics.mean(durations)
        # Normaliza para 0-1 (assumindo que 60 min é foco ideal)
        return min(1.0, avg_duration / 60)
    
    def _calculate_efficiency_score(self, tasks: List[Dict]) -> float:
        """Calcula pontuação de eficiência (tempo real vs estimado)."""
        efficiency_scores = []
        
        for task in tasks:
            estimated = task.get('estimated_duration')
            actual = task.get('actual_duration')
            
            if estimated and actual and estimated > 0:
                # Eficiência = tempo estimado / tempo real (máx 1.0)
                efficiency = min(1.0, estimated / actual)
                efficiency_scores.append(efficiency)
        
        return statistics.mean(efficiency_scores) if efficiency_scores else 0.5
    
    def _create_time_pattern(self, pattern_data: Dict, user_data: Dict) -> TimePattern:
        """Cria um objeto TimePattern a partir dos dados."""
        tasks_in_period = []
        for hour in range(pattern_data['start'], pattern_data['end'] + 1):
            tasks_in_period.extend(self._get_tasks_by_hour(user_data.get('tasks', []), hour))
        
        completion_rate = self._calculate_completion_rate(tasks_in_period)
        avg_focus = statistics.mean([t.get('actual_duration', 30) for t in tasks_in_period]) if tasks_in_period else 30
        
        # Calcula confiança baseada na quantidade de dados
        confidence = min(0.95, len(tasks_in_period) / 20)
        
        # Determina nível de produtividade
        high_count = pattern_data['levels'].count(ProductivityPeriod.HIGH)
        productivity_level = ProductivityPeriod.HIGH if high_count >= len(pattern_data['levels']) / 2 else ProductivityPeriod.MEDIUM
        
        return TimePattern(
            hour_start=pattern_data['start'],
            hour_end=pattern_data['end'],
            productivity_level=productivity_level,
            task_completion_rate=completion_rate,
            average_focus_duration=avg_focus,
            confidence_score=confidence
        )
    
    def _default_schedule(self, tasks: List[Dict]) -> List[Dict]:
        """Cronograma padrão quando não há padrões específicos."""
        scheduled = []
        current_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
        
        for task in tasks:
            duration = task.get('estimated_duration', 60)
            scheduled_task = task.copy()
            scheduled_task['suggested_start_time'] = current_time.strftime('%H:%M')
            scheduled_task['reasoning'] = "Horário padrão - dados insuficientes para personalização"
            
            scheduled.append(scheduled_task)
            current_time += timedelta(minutes=duration + 15)  # 15 min buffer
            
        return scheduled
    
    def _find_best_time_slot(self, task: Dict, productivity_periods: List[TimePattern]) -> datetime:
        """Encontra o melhor horário para uma tarefa."""
        if not productivity_periods:
            return datetime.now().replace(hour=9, minute=0)
            
        # Prioriza períodos de alta produtividade
        best_period = max(productivity_periods, key=lambda p: p.confidence_score)
        
        # Seleciona hora no meio do período
        mid_hour = (best_period.hour_start + best_period.hour_end) // 2
        return datetime.now().replace(hour=mid_hour, minute=0)
    
    def _generate_time_reasoning(self, task: Dict, suggested_time: datetime, patterns: List[TimePattern]) -> str:
        """Gera explicação para sugestão de horário."""
        hour = suggested_time.hour
        
        for pattern in patterns:
            if pattern.hour_start <= hour <= pattern.hour_end:
                if pattern.productivity_level == ProductivityPeriod.HIGH:
                    return f"Horário de alta produtividade ({pattern.hour_start}h-{pattern.hour_end}h) com {pattern.task_completion_rate:.0%} de taxa de conclusão"
                else:
                    return f"Horário de boa produtividade com foco médio de {pattern.average_focus_duration:.0f} minutos"
        
        return "Horário baseado em disponibilidade geral"
    
    def _default_break_analysis(self) -> Dict[str, Any]:
        """Análise padrão de pausas quando não há dados."""
        return {
            'average_break_duration': 15.0,
            'average_work_interval': 45.0,
            'break_effectiveness': 0.7,
            'recommended_break_duration': 15,
            'recommended_work_interval': 45,
            'optimal_break_activities': ['caminhada', 'hidratação', 'alongamento']
        }
    
    def _calculate_work_intervals(self, break_data: List[Dict]) -> List[float]:
        """Calcula intervalos de trabalho entre pausas."""
        intervals = []
        for i in range(1, len(break_data)):
            prev_end = break_data[i-1].get('end_time')
            curr_start = break_data[i].get('start_time')
            if prev_end and curr_start:
                # Simplificado - assumindo dados em minutos
                interval = curr_start - prev_end
                intervals.append(interval)
        return intervals
    
    def _analyze_break_effectiveness(self, user_data: Dict) -> float:
        """Analisa efetividade das pausas."""
        # Simplificado - baseado na produtividade pós-pausa
        return 0.75  # Placeholder para análise mais complexa
    
    def _recommend_break_duration(self, current_avg: float, effectiveness: float) -> int:
        """Recomenda duração ideal de pausa."""
        if effectiveness > 0.8:
            return round(current_avg)
        elif effectiveness < 0.6:
            return max(10, round(current_avg * 0.8))
        else:
            return round(current_avg * 1.1)
    
    def _recommend_work_interval(self, current_avg: float, effectiveness: float) -> int:
        """Recomenda intervalo ideal de trabalho."""
        if effectiveness > 0.8:
            return round(current_avg)
        else:
            return max(30, round(current_avg * 0.9))
    
    def _suggest_break_activities(self, break_data: List[Dict]) -> List[str]:
        """Sugere atividades para pausas."""
        return ['caminhada', 'hidratação', 'exercícios de respiração', 'alongamento']
    
    def _find_similar_tasks(self, task: Dict, history: List[Dict]) -> List[Dict]:
        """Encontra tarefas similares no histórico."""
        similar = []
        task_type = task.get('type', '').lower()
        task_complexity = task.get('complexity', 'medium')
        
        for hist_task in history:
            if (hist_task.get('type', '').lower() == task_type or 
                hist_task.get('complexity') == task_complexity):
                similar.append(hist_task)
                
        return similar[:10]  # Limita a 10 tarefas mais relevantes
    
    def _adjust_duration_for_context(self, base_duration: float, task: Dict, similar_tasks: List[Dict]) -> float:
        """Ajusta duração baseada no contexto atual."""
        # Ajustes baseados em fatores contextuais
        multiplier = 1.0
        
        # Ajuste por horário (se especificado)
        if 'scheduled_hour' in task:
            hour = task['scheduled_hour']
            if 9 <= hour <= 11 or 14 <= hour <= 16:  # Horários de pico
                multiplier *= 0.9
            elif hour < 8 or hour > 18:  # Horários menos produtivos
                multiplier *= 1.2
        
        # Ajuste por complexidade
        complexity = task.get('complexity', 'medium')
        complexity_multipliers = {'low': 0.8, 'medium': 1.0, 'high': 1.3}
        multiplier *= complexity_multipliers.get(complexity, 1.0)
        
        return base_duration * multiplier
    
    def _find_optimal_time_for_activity(self, activity: str, patterns: List[TimePattern], user_data: Dict) -> time:
        """Encontra horário ótimo para tipo de atividade."""
        activity_preferences = {
            'deep_work': lambda p: p.productivity_level == ProductivityPeriod.HIGH and p.average_focus_duration > 45,
            'meetings': lambda p: p.hour_start >= 9 and p.hour_end <= 17,
            'creative_work': lambda p: p.productivity_level == ProductivityPeriod.HIGH,
            'admin_tasks': lambda p: p.productivity_level in [ProductivityPeriod.MEDIUM, ProductivityPeriod.LOW],
            'learning': lambda p: p.productivity_level == ProductivityPeriod.HIGH and p.task_completion_rate > 0.7
        }
        
        preference_func = activity_preferences.get(activity, lambda p: True)
        suitable_patterns = [p for p in patterns if preference_func(p)]
        
        if suitable_patterns:
            best_pattern = max(suitable_patterns, key=lambda p: p.confidence_score)
            optimal_hour = (best_pattern.hour_start + best_pattern.hour_end) // 2
            return time(hour=optimal_hour, minute=0)
        
        # Fallback para horários padrão
        default_times = {
            'deep_work': time(9, 0),
            'meetings': time(10, 0),
            'creative_work': time(8, 30),
            'admin_tasks': time(14, 0),
            'learning': time(16, 0)
        }
        
        return default_times.get(activity, time(10, 0))
    
    def _estimate_optimal_duration(self, activity: str, user_data: Dict) -> int:
        """Estima duração ótima para tipo de atividade."""
        default_durations = {
            'deep_work': 90,
            'meetings': 60,
            'creative_work': 120,
            'admin_tasks': 30,
            'learning': 60
        }
        
        return default_durations.get(activity, 60)
    
    def _calculate_recommendation_confidence(self, activity: str, patterns: List[TimePattern]) -> float:
        """Calcula confiança na recomendação."""
        if not patterns:
            return 0.3
            
        relevant_patterns = [p for p in patterns if p.confidence_score > 0.5]
        if not relevant_patterns:
            return 0.4
            
        avg_confidence = statistics.mean([p.confidence_score for p in relevant_patterns])
        return min(0.95, avg_confidence * 1.1)
    
    def _generate_recommendation_reasoning(self, activity: str, suggested_time: time, patterns: List[TimePattern]) -> str:
        """Gera explicação para recomendação."""
        hour = suggested_time.hour
        
        for pattern in patterns:
            if pattern.hour_start <= hour <= pattern.hour_end:
                return f"Baseado no seu padrão de {pattern.productivity_level.value} produtividade entre {pattern.hour_start}h-{pattern.hour_end}h"
        
        return f"Horário otimizado para {activity.replace('_', ' ')}"

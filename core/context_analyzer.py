import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class ContextAnalysis:
    intent: str
    confidence: float
    entities: Dict[str, Any]
    sentiment: str
    urgency_level: str
    suggested_actions: List[Dict[str, Any]]

class ContextAnalyzer:
    def __init__(self):
        self.intent_patterns = self._initialize_intent_patterns()
        self.entity_extractors = self._initialize_entity_extractors()
        
    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent detection patterns"""
        return {
            "create_task": [
                # Padrões diretos de criação
                "criar tarefa", "nova tarefa", "adicionar tarefa", "preciso fazer",
                "tenho que", "vou fazer", "criar atividade", "nova atividade",
                # Padrões de agenda/planejamento
                "adicione na minha agenda", "agendar", "marcar para", "programar",
                "estudar", "fazer", "trabalhar em", "reunião", "compromisso",
                "lembrar de", "não esquecer de", "amanhã", "hoje", "semana",
                # Padrões temporais específicos
                "às", "na", "no", "durante", "depois", "antes", "até"
            ],
            "start_pomodoro": [
                "começar pomodoro", "iniciar sessão", "vamos trabalhar", "começar agora",
                "iniciar foco", "hora de trabalhar", "começar timer", "focar"
            ],
            "check_progress": [
                "como estou", "meu progresso", "estatísticas", "como vou",
                "meus dados", "resumo", "relatório", "análise", "tarefas pendentes",
                "tenho alguma tarefa", "o que preciso fazer", "pendências"
            ],
            "get_suggestions": [
                "o que fazer", "sugestão", "recomendação", "ajuda", "próximo passo",
                "que tarefa", "me ajude", "orientação", "procrastinando", "procrastinação"
            ],
            "motivational_chat": [
                "não consigo", "difícil", "cansado", "desmotivado", "desanimado",
                "como vai", "oi", "olá", "bom dia", "boa tarde", "procrastinando"
            ],
            "celebrate_achievement": [
                "consegui", "terminei", "completei", "finalizei", "sucesso",
                "acabei", "pronto", "feito"
            ],
            "modify_task": [
                "editar tarefa", "mudar tarefa", "alterar", "atualizar",
                "modificar", "corrigir"
            ],
            "delete_task": [
                "deletar tarefa", "remover tarefa", "apagar", "excluir",
                "cancelar tarefa"
            ],
            "productivity_insights": [
                "insights", "padrões", "quando sou produtivo", "melhor horário",
                "análise comportamental", "meus hábitos"
            ]
        }
    
    def _initialize_entity_extractors(self) -> Dict[str, List[str]]:
        """Initialize entity extraction patterns"""
        return {
            "time": [
                "hoje", "amanhã", "semana", "mês", "hora", "minuto",
                "manhã", "tarde", "noite", "segunda", "terça", "quarta"
            ],
            "priority": [
                "urgente", "importante", "baixa", "média", "alta",
                "crítico", "prioridade", "rápido"
            ],
            "duration": [
                "pomodoro", "minutos", "horas", "tempo", "sessão", "período"
            ],
            "emotion": [
                "feliz", "triste", "cansado", "motivado", "ansioso",
                "estressado", "relaxado", "animado", "preocupado"
            ]
        }
    
    async def analyze_context(self, message: str, user_context: Dict[str, Any]) -> ContextAnalysis:
        """Analyze message context and user intent"""
        try:
            message_lower = message.lower().strip()
            
            # Detect intent
            intent, intent_confidence = self._detect_intent(message_lower)
            
            # Extract entities
            entities = self._extract_entities(message_lower)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(message_lower, entities)
            
            # Determine urgency
            urgency_level = self._determine_urgency(intent, entities, user_context)
            
            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(intent, entities, user_context)
            
            return ContextAnalysis(
                intent=intent,
                confidence=intent_confidence,
                entities=entities,
                sentiment=sentiment,
                urgency_level=urgency_level,
                suggested_actions=suggested_actions
            )
            
        except Exception as e:
            logger.error(f"Error analyzing context: {e}")
            return self._get_default_analysis()
    
    def _detect_intent(self, message: str) -> Tuple[str, float]:
        """Detect user intent from message"""
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0.0
            matched_patterns = 0
            
            for pattern in patterns:
                if pattern in message:
                    score += 1.0
                    matched_patterns += 1
                elif any(word in message for word in pattern.split()):
                    score += 0.5
                    matched_patterns += 0.5
            
            if matched_patterns > 0:
                intent_scores[intent] = score / len(patterns)
        
        if not intent_scores:
            return "motivational_chat", 0.3
        
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return best_intent[0], min(best_intent[1], 1.0)
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from message"""
        entities = {}
        
        for entity_type, patterns in self.entity_extractors.items():
            extracted = []
            for pattern in patterns:
                if pattern in message:
                    extracted.append(pattern)
            
            if extracted:
                entities[entity_type] = extracted
        
        # Extract specific patterns
        entities.update(self._extract_specific_entities(message))
        
        return entities
    
    def _extract_specific_entities(self, message: str) -> Dict[str, Any]:
        """Extract specific entity patterns"""
        entities = {}
        
        # Extract numbers (potential duration, quantity)
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Extract task-like phrases
        task_indicators = ["fazer", "criar", "estudar", "trabalhar", "terminar"]
        for indicator in task_indicators:
            if indicator in message:
                # Try to extract the task description after the indicator
                parts = message.split(indicator, 1)
                if len(parts) > 1:
                    potential_task = parts[1].strip()[:50]  # Limit length
                    if potential_task:
                        entities["potential_task"] = potential_task
                break
        
        # Extract time references
        time_patterns = {
            "hoje": "today",
            "amanhã": "tomorrow",
            "agora": "now",
            "depois": "later",
            "manhã": "morning",
            "tarde": "afternoon",
            "noite": "evening"
        }
        
        for pt_time, en_time in time_patterns.items():
            if pt_time in message:
                entities.setdefault("time_references", []).append(en_time)
        
        return entities
    
    def _analyze_sentiment(self, message: str, entities: Dict[str, Any]) -> str:
        """Analyze message sentiment"""
        positive_words = [
            "bom", "ótimo", "legal", "feliz", "animado", "motivado",
            "consegui", "sucesso", "perfeito", "incrível", "excelente"
        ]
        
        negative_words = [
            "ruim", "péssimo", "triste", "cansado", "difícil", "impossível",
            "não consigo", "desanimado", "estressado", "problema", "erro"
        ]
        
        neutral_words = [
            "ok", "normal", "talvez", "pode ser", "não sei", "tanto faz"
        ]
        
        # Count sentiment indicators
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        neutral_count = sum(1 for word in neutral_words if word in message)
        
        # Check emotional entities
        emotions = entities.get("emotion", [])
        positive_emotions = ["feliz", "motivado", "animado", "relaxado"]
        negative_emotions = ["triste", "cansado", "ansioso", "estressado"]
        
        for emotion in emotions:
            if emotion in positive_emotions:
                positive_count += 1
            elif emotion in negative_emotions:
                negative_count += 1
        
        # Determine overall sentiment
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _determine_urgency(self, intent: str, entities: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Determine urgency level of the request"""
        
        # High urgency intents
        high_urgency_intents = ["start_pomodoro", "create_task"]
        if intent in high_urgency_intents:
            urgency_base = "medium"
        else:
            urgency_base = "low"
        
        # Check for urgency indicators in entities
        urgency_words = entities.get("priority", [])
        if any(word in ["urgente", "crítico", "importante"] for word in urgency_words):
            return "high"
        
        # Check time entities
        time_refs = entities.get("time_references", [])
        if "now" in time_refs or "today" in time_refs:
            if urgency_base == "medium":
                return "high"
            else:
                return "medium"
        
        # Check user context for urgency indicators
        tasks_stats = user_context.get("tasks_stats", {})
        overdue_tasks = tasks_stats.get("overdue_tasks", 0)
        
        if overdue_tasks >= 3:
            return "high"
        elif overdue_tasks >= 1:
            return "medium"
        
        return urgency_base
    
    def _generate_suggested_actions(self, intent: str, entities: Dict[str, Any], 
                                  user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggested actions based on context analysis"""
        actions = []
        
        if intent == "create_task":
            potential_task = entities.get("potential_task")
            actions.append({
                "type": "create_task",
                "data": {
                    "title": potential_task or "Nova tarefa",
                    "priority": self._extract_priority(entities),
                    "due_date": self._extract_due_date(entities)
                }
            })
        
        elif intent == "start_pomodoro":
            # Suggest starting a pomodoro with the most relevant task
            pending_tasks = user_context.get("tasks_stats", {}).get("pending_tasks", 0)
            if pending_tasks > 0:
                actions.append({
                    "type": "start_pomodoro",
                    "data": {
                        "suggested_task": "próxima tarefa pendente",
                        "duration": 25
                    }
                })
        
        elif intent == "check_progress":
            actions.append({
                "type": "show_analytics",
                "data": {
                    "period": "today",
                    "include_insights": True
                }
            })
        
        elif intent == "get_suggestions":
            actions.append({
                "type": "provide_suggestions",
                "data": {
                    "based_on": "current_context",
                    "include_task_recommendations": True
                }
            })
        
        elif intent == "celebrate_achievement":
            actions.append({
                "type": "celebrate",
                "data": {
                    "type": "task_completion",
                    "update_streak": True
                }
            })
        
        elif intent == "productivity_insights":
            actions.append({
                "type": "provide_insights",
                "data": {
                    "analysis_period": "30_days",
                    "include_patterns": True,
                    "include_recommendations": True
                }
            })
        
        return actions
    
    def _extract_priority(self, entities: Dict[str, Any]) -> str:
        """Extract priority from entities"""
        priority_entities = entities.get("priority", [])
        
        if any(p in ["urgente", "crítico"] for p in priority_entities):
            return "high"
        elif any(p in ["importante", "alta"] for p in priority_entities):
            return "high"
        elif any(p in ["média", "normal"] for p in priority_entities):
            return "medium"
        elif any(p in ["baixa", "depois"] for p in priority_entities):
            return "low"
        
        return "medium"
    
    def _extract_due_date(self, entities: Dict[str, Any]) -> Optional[str]:
        """Extract due date from entities"""
        time_refs = entities.get("time_references", [])
        
        if "today" in time_refs:
            return datetime.now().strftime("%Y-%m-%d")
        elif "tomorrow" in time_refs:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "morning" in time_refs and "today" not in time_refs:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        return None
    
    def _get_default_analysis(self) -> ContextAnalysis:
        """Get default context analysis for error cases"""
        return ContextAnalysis(
            intent="motivational_chat",
            confidence=0.3,
            entities={},
            sentiment="neutral",
            urgency_level="low",
            suggested_actions=[]
        )

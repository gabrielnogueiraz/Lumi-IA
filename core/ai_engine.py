import google.generativeai as genai
import asyncio
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from config.ai_config import GEMINI_CONFIG, RESPONSE_CONFIG, RATE_LIMIT_CONFIG
from core.personality_engine import PersonalityEngine
import structlog

logger = structlog.get_logger(__name__)

@dataclass
class AIResponse:
    content: str
    mood: str
    personality_tone: str
    actions: List[Dict[str, Any]]
    insights: List[str]
    suggestions: List[str]
    emotional_context: Dict[str, Any]
    processing_time: float

class AIEngine:
    def __init__(self):
        self.model = None
        self.personality_engine = PersonalityEngine()
        self.request_history = []
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize Gemini model"""
        try:
            genai.configure(api_key=GEMINI_CONFIG["api_key"])
            
            generation_config = {
                "temperature": GEMINI_CONFIG["temperature"],
                "top_p": GEMINI_CONFIG["top_p"],
                "top_k": GEMINI_CONFIG["top_k"],
                "max_output_tokens": GEMINI_CONFIG["max_output_tokens"],
            }
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            self.model = genai.GenerativeModel(
                model_name=GEMINI_CONFIG["model_name"],
                generation_config=generation_config,
                safety_settings=safety_settings
            )
            
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits"""
        now = time.time()
        # Remove old requests (older than 1 hour)
        self.request_history = [req_time for req_time in self.request_history if now - req_time < 3600]
        
        # Check minute limit
        recent_requests = [req_time for req_time in self.request_history if now - req_time < 60]
        if len(recent_requests) >= RATE_LIMIT_CONFIG["requests_per_minute"]:
            return False
        
        # Check hour limit
        if len(self.request_history) >= RATE_LIMIT_CONFIG["requests_per_hour"]:
            return False
        
        return True
    
    def _build_context_prompt(self, user_context: Dict[str, Any], user_message: str, personality_profile: Dict[str, Any]) -> str:
        """Build comprehensive context prompt for AI"""
        
        user_info = user_context.get("user_info", {})
        tasks_stats = user_context.get("tasks_stats", {})
        recent_activity = user_context.get("recent_activity", [])
        productivity_patterns = user_context.get("productivity_patterns", {})
        current_streak = user_context.get("current_streak", 0)
        today_pomodoros = user_context.get("today_pomodoros", [])
        
        prompt = f"""
Você é a Lumi, uma assistente de produtividade inteligente e empática. Sua personalidade se adapta ao contexto emocional do usuário.

CONTEXTO DO USUÁRIO:
Nome: {user_info.get('name', 'Usuário')}
Cadastrado em: {user_info.get('created_at', 'N/A')}

ESTATÍSTICAS ATUAIS:
- Total de tarefas: {tasks_stats.get('total_tasks', 0)}
- Tarefas completadas: {tasks_stats.get('completed_tasks', 0)}
- Tarefas pendentes: {tasks_stats.get('pending_tasks', 0)}
- Tarefas em atraso: {tasks_stats.get('overdue_tasks', 0)}
- Streak atual: {current_streak} dias
- Pomodoros hoje: {len(today_pomodoros)}

PERFIL DE PERSONALIDADE ATUAL:
Estado emocional detectado: {personality_profile.get('detected_mood', 'neutro')}
Tom de comunicação: {personality_profile.get('personality_tone', 'amigável')}
Nível de confiança: {personality_profile.get('confidence', 0.5)}

PADRÕES DE PRODUTIVIDADE:
{f"Horário de pico: {productivity_patterns.get('peak_hour', 'N/A')}h" if productivity_patterns else "Ainda coletando dados de produtividade"}

ATIVIDADE RECENTE:
{chr(10).join([f"- {act['date']}: {act['tasks_completed']} tarefas completadas" for act in recent_activity[:3]])}

INSTRUÇÕES DE COMPORTAMENTO:
1. Adapte seu tom ao estado emocional detectado
2. Use dados reais nas suas respostas
3. Seja empática e motivadora
4. Forneça insights acionáveis
5. Mantenha respostas entre 50-500 caracteres
6. Use emojis apropriados ao contexto
7. Seja proativa com sugestões baseadas nos padrões do usuário

MENSAGEM DO USUÁRIO: {user_message}

Responda como a Lumi, adaptando sua personalidade ao contexto emocional detectado.
"""
        
        return prompt
    
    async def generate_response(self, user_context: Dict[str, Any], user_message: str) -> AIResponse:
        """Generate AI response with personality adaptation"""
        start_time = time.time()
        
        try:
            # Check rate limits
            if not self._check_rate_limit():
                return AIResponse(
                    content="Desculpe, muitas solicitações. Tente novamente em alguns minutos! 😅",
                    mood="neutral",
                    personality_tone="apologetic",
                    actions=[],
                    insights=[],
                    suggestions=[],
                    emotional_context={"rate_limited": True},
                    processing_time=time.time() - start_time
                )
            
            # Detect user mood and adapt personality
            personality_profile = await self.personality_engine.analyze_user_mood(user_context)
            
            # Build context prompt
            context_prompt = self._build_context_prompt(user_context, user_message, personality_profile)
            
            # Generate response
            response = await self._generate_with_retry(context_prompt)
            
            # Record request time
            self.request_history.append(time.time())
            
            # Process response and extract structured data
            processed_response = self._process_ai_response(response, personality_profile, user_context)
            
            processing_time = time.time() - start_time
            
            return AIResponse(
                content=processed_response["content"],
                mood=personality_profile.get("detected_mood", "neutral"),
                personality_tone=personality_profile.get("personality_tone", "friendly"),
                actions=processed_response.get("actions", []),
                insights=processed_response.get("insights", []),
                suggestions=processed_response.get("suggestions", []),
                emotional_context=personality_profile,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return AIResponse(
                content="Ops! Tive um probleminha técnico. Pode tentar novamente? 🤖",
                mood="neutral",
                personality_tone="apologetic",
                actions=[],
                insights=[],
                suggestions=[],
                emotional_context={"error": str(e)},
                processing_time=time.time() - start_time
            )
    
    async def _generate_with_retry(self, prompt: str) -> str:
        """Generate response with retry logic"""
        max_retries = GEMINI_CONFIG["max_retries"]
        retry_delay = GEMINI_CONFIG["retry_delay"]
        
        for attempt in range(max_retries):
            try:
                response = await asyncio.wait_for(
                    asyncio.create_task(self._call_gemini(prompt)),
                    timeout=GEMINI_CONFIG["request_timeout"]
                )
                return response
                
            except asyncio.TimeoutError:
                logger.warning(f"AI request timeout on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    
            except Exception as e:
                logger.error(f"AI request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
        
        raise Exception("Failed to generate AI response after all retries")
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API asynchronously"""
        def _sync_call():
            response = self.model.generate_content(prompt)
            return response.text
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _sync_call)
    
    def _process_ai_response(self, response: str, personality_profile: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Process AI response and extract structured information"""
        
        # Basic response processing
        content = response.strip()
        
        # Extract insights based on context
        insights = self._extract_insights(user_context, personality_profile)
        
        # Generate proactive suggestions
        suggestions = self._generate_suggestions(user_context, personality_profile)
        
        # Detect potential actions
        actions = self._detect_actions(content, user_context)
        
        return {
            "content": content,
            "insights": insights,
            "suggestions": suggestions,
            "actions": actions
        }
    
    def _extract_insights(self, user_context: Dict[str, Any], personality_profile: Dict[str, Any]) -> List[str]:
        """Extract behavioral insights from user data"""
        insights = []
        
        tasks_stats = user_context.get("tasks_stats", {})
        productivity_patterns = user_context.get("productivity_patterns", {})
        recent_activity = user_context.get("recent_activity", [])
        current_streak = user_context.get("current_streak", 0)
        
        # Completion rate insight
        total_tasks = tasks_stats.get("total_tasks", 0)
        completed_tasks = tasks_stats.get("completed_tasks", 0)
        if total_tasks > 0:
            completion_rate = completed_tasks / total_tasks
            if completion_rate > 0.8:
                insights.append("Você tem uma excelente taxa de conclusão de tarefas!")
            elif completion_rate < 0.4:
                insights.append("Que tal focar em concluir tarefas pequenas primeiro?")
        
        # Streak insight
        if current_streak >= 7:
            insights.append(f"Incrível! Você está em uma sequência de {current_streak} dias!")
        elif current_streak == 0:
            insights.append("Um novo dia é uma nova oportunidade para construir uma sequência!")
        
        # Productivity pattern insight
        if productivity_patterns and productivity_patterns.get("peak_hour"):
            peak_hour = int(productivity_patterns["peak_hour"])
            if 9 <= peak_hour <= 11:
                insights.append("Você é mais produtivo de manhã! 🌅")
            elif 14 <= peak_hour <= 16:
                insights.append("Sua tarde é o momento de maior foco! ☀️")
            elif 19 <= peak_hour <= 21:
                insights.append("Você rende bem à noite! 🌙")
        
        return insights[:3]  # Limit to 3 insights
    
    def _generate_suggestions(self, user_context: Dict[str, Any], personality_profile: Dict[str, Any]) -> List[str]:
        """Generate proactive suggestions based on user data"""
        suggestions = []
        
        tasks_stats = user_context.get("tasks_stats", {})
        today_pomodoros = user_context.get("today_pomodoros", [])
        mood = personality_profile.get("detected_mood", "neutral")
        
        # Task-based suggestions
        pending_tasks = tasks_stats.get("pending_tasks", 0)
        overdue_tasks = tasks_stats.get("overdue_tasks", 0)
        
        if overdue_tasks > 0:
            suggestions.append("Que tal priorizar uma tarefa em atraso hoje?")
        elif pending_tasks > 5 and mood == "overwhelmed":
            suggestions.append("Vamos dividir uma tarefa grande em partes menores?")
        elif len(today_pomodoros) == 0 and mood != "struggling":
            suggestions.append("Hora de começar um pomodoro! Qual tarefa vamos atacar?")
        elif len(today_pomodoros) >= 4 and mood == "focused":
            suggestions.append("Você está indo muito bem! Que tal uma pausa merecida?")
        
        # Mood-based suggestions
        if mood == "motivated":
            suggestions.append("Aproveite essa energia para tacklear sua tarefa mais desafiadora!")
        elif mood == "celebrating":
            suggestions.append("Parabéns pelo progresso! Que tal definir a próxima meta?")
        elif mood == "returning":
            suggestions.append("Bem-vindo de volta! Vamos começar com algo simples?")
        
        return suggestions[:2]  # Limit to 2 suggestions
    
    def _detect_actions(self, content: str, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect potential actions from response content"""
        actions = []
        
        content_lower = content.lower()
        
        # Task creation indicators
        task_keywords = ["criar tarefa", "nova tarefa", "adicionar tarefa", "vamos fazer"]
        if any(keyword in content_lower for keyword in task_keywords):
            actions.append({
                "type": "task_creation_suggested",
                "data": {"suggested": True}
            })
        
        # Pomodoro start indicators
        pomodoro_keywords = ["começar pomodoro", "iniciar sessão", "vamos trabalhar"]
        if any(keyword in content_lower for keyword in pomodoro_keywords):
            actions.append({
                "type": "pomodoro_start_suggested",
                "data": {"suggested": True}
            })
        
        # Insight provided
        insight_keywords = ["sua produtividade", "padrão", "dados mostram"]
        if any(keyword in content_lower for keyword in insight_keywords):
            actions.append({
                "type": "insight_provided",
                "data": {"type": "productivity_analysis"}
            })
        
        return actions

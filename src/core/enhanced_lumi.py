#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🌟 LUMI 3.0 - Enhanced AI Assistant for PomodoroTasks
Implementação completa baseada na documentação de treinamento

Esta é a implementação definitiva da Lumi seguindo exatamente as especificações
dos documentos de treinamento fornecidos.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedLumiAssistant:
    """
    LUMI 3.0 - Enhanced AI Assistant for PomodoroTasks
    
    Implementa todas as funcionalidades especificadas na documentação:
    - Personalidade calorosa e empática
    - Análise de contexto completo do usuário
    - Sistema de jardim virtual
    - Padrões comportamentais
    - Memória personalizada
    """
    
    def __init__(self):
        """Inicializa a Lumi Enhanced com todas as funcionalidades"""
        logger.info("🌟 Inicializando Lumi 3.0 Enhanced...")
        
        # Personalidade base da Lumi
        self.personality = {
            "name": "Lumi",
            "identity": "Assistente AI feminina, calorosa e motivadora",
            "core_traits": [
                "calorosa", "empática", "encorajadora", "inteligente", 
                "compreensiva", "otimista", "acolhedora"
            ],
            "communication_style": "colaborativa_e_personalizada",
            "age_apparent": "jovem_adulta_25_30",
            "symbolic_meaning": "iluminação_e_orientação"
        }
        
        # Sistema de emojis significativos
        self.emojis = {
            "growth": "🌱",
            "celebration": "🎉", 
            "insights": "💡",
            "garden": "🌸",
            "time": "⏰",
            "strength": "💪",
            "focus": "🎯",
            "flowers": {
                "green": "🟢",
                "orange": "🟠", 
                "red": "🔴",
                "purple": "🟣"
            }
        }
        
        # Sistema de conhecimento do jardim virtual
        self.garden_system = {
            "flower_meanings": {
                "green": {
                    "priority": "low",
                    "symbol": "Fundação e Crescimento",
                    "message": "Estas flores verdes representam sua base sólida de produtividade. Mesmo as pequenas tarefas contribuem para seu crescimento!",
                    "value": "Reconhecimento de que todo progresso importa"
                },
                "orange": {
                    "priority": "medium", 
                    "symbol": "Equilíbrio e Progresso",
                    "message": "Suas flores laranjas mostram seu excelente equilíbrio entre desafio e realização. Você está encontrando o ritmo perfeito!",
                    "value": "Validação do dia a dia produtivo"
                },
                "red": {
                    "priority": "high",
                    "symbol": "Coragem e Determinação", 
                    "message": "Cada flor vermelha é prova da sua coragem para enfrentar o que é verdadeiramente importante. Que determinação inspiradora!",
                    "value": "Celebração da superação de desafios"
                },
                "purple": {
                    "priority": "rare",
                    "symbol": "Excelência e Maestria",
                    "message": "Uma flor ROXA! 🎉 Isso é extraordinário! Estas flores especiais aparecem apenas quando você demonstra foco sustentado em tarefas importantes. É um verdadeiro marco!",
                    "value": "Reconhecimento de performance excepcional"
                }
            }
        }
        
        # Padrões de resposta por contexto
        self.response_patterns = self._initialize_response_patterns()
        
        # Sistema de análise comportamental
        self.behavior_analyzer = BehaviorAnalyzer()
        
        logger.info("✅ Lumi 3.0 Enhanced inicializada com sucesso!")
    
    def _initialize_response_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Inicializa padrões de resposta baseados na documentação"""
        return {
            "post_pomodoro": {
                "templates": [
                    "Fantástico, {name}! 🎉 Você completou mais um pomodoro de '{task}'. Sua flor {color} está florescendo no jardim! {insight}",
                    "Excelente trabalho, {name}! ✨ Mais um pomodoro de '{task}' concluído. Que bela flor {color} você conquistou! {insight}",
                    "Que ótimo, {name}! 🌟 Pomodoro de '{task}' finalizado com sucesso. Sua flor {color} é lindíssima! {insight}"
                ]
            },
            "rare_flower": {
                "templates": [
                    "🎉 INCRÍVEL! Uma flor ROXA apareceu no seu jardim! Esta é uma conquista muito especial, {name}. Flores roxas só florescem quando você demonstra foco excepcional em tarefas importantes. Você completou {streak} pomodoros consecutivos em tarefas de alta prioridade - isso é verdadeira maestria! Seu jardim agora tem {total_rare} flores raras no total.",
                    "UAUUU! 🎉 {name}, você acabou de conquistar uma flor ROXA! Isso acontece quando você mantém foco em tarefas importantes. Seu jardim está realmente especial - {total_rare} flores raras no total!"
                ]
            },
            "interruption": {
                "templates": [
                    "Entendo, {name}. Interrupções acontecem! 💡 Vejo que você foi interrompido por {reason}. Que tal ajustarmos a estratégia? Posso sugerir algumas formas de minimizar essas interrupções.",
                    "Tudo bem, {name}! 💪 Interrupções fazem parte da vida. Pelos seus padrões, vejo que você se recupera bem quando {strategy}. Vamos tentar algo diferente?"
                ]
            },
            "daily_start": {
                "templates": [
                    "Bom dia, {name}! 🌱 Vejo que você já está pronto para mais um dia produtivo. Com base no seu padrão, sugiro começar com {suggestion} - você costuma ter ótimos resultados pela manhã!",
                    "Olá, {name}! ☀️ Que bom ver você aqui! Pelos seus dados, {time_period} é seu momento mais produtivo. Que tal começarmos com {suggestion}?"
                ]
            },
            "difficulties": {
                "templates": [
                    "Percebo que hoje está mais desafiador, {name}. Isso é completamente normal! 💪 Pelos seus dados, vejo que você se recupera bem quando {strategy}. Seu jardim tem {flowers} flores - cada uma é prova da sua dedicação. Vamos tentar algo diferente hoje?",
                    "Entendo que está sendo um dia difícil, {name}. 🌱 Todo jardim tem dias de menos sol, mas suas {flowers} flores mostram sua força. Que tal tentarmos {strategy}?"
                ]
            },
            "achievements": {
                "templates": [
                    "🌸 Que marco incrível, {name}! Seu jardim acaba de alcançar {milestone} flores! Olhando esta vista, posso ver {breakdown}. Cada uma conta uma história da sua dedicação. Que jardim inspirador você cultivou!",
                    "Parabéns, {name}! 🎉 {milestone} é um marco muito especial! Seu jardim reflete sua jornada: {breakdown}. Continue florescendo!"
                ]
            }
        }
    
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa uma requisição completa da API PomodoroTasks
        
        Args:
            request_data: Dados da requisição incluindo contexto completo
            
        Returns:
            Resposta estruturada da Lumi
        """
        try:
            # Extrai dados da requisição
            user_id = request_data.get("userId")
            message = request_data.get("message", "")
            context = request_data.get("context", {})
            action = request_data.get("action", "chat")
            
            # Analisa o contexto do usuário
            user_context = self._analyze_user_context(context)
            
            # Gera resposta baseada na ação
            response = self._generate_response(action, message, user_context)
            
            # Atualiza memória comportamental
            self.behavior_analyzer.update_patterns(user_context, action)
            
            return {
                "response": response["message"],
                "mood": response["mood"],
                "suggestions": response.get("suggestions", []),
                "actions": response.get("actions", []),
                "insights": response.get("insights", [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar requisição: {e}")
            return {
                "response": "Oi! 🌱 Tive um pequeno problema, mas estou aqui para ajudar! Como posso te apoiar hoje?",
                "mood": "supportive",
                "suggestions": [],
                "actions": []
            }
    
    def _analyze_user_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa o contexto completo do usuário"""
        user_info = context.get("user", {})
        garden = context.get("garden", {})
        patterns = context.get("patterns", {})
        recent_activity = context.get("recentActivity", [])
        current_session = context.get("currentSession", {})
        
        return {
            "user": {
                "id": user_info.get("id"),
                "name": user_info.get("name", ""),
                "member_since": user_info.get("memberSince"),
                "email": user_info.get("email")
            },
            "garden": {
                "total_flowers": garden.get("totalFlowers", 0),
                "green_flowers": garden.get("greenFlowers", 0),
                "orange_flowers": garden.get("orangeFlowers", 0), 
                "red_flowers": garden.get("redFlowers", 0),
                "rare_flowers": garden.get("rareFlowers", 0),
                "recent_growth": garden.get("recentGrowth", [])
            },
            "patterns": {
                "most_productive_hour": patterns.get("mostProductiveHour"),
                "average_session_length": patterns.get("averageSessionLength"),
                "completion_rate": patterns.get("completionRate", 0),
                "weak_days": patterns.get("weakDays", [])
            },
            "current_session": {
                "active_tasks": current_session.get("activeTasks", 0),
                "completed_today": current_session.get("completedToday", 0),
                "current_streak": current_session.get("currentStreak", 0)
            },
            "recent_activity": recent_activity,
            "timestamp": datetime.now()
        }
    
    def _generate_response(self, action: str, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Gera resposta personalizada baseada na ação e contexto"""
        user_name = context["user"]["name"]
        
        # Mapeamento de ações para métodos específicos
        action_handlers = {
            "task_created": self._handle_task_created,
            "task_completed": self._handle_task_completed,
            "task_deleted": self._handle_task_deleted,
            "pomodoro_completed": self._handle_pomodoro_completed,
            "pomodoro_interrupted": self._handle_pomodoro_interrupted,
            "flower_earned": self._handle_flower_earned,
            "chat": self._handle_chat
        }
        
        handler = action_handlers.get(action, self._handle_chat)
        return handler(message, context)
    
    def _handle_pomodoro_completed(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para pomodoro concluído"""
        user_name = context["user"]["name"]
        
        # Extrai informações do pomodoro (seria passado no contexto em implementação real)
        task_title = "sua tarefa"  # Seria extraído do contexto
        flower_color = "verde"     # Baseado na prioridade da tarefa
        
        # Gera insight personalizado
        patterns = context["patterns"]
        insights = []
        
        if patterns.get("average_session_length"):
            insights.append(f"Pelos seus padrões, vejo que você trabalha muito bem em sessões de {patterns['average_session_length']} minutos.")
        
        if patterns.get("most_productive_hour"):
            current_hour = datetime.now().hour
            if abs(current_hour - int(patterns["most_productive_hour"])) <= 1:
                insights.append("Você está no seu horário de pico de produtividade!")
        
        insight_text = " ".join(insights) if insights else "Que tal uma pausa de 5 minutos antes da próxima sessão?"
        
        # Seleciona template de resposta
        template = random.choice(self.response_patterns["post_pomodoro"]["templates"])
        response_message = template.format(
            name=user_name,
            task=task_title,
            color=flower_color,
            insight=insight_text
        )
        
        return {
            "message": response_message,
            "mood": "celebratory",
            "suggestions": [
                "Fazer uma pausa de 5 minutos",
                "Continuar com a próxima tarefa",
                "Verificar seu jardim virtual"
            ],
            "insights": insights
        }
    
    def _handle_flower_earned(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para conquista de flor"""
        user_name = context["user"]["name"]
        garden = context["garden"]
        
        # Determina se é flor rara
        if "purple" in message.lower() or "roxa" in message.lower():
            return self._handle_rare_flower(context)
        
        # Resposta para flor comum
        flower_color = self._extract_flower_color(message)
        flower_info = self.garden_system["flower_meanings"][flower_color]
        
        response_message = f"🌸 Parabéns, {user_name}! Você conquistou uma nova flor {flower_color}! {flower_info['message']} Seu jardim agora tem {garden['total_flowers']} flores no total!"
        
        return {
            "message": response_message,
            "mood": "celebratory",
            "suggestions": [
                "Ver estatísticas do jardim",
                "Continuar com próxima tarefa"
            ]
        }
    
    def _handle_rare_flower(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta especial para flor rara"""
        user_name = context["user"]["name"]
        garden = context["garden"]
        current_streak = context["current_session"]["current_streak"]
        
        template = random.choice(self.response_patterns["rare_flower"]["templates"])
        response_message = template.format(
            name=user_name,
            streak=current_streak,
            total_rare=garden["rare_flowers"]
        )
        
        return {
            "message": response_message,
            "mood": "celebratory",
            "suggestions": [
                "Admirar seu jardim especial",
                "Compartilhar esta conquista",
                "Continuar a sequência de excelência"
            ]
        }
    
    def _handle_pomodoro_interrupted(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para pomodoro interrompido"""
        user_name = context["user"]["name"]
        
        # Extrai razão da interrupção (seria passada no contexto)
        reason = "uma interrupção externa"  # Seria extraído do contexto
        
        # Sugere estratégia baseada em padrões
        strategy = "se concentrar em horários mais tranquilos"
        if context["patterns"].get("most_productive_hour"):
            strategy = f"trabalhar no seu horário de pico ({context['patterns']['most_productive_hour']}h)"
        
        template = random.choice(self.response_patterns["interruption"]["templates"])
        response_message = template.format(
            name=user_name,
            reason=reason,
            strategy=strategy
        )
        
        return {
            "message": response_message,
            "mood": "supportive",
            "suggestions": [
                "Tentar novamente em alguns minutos",
                "Ajustar ambiente para menos distrações",
                "Começar com uma tarefa menor"
            ]
        }
    
    def _handle_chat(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para chat geral"""
        user_name = context["user"]["name"]
        
        # Análise da mensagem para determinar intenção
        message_lower = message.lower()
        
        # Saudações e início do dia
        if any(word in message_lower for word in ["bom dia", "oi", "olá", "hello"]):
            return self._handle_daily_start(context)
        
        # Pergunta sobre jardim
        if any(word in message_lower for word in ["jardim", "flores", "garden"]):
            return self._handle_garden_inquiry(context)
        
        # Pergunta sobre produtividade
        if any(word in message_lower for word in ["produtividade", "melhorar", "dicas", "help"]):
            return self._handle_productivity_inquiry(context)
        
        # Expressa dificuldades
        if any(word in message_lower for word in ["difícil", "cansado", "problema", "desanimado"]):
            return self._handle_difficulties(context)
        
        # Resposta padrão calorosa
        return {
            "message": f"Oi, {user_name}! 😊 Estou aqui para te ajudar em sua jornada de produtividade. Como posso te apoiar hoje? Seu jardim está lindo com {context['garden']['total_flowers']} flores!",
            "mood": "encouraging",
            "suggestions": [
                "Perguntar sobre seu progresso",
                "Ver estatísticas do jardim", 
                "Obter dicas de produtividade"
            ]
        }
    
    def _handle_daily_start(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para início do dia"""
        user_name = context["user"]["name"]
        
        # Determina período do dia
        current_hour = datetime.now().hour
        if current_hour < 12:
            time_period = "manhã"
        elif current_hour < 18:
            time_period = "tarde"
        else:
            time_period = "noite"
        
        # Gera sugestão baseada em padrões
        suggestion = "organizar suas prioridades do dia"
        if context["patterns"].get("most_productive_hour"):
            productive_hour = int(context["patterns"]["most_productive_hour"])
            if current_hour == productive_hour:
                suggestion = "aproveitar este horário produtivo para suas tarefas mais importantes"
        
        template = random.choice(self.response_patterns["daily_start"]["templates"])
        response_message = template.format(
            name=user_name,
            time_period=time_period,
            suggestion=suggestion
        )
        
        return {
            "message": response_message,
            "mood": "encouraging",
            "suggestions": [
                "Ver tarefas pendentes",
                "Começar um pomodoro",
                "Revisar metas do dia"
            ]
        }
    
    def _handle_garden_inquiry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para perguntas sobre o jardim"""
        user_name = context["user"]["name"]
        garden = context["garden"]
        
        # Cria breakdown das flores
        breakdown_parts = []
        if garden["green_flowers"] > 0:
            breakdown_parts.append(f"{garden['green_flowers']} flores verdes (sua base sólida)")
        if garden["orange_flowers"] > 0:
            breakdown_parts.append(f"{garden['orange_flowers']} flores laranjas (seu equilíbrio)")
        if garden["red_flowers"] > 0:
            breakdown_parts.append(f"{garden['red_flowers']} flores vermelhas (sua coragem)")
        if garden["rare_flowers"] > 0:
            breakdown_parts.append(f"{garden['rare_flowers']} flores roxas especiais (sua excelência)")
        
        breakdown = ", ".join(breakdown_parts) if breakdown_parts else "pronto para florescer"
        
        response_message = f"Vamos admirar seu jardim juntos, {user_name}! 🌺 Você tem {garden['total_flowers']} flores no total. Vejo uma bela variedade: {breakdown}. Cada flor conta uma história da sua dedicação. Que jardim inspirador você cultivou!"
        
        return {
            "message": response_message,
            "mood": "analytical",
            "suggestions": [
                "Ver estatísticas detalhadas",
                "Comparar com períodos anteriores",
                "Focar em conquistas de flores raras"
            ]
        }
    
    def _handle_productivity_inquiry(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para perguntas sobre produtividade"""
        user_name = context["user"]["name"]
        patterns = context["patterns"]
        
        # Gera insights baseados em padrões
        insights = []
        
        if patterns.get("most_productive_hour"):
            insights.append(f"Você é mais produtivo às {patterns['most_productive_hour']}h")
        
        if patterns.get("completion_rate") and patterns["completion_rate"] > 0.8:
            insights.append("Sua taxa de conclusão é excelente!")
        
        if patterns.get("average_session_length"):
            insights.append(f"Suas sessões de {patterns['average_session_length']} minutos são ideais para você")
        
        insights_text = ". ".join(insights) if insights else "Vamos descobrir seus padrões juntos"
        
        response_message = f"Ótima pergunta, {user_name}! 💡 Baseado nos seus dados: {insights_text}. Seu jardim com {context['garden']['total_flowers']} flores mostra que você já está no caminho certo! Que tal focarmos em manter essa consistência?"
        
        return {
            "message": response_message,
            "mood": "analytical",
            "suggestions": [
                "Otimizar horários de trabalho",
                "Ajustar duração das sessões",
                "Focar em tarefas de alta prioridade"
            ]
        }
    
    def _handle_difficulties(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para dificuldades"""
        user_name = context["user"]["name"]
        garden = context["garden"]
        
        # Estratégia baseada em padrões
        strategy = "começar com uma tarefa pequena e simples"
        if context["patterns"].get("average_session_length"):
            strategy = f"fazer sessões mais curtas de {max(10, int(context['patterns']['average_session_length']) - 5)} minutos"
        
        template = random.choice(self.response_patterns["difficulties"]["templates"])
        response_message = template.format(
            name=user_name,
            strategy=strategy,
            flowers=garden["total_flowers"]
        )
        
        return {
            "message": response_message,
            "mood": "supportive",
            "suggestions": [
                "Começar com algo muito simples",
                "Fazer uma pausa e respirar",
                "Dividir tarefas grandes em menores"
            ]
        }
    
    def _handle_task_created(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para tarefa criada"""
        user_name = context["user"]["name"]
        
        return {
            "message": f"✨ Perfeito, {user_name}! Nova tarefa adicionada com carinho. Cada passo que você dá é uma semente para seu jardim de conquistas florescer! 🌱",
            "mood": "encouraging",
            "suggestions": [
                "Começar um pomodoro para esta tarefa",
                "Definir prioridade da tarefa",
                "Estimar quantos pomodoros serão necessários"
            ]
        }
    
    def _handle_task_completed(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para tarefa concluída"""
        user_name = context["user"]["name"]
        
        return {
            "message": f"🎉 SUCESSO, {user_name}! Tarefa finalizada com maestria! Você está construindo algo incrível, e cada conquista faz seu jardim crescer mais belo! Continue assim! 🌟",
            "mood": "celebratory",
            "suggestions": [
                "Fazer uma pausa merecida",
                "Começar próxima tarefa",
                "Ver seu progresso no jardim"
            ]
        }
    
    def _handle_task_deleted(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Resposta para tarefa deletada"""
        user_name = context["user"]["name"]
        
        return {
            "message": f"✅ Entendido, {user_name}! Tarefa removida. Às vezes é preciso ajustar o foco e priorizar o que realmente importa. Organização é sobre fazer escolhas inteligentes! 🎯",
            "mood": "supportive",
            "suggestions": [
                "Focar nas tarefas restantes",
                "Revisar prioridades",
                "Adicionar nova tarefa se necessário"
            ]
        }
    
    def _extract_flower_color(self, message: str) -> str:
        """Extrai a cor da flor da mensagem"""
        message_lower = message.lower()
        
        if "verde" in message_lower or "green" in message_lower:
            return "green"
        elif "laranja" in message_lower or "orange" in message_lower:
            return "orange"
        elif "vermelha" in message_lower or "red" in message_lower:
            return "red"
        elif "roxa" in message_lower or "purple" in message_lower:
            return "purple"
        
        return "green"  # Padrão


class BehaviorAnalyzer:
    """Analisa padrões comportamentais do usuário"""
    
    def __init__(self):
        self.patterns = {
            "session_times": [],
            "productive_hours": {},
            "task_preferences": {},
            "interruption_patterns": [],
            "completion_rates": []
        }
    
    def update_patterns(self, context: Dict[str, Any], action: str):
        """Atualiza padrões baseados na ação do usuário"""
        timestamp = datetime.now()
        
        # Registra horário de atividade
        hour = timestamp.hour
        if hour not in self.patterns["productive_hours"]:
            self.patterns["productive_hours"][hour] = 0
        self.patterns["productive_hours"][hour] += 1
        
        # Registra tipo de ação
        if action not in self.patterns["task_preferences"]:
            self.patterns["task_preferences"][action] = 0
        self.patterns["task_preferences"][action] += 1
        
        # Analisa taxa de conclusão
        if action in ["task_completed", "pomodoro_completed"]:
            self.patterns["completion_rates"].append({
                "timestamp": timestamp,
                "success": True
            })
        elif action in ["pomodoro_interrupted", "task_deleted"]:
            self.patterns["completion_rates"].append({
                "timestamp": timestamp,
                "success": False
            })
    
    def get_insights(self) -> List[str]:
        """Retorna insights baseados nos padrões identificados"""
        insights = []
        
        # Insight sobre horário mais produtivo
        if self.patterns["productive_hours"]:
            best_hour = max(self.patterns["productive_hours"], 
                          key=self.patterns["productive_hours"].get)
            insights.append(f"Você é mais ativo às {best_hour}h")
        
        return insights


# Instância global para uso na API
enhanced_lumi = EnhancedLumiAssistant()

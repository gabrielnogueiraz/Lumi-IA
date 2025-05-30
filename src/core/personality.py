#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Personality Module for Lumi Assistant

Handles personality traits, emotional responses, and conversation style
"""

import random
from datetime import datetime


class Personality:
    """
    Manages Lumi's personality traits and response styles
    """

    def __init__(self):
        """Initialize personality system"""
        self.personality_traits = {
            "emotional_state": "enthusiastic",  # enthusiastic, supportive, focused, celebratory
            "energy_level": 0.8,  # 0.0 to 1.0
            "conversation_style": "friendly_professional",
            "humor_level": 0.6,  # Sutil, não exagerado
            "motivation_mode": "encouraging",
        }

        # Conversation memory and context
        self.conversation_memory = []
        self.user_context = {
            "current_focus": None,
            "productivity_patterns": [],
            "preferences": {},
            "interaction_count": 0,
            "last_task_added": None,
            "mood_indicators": [],
        }

        # Response cache
        self.response_cache = {}

    def get_personality_response_style(self, action_type, success=True):
        """
        Generate response style based on Lumi's personality
        """
        styles = {
            "task_added": {
                True: [
                    "✨ Perfeito! Adicionei '{}' às suas tarefas. Você está construindo algo incrível!",
                    "🎯 Ótimo! '{}' está na sua lista agora. Vamos transformar isso em realidade!",
                    "⚡ Excelente! Acabei de incluir '{}'. Cada passo conta para o seu sucesso!",
                    "🌟 Pronto! '{}' adicionada com carinho. Você está no caminho certo!",
                    "🚀 Fantástico! '{}' já está na sua agenda produtiva. Bora conquistar!",
                ],
                False: [
                    "😅 Ops! Tive um pequeno problema para adicionar essa tarefa. Pode tentar novamente?",
                    "🤔 Hmm, algo não funcionou como esperado. Vamos tentar de novo?",
                    "💡 Parece que preciso de um pouco mais de informação. Pode reformular?",
                ],
            },
            "tasks_listed": {
                True: [
                    "📋 Aqui estão suas tarefas! Cada uma é um passo rumo ao seu objetivo:",
                    "✨ Sua lista produtiva está aqui! Qual vai ser a próxima conquista?",
                    "🎯 Olha só sua organização! Estas são suas missões atuais:",
                    "⚡ Suas tarefas estão aqui, prontas para serem conquistadas!",
                    "🌟 Sua agenda produtiva! Cada item é uma oportunidade de crescimento:",
                ],
                False: [
                    "🎉 Que maravilha! Sua lista está vazia - significa que você está em dia!",
                    "✨ Nenhuma tarefa pendente! Momento perfeito para relaxar ou planejar algo novo!",
                    "🌟 Lista limpa! Você está mandando muito bem na organização!",
                ],
            },
            "task_completed": {
                True: [
                    "🎉 SUCESSO! '{}' foi finalizada! Você está arrasando!",
                    "⭐ Parabéns! '{}' concluída com maestria! Continue assim!",
                    "🏆 Excelente! Mais uma conquista: '{}' finalizada!",
                    "✨ Incrível! '{}' completada! Cada vitória te leva mais longe!",
                    "🚀 Fantástico! '{}' foi um sucesso! Você é imparável!",
                ],
                False: [
                    "🤔 Não consegui encontrar essa tarefa. Quer verificar o nome exato?",
                    "💡 Hmm, essa tarefa não está na sua lista. Pode conferir para mim?",
                ],
            },
            "task_removed": {
                True: [
                    "✅ Pronto! '{}' foi removida. Às vezes é preciso ajustar o foco!",
                    "🔄 '{}' saiu da lista. Organização é sobre priorizar!",
                    "✨ '{}' removida com sucesso! Foco no que realmente importa!",
                    "🎯 Feito! '{}' não está mais na sua lista. Excelente gestão de prioridades!",
                ],
                False: [
                    "🤔 Não encontrei essa tarefa para remover. Pode verificar o nome?",
                    "💡 Essa tarefa não está na sua lista atual. Quer ver o que tem disponível?",
                ],
            },
        }

        if success:
            return random.choice(
                styles.get(action_type, {}).get(
                    True, ["✨ Operação realizada com sucesso!"]
                )
            )
        else:
            return random.choice(
                styles.get(action_type, {}).get(
                    False, ["Algo não funcionou como esperado."]
                )
            )

    def analyze_context_and_mood(self, message):
        """
        Analyze context and mood of the message to adapt response
        """
        message_lower = message.lower()

        # Urgency indicators
        urgency_indicators = ["urgente", "rápido", "importante", "prioridade", "hoje"]
        urgency_level = sum(1 for word in urgency_indicators if word in message_lower)

        # Emotional indicators
        stress_indicators = [
            "estressado",
            "cansado",
            "difícil",
            "complicado",
            "problema",
        ]
        motivation_indicators = ["motivado", "animado", "pronto", "vamos", "conseguir"]

        mood = "neutral"
        if any(word in message_lower for word in stress_indicators):
            mood = "stressed"
        elif any(word in message_lower for word in motivation_indicators):
            mood = "motivated"

        # Update user context
        self.user_context["mood_indicators"].append(
            {"timestamp": datetime.now(), "mood": mood, "urgency": urgency_level}
        )

        # Keep only last 10 indicators
        if len(self.user_context["mood_indicators"]) > 10:
            self.user_context["mood_indicators"] = self.user_context["mood_indicators"][
                -10:
            ]

        return {
            "mood": mood,
            "urgency_level": urgency_level,
            "message_length": len(message),
            "politeness_level": (
                1
                if any(
                    word in message_lower
                    for word in ["por favor", "obrigado", "obrigada"]
                )
                else 0
            ),
        }

    def get_casual_response(self, message_lower):
        """
        Responses for casual and social interactions
        """
        if any(word in message_lower for word in ["oi", "olá", "hello", "hi"]):
            responses = [
                "✨ Oi! Como posso turbinar sua produtividade hoje?",
                "🌟 Olá! Pronta para conquistar suas metas?",
                "⚡ Oi! Que bom te ver! Vamos organizar o seu dia?",
                "🎯 Olá! Estou aqui para te ajudar a ser ainda mais produtivo(a)!",
            ]
            return random.choice(responses)

        elif any(word in message_lower for word in ["como vai", "tudo bem", "como está"]):
            responses = [
                "🌟 Estou ótima e super animada para te ajudar! E você, como está?",
                "⚡ Indo muito bem, obrigada! Pronta para mais um dia produtivo?",
                "✨ Estou excelente! Qual é o plano para hoje?",
                "🎯 Muito bem! Vamos focar no que realmente importa hoje?",
            ]
            return random.choice(responses)

        elif any(word in message_lower for word in ["obrigad", "thanks", "valeu"]):
            responses = [
                "🌟 De nada! Estou sempre aqui para te ajudar!",
                "✨ Foi um prazer! Vamos continuar conquistando metas?",
                "⚡ Imagina! Juntos somos mais produtivos!",
                "🎯 Sempre às ordens! O que mais posso fazer por você?",
            ]
            return random.choice(responses)

        elif any(word in message_lower for word in ["tchau", "bye", "até logo"]):
            responses = [
                "✨ Até logo! Continue sendo incrível!",
                "🌟 Tchau! Que sua produtividade seja ainda maior amanhã!",
                "⚡ Até mais! Lembre-se: pequenos passos, grandes conquistas!",
                "🎯 Tchau! Estarei aqui quando precisar de mim!",
            ]
            return random.choice(responses)

        return "✨ Estou aqui para te ajudar! Como posso tornar seu dia mais produtivo?"

    def update_conversation_memory(self, message, context):
        """
        Update conversation memory with new interaction
        """
        self.conversation_memory.append(
            {"timestamp": datetime.now(), "message": message, "context": context}
        )

        # Keep only last 20 interactions in memory
        if len(self.conversation_memory) > 20:
            self.conversation_memory = self.conversation_memory[-20:]

        # Increment interaction count
        self.user_context["interaction_count"] += 1

    def get_user_stats(self):
        """
        Return humanized user statistics
        """
        return {
            "interaction_count": self.user_context["interaction_count"],
            "mood_trend": self._analyze_mood_trend(),
            "productivity_level": self._calculate_productivity_level(),
        }

    def _analyze_mood_trend(self):
        """
        Analyze mood trend based on recent interactions
        """
        if len(self.user_context["mood_indicators"]) < 3:
            return "neutral"

        recent_moods = [item["mood"] for item in self.user_context["mood_indicators"][-5:]]
        stressed_count = recent_moods.count("stressed")
        motivated_count = recent_moods.count("motivated")

        if stressed_count > motivated_count:
            return "stressed"
        elif motivated_count > stressed_count:
            return "motivated"
        else:
            return "balanced"

    def _calculate_productivity_level(self):
        """
        Calculate productivity level based on usage patterns
        """
        # Simple calculation based on interaction frequency
        if self.user_context["interaction_count"] > 20:
            return "high"
        elif self.user_context["interaction_count"] > 10:
            return "medium"
        else:
            return "building"

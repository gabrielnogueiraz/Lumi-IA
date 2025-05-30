#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mood Analyzer Module for Lumi Assistant

Analyzes user mood and context to provide personalized responses
"""

from datetime import datetime


class MoodAnalyzer:
    """
    Analyzes user mood and emotional context for personalized interactions
    """

    def __init__(self):
        """Initialize mood analyzer"""
        self.mood_history = []

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
            "estressado", "cansado", "difícil", "complicado", "problema",
        ]
        motivation_indicators = ["motivado", "animado", "pronto", "vamos", "conseguir"]

        mood = "neutral"
        if any(word in message_lower for word in stress_indicators):
            mood = "stressed"
        elif any(word in message_lower for word in motivation_indicators):
            mood = "motivated"

        # Store mood history
        mood_entry = {
            "timestamp": datetime.now(),
            "mood": mood,
            "urgency": urgency_level,
            "message_length": len(message)
        }
        
        self.mood_history.append(mood_entry)

        # Keep only last 10 mood entries
        if len(self.mood_history) > 10:
            self.mood_history = self.mood_history[-10:]

        return {
            "mood": mood,
            "urgency_level": urgency_level,
            "message_length": len(message),
            "politeness_level": self._calculate_politeness(message_lower),
            "mood_trend": self._analyze_mood_trend(),
        }

    def _calculate_politeness(self, message_lower):
        """Calculate politeness level from message"""
        politeness_words = ["por favor", "obrigado", "obrigada", "please", "thanks"]
        return 1 if any(word in message_lower for word in politeness_words) else 0

    def _analyze_mood_trend(self):
        """Analyze mood trend based on recent interactions"""
        if len(self.mood_history) < 3:
            return "neutral"

        recent_moods = [entry["mood"] for entry in self.mood_history[-5:]]
        stressed_count = recent_moods.count("stressed")
        motivated_count = recent_moods.count("motivated")

        if stressed_count > motivated_count:
            return "stressed_trend"
        elif motivated_count > stressed_count:
            return "motivated_trend"
        else:
            return "balanced"

    def get_mood_based_suggestion(self, context):
        """Get mood-based suggestions for user interaction"""
        mood = context.get("mood", "neutral")
        urgency = context.get("urgency_level", 0)

        if mood == "stressed":
            return "\n\n💪 Respirar fundo e focar numa tarefa de cada vez. Você consegue!"
        elif urgency > 0:
            return "\n\n⚡ Detectei que é importante! Que tal começar por essa?"
        elif mood == "motivated":
            return "\n\n🚀 Adorei sua energia! Vamos canalizar isso para ser super produtivo(a)!"
        else:
            return "\n\n✨ Você está no caminho certo! Cada pequeno passo é uma vitória!"

    def get_current_mood_state(self):
        """Get current mood state summary"""
        if not self.mood_history:
            return {"current_mood": "neutral", "trend": "stable", "energy": "medium"}

        latest = self.mood_history[-1]
        trend = self._analyze_mood_trend()
        
        return {
            "current_mood": latest["mood"],
            "trend": trend,
            "energy": "high" if latest["mood"] == "motivated" else "medium" if latest["mood"] == "neutral" else "low"
        }

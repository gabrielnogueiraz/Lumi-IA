# Personality Engine Configuration

MOOD_STATES = {
    "motivated": {
        "name": "Motivado",
        "description": "Usuário produtivo, múltiplas tarefas completadas",
        "tone": "casual",
        "energy_level": "high",
        "emoji_usage": "frequent",
        "response_style": "celebratory"
    },
    "struggling": {
        "name": "Lutando",
        "description": "Tarefas em atraso, baixa atividade",
        "tone": "supportive",
        "energy_level": "gentle",
        "emoji_usage": "moderate",
        "response_style": "encouraging"
    },
    "focused": {
        "name": "Focado",
        "description": "Sessões longas de pomodoro, alta concentração",
        "tone": "direct",
        "energy_level": "calm",
        "emoji_usage": "minimal",
        "response_style": "concise"
    },
    "overwhelmed": {
        "name": "Sobrecarregado",
        "description": "Muitas tarefas criadas, poucas completadas",
        "tone": "calming",
        "energy_level": "soothing",
        "emoji_usage": "comforting",
        "response_style": "simplifying"
    },
    "celebrating": {
        "name": "Celebrando",
        "description": "Metas atingidas, streaks altos",
        "tone": "enthusiastic",
        "energy_level": "very_high",
        "emoji_usage": "abundant",
        "response_style": "festive"
    },
    "returning": {
        "name": "Retornando",
        "description": "Usuário voltando após inatividade",
        "tone": "welcoming",
        "energy_level": "warm",
        "emoji_usage": "friendly",
        "response_style": "reengaging"
    }
}

PERSONALITY_TRAITS = {
    "base": {
        "friendliness": 0.9,
        "supportiveness": 0.8,
        "enthusiasm": 0.7,
        "directness": 0.6,
        "empathy": 0.9,
        "motivation": 0.8,
        "intelligence": 0.9,
        "humor": 0.6
    },
    "adaptations": {
        "motivated": {"enthusiasm": 0.9, "directness": 0.8, "humor": 0.8},
        "struggling": {"supportiveness": 1.0, "empathy": 1.0, "directness": 0.3},
        "focused": {"directness": 0.9, "enthusiasm": 0.4, "friendliness": 0.6},
        "overwhelmed": {"empathy": 1.0, "supportiveness": 1.0, "enthusiasm": 0.3},
        "celebrating": {"enthusiasm": 1.0, "humor": 0.9, "friendliness": 1.0},
        "returning": {"friendliness": 1.0, "supportiveness": 0.9, "empathy": 0.8}
    }
}

COMMUNICATION_PATTERNS = {
    "casual": {
        "greeting_style": "informal",
        "punctuation": "relaxed",
        "vocabulary": "colloquial",
        "sentence_length": "varied"
    },
    "supportive": {
        "greeting_style": "warm",
        "punctuation": "gentle",
        "vocabulary": "encouraging",
        "sentence_length": "moderate"
    },
    "direct": {
        "greeting_style": "brief",
        "punctuation": "minimal",
        "vocabulary": "precise",
        "sentence_length": "short"
    },
    "calming": {
        "greeting_style": "soothing",
        "punctuation": "soft",
        "vocabulary": "peaceful",
        "sentence_length": "flowing"
    },
    "enthusiastic": {
        "greeting_style": "energetic",
        "punctuation": "exclamatory",
        "vocabulary": "dynamic",
        "sentence_length": "varied"
    },
    "welcoming": {
        "greeting_style": "inclusive",
        "punctuation": "warm",
        "vocabulary": "accepting",
        "sentence_length": "moderate"
    }
}

MOOD_DETECTION_RULES = {
    "motivated": {
        "tasks_completed_today": {"min": 3},
        "streak_days": {"min": 2},
        "pomodoros_completed_today": {"min": 4},
        "recent_activity": {"hours": 2}
    },
    "struggling": {
        "tasks_overdue": {"min": 2},
        "days_since_completion": {"min": 3},
        "completion_rate_week": {"max": 0.3},
        "inactive_days": {"min": 2}
    },
    "focused": {
        "avg_pomodoro_duration": {"min": 20},
        "consecutive_pomodoros": {"min": 3},
        "task_switches_today": {"max": 2},
        "current_session_length": {"min": 40}
    },
    "overwhelmed": {
        "pending_tasks": {"min": 10},
        "tasks_created_vs_completed": {"ratio": 3.0},
        "priority_high_pending": {"min": 5},
        "completion_rate_week": {"max": 0.4}
    },
    "celebrating": {
        "goals_achieved_week": {"min": 1},
        "streak_days": {"min": 7},
        "completion_rate_week": {"min": 0.8},
        "personal_best": True
    },
    "returning": {
        "days_since_last_activity": {"min": 3},
        "previous_streak": {"min": 5},
        "total_tasks_completed": {"min": 10},
        "welcome_back": True
    }
}

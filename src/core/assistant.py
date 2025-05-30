#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Modular Lumi Assistant

Main assistant class that integrates all modules for a clean, maintainable architecture
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório pai ao path para imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import core modules
try:
    from .ai_engine import AIEngine
    from .personality import Personality
    from .task_handler import TaskHandler
    from .education import Education

    # Import utility modules
    from ..utils.patterns import PatternDetector
    from ..utils.mood_analyzer import MoodAnalyzer
except ImportError:
    # Fallback para imports absolutos
    try:
        from core.ai_engine import AIEngine
        from core.personality import Personality
        from core.task_handler import TaskHandler
        from core.education import Education

        from utils.patterns import PatternDetector
        from utils.mood_analyzer import MoodAnalyzer
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")

        # Definir classes vazias como fallback
        class AIEngine:
            def __init__(self):
                pass

            def call_ai_api(self, messages):
                return "Sistema indisponível"

        class Personality:
            def __init__(self):
                pass

        class TaskHandler:
            def __init__(self, tm, p):
                pass

        class Education:
            def __init__(self):
                pass

        class PatternDetector:
            def __init__(self):
                pass

        class MoodAnalyzer:
            def __init__(self):
                pass


class LumiAssistant:
    """
    LUMI 2.0 - Modular AI Assistant for Productivity
    """

    def __init__(self, task_manager, reports_generator):
        """Initialize modular Lumi"""
        print("🚀 Inicializando Lumi 2.0 Modular...")

        # Core dependencies
        self.task_manager = task_manager
        self.reports_generator = reports_generator

        # Initialize all modules
        self._initialize_modules()

        print("✅ Lumi 2.0 Modular inicializada com sucesso!")

    def _initialize_modules(self):
        """Initialize all modular components"""
        try:
            # Core modules
            self.ai_engine = AIEngine()
            self.personality = Personality()
            self.education = Education()

            # Utility modules
            self.pattern_detector = PatternDetector()
            self.mood_analyzer = MoodAnalyzer()

            # Task handler (needs personality and ai_engine)
            self.task_handler = TaskHandler(self.task_manager, self.personality)

            print("✅ Todos os módulos carregados com sucesso!")

        except Exception as e:
            print(f"⚠️ Erro ao inicializar módulos: {e}")
            # Continue with basic functionality
            self.ai_engine = None

    def process_message(self, message):
        """Process message with modular intelligence"""
        try:
            # Update conversation memory and context
            context = self.mood_analyzer.analyze_context_and_mood(message)
            self.personality.update_conversation_memory(message, context)

            # Detect action using pattern detector
            action = self.pattern_detector.detect_action(message)

            # Check if it's an educational question FIRST
            if self.education.detect_educational_intent(message):
                return self.education.process_educational_query(message)

            # Process based on detected action
            if action == "adicionar":
                return self.task_handler.process_add_task(message)
            elif action == "listar":
                return self.task_handler.process_list_tasks(message)
            elif action == "concluir":
                return self.task_handler.process_complete_task(message)
            elif action == "remover":
                return self.task_handler.process_remove_task(message)
            elif action == "relatório":
                return self._process_generate_report(message)
            elif action == "editar":
                return self.task_handler.process_edit_task(message)
            elif action in ["saudacao", "gratidao"]:
                return self._process_casual_interaction(message)
            else:
                return self._process_general_query(message)

        except Exception as e:
            return f"🤖 Ops! Algo inesperado aconteceu: {str(e)}"

    def _process_casual_interaction(self, message):
        """Process casual interactions"""
        return self.personality.get_casual_response(message.lower())

    def _process_general_query(self, message):
        """Process general queries using AI"""
        try:
            if self.pattern_detector.detect_casual_patterns(message):
                return self.personality.get_casual_response(message.lower())

            if self.ai_engine:
                return self.ai_engine.generate_general_response(message)
            else:
                return "✨ Estou aqui para te ajudar com suas tarefas!"

        except Exception as e:
            return "✨ Como posso te ajudar com suas tarefas hoje?"

    def _process_generate_report(self, message):
        """Generate report with AI enhancement"""
        try:
            report = self.reports_generator.gerar_relatório(message)

            if self.ai_engine:
                intro = self.ai_engine.generate_task_response(
                    "gerando relatório", message
                )
                return f"{intro}\n\n{report}"
            else:
                return f"📊 Aqui está seu relatório:\n\n{report}"

        except Exception as e:
            return f"😅 Erro ao gerar relatório: {str(e)}"

    # Compatibility methods
    def add_task(self, title):
        return self.task_manager.add_task(title)

    def list_tasks(self):
        return self.task_manager.list_tasks()

    def complete_task(self, identifier):
        return self.task_manager.complete_task(identifier)

    def remove_task(self, identifier):
        return self.task_manager.remove_task(identifier)

    def get_task_count(self):
        return self.task_manager.get_task_count()

    def get_user_stats(self):
        return {
            "interaction_count": getattr(self.personality, "user_context", {}).get(
                "interaction_count", 0
            ),
            "ai_engine_active": self.ai_engine is not None,
            "modules_loaded": self._get_module_status(),
        }

    def _get_module_status(self):
        """Get status of all loaded modules"""
        return {
            "ai_engine": self.ai_engine is not None,
            "personality": self.personality is not None,
            "education": self.education is not None,
            "task_handler": self.task_handler is not None,
            "pattern_detector": self.pattern_detector is not None,
            "mood_analyzer": self.mood_analyzer is not None,
        }

    # Legacy method support
    def _detect_educational_intent(self, message):
        return self.education.detect_educational_intent(message)

    def _process_educational_query(self, message):
        return self.education.process_educational_query(message)

    def _get_personality_response_style(self, action_type, success=True):
        return self.personality.get_personality_response_style(action_type, success)

    def _detect_action(self, message):
        return self.pattern_detector.detect_action(message)

    def _analyze_context_and_mood(self, message):
        return self.mood_analyzer.analyze_context_and_mood(message)

    def _call_ai_api(self, messages):
        if self.ai_engine:
            return self.ai_engine.call_ai_api(messages)
        else:
            return "AI engine não disponível."

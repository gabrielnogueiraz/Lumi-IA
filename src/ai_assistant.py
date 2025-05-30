#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LUMI 2.0 - AI Assistant for Productivity

Clean wrapper that uses modular architecture internally while maintaining
full backward compatibility with the original API.
"""

import os
import sys
from datetime import datetime

# Adiciona o diretório atual ao path para imports absolutos
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the modular assistant usando caminho absoluto
try:
    from core.assistant import LumiAssistant as ModularLumiAssistant
except ImportError:
    # Fallback para imports relativos se absolutos falharem
    try:
        from .core.assistant import LumiAssistant as ModularLumiAssistant
    except ImportError:
        print("❌ Erro: Não foi possível importar ModularLumiAssistant")
        print("🔄 Usando implementação de fallback...")
        ModularLumiAssistant = None


class LumiAssistant:
    """
    LUMI 2.0 - AI Assistant for Productivity

    Clean wrapper that uses modular architecture internally while maintaining
    full backward compatibility with the original API.

    Features:
    - Google Gemini AI integration for all functionalities
    - Modular, maintainable codebase
    - Advanced personality and mood analysis
    - Educational query processing
    - Task management with AI-enhanced responses
    - Full backward compatibility
    """

    def __init__(self, task_manager, reports_generator):
        """
        Initialize Lumi with modular architecture

        Args:
            task_manager: Task management instance
            reports_generator: Reports generation instance
        """
        print("🚀 Inicializando Lumi 2.0...")

        # Store references for direct access
        self.task_manager = task_manager
        self.reports_generator = reports_generator

        # Try to initialize modular assistant
        if ModularLumiAssistant:
            try:
                print("🔧 Carregando arquitetura modular...")
                self._modular_assistant = ModularLumiAssistant(
                    task_manager, reports_generator
                )
                self._use_modular = True
                print("✅ Lumi 2.0 inicializada com arquitetura modular!")
            except Exception as e:
                print(f"⚠️ Erro ao carregar módulos: {e}")
                print("🔄 Usando implementação de fallback...")
                self._use_modular = False
                self._init_fallback()
        else:
            print("🔄 Módulos não disponíveis, usando implementação de fallback...")
            self._use_modular = False
            self._init_fallback()

    def _init_fallback(self):
        """Initialize fallback functionality if modular system fails"""
        print("🔄 Inicializando sistema de fallback...")
        self._modular_assistant = None

        # Importar e usar o sistema legado como fallback
        try:
            # Importa a implementação legada
            import importlib.util

            backup_path = os.path.join(
                os.path.dirname(__file__), "ai_assistant_legacy_backup.py"
            )

            if os.path.exists(backup_path):
                spec = importlib.util.spec_from_file_location(
                    "legacy_lumi", backup_path
                )
                legacy_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(legacy_module)

                # Usa a classe legada
                self._legacy_assistant = legacy_module.LumiAssistant(
                    task_manager, reports_generator
                )
                print("✅ Sistema de fallback inicializado com sucesso!")
            else:
                print("❌ Sistema de fallback não encontrado!")
                self._legacy_assistant = None

        except Exception as e:
            print(f"❌ Erro ao inicializar fallback: {e}")
            self._legacy_assistant = None

    def process_message(self, message):
        """
        Process message using modular architecture or fallback

        Args:
            message (str): User message to process

        Returns:
            str: AI-generated response
        """
        if self._use_modular and self._modular_assistant:
            try:
                return self._modular_assistant.process_message(message)
            except Exception as e:
                print(f"⚠️ Erro no sistema modular: {e}")
                print("🔄 Tentando fallback...")

        # Usa sistema de fallback
        if hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            try:
                return self._legacy_assistant.process_message(message)
            except Exception as e:
                print(f"⚠️ Erro no sistema de fallback: {e}")

        # Resposta de emergência
        return "🤖 Sistema temporariamente indisponível. Como posso ajudá-lo com suas tarefas?"

    # ========== COMPATIBILITY METHODS ==========
    # These methods delegate to the appropriate system

    def add_task(self, title):
        """Add a task using available system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant.add_task(title)
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self.task_manager.add_task(title)
        else:
            return self.task_manager.add_task(title)

    def list_tasks(self):
        """List tasks using available system"""
        return self.task_manager.list_tasks()

    def complete_task(self, identifier):
        """Complete a task using available system"""
        return self.task_manager.complete_task(identifier)

    def remove_task(self, identifier):
        """Remove a task using available system"""
        return self.task_manager.remove_task(identifier)

    def get_task_count(self):
        """Get task statistics using available system"""
        return self.task_manager.get_task_count()

    def get_user_stats(self):
        """Get enhanced user statistics from available system"""
        if self._use_modular and self._modular_assistant:
            try:
                return self._modular_assistant.get_user_stats()
            except:
                pass

        # Fallback stats
        return {
            "interaction_count": 0,
            "mood_state": {"current_mood": "neutral", "trend": "stable"},
            "ai_engine_active": False,
            "system_mode": "fallback" if not self._use_modular else "modular",
        }

    # ========== LEGACY METHOD DELEGATION ==========
    # These methods ensure compatibility with any legacy code

    def _detect_educational_intent(self, message):
        """Delegate to appropriate system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant._detect_educational_intent(message)
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self._legacy_assistant._detect_educational_intent(message)
        return False

    def _process_educational_query(self, message):
        """Delegate to appropriate system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant._process_educational_query(message)
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self._legacy_assistant._process_educational_query(message)
        return "Funcionalidade educacional temporariamente indisponível."

    def _get_personality_response_style(self, action_type, success=True):
        """Delegate to appropriate system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant._get_personality_response_style(
                action_type, success
            )
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self._legacy_assistant._get_personality_response_style(
                action_type, success
            )
        return "✨ Operação realizada!" if success else "Algo deu errado."

    def _detect_action(self, message):
        """Delegate to appropriate system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant._detect_action(message)
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self._legacy_assistant._detect_action(message)
        return "consulta"

    def _analyze_context_and_mood(self, message):
        """Delegate to appropriate system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant._analyze_context_and_mood(message)
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self._legacy_assistant._analyze_context_and_mood(message)
        return {"mood": "neutral", "urgency_level": 0}

    def _call_ai_api(self, messages):
        """Delegate to appropriate system"""
        if self._use_modular and self._modular_assistant:
            return self._modular_assistant._call_ai_api(messages)
        elif hasattr(self, "_legacy_assistant") and self._legacy_assistant:
            return self._legacy_assistant._call_ai_api(messages)
        return "Sistema de IA temporariamente indisponível."

    def __str__(self):
        """String representation"""
        mode = "Modular" if self._use_modular else "Fallback"
        return f"Lumi AI Assistant 2.0 ({mode} Mode)"

    def __repr__(self):
        """Developer representation"""
        return f"LumiAssistant(modular={self._use_modular})"


# ========== FACTORY FUNCTIONS FOR EASY MIGRATION ==========


def create_lumi_assistant(task_manager, reports_generator):
    """
    Factory function to create a Lumi assistant instance

    Args:
        task_manager: Task management instance
        reports_generator: Reports generation instance

    Returns:
        LumiAssistant: Configured Lumi assistant instance
    """
    return LumiAssistant(task_manager, reports_generator)


if __name__ == "__main__":
    print("🤖 Lumi AI Assistant 2.0 - Hybrid Architecture")
    print("Sistema modular com fallback automático para máxima compatibilidade.")

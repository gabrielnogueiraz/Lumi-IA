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
                spec.loader.exec_module(legacy_module)                # Usa a classe legada
                self._legacy_assistant = legacy_module.LumiAssistant(
                    self.task_manager, self.reports_generator
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

    def process_request(self, request_data):
        """
        Processa request estruturado seguindo nova especificação da API

        Args:
            request_data (dict): Dados da requisição com userId, message, context, action

        Returns:
            dict: Resposta estruturada com response, mood, suggestions, actions, insights
        """
        try:
            user_id = request_data.get("userId")
            message = request_data.get("message", "")
            context = request_data.get("context", {})
            action = request_data.get("action", "chat")

            # Processa a mensagem usando o sistema existente
            response_text = self.process_message(message)

            # Analisa o contexto para gerar dados adicionais
            mood = self._analyze_user_mood(message, context)
            suggestions = self._generate_suggestions(message, context)
            actions = self._extract_actions(message, response_text)
            insights = self._generate_insights(user_id, context)

            return {
                "response": response_text,
                "mood": mood,
                "suggestions": suggestions,
                "actions": actions,
                "insights": insights,
                "garden_status": self._get_garden_status(user_id),
                "user_stats": self.get_user_stats(),
            }

        except Exception as e:
            print(f"⚠️ Erro ao processar request: {e}")
            return {
                "response": "🤖 Desculpe, encontrei um problema técnico. Como posso ajudá-lo?",
                "mood": "understanding",
                "suggestions": ["Tente reformular sua pergunta", "Verifique sua conexão"],                "actions": [],
                "insights": [],
            }

    def _analyze_user_mood(self, message, context):
        """Analisa o humor do usuário baseado na mensagem e contexto específico do PomodoroTasks"""
        message_lower = message.lower()
        
        # Contexto específico do PomodoroTasks
        task_context = context.get('tasks', [])
        garden_context = context.get('garden_status', {})
        completed_tasks = len([t for t in task_context if t.get('completed', False)])
        total_flowers = garden_context.get('total_flowers', 0)

        # Indicadores de produtividade e conquistas
        if any(word in message_lower for word in ["completei", "terminei", "finalizei", "consegui fazer"]):
            return "accomplished"
            
        # Indicadores positivos relacionados ao jardim/pomodoro
        if any(word in message_lower for word in ["jardim", "flores", "pomodoro", "produtivo", "foco"]):
            if total_flowers > 10:
                return "proud"
            elif total_flowers > 0:
                return "motivated"
                
        # Indicadores positivos gerais
        if any(word in message_lower for word in ["obrigado", "ótimo", "excelente", "perfeito", "consegui"]):
            return "grateful"

        # Indicadores de procrastinação/desmotivação
        if any(word in message_lower for word in ["procrastinando", "sem foco", "disperso", "difícil concentrar"]):
            return "unmotivated"
            
        # Indicadores relacionados a tarefas
        if any(word in message_lower for word in ["tarefa", "fazer", "preciso"]):
            if completed_tasks > len(task_context) * 0.7:  # Mais de 70% completas
                return "accomplished"
            elif len(task_context) > 10:  # Muitas tarefas pendentes
                return "overwhelmed"
            else:
                return "focused"

        # Indicadores de stress/urgência
        if any(word in message_lower for word in ["urgente", "rápido", "pressa", "atrasado", "stress"]):
            return "stressed"

        # Indicadores de confusão sobre o sistema
        if any(word in message_lower for word in ["não entendo", "confuso", "ajuda", "como funciona"]):
            if "pomodoro" in message_lower or "jardim" in message_lower:
                return "curious"
            return "confused"

        # Indicadores motivacionais
        if any(word in message_lower for word in ["vamos", "começar", "foco", "produtivo", "meta"]):
            return "motivated"
            
        # Indicadores de satisfação com progresso
        if any(word in message_lower for word in ["progresso", "melhorando", "evoluindo"]):
            return "satisfied"

        return "neutral"

    def _generate_suggestions(self, message, context):
        """Gera sugestões baseadas na mensagem e contexto específico do PomodoroTasks"""
        suggestions = []
        message_lower = message.lower()
        
        # Contexto específico do PomodoroTasks
        task_context = context.get('tasks', [])
        garden_context = context.get('garden_status', {})
        completed_tasks = len([t for t in task_context if t.get('completed', False)])
        total_flowers = garden_context.get('total_flowers', 0)

        # Sugestões baseadas no jardim virtual
        if any(word in message_lower for word in ["jardim", "flores"]):
            if total_flowers == 0:
                suggestions.extend([
                    "🌱 Complete sua primeira tarefa para ganhar uma flor verde!",
                    "📝 Adicione algumas tarefas para começar seu jardim",
                    "⏰ Use a técnica pomodoro para focar nas tarefas"
                ])
            elif total_flowers < 5:
                suggestions.extend([
                    "🌻 Continue completando tarefas para fazer seu jardim crescer!",
                    "🎯 Complete 3 tarefas seguidas para ganhar uma flor laranja",
                    "💪 Mantenha a consistência para desbloquear flores especiais"
                ])
            else:
                suggestions.extend([
                    "🌺 Seu jardim está florescendo! Continue assim!",
                    "🏆 Tente completar 10 tarefas para ganhar flores roxas",
                    "📊 Verifique suas estatísticas de progresso"
                ])

        # Sugestões para tarefas baseadas no contexto atual
        if any(word in message_lower for word in ["tarefa", "task", "fazer"]):
            if len(task_context) == 0:
                suggestions.extend([
                    "📝 Comece adicionando sua primeira tarefa",
                    "🎯 Defina 3 metas principais para hoje",
                    "⭐ Priorize tarefas por importância e urgência"
                ])
            elif completed_tasks == 0:
                suggestions.extend([
                    "🚀 Escolha a tarefa mais fácil para começar",
                    "⏰ Configure um pomodoro de 25 minutos",
                    "🎵 Prepare um ambiente livre de distrações"
                ])
            else:
                suggestions.extend([
                    f"✨ Você já completou {completed_tasks} tarefas hoje!",
                    "🌸 Cada tarefa completa adiciona flores ao seu jardim",
                    "📈 Continue o ritmo para manter seu streak"
                ])

        # Sugestões específicas para pomodoro
        if "pomodoro" in message_lower:
            suggestions.extend([
                "🍅 Ciclo ideal: 25min trabalho + 5min pausa",
                "🎯 Escolha uma tarefa específica antes de começar",
                "🔕 Desligue notificações durante o pomodoro",
                "☕ A cada 4 pomodoros, faça uma pausa longa (15-30min)"
            ])

        # Sugestões para produtividade contextual
        if any(word in message_lower for word in ["produtivo", "foco", "concentrar"]):
            current_hour = datetime.now().hour
            if 6 <= current_hour <= 12:
                suggestions.extend([
                    "🌅 Manhã perfeita para tarefas complexas!",
                    "🧠 Aproveite o pico de energia matinal",
                    "📝 Comece pelas tarefas mais importantes"
                ])
            elif 13 <= current_hour <= 18:
                suggestions.extend([
                    "☀️ Tarde ideal para revisões e organização",
                    "🤝 Bom momento para tarefas colaborativas",
                    "📊 Faça uma pausa e avalie seu progresso"
                ])
            else:
                suggestions.extend([
                    "🌙 Período noturno ideal para planejamento",
                    "📋 Organize as tarefas de amanhã",
                    "🧘 Considere atividades mais leves"
                ])

        # Sugestões motivacionais baseadas no humor
        user_mood = self._analyze_user_mood(message, context)
        if user_mood == "overwhelmed":
            suggestions.extend([
                "🎯 Foque em apenas uma tarefa por vez",
                "✂️ Divida tarefas grandes em partes menores",
                "💆 Faça uma pausa para respirar fundo"
            ])
        elif user_mood == "unmotivated":
            suggestions.extend([
                "🌟 Comece com uma tarefa de 5 minutos",
                "🎵 Coloque sua música favorita",
                "🏆 Recompense-se após completar uma tarefa"
            ])

        return suggestions[:4]  # Limita a 4 sugestões mais relevantes

    def _extract_actions(self, message, response):
        """Extrai ações realizadas ou sugeridas com melhor detecção de comandos PomodoroTasks"""
        actions = []
        message_lower = message.lower()

        # Ações de tarefas - detecção mais robusta
        if any(word in message_lower for word in ["adicionar tarefa", "criar tarefa", "nova tarefa", "quero fazer"]):
            actions.append({"type": "task_add", "status": "suggested", "description": "Adicionar nova tarefa"})
        elif any(word in message_lower for word in ["completar", "concluir", "finalizar", "marcar como feito"]):
            actions.append({"type": "task_complete", "status": "suggested", "description": "Marcar tarefa como completa"})
        elif any(word in message_lower for word in ["remover tarefa", "apagar tarefa", "deletar tarefa", "excluir"]):
            actions.append({"type": "task_remove", "status": "suggested", "description": "Remover tarefa"})
        elif any(word in message_lower for word in ["editar tarefa", "modificar tarefa", "alterar tarefa"]):
            actions.append({"type": "task_edit", "status": "suggested", "description": "Editar tarefa existente"})
        elif any(word in message_lower for word in ["listar tarefas", "mostrar tarefas", "ver tarefas", "minhas tarefas"]):
            actions.append({"type": "task_list", "status": "suggested", "description": "Listar tarefas"})

        # Ações de pomodoro - detecção expandida
        if any(word in message_lower for word in ["iniciar pomodoro", "começar pomodoro", "pomodoro agora"]):
            actions.append({"type": "pomodoro_start", "status": "suggested", "description": "Iniciar sessão pomodoro"})
        elif any(word in message_lower for word in ["técnica pomodoro", "como funciona pomodoro", "o que é pomodoro"]):
            actions.append({"type": "pomodoro_explain", "status": "suggested", "description": "Explicar técnica pomodoro"})
        elif "pomodoro" in message_lower:
            actions.append({"type": "pomodoro_suggest", "status": "suggested", "description": "Sugerir uso do pomodoro"})

        # Ações do jardim virtual
        if any(word in message_lower for word in ["jardim", "flores", "como está meu jardim"]):
            actions.append({"type": "garden_check", "status": "suggested", "description": "Verificar status do jardim"})
        elif any(word in message_lower for word in ["ganhar flores", "como ganho flores", "flores funcionam"]):
            actions.append({"type": "garden_explain", "status": "suggested", "description": "Explicar sistema de flores"})

        # Ações de produtividade e foco
        if any(word in message_lower for word in ["preciso focar", "ajuda concentrar", "dicas produtividade"]):
            actions.append({"type": "focus_help", "status": "suggested", "description": "Oferecer dicas de foco"})
        elif any(word in message_lower for word in ["relatório", "progresso", "estatísticas"]):
            actions.append({"type": "stats_show", "status": "suggested", "description": "Mostrar estatísticas"})

        # Ações de configuração e ajuda
        if any(word in message_lower for word in ["como usar", "ajuda", "comandos", "o que você faz"]):
            actions.append({"type": "help_show", "status": "suggested", "description": "Mostrar ajuda e comandos"})

        return actions

    def _generate_insights(self, user_id, context):
        """Gera insights personalizados para o usuário"""
        insights = []

        # Insight baseado no horário
        current_hour = datetime.now().hour
        if 6 <= current_hour <= 12:
            insights.append(
                "🌅 Você está ativo de manhã! Aproveite para tarefas que exigem mais concentração."
            )
        elif 13 <= current_hour <= 18:
            insights.append("☀️ Período da tarde ideal para colaboração e reuniões.")
        elif 19 <= current_hour <= 23:
            insights.append("🌙 Noite perfeita para revisão e planejamento do próximo dia.")        # Insights sobre tarefas (se houver contexto)
        if context.get("task_count", 0) > 5:
            insights.append(
                "📊 Você tem muitas tarefas. Considere priorizar as 3 mais importantes."
            )
        elif context.get("task_count", 0) == 0:
            insights.append("✨ Sua agenda está livre! Que tal definir algumas metas para hoje?")

        return insights[:2]  # Limita a 2 insights

    def _get_garden_status(self, user_id):
        """Retorna status do jardim virtual do usuário com sistema de gamificação"""
        task_stats = self.get_task_count()
        
        # Extrai dados das tarefas
        if isinstance(task_stats, dict):
            total_tasks = task_stats.get('total', 0)
            completed_tasks = task_stats.get('completed', 0)
        else:
            total_tasks = 0
            completed_tasks = 0

        # Sistema de flores baseado em gamificação do PomodoroTasks
        # Flores verdes (tarefas básicas) - 1 para cada tarefa completada
        green_flowers = min(completed_tasks, 20)  # máximo 20 flores verdes
        
        # Flores laranjas (consistência) - 1 para cada 3 tarefas completadas
        orange_flowers = min(completed_tasks // 3, 10)  # máximo 10 flores laranjas
        
        # Flores vermelhas (desafios) - 1 para cada 5 tarefas completadas
        red_flowers = min(completed_tasks // 5, 5)  # máximo 5 flores vermelhas
        
        # Flores roxas (excelência) - flores raras para marcos especiais
        purple_flowers = min(completed_tasks // 10, 3)  # máximo 3 flores roxas
        
        total_flowers = green_flowers + orange_flowers + red_flowers + purple_flowers

        # Mensagens contextuais do jardim virtual
        if total_flowers >= 25:
            message = "🌺 Que jardim ESPETACULAR! Você é um verdadeiro mestre da produtividade!"
        elif total_flowers >= 15:
            message = "🌸 Seu jardim está florescendo magnificamente! Cada flor conta sua história de dedicação!"
        elif total_flowers >= 8:
            message = "🌻 Que lindo jardim você está cultivando! Sua consistência está dando frutos!"
        elif total_flowers >= 3:
            message = "🌱 Suas primeiras flores estão brotando! Continue que logo terá um jardim cheio!"
        elif total_flowers > 0:
            message = "🌿 Vejo as primeiras sementes germinando! Cada tarefa é uma flor em potencial!"
        else:
            message = "🌱 Seu jardim está preparado para florescer! Que tal plantar a primeira semente com uma tarefa?"

        # Breakdown detalhado das flores
        flower_breakdown = []
        if green_flowers > 0:
            flower_breakdown.append(f"{green_flowers} 🟢 flores verdes (sua base sólida)")
        if orange_flowers > 0:
            flower_breakdown.append(f"{orange_flowers} 🟠 flores laranjas (sua consistência)")
        if red_flowers > 0:
            flower_breakdown.append(f"{red_flowers} 🔴 flores vermelhas (seus desafios)")
        if purple_flowers > 0:
            flower_breakdown.append(f"{purple_flowers} 🟣 flores roxas (sua excelência!)")

        return {
            "total_flowers": total_flowers,
            "green_flowers": green_flowers,
            "orange_flowers": orange_flowers,
            "red_flowers": red_flowers,
            "purple_flowers": purple_flowers,
            "message": message,
            "breakdown": ", ".join(flower_breakdown) if flower_breakdown else "pronto para florescer",
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "streak": max(1, completed_tasks // 2),  # Streak simples baseado em tarefas completadas
        }

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

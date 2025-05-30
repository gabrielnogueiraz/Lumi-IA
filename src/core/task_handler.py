#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Task Handler Module for Lumi Assistant

Handles all task-related operations with AI-powered responses
"""

import re
from .ai_engine import AIEngine


class TaskHandler:
    """
    Handles task management operations with AI-powered responses
    """

    def __init__(self, task_manager, personality):
        """Initialize task handler"""
        self.task_manager = task_manager
        self.personality = personality
        self.ai_engine = AIEngine()

        # Advanced patterns for task title extraction
        self.task_patterns = [
            # Main pattern for "Add to my agenda, study postgresql today at 22:00"
            r"(?:adicionar?|adicione|criar?|crie|incluir?|inclua|colocar?|coloque|agendar?|agende|marcar?|marque)\s+(?:na\s+(?:minha\s+)?(?:agenda|lista)\s*,?\s*)?(.+?)(?:\s+(?:hoje|amanhã|amanha|para|até|às?|as|em|na|no|dia|hora)\s+(?:\d+|segunda|terça|quarta|quinta|sexta|sábado|domingo)|$)",
            # Patterns for direct commands with quotes
            r'["\']([^"\']+)["\']',
            # Patterns for "need to/have to/going to" + task
            r"(?:preciso|tenho que|vou|quero|gostaria de)\s+(.+?)(?:\s+(?:hoje|amanhã|amanha|na|no|em|para|até|às?|as)\s+|$)",
            # Pattern for tasks after colon or comma
            r"[,:]\s*(.+?)(?:\s+(?:para|até|em|na|no|hoje|amanhã|às?|as)\s+|$)",
            # More specific pattern to capture main action
            r"(?:fazer|estudar|comprar|ligar|enviar|terminar|completar|preparar|organizar|planejar)\s+(.+?)(?:\s+(?:hoje|amanhã|na|no|em|para|até|às?|as)\s+|$)",
            # Generic improved pattern (last resort)
            r"(?:tarefa|task|atividade)\s+(.+?)(?:\s+(?:para|até|em|na|no|hoje|amanhã|às?|as)\s+|$)",
        ]

        # Improved filters for title cleaning
        self.noise_words = [
            "adicionar", "adicione", "criar", "crie", "nova", "novo", "tarefa", "task",
            "preciso", "tenho", "que", "vou", "quero", "gostaria", "favor", "por",
            "fazer", "incluir", "na", "nas", "lista", "tarefas", "minha", "meu",
            "agenda", "hoje", "amanhã", "amanha", "às", "as", "em", "no", "da", "do", "a", "o",
        ]

    def process_add_task(self, message):
        """
        Add task with AI-powered personalized response
        """
        try:
            # Extract task title
            task_title = self._extract_task_title_intelligent(message)

            if not task_title or len(task_title.strip()) < 3:
                return self.ai_engine.generate_task_response(
                    "solicitando mais detalhes sobre uma tarefa", 
                    message
                )

            # Add the task
            success = self.task_manager.add_task(task_title)

            if success:
                # Update context
                self.personality.user_context["last_task_added"] = task_title
                self.personality.user_context["current_focus"] = task_title

                # Generate AI-powered response
                return self.ai_engine.generate_task_response(
                    "adicionar", 
                    message, 
                    {"title": task_title}
                )
            else:
                return self.ai_engine.generate_task_response(
                    "tendo dificuldade para adicionar a tarefa", 
                    message
                )

        except Exception as e:
            return f"😅 Tive uma pequena dificuldade técnica para adicionar a tarefa, mas vamos tentar novamente! (Erro: {str(e)})"

    def process_list_tasks(self, message):
        """
        List tasks with AI-enhanced humanized presentation
        """
        try:
            tasks = self.task_manager.list_tasks()

            if not tasks:
                return self.ai_engine.generate_task_response(
                    "verificando uma lista vazia de tarefas", 
                    message
                )

            # Generate AI-powered introduction
            intro_response = self.ai_engine.generate_task_response(
                "listando tarefas", 
                message
            )

            response = intro_response + "\n\n"

            # List tasks with friendly formatting
            for i, task in enumerate(tasks, 1):
                status_emoji = "✅" if task.get("completed", False) else "📌"
                priority_indicator = ""

                # Add priority indicator based on keywords
                task_lower = task["title"].lower()
                if any(
                    word in task_lower
                    for word in ["urgente", "importante", "prioridade"]
                ):
                    priority_indicator = " 🔥"

                response += f"{status_emoji} {i}. {task['title']}{priority_indicator}\n"

            # Add motivational statistics
            completed_count = sum(1 for task in tasks if task.get("completed", False))
            total_count = len(tasks)
            pending_count = total_count - completed_count

            if completed_count > 0:
                response += f"\n🎯 Progresso: {completed_count}/{total_count} tarefas concluídas!"

            if pending_count > 0:
                response += f"\n⚡ {pending_count} tarefa(s) aguardando sua atenção!"

            # Contextual tip
            if pending_count > 5:
                response += "\n\n💡 Dica: Que tal focar nas 3 mais importantes primeiro?"
            elif pending_count <= 2:
                response += "\n\n🌟 Você está quase lá! Foco total!"

            return response

        except Exception as e:
            return f"😅 Tive um problema para acessar sua lista de tarefas. Vamos tentar novamente? (Erro: {str(e)})"

    def process_complete_task(self, message):
        """
        Mark task as completed with AI-powered celebration
        """
        try:
            # Extract task identifier (number or name)
            task_identifier = self._extract_task_identifier(message)

            if not task_identifier:
                return self.ai_engine.generate_task_response(
                    "precisando identificar qual tarefa foi concluída", 
                    message
                )

            # Try to mark as completed
            success, task_title = self.task_manager.complete_task(task_identifier)

            if success:
                return self.ai_engine.generate_task_response(
                    "celebrando a conclusão de", 
                    message, 
                    {"title": task_title}
                )
            else:
                return self.ai_engine.generate_task_response(
                    "não conseguindo encontrar a tarefa para concluir", 
                    message
                )

        except Exception as e:
            return f"😅 Ops! Tive dificuldade para marcar a tarefa como concluída. Pode tentar novamente? (Erro: {str(e)})"

    def process_remove_task(self, message):
        """
        Remove task with AI-powered confirmation
        """
        try:
            # Extract task identifier
            task_identifier = self._extract_task_identifier(message)

            if not task_identifier:
                return self.ai_engine.generate_task_response(
                    "precisando identificar qual tarefa remover", 
                    message
                )

            # Try to remove
            success, task_title = self.task_manager.remove_task(task_identifier)

            if success:
                return self.ai_engine.generate_task_response(
                    "removendo", 
                    message, 
                    {"title": task_title}
                )
            else:
                return self.ai_engine.generate_task_response(
                    "não conseguindo encontrar a tarefa para remover", 
                    message
                )

        except Exception as e:
            return f"😅 Tive dificuldade para remover a tarefa. Pode tentar novamente? (Erro: {str(e)})"

    def process_edit_task(self, message):
        """
        Process task editing (future functionality)
        """
        return self.ai_engine.generate_task_response(
            "explorando funcionalidades de edição", 
            message
        )

    def _extract_task_title_intelligent(self, message):
        """
        Intelligent task title extraction using multiple patterns
        """
        message_clean = message.strip()

        # First, try regex patterns
        for pattern in self.task_patterns:
            match = re.search(pattern, message_clean, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Remove unnecessary words
                title = self._clean_task_title(title)
                if len(title) > 3:  # Title must have at least 3 characters
                    return title

        # If not found with regex, try simple semantic analysis
        words = message_clean.lower().split()

        # Remove noise words from beginning
        start_index = 0
        for i, word in enumerate(words):
            if word not in self.noise_words:
                start_index = i
                break

        # Rebuild title
        title_words = words[start_index:]
        if title_words:
            title = " ".join(title_words)
            title = self._clean_task_title(title)
            if len(title) > 3:
                return title

        # As last resort, use entire message
        fallback_title = self._clean_task_title(message_clean)
        return fallback_title if len(fallback_title) > 3 else "Nova tarefa"

    def _clean_task_title(self, title):
        """
        Clean task title removing noise and formatting appropriately - CORRECTED VERSION
        """
        if not title:
            return ""

        # Remove extra quotes and spaces
        title = title.strip("\"'").strip()

        # Remove noise words from beginning and end
        words = title.lower().split()
        original_words = title.split()  # Keep original capitalization
        filtered_words = []

        # Skip noise words at beginning
        start_idx = 0
        for i, word in enumerate(words):
            if word not in self.noise_words:
                start_idx = i
                break

        # Get relevant words, stopping BEFORE temporal indicators
        for i in range(start_idx, len(words)):
            word = words[i]

            # IMPROVEMENT: Stop BEFORE finding time/date indicators
            if word in [
                "hoje", "amanhã", "amanha", "para", "às", "as", "em", "na", "no",
                "dia", "hora", "ontem", "semana", "mes", "ano",
            ]:
                break

            # IMPROVEMENT: Stop BEFORE numbers indicating time (22:00, 14h, etc.)
            if re.search(r"\d+[:h]", word) or (word.isdigit() and len(word) <= 2):
                break

            # Remove only small unnecessary articles, but not at beginning
            if word not in ["a", "o", "de", "da", "do"] or len(filtered_words) == 0:
                filtered_words.append(original_words[i])  # Keep original capitalization

        if filtered_words:
            title = " ".join(filtered_words)

        # Remove residual temporal indicators from end
        title = re.sub(
            r"\s+(hoje|amanhã|amanha|para|às?|as|em|na|no|dia|hora).*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Proper capitalization of first letter only
        title = title.strip()
        if title and len(title) > 0:
            title = title[0].upper() + title[1:]

        return title

    def _extract_task_identifier(self, message):
        """
        Extract task identifier (number or name) from message
        """
        # Look for numbers
        number_match = re.search(r"\b(\d+)\b", message)
        if number_match:
            return int(number_match.group(1))

        # Look for names in quotes
        quote_match = re.search(r'["\']([^"\']+)["\']', message)
        if quote_match:
            return quote_match.group(1)

        # Try to extract using patterns similar to adding task
        patterns = [
            r"(?:concluir|finalizar|completar|terminar|concluída|feita)\s+(.+?)(?:\s+(?:hoje|agora|já)\s*|$)",
            r"(?:remover|deletar|excluir|tirar)\s+(.+?)(?:\s+(?:da lista|das tarefas)\s*|$)",
            r"(?:tarefa|task)\s+(.+?)(?:\s+(?:concluída|removida|deletada)\s*|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

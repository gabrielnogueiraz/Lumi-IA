#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Task Handler Module for Lumi Assistant - VERSÃO SIMPLIFICADA E CORRIGIDA

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

    def process_add_task(self, message):
        """
        Add task(s) with improved parsing
        """
        try:
            # PRIMEIRO: Verifica se é múltiplas tarefas
            multiple_tasks = self._extract_multiple_tasks_improved(message)

            if multiple_tasks and len(multiple_tasks) > 1:
                return self._process_multiple_tasks(message, multiple_tasks)

            # SEGUNDO: Processamento para tarefa única MELHORADO
            task_info = self._extract_single_task_improved(message)

            if (
                not task_info
                or not task_info.get("title")
                or len(task_info["title"].strip()) < 3
            ):
                return self.ai_engine.generate_task_response(
                    "solicitando mais detalhes sobre uma tarefa", message
                )

            # Adiciona a tarefa
            success = self.task_manager.add_task(
                task_info["title"],
                date=task_info.get("date"),
                time=task_info.get("time"),
            )

            if success:
                # Update context with AWARENESS
                self._update_context("task_added", task_info["title"], True)

                return self.ai_engine.generate_task_response(
                    "adicionar",
                    message,
                    {"title": task_info["title"], "confirmed": True},
                )
            else:
                self._update_context("task_add_failed", task_info["title"], False)
                return self.ai_engine.generate_task_response(
                    "tendo dificuldade para adicionar a tarefa", message
                )

        except Exception as e:
            self._update_context("task_add_error", "", False)
            return f"😅 Tive uma pequena dificuldade técnica para adicionar a tarefa, mas vamos tentar novamente! (Erro: {str(e)})"

    def _extract_single_task_improved(self, message):
        """
        NOVA VERSÃO: Extração inteligente de tarefa única CORRIGIDA
        """
        # Padrões mais específicos e organizados
        patterns = [
            # Padrão 1: "Preciso estudar minecraft hoje as 15:00"
            r"(?:preciso|tenho que|vou)\s+(.+?)\s+(?:hoje|amanhã)\s+(?:às?|as)\s+(\d{1,2}[:h]\d{0,2})",
            # Padrão 2: "Adicione estudar minecraft às 15:00"
            r"(?:adicione?|adicionar)\s+(.+?)\s+(?:às?|as)\s+(\d{1,2}[:h]\d{0,2})",
            # Padrão 3: "Estudar minecraft hoje às 15:00"
            r"^(?!.*(?:adicionar|adicione|preciso adicionar|que são))(.+?)\s+(?:hoje|amanhã)\s+(?:às?|as)\s+(\d{1,2}[:h]\d{0,2})",
            # Padrão 4: Após "adicione na minha agenda:"
            r"(?:adicione?|adicionar)\s+(?:na|à)\s+(?:minha\s+)?agenda[,:]\s*(.+?)(?:\s+(?:às?|as)\s+(\d{1,2}[:h]\d{0,2}))?",
            # Padrão 5: Genérico sem horário
            r"(?:preciso|tenho que|vou|adicione?)\s+(.+?)(?:\s+(?:hoje|amanhã|para))?$",
        ]

        message_clean = message.strip()

        for pattern in patterns:
            match = re.search(pattern, message_clean, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                time = match.group(2) if len(match.groups()) > 1 else None

                # Limpa o título
                title = self._clean_task_title_improved(title)

                # Valida se o título faz sentido
                if self._is_valid_task_title(title):
                    from datetime import datetime

                    return {
                        "title": title,
                        "time": time,
                        "date": datetime.now().strftime("%d/%m/%Y"),
                    }

        return None

    def _clean_task_title_improved(self, title):
        """
        NOVA VERSÃO: Limpeza melhorada de título
        """
        if not title:
            return ""

        # Remove aspas e espaços extras
        title = title.strip("\"'").strip()

        # Remove palavras de ruído específicas do FINAL
        noise_endings = [
            r"\s+(?:na|à)\s+(?:minha\s+)?agenda$",
            r"\s+(?:para|até|em)\s+(?:hoje|amanhã)$",
            r"\s+(?:hoje|amanhã)$",
        ]

        for pattern in noise_endings:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        # Remove palavras de ruído do INÍCIO
        noise_beginnings = [
            r"^(?:adicionar|adicione|incluir|inclua|anotar|marcar)\s+",
            r"^(?:que|são|tarefas?)\s*[:\-]?\s*",
        ]

        for pattern in noise_beginnings:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        # Capitaliza primeira letra
        title = title.strip()
        if title and len(title) > 0:
            title = title[0].upper() + title[1:]

        return title

    def _is_valid_task_title(self, title):
        """
        Valida se o título da tarefa faz sentido
        """
        if not title or len(title) < 3:
            return False

        # Lista de títulos inválidos comuns
        invalid_titles = [
            "minha agenda",
            "na agenda",
            "agenda",
            "tarefa",
            "tarefas",
            "que são",
            "são",
            "algumas",
            "hoje",
            "amanhã",
            "às",
            "as",
        ]

        title_lower = title.lower()
        for invalid in invalid_titles:
            if title_lower == invalid or title_lower.startswith(invalid + " "):
                return False

        return True

    def _extract_multiple_tasks_improved(self, message):
        """
        NOVA VERSÃO: Extração melhorada de múltiplas tarefas
        """
        # Detecta padrão de lista numerada
        list_pattern = r"(?:que são|são|tarefas?)[:\s]*(.+?)(?=\s*$)"
        list_match = re.search(list_pattern, message, re.IGNORECASE)

        if not list_match:
            return []

        tasks_text = list_match.group(1)

        # Extrai tarefas numeradas
        task_pattern = r"(\d+)\.\s*([^,\d]+?)(?=\s*(?:\d+\.|$|,\s*\d+))"
        matches = re.findall(task_pattern, tasks_text, re.IGNORECASE)

        tasks = []
        for num, task_text in matches:
            task_info = self._parse_single_task_from_text(task_text.strip())
            if task_info and self._is_valid_task_title(task_info["title"]):
                tasks.append(task_info)

        return tasks if len(tasks) > 1 else []

    def _parse_single_task_from_text(self, text):
        """
        Analisa uma única tarefa extraída de uma lista
        """
        # Padrões para extrair título, horário e data
        time_patterns = [r"(?:às?|as)\s*(\d{1,2}[:h]\d{0,2})", r"(\d{1,2}:\d{2})"]

        time = None
        clean_title = text

        # Extrai horário
        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time = match.group(1)
                clean_title = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
                break

        # Remove conectores temporais
        clean_title = re.sub(
            r"\s*(?:hoje|amanhã|para|até|em|na|no)\s*",
            " ",
            clean_title,
            flags=re.IGNORECASE,
        ).strip()

        # Remove palavras de início desnecessárias
        clean_title = re.sub(
            r"^(?:tenho|preciso|vou|que)\s+", "", clean_title, flags=re.IGNORECASE
        ).strip()

        # Capitaliza
        if clean_title:
            clean_title = clean_title[0].upper() + clean_title[1:]

        from datetime import datetime

        return {
            "title": clean_title,
            "time": time,
            "date": datetime.now().strftime("%d/%m/%Y"),
        }

    def _process_multiple_tasks(self, message, tasks):
        """
        Processa múltiplas tarefas - SIMPLIFICADO
        """
        try:
            added_tasks = []
            failed_tasks = []

            for task_info in tasks:
                success = self.task_manager.add_task(
                    task_info["title"],
                    date=task_info.get("date"),
                    time=task_info.get("time"),
                )

                if success:
                    added_tasks.append(task_info)
                else:
                    failed_tasks.append(task_info)

            # Update context
            self._update_context(
                "multiple_tasks_added",
                f"{len(added_tasks)} tarefas",
                len(failed_tasks) == 0,
            )

            if len(added_tasks) == len(tasks):
                # Todas adicionadas com sucesso
                response = f"✅ **Perfeito!** Adicionei todas as {len(added_tasks)} tarefas na sua agenda:\n\n"

                for i, task in enumerate(added_tasks, 1):
                    time_info = f" às {task['time']}" if task.get("time") else ""
                    response += f"📌 {i}. {task['title']}{time_info}\n"

                response += f"\n🎯 **Status:** {len(added_tasks)} nova(s) tarefa(s) adicionada(s)!\n"
                response += "✨ **Organização:** Sua agenda está atualizada!\n\n"
                response += "🌟 Que tal começarmos pela primeira? 💪"

                return response

            elif len(added_tasks) > 0:
                # Algumas adicionadas
                response = f"✅ Consegui adicionar {len(added_tasks)} de {len(tasks)} tarefas:\n\n"

                for i, task in enumerate(added_tasks, 1):
                    time_info = f" às {task['time']}" if task.get("time") else ""
                    response += f"📌 {i}. {task['title']}{time_info}\n"

                if failed_tasks:
                    response += f"\n⚠️ {len(failed_tasks)} tarefa(s) não puderam ser adicionadas."

                return response
            else:
                return "😅 Tive dificuldade para adicionar as tarefas. Pode tentar uma por vez?"

        except Exception as e:
            return f"😅 Problema ao processar múltiplas tarefas: {str(e)}"

    def process_list_tasks(self, message):
        """
        Lista tarefas - SIMPLIFICADO
        """
        try:
            tasks = self.task_manager.list_tasks()

            # Update context
            self._update_context("list_tasks", f"{len(tasks)} tarefas", True)

            if not tasks:
                return self._generate_empty_agenda_response()

            return self._generate_tasks_list_response(tasks)

        except Exception as e:
            self._update_context("list_tasks_error", "", False)
            return f"😅 Problema para acessar sua lista. Erro: {str(e)}"

    def _generate_empty_agenda_response(self):
        """
        Gera resposta para agenda vazia
        """
        responses = [
            "🎉 Sua agenda está completamente livre! ✨\n\n**Estado atual:** Nenhuma tarefa pendente\n\nVocê pode:\n📝 Adicionar novas tarefas\n🎯 Focar em planejamento\n💡 Ser criativo\n\n**Quer adicionar uma tarefa?**",
            "✨ Lista de tarefas limpa! 🌟\n\n**Status:** 0 tarefas na agenda\n\nMomento perfeito para:\n🚀 Planejar próximos passos\n📋 Definir novas metas\n💪 Relaxar\n\n**Pronto para algo novo?**",
        ]

        import random

        return random.choice(responses)

    def _generate_tasks_list_response(self, tasks):
        """
        Gera resposta com lista de tarefas
        """
        import random

        intro = f"📋 Sua agenda tem {len(tasks)} tarefa(s):\n\n"

        task_list = ""
        completed_count = 0

        for i, task in enumerate(tasks, 1):
            status = "✅" if task.get("completed", False) else "📌"

            if task.get("completed", False):
                completed_count += 1

            time_info = ""
            if task.get("time"):
                time_info += f" às {task['time']}"
            if task.get("date"):
                time_info += f" - {task['date']}"

            task_list += f"{status} {i}. {task['title']}{time_info}\n"

        pending_count = len(tasks) - completed_count

        status_info = f"\n📊 **Status:** {pending_count} pendente(s)"
        if completed_count > 0:
            status_info += f", {completed_count} concluída(s)"

        motivational = [
            "\n\n🚀 **Qual vamos atacar primeiro?**",
            "\n\n💪 **Vamos começar?**",
            "\n\n✨ **Pronto para conquistar tudo?**",
        ]

        return intro + task_list + status_info + random.choice(motivational)

    def process_complete_task(self, message):
        """
        Marca tarefa como concluída - SIMPLIFICADO
        """
        try:
            task_identifier = self._extract_task_identifier(message)

            if not task_identifier:
                return (
                    "😊 Qual tarefa você concluiu? Me diga o número ou nome da tarefa."
                )

            success, task_title = self.task_manager.complete_task(task_identifier)

            if success:
                self._update_context("task_completed", task_title, True)
                return f"🎉 **Parabéns!** Tarefa '{task_title}' concluída! Você está arrasando! 💪"
            else:
                self._update_context("task_complete_failed", "", False)
                return (
                    "😅 Não encontrei essa tarefa. Pode me dar o número ou nome exato?"
                )

        except Exception as e:
            return f"😅 Problema para concluir tarefa: {str(e)}"

    def process_remove_task(self, message):
        """
        Remove tarefa - SIMPLIFICADO
        """
        try:
            # Verifica remoção em massa
            if any(word in message.lower() for word in ["todas", "tudo", "all"]):
                return self._process_remove_all_tasks()

            task_identifier = self._extract_task_identifier(message)

            if not task_identifier:
                return "😊 Qual tarefa você quer remover? Me diga o número ou nome."

            success, task_title = self.task_manager.remove_task(task_identifier)

            if success:
                self._update_context("task_removed", task_title, True)
                return f"✅ **Removido!** Tarefa '{task_title}' foi retirada da sua agenda!"
            else:
                self._update_context("task_remove_failed", "", False)
                return "😅 Não encontrei essa tarefa. Pode verificar o número ou nome?"

        except Exception as e:
            return f"😅 Problema para remover tarefa: {str(e)}"

    def _process_remove_all_tasks(self):
        """
        Remove todas as tarefas
        """
        try:
            current_tasks = self.task_manager.list_tasks()
            task_count = len(current_tasks)

            if task_count == 0:
                return "😊 Sua agenda já está vazia! Quer adicionar algumas tarefas?"

            # Remove todas
            removed_count = 0
            for task in current_tasks:
                success, _ = self.task_manager.remove_task(task["id"])
                if success:
                    removed_count += 1

            self._update_context("all_tasks_removed", f"{removed_count} tarefas", True)

            if removed_count == task_count:
                return f"✅ **Pronto!** Removi todas as {task_count} tarefas!\n\n🎯 **Agenda limpa!** Agora você pode começar do zero! 🚀"
            else:
                return f"⚠️ Consegui remover {removed_count} de {task_count} tarefas."

        except Exception as e:
            return f"😅 Problema para remover todas: {str(e)}"

    def process_edit_task(self, message):
        """
        Edita tarefa (funcionalidade futura)
        """
        return "🔧 Funcionalidade de edição em desenvolvimento! Por enquanto, você pode remover e adicionar novamente."

    def _extract_task_identifier(self, message):
        """
        Extrai identificador da tarefa (número ou nome)
        """
        # Procura números
        number_match = re.search(r"\b(\d+)\b", message)
        if number_match:
            return int(number_match.group(1))

        # Procura nomes entre aspas
        quote_match = re.search(r'["\']([^"\']+)["\']', message)
        if quote_match:
            return quote_match.group(1)

        # Padrões específicos
        patterns = [
            r"(?:concluir|terminei|feito|pronto)\s+(.+?)(?:\s+(?:hoje|agora)\s*|$)",
            r"(?:remover|deletar|tirar)\s+(.+?)(?:\s+(?:da lista)\s*|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _update_context(self, action, details, success):
        """
        Atualiza contexto da personalidade - HELPER
        """
        self.personality.user_context["last_action"] = action
        self.personality.user_context["last_action_details"] = details
        self.personality.user_context["last_action_success"] = success

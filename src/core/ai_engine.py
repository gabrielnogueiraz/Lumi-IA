#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Engine Module for Lumi Assistant

Handles communication with Google Gemini and OpenRouter APIs
"""

import logging
import requests
import json

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class AIEngine:
    """
    Manages AI API calls with Google Gemini as primary and OpenRouter as fallback
    """

    def __init__(self):
        """Initialize AI Engine with API configurations"""
        # Google Gemini configuration
        self.GEMINI_API_KEY = "AIzaSyAButmMFCGLI48y2BeU1kAdOkL1rggdujA"
        self.GEMINI_MODEL = "gemma-3-1b-it"

        # OpenRouter fallback configuration
        self.OPENROUTER_API_KEY = (
            "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"
        )
        self.OPENROUTER_MODEL = "meta-llama/llama-3.1-8b-instruct:free"
        self.OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

        # Initialize Google Gemini client
        self.genai_client = None
        if genai:
            try:
                genai.configure(api_key=self.GEMINI_API_KEY)
                self.genai_client = genai
                print("✅ Google Gemini inicializado com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro ao inicializar Google GenAI: {e}")

        # Setup logging
        self.logger = logging.getLogger(__name__)

    def call_ai_api(self, messages):
        """
        Call AI API with Google Gemini as primary and OpenRouter as fallback
        """
        # First try Google Gemini
        if self.genai_client:
            try:
                content = self._convert_messages_to_gemini_format(messages)
                model = self.genai_client.GenerativeModel(self.GEMINI_MODEL)
                response = model.generate_content(content)

                self.logger.info(f"✅ Resposta gerada pelo {self.GEMINI_MODEL}")
                print(f"✅ Resposta gerada pelo {self.GEMINI_MODEL}")
                return response.text

            except Exception as e:
                self.logger.warning(f"⚠️ Erro no Google Gemini, tentando fallback: {e}")
                print(f"⚠️ Erro no Google Gemini, tentando fallback: {e}")

        # Fallback to OpenRouter
        self.logger.info("🔄 Usando OpenRouter como fallback")
        print("🔄 Usando OpenRouter como fallback")
        return self._call_openrouter_fallback(messages)

    def _convert_messages_to_gemini_format(self, messages):
        """
        Convert messages from OpenAI format to Gemini format
        """
        if not messages:
            return "Como posso te ajudar?"

        # Get only the last user message for Gemini
        last_message = (
            messages[-1] if messages else {"content": "Como posso te ajudar?"}
        )
        return last_message.get("content", "Como posso te ajudar?")

    def _call_openrouter_fallback(self, messages):
        """
        Call OpenRouter API as fallback with humanized error handling
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/lumiassistant",
                "X-Title": "Lumi Assistant",
            }

            data = {
                "model": self.OPENROUTER_MODEL,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7,
            }

            response = requests.post(
                self.OPENROUTER_BASE_URL, headers=headers, json=data, timeout=30
            )

            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and response_data["choices"]:
                    return response_data["choices"][0]["message"]["content"]
                else:
                    return "✨ Estou processando sua solicitação, mas houve um pequeno problema técnico. Vamos continuar!"

            else:
                return f"🤖 Desculpe, estou com dificuldades técnicas no momento. Mas posso te ajudar com suas tarefas da forma tradicional!"

        except requests.exceptions.Timeout:
            return "⏰ A resposta está demorando um pouco. Que tal focarmos nas suas tarefas por enquanto?"

        except Exception as e:
            self.logger.error(f"Erro na API: {e}")
            return "✨ Estou aqui para te ajudar com suas tarefas e produtividade! Como posso te ajudar?"

    def generate_educational_explanation(self, topic, message):
        """
        Generate educational explanations using AI
        """
        messages = [
            {
                "role": "system",
                "content": f"""Você é Lumi, uma assistente educacional carismática e didática.
                Explique sobre {topic} de forma clara, simples e motivadora.
                Use emojis sutilmente e inclua sempre uma sugestão para criar uma tarefa de estudo.
                Mantenha a resposta concisa (máximo 200 palavras).""",
            },
            {"role": "user", "content": message},
        ]

        return self.call_ai_api(messages)

    def generate_task_response(self, context, message, task_info=None):
        """
        Generate responses for task management operations using AI
        """
        if task_info:
            system_content = f"""Você é Lumi, uma assistente de produtividade carismática e motivadora.
            O usuário acabou de {context} a tarefa: "{task_info.get('title', 'Nova tarefa')}"
            Responda de forma entusiasmada, motivacional e personalizada.
            Use emojis sutilmente e mantenha o tom inspirador.
            Máximo 100 palavras."""
        else:
            system_content = f"""Você é Lumi, uma assistente de produtividade carismática e motivadora.
            O usuário está {context}.
            Responda de forma útil, motivacional e personalizada.
            Use emojis sutilmente e mantenha o tom inspirador.
            Máximo 150 palavras."""

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": message},
        ]

        return self.call_ai_api(messages)

    def generate_general_response(self, message):
        """
        Generate responses for general queries using AI
        """
        messages = [
            {
                "role": "system",
                "content": """Você é Lumi, uma assistente de produtividade carismática, inteligente e motivadora.
                Responda de forma amigável, útil e sempre tente conectar a resposta com produtividade, organização ou bem-estar.
                Use emojis sutilmente e mantenha o tom inspirador mas profissional.
                Se a pergunta não for relacionada a produtividade, redirecione gentilmente para suas funcionalidades.""",
            },
            {"role": "user", "content": message},
        ]

        return self.call_ai_api(messages)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Education Module for Lumi Assistant

Handles educational queries and explanations with AI integration
"""

import re
from .ai_engine import AIEngine


class Education:
    """
    Handles educational queries and provides AI-powered explanations
    """

    def __init__(self):
        """Initialize education module"""
        self.ai_engine = AIEngine()

    def detect_educational_intent(self, message):
        """
        Detect if message is an educational question or explanation request
        """
        educational_patterns = [
            r"(?:explique|explica|me explique|como funciona|o que é|what is)",
            r"(?:ensine|ensina|me ensine|como fazer|how to)",
            r"(?:qual a diferença|diferença entre|compare)",
            r"(?:me ajude a entender|help me understand|não entendo)",
            r"(?:exemplo|exemplos|give me an example)",
            r"(?:resumo|summary|summarize|resuma)",
            r"(?:defina|define|definição|definition)",
            r"(?:por que|why|porque|razão|motivo)",
            r"(?:conceitos|conceito|principais.*estudar)",
            r"(?:dicas|dica|ajuda.*estudar|como estudar)",
        ]

        message_lower = message.lower()
        for pattern in educational_patterns:
            if re.search(pattern, message_lower):
                return True
        return False

    def process_educational_query(self, message):
        """
        Process educational questions with AI-powered responses
        """
        try:
            # Extract topic from question
            topic = self._extract_educational_topic(message)

            # Check if it's request for study tips
            if any(
                phrase in message.lower()
                for phrase in ["dicas", "como estudar", "cronograma", "plano de estudo"]
            ):
                return self._provide_study_tips(topic)

            # Check if it's about key concepts
            if any(
                phrase in message.lower()
                for phrase in ["conceitos", "principais", "importantes"]
            ):
                return self._explain_key_concepts(topic)

            # Generate AI-powered educational explanation
            return self.ai_engine.generate_educational_explanation(topic, message)

        except Exception as e:
            return f"🤔 Adoraria te ajudar a entender melhor! Pode reformular sua pergunta? Enquanto isso, que tal adicionarmos uma tarefa de estudo sobre esse assunto?"

    def _extract_educational_topic(self, message):
        """
        Extract educational topic from message
        """
        # Remove question words to focus on topic
        message_clean = re.sub(
            r"\b(explique|explica|o que é|como funciona|ensine|ensina|me ajude|help)\b",
            "",
            message.lower(),
        )
        message_clean = re.sub(
            r"\b(sobre|about|acerca de|conceitos|mais importantes)\b", "", message_clean
        )
        message_clean = message_clean.strip()

        # Known specific topics
        known_topics = {
            "postgresql": ["postgresql", "postgres", "sql", "banco de dados"],
            "python": ["python", "programação python", "linguagem python"],
            "javascript": ["javascript", "js", "programação web"],
            "html": ["html", "markup", "web"],
            "css": ["css", "estilo", "design web"],
            "react": ["react", "reactjs", "biblioteca javascript"],
            "nodejs": ["nodejs", "node.js", "node", "backend javascript"],
            "git": ["git", "controle de versão", "versionamento"],
            "docker": ["docker", "container", "containerização"],
            "api": ["api", "rest", "restful", "webservice"],
        }

        # Search for known topics
        for topic, keywords in known_topics.items():
            for keyword in keywords:
                if keyword in message_clean:
                    return topic

        # If no specific topic found, return main words
        words = message_clean.split()
        # Remove very common words
        stop_words = [
            "a", "o", "e", "de", "da", "do", "em", "na", "no", "para", "com",
            "como", "que", "é", "são", "no",
        ]
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]

        if meaningful_words:
            return " ".join(meaningful_words[:3])  # Maximum 3 words

        return "programação"  # Default fallback

    def _explain_key_concepts(self, topic):
        """
        Explain key concepts about a specific topic using AI
        """
        # Use AI to generate key concepts explanation
        message = f"Explique os conceitos mais importantes sobre {topic}"
        return self.ai_engine.generate_educational_explanation(topic, message)

    def _provide_study_tips(self, subject=None):
        """
        Provide motivational and practical study tips using AI
        """
        if subject:
            message = f"Dê dicas práticas e motivacionais para estudar {subject}"
            return self.ai_engine.generate_educational_explanation(subject, message)
        else:
            # General study tips with AI enhancement
            message = "Dê dicas gerais de estudo eficiente e motivacional"
            return self.ai_engine.generate_general_response(message)

    def _fallback_educational_response(self, topic, message):
        """
        Fallback educational response when external API is not available
        """
        # Basic knowledge base for common topics
        basic_knowledge = {
            "postgresql": {
                "explanation": "🗄️ **PostgreSQL** é um sistema de gerenciamento de banco de dados relacional open-source, conhecido por sua robustez e conformidade com padrões SQL!",
                "tips": "💡 **Dicas**: Comece praticando comandos básicos SQL, explore as funcionalidades avançadas como JSON support, e sempre pratique com datasets reais!"
            },
            "python": {
                "explanation": "🐍 **Python** é uma linguagem de programação versátil e amigável, perfeita para iniciantes e poderosa para experts!",
                "tips": "💡 **Dicas**: Pratique diariamente, trabalhe em projetos reais, participe da comunidade Python e explore bibliotecas como pandas, numpy e Django!"
            },
            "sql": {
                "explanation": "📊 **SQL** (Structured Query Language) é a linguagem padrão para gerenciar e consultar bancos de dados relacionais!",
                "tips": "💡 **Dicas**: Pratique com datasets reais, aprenda JOINs e subconsultas, e sempre otimize suas queries para performance!"
            }
        }

        if topic.lower() in basic_knowledge:
            response = basic_knowledge[topic.lower()]
            return f"{response['explanation']}\n\n{response['tips']}\n\n✨ **Quer que eu ajude você a criar uma tarefa de estudo sobre isso?** É só me dizer!"

        # Generic motivational response
        return f"""🤔 Essa é uma pergunta interessante sobre **{topic}**! 

📚 Embora eu não tenha uma explicação específica na ponta da língua, posso te ajudar de outras formas incríveis:

✅ **Criar uma tarefa de estudo** sobre {topic}
🎯 **Sugerir fontes de pesquisa** confiáveis  
📝 **Organizar um cronograma** de estudos personalizado
💡 **Dar dicas de como estudar** de forma mais eficiente

🌟 **Que tal começarmos adicionando "{topic}" nas suas tarefas de estudo?** Assim você não esquece de pesquisar sobre isso!

💪 **Fala comigo**: "Adicione estudar {topic}" e eu organizo tudo para você!"""

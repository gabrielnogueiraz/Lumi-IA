#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Patterns Module for Lumi Assistant

Handles pattern detection for actions, intents, and message analysis
"""

import re


class PatternDetector:
    """
    Detects patterns in user messages to determine actions and intents
    """

    def __init__(self):
        """Initialize pattern detection vocabularies"""
        # Expanded vocabulary for intelligent intent detection
        self.vocabulario = {
            "adicionar": [
                "adicionar", "adicione", "criar", "crie", "nova", "novo", "fazer",
                "preciso", "tenho que", "vou", "quero", "gostaria", "incluir",
                "anotar", "lembrar", "marcar", "registrar", "planear", "agendar",
            ],
            "listar": [
                "listar", "mostrar", "ver", "quais", "que", "minhas", "tarefas",
                "lista", "pendente", "pendentes", "fazer", "falta", "restante",
                "próximas", "status", "situação", "andamento",
            ],
            "concluir": [
                "concluir", "concluída", "terminei", "pronto", "finalizar", "feito",
                "feita", "completar", "acabei", "terminar", "finalizado", "marcar",
                "completo", "done", "finished",
            ],
            "remover": [
                "remover", "deletar", "excluir", "tirar", "cancelar", "eliminar",
                "apagar", "retirar", "descartar", "não precisa", "esquecer",
            ],
            "relatório": [
                "relatório", "relatorio", "resumo", "estatística", "estatisticas",
                "progresso", "performance", "desempenho", "análise", "balanço",
                "overview", "dashboard", "métricas",
            ],
            "editar": [
                "editar", "alterar", "modificar", "mudar", "corrigir", "ajustar",
                "atualizar", "revisar", "refinar", "trocar",
            ],
        }

    def detect_action(self, message):
        """
        Intelligent action detection with enhanced context analysis
        """
        message_lower = message.lower()
        detected_actions = []

        # Specific patterns for each action
        action_patterns = {
            "adicionar": [
                r"(?:adiciona|adicione|cria|crie|nova|novo)",
                r"(?:preciso|tenho que|vou) (?:fazer|estudar|comprar)",
                r"(?:me lembre|lembrar) de",
                r"(?:marcar|agendar|anotar)",
            ],
            "listar": [
                r"(?:quais|que|o que) (?:são|tenho|tem)",
                r"(?:mostra|mostre|lista|liste)",
                r"(?:minhas? tarefas?|minha agenda)",
                r"(?:como está|verificar) (?:minha|a) (?:agenda|lista)",
            ],
            "concluir": [
                r"(?:concluí|terminei|acabei|finalizei|completei)",
                r"(?:feito|pronto|done)",
                r"(?:marcar? como) (?:concluída?|feita?)",
                r"(?:está|ficou) (?:pronto|feito)",
            ],
            "remover": [
                r"(?:remove|remova|delete|exclui|cancela)",
                r"(?:apaga|tira|tire) (?:a|da|essa) tarefa",
                r"(?:não precisa|descartar|eliminar)",
            ],
            "saudacao": [
                r"^(?:oi|olá|hey|oie|e aí|salve)",
                r"^(?:bom dia|boa tarde|boa noite)",
                r"^(?:como está|como vai|tudo bem)",
            ],
            "gratidao": [
                r"(?:obrigad[oa]|obrigad[oa] mesmo|muito obrigad[oa])",
                r"(?:valeu|brigadão|vlw)",
                r"(?:você é|és) (?:incrível|ótim[oa]|demais)",
            ],
        }

        # Check patterns first (more precise)
        for action, patterns in action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_actions.append((action, 10))  # High score for patterns
                    break

        # If no patterns found, check keywords
        if not detected_actions:
            for action, keywords in self.vocabulario.items():
                score = 0
                for keyword in keywords:
                    if keyword in message_lower:
                        # Score based on word relevance
                        if len(keyword) > 4:  # More specific words have more weight
                            score += 2
                        else:
                            score += 1

                if score > 0:
                    detected_actions.append((action, score))

        # Sort by score and return most likely action
        if detected_actions:
            detected_actions.sort(key=lambda x: x[1], reverse=True)
            return detected_actions[0][0]

        # If still nothing detected, check if it's an educational question first
        from .education import Education
        education = Education()
        if education.detect_educational_intent(message):
            return "consulta"

        # Declarative sentences can be tasks to add, but only if they have action verbs
        action_verbs = [
            "preciso", "tenho que", "vou", "devo", "quero", "vou fazer", "fazer",
            "estudar", "comprar", "terminar"
        ]
        if len(message.split()) > 2 and not message.endswith("?"):
            if any(verb in message_lower for verb in action_verbs):
                return "adicionar"

        # Otherwise, it's a general query
        return "consulta"

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

    def detect_casual_patterns(self, message):
        """
        Detect casual conversation patterns
        """
        message_lower = message.lower()

        casual_patterns = [
            r"\b(oi|olá|hello|hi|ola)\b",
            r"\b(como vai|tudo bem|como está)\b",
            r"\b(obrigad[oa]|thanks|valeu)\b",
            r"\b(tchau|bye|até logo)\b",
        ]

        for pattern in casual_patterns:
            if re.search(pattern, message_lower):
                return True
        return False

    def extract_urgency_indicators(self, message):
        """
        Extract urgency indicators from message
        """
        urgency_indicators = ["urgente", "rápido", "importante", "prioridade", "hoje"]
        message_lower = message.lower()
        
        urgency_level = sum(1 for word in urgency_indicators if word in message_lower)
        return urgency_level

    def extract_emotional_indicators(self, message):
        """
        Extract emotional indicators from message
        """
        message_lower = message.lower()

        stress_indicators = [
            "estressado", "cansado", "difícil", "complicado", "problema",
        ]
        motivation_indicators = ["motivado", "animado", "pronto", "vamos", "conseguir"]

        mood = "neutral"
        if any(word in message_lower for word in stress_indicators):
            mood = "stressed"
        elif any(word in message_lower for word in motivation_indicators):
            mood = "motivated"

        return mood

    def extract_politeness_level(self, message):
        """
        Extract politeness level from message
        """
        message_lower = message.lower()
        politeness_words = ["por favor", "obrigado", "obrigada", "please", "thanks"]
        
        politeness_level = (
            1 if any(word in message_lower for word in politeness_words) else 0
        )
        
        return politeness_level

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import sys
import random
from datetime import datetime, timedelta

# Verificar se os módulos necessários estão instalados
try:
    import requests
    import google.generativeai as genai
except ImportError:
    # Este erro será tratado pelo main.py, então não precisamos exibi-lo aqui
    pass


class LumiAssistant:
    """
    LUMI 2.0 - Assistente de Produtividade Humanizada e Inteligente

    Uma assistente que não é apenas funcional, mas verdadeiramente útil, carismática e indispensável.
    Ela entende contexto, tem personalidade própria e cria conexão real com o usuário.
    """

    def __init__(self, task_manager, reports_generator):
        """
        Inicializa a nova Lumi com inteligência aprimorada e personalidade humanizada
        Agora com Google Gemini para máxima inteligência!
        """        # Configuração do Google Gemini
        self.GEMINI_API_KEY = "AIzaSyAButmMFCGLI48y2BeU1kAdOkL1rggdujA"
        self.GEMINI_MODEL = "gemma-3-1b-it"  # Usando modelo estável disponível

        # Inicializa cliente do Google GenAI
        try:
            genai.configure(api_key=self.GEMINI_API_KEY)
            self.genai_client = genai
            print("✅ Google Gemini inicializado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar Google GenAI: {e}")
            self.genai_client = None

        # Mantém OpenRouter como fallback
        self.API_KEY = (
            "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"
        )
        self.MODEL = "meta-llama/llama-3.1-8b-instruct:free"
        self.BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

        self.task_manager = task_manager
        self.reports_generator = reports_generator

        # Sistema de personalidade e contexto emocional
        self.personality = {
            "emotional_state": "enthusiastic",  # enthusiastic, supportive, focused, celebratory
            "energy_level": 0.8,  # 0.0 to 1.0
            "conversation_style": "friendly_professional",
            "humor_level": 0.6,  # Sutil, não exagerado
            "motivation_mode": "encouraging",
        }

        # Memória de conversa e contexto
        self.conversation_memory = []
        self.user_context = {
            "current_focus": None,
            "productivity_patterns": [],
            "preferences": {},
            "interaction_count": 0,
            "last_task_added": None,
            "mood_indicators": [],
        }

        # Cache inteligente de respostas
        self.response_cache = {}

        # Vocabulário expandido e inteligente para detecção de intenções
        self.vocabulario = {
            "adicionar": [
                "adicionar",
                "adicione",
                "criar",
                "crie",
                "nova",
                "novo",
                "fazer",
                "preciso",
                "tenho que",
                "vou",
                "quero",
                "gostaria",
                "incluir",
                "anotar",
                "lembrar",
                "marcar",
                "registrar",
                "planear",
                "agendar",
            ],
            "listar": [
                "listar",
                "mostrar",
                "ver",
                "quais",
                "que",
                "minhas",
                "tarefas",
                "lista",
                "pendente",
                "pendentes",
                "fazer",
                "falta",
                "restante",
                "próximas",
                "status",
                "situação",
                "andamento",
            ],
            "concluir": [
                "concluir",
                "concluída",
                "terminei",
                "pronto",
                "finalizar",
                "feito",
                "feita",
                "completar",
                "acabei",
                "terminar",
                "finalizado",
                "marcar",
                "completo",
                "done",
                "finished",
            ],
            "remover": [
                "remover",
                "deletar",
                "excluir",
                "tirar",
                "cancelar",
                "eliminar",
                "apagar",
                "retirar",
                "descartar",
                "não precisa",
                "esquecer",
            ],
            "relatório": [
                "relatório",
                "relatorio",
                "resumo",
                "estatística",
                "estatisticas",
                "progresso",
                "performance",
                "desempenho",
                "análise",
                "balanço",
                "overview",
                "dashboard",
                "métricas",
            ],
            "editar": [
                "editar",
                "alterar",
                "modificar",
                "mudar",
                "corrigir",
                "ajustar",
                "atualizar",
                "revisar",
                "refinar",
                "trocar",
            ],
        }  # Padrões regex CORRIGIDOS para extração precisa de títulos de tarefas
        self.task_patterns = [
            # Padrão principal CORRIGIDO para "Adicione na minha agenda, estudar postgresql hoje as 22:00"
            r"(?:adicionar?|adicione|criar?|crie|incluir?|inclua|colocar?|coloque|agendar?|agende|marcar?|marque)\s+(?:na\s+(?:minha\s+)?(?:agenda|lista)\s*,?\s*)?(.+?)(?:\s+(?:hoje|amanhã|amanha|para|até|às?|as|em|na|no|dia|hora)\s+(?:\d+|segunda|terça|quarta|quinta|sexta|sábado|domingo)|$)",
            # Padrões para comandos diretos com aspas
            r'["\']([^"\']+)["\']',
            # Padrões para "preciso/tenho que/vou" + tarefa
            r"(?:preciso|tenho que|vou|quero|gostaria de)\s+(.+?)(?:\s+(?:hoje|amanhã|amanha|na|no|em|para|até|às?|as)\s+|$)",
            # Padrão para tarefas após dois pontos ou vírgula
            r"[,:]\s*(.+?)(?:\s+(?:para|até|em|na|no|hoje|amanhã|às?|as)\s+|$)",
            # Padrão mais específico para capturar a ação principal
            r"(?:fazer|estudar|comprar|ligar|enviar|terminar|completar|preparar|organizar|planejar)\s+(.+?)(?:\s+(?:hoje|amanhã|na|no|em|para|até|às?|as)\s+|$)",
            # Padrão genérico melhorado (último recurso)
            r"(?:tarefa|task|atividade)\s+(.+?)(?:\s+(?:para|até|em|na|no|hoje|amanhã|às?|as)\s+|$)",
        ]

        # Filtros APRIMORADOS para limpeza de títulos
        self.noise_words = [
            "adicionar",
            "adicione",
            "criar",
            "crie",
            "nova",
            "novo",
            "tarefa",
            "task",
            "preciso",
            "tenho",
            "que",
            "vou",
            "quero",
            "gostaria",
            "favor",
            "por",
            "favor",
            "para",
            "de",
            "fazer",
            "incluir",
            "na",
            "nas",
            "lista",
            "tarefas",
            "minha",
            "meu",
            "agenda",
            "hoje",
            "amanhã",
            "amanha",
            "às",
            "as",
            "em",
            "no",
            "da",
            "do",
            "a",
            "o",
        ]

    def _get_personality_response_style(self, action_type, success=True):
        """
        Gera estilo de resposta baseado na personalidade da Lumi
        """
        styles = {
            "task_added": {
                True: [
                    "✨ Perfeito! Adicionei '{}' às suas tarefas. Você está construindo algo incrível!",
                    "🎯 Ótimo! '{}' está na sua lista agora. Vamos transformar isso em realidade!",
                    "⚡ Excelente! Acabei de incluir '{}'. Cada passo conta para o seu sucesso!",
                    "🌟 Pronto! '{}' adicionada com carinho. Você está no caminho certo!",
                    "🚀 Fantástico! '{}' já está na sua agenda produtiva. Bora conquistar!",
                ],
                False: [
                    "😅 Ops! Tive um pequeno problema para adicionar essa tarefa. Pode tentar novamente?",
                    "🤔 Hmm, algo não funcionou como esperado. Vamos tentar de novo?",
                    "💡 Parece que preciso de um pouco mais de informação. Pode reformular?",
                ],
            },
            "tasks_listed": {
                True: [
                    "📋 Aqui estão suas tarefas! Cada uma é um passo rumo ao seu objetivo:",
                    "✨ Sua lista produtiva está aqui! Qual vai ser a próxima conquista?",
                    "🎯 Olha só sua organização! Estas são suas missões atuais:",
                    "⚡ Suas tarefas estão aqui, prontas para serem conquistadas!",
                    "🌟 Sua agenda produtiva! Cada item é uma oportunidade de crescimento:",
                ],
                False: [
                    "🎉 Que maravilha! Sua lista está vazia - significa que você está em dia!",
                    "✨ Nenhuma tarefa pendente! Momento perfeito para relaxar ou planejar algo novo!",
                    "🌟 Lista limpa! Você está mandando muito bem na organização!",
                ],
            },
            "task_completed": {
                True: [
                    "🎉 SUCESSO! '{}' foi finalizada! Você está arrasando!",
                    "⭐ Parabéns! '{}' concluída com maestria! Continue assim!",
                    "🏆 Excelente! Mais uma conquista: '{}' finalizada!",
                    "✨ Incrível! '{}' completada! Cada vitória te leva mais longe!",
                    "🚀 Fantástico! '{}' foi um sucesso! Você é imparável!",
                ],
                False: [
                    "🤔 Não consegui encontrar essa tarefa. Quer verificar o nome exato?",
                    "💡 Hmm, essa tarefa não está na sua lista. Pode conferir para mim?",
                ],
            },
            "task_removed": {
                True: [
                    "✅ Pronto! '{}' foi removida. Às vezes é preciso ajustar o foco!",
                    "🔄 '{}' saiu da lista. Organização é sobre priorizar!",
                    "✨ '{}' removida com sucesso! Foco no que realmente importa!",
                    "🎯 Feito! '{}' não está mais na sua lista. Excelente gestão de prioridades!",
                ],
                False: [
                    "🤔 Não encontrei essa tarefa para remover. Pode verificar o nome?",
                    "💡 Essa tarefa não está na sua lista atual. Quer ver o que tem disponível?",
                ],
            },
        }

        if success:
            import random

            return random.choice(
                styles.get(action_type, {}).get(
                    True, ["✨ Operação realizada com sucesso!"]
                )
            )
        else:
            import random

            return random.choice(
                styles.get(action_type, {}).get(
                    False, ["Algo não funcionou como esperado."]
                )
            )

    def _analyze_context_and_mood(self, message):
        """
        Analisa o contexto e humor da mensagem para adaptar a resposta
        """
        message_lower = message.lower()

        # Indicadores de urgência
        urgency_indicators = ["urgente", "rápido", "importante", "prioridade", "hoje"]
        urgency_level = sum(1 for word in urgency_indicators if word in message_lower)

        # Indicadores emocionais
        stress_indicators = [
            "estressado",
            "cansado",
            "difícil",
            "complicado",
            "problema",
        ]
        motivation_indicators = ["motivado", "animado", "pronto", "vamos", "conseguir"]

        mood = "neutral"
        if any(word in message_lower for word in stress_indicators):
            mood = "stressed"
        elif any(word in message_lower for word in motivation_indicators):
            mood = "motivated"

        # Atualiza contexto do usuário
        self.user_context["mood_indicators"].append(
            {"timestamp": datetime.now(), "mood": mood, "urgency": urgency_level}
        )

        # Mantém apenas os últimos 10 indicadores
        if len(self.user_context["mood_indicators"]) > 10:
            self.user_context["mood_indicators"] = self.user_context["mood_indicators"][
                -10:
            ]

        return {
            "mood": mood,
            "urgency_level": urgency_level,
            "message_length": len(message),
            "politeness_level": (
                1
                if any(
                    word in message_lower
                    for word in ["por favor", "obrigado", "obrigada"]
                )
                else 0
            ),
        }

    def _extract_task_title_intelligent(self, message):
        """
        Extração inteligente de título de tarefa usando múltiplos padrões
        """
        message_clean = message.strip()

        # Primeiro, tenta os padrões regex
        for pattern in self.task_patterns:
            match = re.search(pattern, message_clean, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Remove palavras desnecessárias
                title = self._clean_task_title(title)
                if len(title) > 3:  # Título deve ter pelo menos 3 caracteres
                    return title

        # Se não encontrou com regex, tenta análise semântica simples
        words = message_clean.lower().split()

        # Remove palavras de ruído do início
        start_index = 0
        for i, word in enumerate(words):
            if word not in self.noise_words:
                start_index = i
                break

        # Reconstrói o título
        title_words = words[start_index:]
        if title_words:
            title = " ".join(title_words)
            title = self._clean_task_title(title)
            if len(title) > 3:
                return title  # Como último recurso, usa a mensagem inteira
        fallback_title = self._clean_task_title(message_clean)
        return fallback_title if len(fallback_title) > 3 else "Nova tarefa"

    def _clean_task_title(self, title):
        """
        Limpa o título da tarefa removendo ruídos e formatando adequadamente - VERSÃO CORRIGIDA
        """
        if not title:
            return ""

        # Remove aspas extras e espaços
        title = title.strip("\"'").strip()

        # Remove palavras de ruído do início e fim
        words = title.lower().split()
        original_words = title.split()  # Mantém capitalização original
        filtered_words = []

        # Pula palavras de ruído no início
        start_idx = 0
        for i, word in enumerate(words):
            if word not in self.noise_words:
                start_idx = i
                break

        # Pega palavras relevantes, parando ANTES de indicadores temporais
        for i in range(start_idx, len(words)):
            word = words[i]

            # MELHORIA: Para ANTES de encontrar indicadores de tempo/data
            if word in [
                "hoje",
                "amanhã",
                "amanha",
                "para",
                "às",
                "as",
                "em",
                "na",
                "no",
                "dia",
                "hora",
                "ontem",
                "semana",
                "mes",
                "ano",
            ]:
                break

            # MELHORIA: Para ANTES de números que indicam horário (22:00, 14h, etc.)
            if re.search(r"\d+[:h]", word) or (word.isdigit() and len(word) <= 2):
                break

            # Remove apenas artigos pequenos desnecessários, mas não no começo
            if word not in ["a", "o", "de", "da", "do"] or len(filtered_words) == 0:
                filtered_words.append(
                    original_words[i]
                )  # Mantém capitalização original

        if filtered_words:
            title = " ".join(filtered_words)

        # Remove indicadores temporais residuais do final
        title = re.sub(
            r"\s+(hoje|amanhã|amanha|para|às?|as|em|na|no|dia|hora).*$",
            "",
            title,
            flags=re.IGNORECASE,
        )

        # Capitalização adequada apenas da primeira letra
        title = title.strip()
        if title and len(title) > 0:
            title = title[0].upper() + title[1:]

        return title

    def _detect_action(self, message):
        """
        Detecção inteligente de ação com análise de contexto aprimorada
        """
        message_lower = message.lower()
        detected_actions = []

        # Padrões específicos para cada ação
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

        # Verifica padrões primeiro (mais preciso)
        for action, patterns in action_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    detected_actions.append((action, 10))  # Alta pontuação para padrões
                    break

        # Se não encontrou padrões, verifica palavras-chave
        if not detected_actions:
            for action, keywords in self.vocabulario.items():
                score = 0
                for keyword in keywords:
                    if keyword in message_lower:
                        # Pontuação baseada na relevância da palavra
                        if len(keyword) > 4:  # Palavras mais específicas têm mais peso
                            score += 2
                        else:
                            score += 1

                if score > 0:
                    detected_actions.append((action, score))

        # Ordena por pontuação e retorna a ação mais provável
        if detected_actions:
            detected_actions.sort(key=lambda x: x[1], reverse=True)
            return detected_actions[0][0]        # Se ainda não detectou nada, verifica se é uma pergunta educacional primeiro
        if self._detect_educational_intent(message):
            return "consulta"
              # Frases declarativas podem ser tarefas para adicionar, mas só se tiverem verbos de ação
        action_verbs = ["preciso", "tenho que", "vou", "devo", "quero", "vou fazer", "fazer", "estudar", "comprar", "terminar"]
        if len(message.split()) > 2 and not message.endswith("?"):
            message_lower = message.lower()
            if any(verb in message_lower for verb in action_verbs):
                return "adicionar"
                
        # Caso contrário, é uma consulta geral
        return "consulta"

    def _call_ai_api(self, messages):
        """
        Chama a API de IA com Google Gemini como principal e OpenRouter como fallback
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Primeiro tenta usar o Google Gemini
        if self.genai_client:
            try:
                # Converte as mensagens para o formato do Gemini
                content = self._convert_messages_to_gemini_format(messages)
                
                # Cria o modelo Gemini
                model = self.genai_client.GenerativeModel(self.GEMINI_MODEL)
                
                # Gera o conteúdo
                response = model.generate_content(content)
                
                logger.info(f"✅ Resposta gerada pelo {self.GEMINI_MODEL}")
                print(f"✅ Resposta gerada pelo {self.GEMINI_MODEL}")
                return response.text

            except Exception as e:
                logger.warning(f"⚠️ Erro no Google Gemini, tentando fallback: {e}")
                print(f"⚠️ Erro no Google Gemini, tentando fallback: {e}")

        # Fallback para OpenRouter
        logger.info("🔄 Usando OpenRouter como fallback")
        print("🔄 Usando OpenRouter como fallback")
        return self._call_openrouter_fallback(messages)

    def _convert_messages_to_gemini_format(self, messages):
        """
        Converte mensagens do formato OpenAI para o formato Gemini
        """
        if not messages:
            return "Como posso te ajudar?"

        # Pega apenas a última mensagem do usuário para o Gemini
        last_message = (
            messages[-1] if messages else {"content": "Como posso te ajudar?"}
        )
        return last_message.get("content", "Como posso te ajudar?")

    def _call_openrouter_fallback(self, messages):
        """
        Chama a API do OpenRouter como fallback com tratamento de erro humanizado
        """
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.MODEL,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        try:
            response = requests.post(
                self.BASE_URL, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            return "⏰ Ops! A IA está um pouco lenta hoje. Vou processar sua solicitação diretamente!"
        except requests.exceptions.RequestException as e:
            return f"🤖 A IA externa está indisponível, mas eu posso te ajudar da mesma forma! (Erro: {str(e)})"
        except Exception as e:
            return f"✨ Algo inesperado aconteceu, mas não se preocupe! Vou resolver para você. (Erro: {str(e)})"

    def process_message(self, message):
        """
        Processa mensagem com inteligência contextual e personalidade humanizada
        """
        try:
            # Incrementa contador de interações
            self.user_context["interaction_count"] += 1

            # Analisa contexto e humor
            context = self._analyze_context_and_mood(message)

            # Adiciona à memória de conversa
            self.conversation_memory.append(
                {"timestamp": datetime.now(), "message": message, "context": context}
            )

            # Mantém apenas as últimas 20 interações na memória
            if len(self.conversation_memory) > 20:
                self.conversation_memory = self.conversation_memory[-20:]
            # Detecta ação
            action = self._detect_action(message)

            # NOVA FUNCIONALIDADE: Verifica se é uma pergunta educacional
            if self._detect_educational_intent(message):
                return self._process_educational_query(message)

            # Processa baseado na ação detectada
            if action == "adicionar":
                return self._process_add_task(message)
            elif action == "listar":
                return self._process_list_tasks(message)
            elif action == "concluir":
                return self._process_complete_task(message)
            elif action == "remover":
                return self._process_remove_task(message)
            elif action == "relatório":
                return self._process_generate_report(message)
            elif action == "editar":
                return self._process_edit_task(message)
            else:
                return self._process_general_query(message)

        except Exception as e:
            return f"🤖 Ops! Algo inesperado aconteceu, mas estou aqui para te ajudar de qualquer forma! Erro técnico: {str(e)}"

    def _process_add_task(self, message):
        """
        Adiciona tarefa com resposta personalizada e inteligente
        """
        try:
            # Extrai o título da tarefa
            task_title = self._extract_task_title_intelligent(message)

            if not task_title or len(task_title.strip()) < 3:
                return "💡 Preciso de um pouco mais de detalhes sobre a tarefa que você quer adicionar. Pode me contar melhor?"

            # Adiciona a tarefa
            success = self.task_manager.add_task(task_title)

            if success:
                # Atualiza contexto
                self.user_context["last_task_added"] = task_title
                self.user_context["current_focus"] = task_title

                # Resposta personalizada baseada na personalidade
                response = self._get_personality_response_style(
                    "task_added", True
                ).format(task_title)

                # Adiciona dica motivacional baseada no contexto
                context = self._analyze_context_and_mood(message)
                if context["mood"] == "stressed":
                    response += "\n\n💪 Respirar fundo e focar numa tarefa de cada vez. Você consegue!"
                elif context["urgency_level"] > 0:
                    response += (
                        "\n\n⚡ Detectei que é importante! Que tal começar por essa?"
                    )

                return response
            else:
                return self._get_personality_response_style("task_added", False)

        except Exception as e:
            return f"😅 Tive uma pequena dificuldade técnica para adicionar a tarefa, mas vamos tentar novamente! (Erro: {str(e)})"

    def _process_list_tasks(self, message):
        """
        Lista tarefas com apresentação humanizada e motivacional
        """
        try:
            tasks = self.task_manager.list_tasks()

            if not tasks:
                return self._get_personality_response_style("tasks_listed", False)

            # Cabeçalho motivacional
            response = self._get_personality_response_style("tasks_listed", True)
            response += "\n\n"

            # Lista as tarefas com formatação amigável
            for i, task in enumerate(tasks, 1):
                status_emoji = "✅" if task.get("completed", False) else "📌"
                priority_indicator = ""

                # Adiciona indicador de prioridade baseado na palavra-chave
                task_lower = task["title"].lower()
                if any(
                    word in task_lower
                    for word in ["urgente", "importante", "prioridade"]
                ):
                    priority_indicator = " 🔥"

                response += f"{status_emoji} {i}. {task['title']}{priority_indicator}\n"

            # Adiciona estatística motivacional
            completed_count = sum(1 for task in tasks if task.get("completed", False))
            total_count = len(tasks)
            pending_count = total_count - completed_count

            if completed_count > 0:
                response += f"\n🎯 Progresso: {completed_count}/{total_count} tarefas concluídas!"

            if pending_count > 0:
                response += f"\n⚡ {pending_count} tarefa(s) aguardando sua atenção!"

            # Dica contextual
            if pending_count > 5:
                response += (
                    "\n\n💡 Dica: Que tal focar nas 3 mais importantes primeiro?"
                )
            elif pending_count <= 2:
                response += "\n\n🌟 Você está quase lá! Foco total!"

            return response

        except Exception as e:
            return f"😅 Tive um problema para acessar sua lista de tarefas. Vamos tentar novamente? (Erro: {str(e)})"

    def _process_complete_task(self, message):
        """
        Marca tarefa como concluída com celebração adequada
        """
        try:
            # Extrai identificador da tarefa (número ou nome)
            task_identifier = self._extract_task_identifier(message)

            if not task_identifier:
                return (
                    "🤔 Qual tarefa você concluiu? Pode me dar o número ou nome dela?"
                )

            # Tenta marcar como concluída
            success, task_title = self.task_manager.complete_task(task_identifier)

            if success:
                return self._get_personality_response_style(
                    "task_completed", True
                ).format(task_title)
            else:
                return self._get_personality_response_style("task_completed", False)

        except Exception as e:
            return f"😅 Ops! Tive dificuldade para marcar a tarefa como concluída. Pode tentar novamente? (Erro: {str(e)})"

    def _process_remove_task(self, message):
        """
        Remove tarefa com confirmação humanizada
        """
        try:
            # Extrai identificador da tarefa
            task_identifier = self._extract_task_identifier(message)

            if not task_identifier:
                return "🤔 Qual tarefa você quer remover? Pode me dar o número ou nome dela?"

            # Tenta remover
            success, task_title = self.task_manager.remove_task(task_identifier)

            if success:
                return self._get_personality_response_style(
                    "task_removed", True
                ).format(task_title)
            else:
                return self._get_personality_response_style("task_removed", False)

        except Exception as e:
            return f"😅 Tive dificuldade para remover a tarefa. Pode tentar novamente? (Erro: {str(e)})"

    def _extract_task_identifier(self, message):
        """
        Extrai identificador de tarefa (número ou nome) da mensagem
        """
        # Procura por números
        number_match = re.search(r"\b(\d+)\b", message)
        if number_match:
            return int(number_match.group(1))

        # Procura por nomes entre aspas
        quote_match = re.search(r'["\']([^"\']+)["\']', message)
        if quote_match:
            return quote_match.group(1)

        # Tenta extrair usando padrões similares ao de adicionar tarefa
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

    def _process_edit_task(self, message):
        """
        Processa edição de tarefa (funcionalidade futura)
        """
        return "✨ A funcionalidade de edição está sendo aprimorada! Por enquanto, você pode remover a tarefa e criar uma nova versão."

    def _process_generate_report(self, message):
        """
        Gera relatório com apresentação humanizada
        """
        try:
            report = self.reports_generator.generate_daily_report()

            if not report or "Nenhuma tarefa encontrada" in report:
                return "📊 Ainda não temos dados suficientes para um relatório completo. Que tal adicionar algumas tarefas primeiro?"

            # Humaniza o relatório
            humanized_report = "📈 **SEU RELATÓRIO DE PRODUTIVIDADE**\n\n"
            humanized_report += "Aqui está um resumo do seu progresso incrível:\n\n"
            humanized_report += report
            humanized_report += (
                "\n\n✨ Cada número aqui representa seu crescimento e dedicação!"
            )

            return humanized_report

        except Exception as e:
            return f"😅 Tive dificuldade para gerar o relatório. Vamos tentar novamente? (Erro: {str(e)})"

    def _process_general_query(self, message):
        """
        Processa consultas gerais usando IA quando necessário
        """
        try:
            # Verifica se é uma saudação ou conversa casual
            casual_patterns = [
                r"\b(oi|olá|hello|hi|ola)\b",
                r"\b(como vai|tudo bem|como está)\b",
                r"\b(obrigad[oa]|thanks|valeu)\b",
                r"\b(tchau|bye|até logo)\b",
            ]

            message_lower = message.lower()
            for pattern in casual_patterns:
                if re.search(pattern, message_lower):
                    return self._get_casual_response(message_lower)

            # Para consultas mais complexas, usa a IA
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

            ai_response = self._call_ai_api(messages)
            return ai_response

        except Exception as e:
            return "✨ Estou aqui para te ajudar com suas tarefas e produtividade! Que tal começarmos adicionando uma nova tarefa?"

    def _get_casual_response(self, message_lower):
        """
        Respostas para interações casuais e sociais
        """
        if any(word in message_lower for word in ["oi", "olá", "hello", "hi", "ola"]):
            greetings = [
                "✨ Oi! Sou a Lumi, sua assistente de produtividade! Como posso te ajudar hoje?",
                "🌟 Olá! Pronta para tornar seu dia mais produtivo! O que vamos conquistar?",
                "⚡ Oi! Que bom te ver! Vamos organizar suas tarefas e arrasar hoje?",
                "🎯 Olá! Sou a Lumi e estou aqui para te ajudar a ser ainda mais incrível!",
            ]
            import random

            return random.choice(greetings)

        elif any(
            word in message_lower for word in ["como vai", "tudo bem", "como está"]
        ):
            return "🌟 Estou ótima e super motivada para te ajudar! Como está seu dia produtivo? Posso te ajudar com alguma tarefa?"

        elif any(word in message_lower for word in ["obrigad", "thanks", "valeu"]):
            return "😊 Fico feliz em ajudar! Estou sempre aqui quando precisar. Vamos continuar construindo seu sucesso juntas!"

        elif any(word in message_lower for word in ["tchau", "bye", "até logo"]):
            return "� Até logo! Espero te ver em breve para mais conquistas! Lembre-se: você é capaz de coisas incríveis!"

        return "✨ Estou aqui para te ajudar com suas tarefas e produtividade! Como posso tornar seu dia melhor?"

    def get_user_stats(self):
        """
        Retorna estatísticas humanizadas do usuário
        """
        stats = {
            "interactions": self.user_context["interaction_count"],
            "tasks_in_memory": len(
                [
                    m
                    for m in self.conversation_memory
                    if "tarefa" in m.get("message", "").lower()
                ]
            ),
            "last_task": self.user_context.get("last_task_added", "Nenhuma"),
            "mood_trend": self._analyze_mood_trend(),
            "productivity_level": self._calculate_productivity_level(),
        }
        return stats

    def _analyze_mood_trend(self):
        """
        Analisa tendência de humor baseada nas últimas interações
        """
        if not self.user_context["mood_indicators"]:
            return "neutral"

        recent_moods = [m["mood"] for m in self.user_context["mood_indicators"][-5:]]
        if recent_moods.count("motivated") > recent_moods.count("stressed"):
            return "positive"
        elif recent_moods.count("stressed") > recent_moods.count("motivated"):
            return "needs_support"
        return "balanced"

    def _calculate_productivity_level(self):
        """
        Calcula nível de produtividade baseado em padrões de uso
        """
        if self.user_context["interaction_count"] < 5:
            return "getting_started"
        elif self.user_context["interaction_count"] < 20:
            return "building_momentum"
        elif self.user_context["interaction_count"] < 50:
            return "productive"
        else:
            return "power_user"

    # ========== CAPACIDADES EDUCACIONAIS DA LUMI ==========

    def _detect_educational_intent(self, message):
        """
        Detecta se a mensagem é uma pergunta educacional ou pedido de explicação
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

    def _process_educational_query(self, message):
        """
        Processa perguntas educacionais com a personalidade da Lumi
        """
        try:
            # Extrai o tópico da pergunta
            topic = self._extract_educational_topic(message)

            # Verifica se é pedido de dicas de estudo
            if any(
                phrase in message.lower()
                for phrase in ["dicas", "como estudar", "cronograma", "plano de estudo"]
            ):
                return self._provide_study_tips(topic)

            # Verifica se é sobre conceitos importantes
            if any(
                phrase in message.lower()
                for phrase in ["conceitos", "principais", "importantes"]
            ):
                return self._explain_key_concepts(topic)

            # Gera explicação educacional
            return self._generate_educational_explanation(topic, message)

        except Exception as e:
            return f"🤔 Adoraria te ajudar a entender melhor! Pode reformular sua pergunta? Enquanto isso, que tal adicionarmos uma tarefa de estudo sobre esse assunto?"

    def _extract_educational_topic(self, message):
        """
        Extrai o tópico educacional da mensagem
        """
        # Remove palavras de pergunta para focar no tópico
        message_clean = re.sub(
            r"\b(explique|explica|o que é|como funciona|ensine|ensina|me ajude|help)\b",
            "",
            message.lower(),
        )
        message_clean = re.sub(
            r"\b(sobre|about|acerca de|conceitos|mais importantes)\b", "", message_clean
        )
        message_clean = message_clean.strip()

        # Tópicos específicos conhecidos
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

        # Procura por tópicos conhecidos
        for topic, keywords in known_topics.items():
            for keyword in keywords:
                if keyword in message_clean:
                    return topic

        # Se não encontrou tópico específico, retorna as palavras principais
        words = message_clean.split()
        # Remove palavras muito comuns
        stop_words = [
            "a",
            "o",
            "e",
            "de",
            "da",
            "do",
            "em",
            "na",
            "no",
            "para",
            "com",
            "como",
            "que",
            "é",
            "são",
            "no",
        ]
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]

        if meaningful_words:
            return " ".join(meaningful_words[:3])  # Máximo 3 palavras

        return "programação"  # Fallback padrão

    def _explain_key_concepts(self, topic):
        """
        Explica conceitos principais sobre um tópico específico
        """
        concepts = {
            "postgresql": {
                "concepts": [
                    "🗄️ **Tabelas e Esquemas**: A estrutura básica onde seus dados ficam organizados",
                    "🔗 **Relacionamentos (JOINs)**: Como conectar informações entre tabelas",
                    "🔍 **Consultas SQL**: SELECT, INSERT, UPDATE, DELETE - os comandos essenciais",
                    "🎯 **Índices**: Para fazer suas consultas voarem!",
                    "🔐 **Constraints**: Regras que mantêm seus dados íntegros",
                    "⚡ **Stored Procedures**: Funções que rodam direto no banco",
                    "📊 **Views**: Consultas salvas para facilitar sua vida",
                ],
                "tip": "💡 **Dica da Lumi**: Comece dominando SELECT com JOINs - é a base de tudo no PostgreSQL! Depois parta para INSERT/UPDATE/DELETE.",
            },
            "python": {
                "concepts": [
                    "📝 **Variáveis e Tipos**: int, str, list, dict - os blocos básicos",
                    "🔄 **Estruturas de Controle**: if/else, for, while - controlando o fluxo",
                    "🎯 **Funções**: Organizando seu código em pedaços reutilizáveis",
                    "📦 **Modules e Packages**: Usando bibliotecas e organizando projetos",
                    "🏗️ **Classes e Objetos**: Programação orientada a objetos",
                    "⚠️ **Tratamento de Erros**: try/except para código robusto",
                    "📚 **Bibliotecas**: pandas, numpy, requests e outras ferramentas poderosas",
                ],
                "tip": "💡 **Dica da Lumi**: Python é como conversar com o computador de forma amigável! Comece com variáveis e funções, pratique um pouquinho todo dia.",
            },
            "javascript": {
                "concepts": [
                    "⚡ **Variáveis e Escopo**: let, const, var - como armazenar dados",
                    "🎭 **Funções**: function, arrow functions, callbacks",
                    "🏠 **DOM Manipulation**: Fazendo páginas interativas",
                    "⏰ **Eventos**: Click, hover, submit - reagindo às ações do usuário",
                    "🔄 **Promises e Async/Await**: Lidando com operações assíncronas",
                    "📡 **APIs e Fetch**: Buscando dados de serviços externos",
                    "🎨 **Frameworks**: React, Vue, Angular - construindo apps modernas",
                ],
                "tip": "💡 **Dica da Lumi**: JavaScript é a magia por trás da web! Comece entendendo como manipular elementos da página, depois evolua para APIs.",
            },
        }

        topic_lower = topic.lower()
        for key in concepts:
            if key in topic_lower:
                info = concepts[key]
                response = f"🎯 **Conceitos principais de {topic.upper()}:**\n\n"
                response += "\n\n".join(info["concepts"])
                response += f"\n\n{info['tip']}"
                response += f"\n\n✨ Quer que eu adicione uma tarefa de estudo sobre algum desses conceitos? É só me dizer!"
                return response

        # Resposta genérica para tópicos não mapeados
        return f"""🤔 **{topic.title()}** é um assunto bem interessante! 

📚 Embora eu não tenha os conceitos específicos na ponta da língua, posso te ajudar de outras formas:

✅ **Criar tarefas de estudo estruturadas** sobre {topic}
🎯 **Sugerir um cronograma** de aprendizado
📝 **Organizar suas sessões de estudo** para máxima eficiência

💡 **Dica**: Que tal começarmos adicionando "Pesquisar conceitos básicos de {topic}" às suas tarefas? Assim você pode começar a explorar!

🌟 **Fala comigo**: "Adicione estudar conceitos de {topic}" e eu organizo isso para você!"""

    def _generate_educational_explanation(self, topic, message):
        """
        Gera explicações educacionais claras e didáticas com a personalidade da Lumi
        """
        try:
            # Monta um prompt educacional para a IA
            educational_prompt = f"""Como Lumi, uma assistente educacional entusiástica e didática, responda a esta pergunta de forma clara e motivadora:

Pergunta: {message}
Tópico: {topic}

Diretrizes para sua resposta:
- Use linguagem acessível e exemplos práticos
- Seja didática mas não condescendente  
- Mantenha tom motivacional e encorajador
- Use emojis para tornar mais visual (mas sem exagerar)
- Inclua dicas práticas quando relevante
- Mantenha explicação concisa mas completa
- Sempre termine sugerindo como posso ajudar mais (tarefas, cronograma, etc.)

Seja a Lumi: carismática, inteligente e genuinamente preocupada em ajudar o usuário a aprender!"""

            # Chama a IA externa
            messages = [
                {"role": "system", "content": educational_prompt},
                {"role": "user", "content": message},
            ]

            response = self._call_ai_api(messages)

            if response and "erro" not in response.lower():
                return response
            else:
                return self._fallback_educational_response(topic, message)

        except Exception as e:
            return self._fallback_educational_response(topic, message)

    def _fallback_educational_response(self, topic, message):
        """
        Resposta educacional de fallback quando a API externa não está disponível
        """
        fallback_responses = {
            "postgresql": {
                "explanation": "🗄️ **PostgreSQL** é um sistema de banco de dados relacional super poderoso! É como um armário gigante e organizado onde você guarda informações de forma estruturada.",
                "tips": "📝 **Dica de estudo**: Comece aprendendo SQL básico (SELECT, INSERT, UPDATE, DELETE), depois explore funcionalidades avançadas como JOINs e stored procedures!",
            },
            "python": {
                "explanation": "🐍 **Python** é uma linguagem de programação incrível! É como aprender um novo idioma para conversar com computadores, mas muito mais amigável que outros.",
                "tips": "💡 **Dica**: Pratique um pouquinho todo dia. Python é perfeito para iniciantes porque a sintaxe é bem clara e legível!",
            },
            "javascript": {
                "explanation": "⚡ **JavaScript** é a linguagem que dá vida às páginas web! É como a mágica que faz botões funcionarem e páginas ficarem interativas.",
                "tips": "🚀 **Dica**: Comece com o básico (variáveis, funções) e depois parta para manipulação do DOM (elementos da página)!",
            },
        }

        topic_lower = topic.lower()
        for key in fallback_responses:
            if key in topic_lower:
                response = fallback_responses[key]
                return f"{response['explanation']}\n\n{response['tips']}\n\n✨ **Quer que eu ajude você a criar uma tarefa de estudo sobre isso?** É só me dizer!"

        # Resposta genérica motivacional
        return f"""🤔 Essa é uma pergunta interessante sobre **{topic}**! 

📚 Embora eu não tenha uma explicação específica na ponta da língua, posso te ajudar de outras formas incríveis:

✅ **Criar uma tarefa de estudo** sobre {topic}
🎯 **Sugerir fontes de pesquisa** confiáveis  
📝 **Organizar um cronograma** de estudos personalizado
💡 **Dar dicas de como estudar** de forma mais eficiente

🌟 **Que tal começarmos adicionando "{topic}" nas suas tarefas de estudo?** Assim você não esquece de pesquisar sobre isso!

💪 **Fala comigo**: "Adicione estudar {topic}" e eu organizo tudo para você!"""

    def _provide_study_tips(self, subject=None):
        """
        Fornece dicas de estudo motivacionais e práticas com a personalidade da Lumi
        """
        general_tips = [
            "🧠 **Técnica Pomodoro**: 25 min focado + 5 min pausa = produtividade máxima!",
            "📝 **Anote à mão**: pesquisas mostram que escrever à mão melhora a memorização!",
            "🔄 **Revisão espaçada**: revise o conteúdo em 1 dia, 3 dias, 1 semana e 1 mês!",
            "👥 **Ensine para alguém**: se conseguir explicar, você realmente entendeu!",
            "🎯 **Metas pequenas**: divida tópicos grandes em partes menores e celebre cada conquista!",
            "🏃‍♀️ **Estude ativamente**: faça resumos, mapas mentais, exercícios práticos!",
            "😴 **Durma bem**: o cérebro consolida o aprendizado durante o sono!",
        ]

        specific_tips = {
            "programação": [
                "💻 **Pratique diariamente**: mesmo 15 minutos por dia fazem diferença!",
                "🐛 **Depure com paciência**: cada erro é uma oportunidade de aprender!",
                "🔨 **Projetos práticos**: teoria + prática = aprendizado sólido!",
                "👥 **Comunidade**: participe de fóruns e grupos de estudo!",
            ],
            "banco de dados": [
                "🗄️ **Modele antes de codificar**: desenhe o banco primeiro!",
                "📊 **Dados de exemplo**: sempre teste com dados reais!",
                "⚡ **Performance**: aprenda sobre índices e otimização!",
                "🔍 **Explore**: use ferramentas visuais para entender melhor!",
            ],
        }

        tips = general_tips.copy()
        if subject:
            subject_lower = subject.lower()
            if any(
                lang in subject_lower
                for lang in ["python", "javascript", "programação", "programming"]
            ):
                tips.extend(specific_tips["programação"])
            elif any(
                db in subject_lower for db in ["postgresql", "sql", "banco", "database"]
            ):
                tips.extend(specific_tips["banco de dados"])

        selected_tips = random.sample(tips, min(4, len(tips)))
        response = "💡 **Dicas de estudo da Lumi:**\n\n"
        response += "\n\n".join(selected_tips)
        response += "\n\n🌟 **Lembre-se**: consistência supera intensidade! Pequenos passos todos os dias levam a grandes conquistas!"
        response += "\n\n✨ **Quer que eu crie um cronograma de estudos personalizado para você?** É só me dizer o assunto!"

        return response

    # Mantendo compatibilidade com métodos antigos
    def generate_response(self, message):
        """Método de compatibilidade - redireciona para process_message"""
        return self.process_message(message)

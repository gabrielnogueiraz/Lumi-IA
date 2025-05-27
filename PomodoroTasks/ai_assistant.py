#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import sys
from datetime import datetime, timedelta

# Verificar se o módulo requests está instalado
try:
    import requests
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
        """
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
            "motivation_mode": "encouraging"
        }
        
        # Memória de conversa e contexto
        self.conversation_memory = []
        self.user_context = {
            "current_focus": None,
            "productivity_patterns": [],
            "preferences": {},
            "interaction_count": 0,
            "last_task_added": None,
            "mood_indicators": []
        }

        # Cache inteligente de respostas
        self.response_cache = {}
        
        # Vocabulário expandido e inteligente para detecção de intenções
        self.vocabulario = {
            "adicionar": [
                "adicionar", "adicione", "criar", "crie", "nova", "novo", "fazer", 
                "preciso", "tenho que", "vou", "quero", "gostaria", "incluir",
                "anotar", "lembrar", "marcar", "registrar", "planear", "agendar"
            ],
            "listar": [
                "listar", "mostrar", "ver", "quais", "que", "minhas", "tarefas",
                "lista", "pendente", "pendentes", "fazer", "falta", "restante",
                "próximas", "status", "situação", "andamento"
            ],
            "concluir": [
                "concluir", "concluída", "terminei", "pronto", "finalizar",
                "feito", "feita", "completar", "acabei", "terminar", "finalizado",
                "marcar", "completo", "done", "finished"
            ],
            "remover": [
                "remover", "deletar", "excluir", "tirar", "cancelar", "eliminar",
                "apagar", "retirar", "descartar", "não precisa", "esquecer"
            ],
            "relatório": [
                "relatório", "relatorio", "resumo", "estatística", "estatisticas",
                "progresso", "performance", "desempenho", "análise", "balanço",
                "overview", "dashboard", "métricas"
            ],
            "editar": [
                "editar", "alterar", "modificar", "mudar", "corrigir", "ajustar",
                "atualizar", "revisar", "refinar", "trocar"
            ]
        }

        # Padrões regex avançados para extração de títulos de tarefas
        self.task_patterns = [
            # Padrões diretos com palavras-chave
            r'(?:adicionar|criar|nova|novo|incluir)\s+(?:tarefa\s+)?["\']([^"\']+)["\']',
            r'(?:adicionar|criar|nova|novo|incluir)\s+(?:tarefa\s+)?(.+?)(?:\s+(?:para|até|em|na|no)\s+|$)',
            
            # Padrões com "preciso", "tenho que", "vou"
            r'(?:preciso|tenho que|vou|quero|gostaria de)\s+(.+?)(?:\s+(?:hoje|amanhã|na|no|em|para|até)\s+|$)',
            
            # Padrões entre aspas
            r'["\']([^"\']+)["\']',
            
            # Padrões após dois pontos
            r':\s*(.+?)(?:\s+(?:para|até|em|na|no)\s+|$)',
            
            # Padrão genérico (último recurso)
            r'(?:tarefa|task|fazer|lembrar)\s+(.+?)(?:\s+(?:para|até|em|na|no|hoje|amanhã)\s+|$)'
        ]
        
        # Filtros para limpeza de títulos
        self.noise_words = [
            'adicionar', 'criar', 'nova', 'novo', 'tarefa', 'task', 'preciso', 
            'tenho que', 'vou', 'quero', 'gostaria', 'favor', 'por favor',
            'para', 'de', 'fazer', 'incluir', 'na lista', 'nas tarefas'
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
                    "🚀 Fantástico! '{}' já está na sua agenda produtiva. Bora conquistar!"
                ],
                False: [
                    "😅 Ops! Tive um pequeno problema para adicionar essa tarefa. Pode tentar novamente?",
                    "🤔 Hmm, algo não funcionou como esperado. Vamos tentar de novo?",
                    "💡 Parece que preciso de um pouco mais de informação. Pode reformular?"
                ]
            },
            "tasks_listed": {
                True: [
                    "📋 Aqui estão suas tarefas! Cada uma é um passo rumo ao seu objetivo:",
                    "✨ Sua lista produtiva está aqui! Qual vai ser a próxima conquista?",
                    "🎯 Olha só sua organização! Estas são suas missões atuais:",
                    "⚡ Suas tarefas estão aqui, prontas para serem conquistadas!",
                    "🌟 Sua agenda produtiva! Cada item é uma oportunidade de crescimento:"
                ],
                False: [
                    "🎉 Que maravilha! Sua lista está vazia - significa que você está em dia!",
                    "✨ Nenhuma tarefa pendente! Momento perfeito para relaxar ou planejar algo novo!",
                    "🌟 Lista limpa! Você está mandando muito bem na organização!"
                ]
            },
            "task_completed": {
                True: [
                    "🎉 SUCESSO! '{}' foi finalizada! Você está arrasando!",
                    "⭐ Parabéns! '{}' concluída com maestria! Continue assim!",
                    "🏆 Excelente! Mais uma conquista: '{}' finalizada!",
                    "✨ Incrível! '{}' completada! Cada vitória te leva mais longe!",
                    "🚀 Fantástico! '{}' foi um sucesso! Você é imparável!"
                ],
                False: [
                    "🤔 Não consegui encontrar essa tarefa. Quer verificar o nome exato?",
                    "💡 Hmm, essa tarefa não está na sua lista. Pode conferir para mim?"
                ]
            },
            "task_removed": {
                True: [
                    "✅ Pronto! '{}' foi removida. Às vezes é preciso ajustar o foco!",
                    "🔄 '{}' saiu da lista. Organização é sobre priorizar!",
                    "✨ '{}' removida com sucesso! Foco no que realmente importa!",
                    "🎯 Feito! '{}' não está mais na sua lista. Excelente gestão de prioridades!"
                ],
                False: [
                    "🤔 Não encontrei essa tarefa para remover. Pode verificar o nome?",
                    "💡 Essa tarefa não está na sua lista atual. Quer ver o que tem disponível?"
                ]
            }
        }
        
        if success:
            import random
            return random.choice(styles.get(action_type, {}).get(True, ["✨ Operação realizada com sucesso!"]))
        else:
            import random
            return random.choice(styles.get(action_type, {}).get(False, ["Algo não funcionou como esperado."]))

    def _analyze_context_and_mood(self, message):
        """
        Analisa o contexto e humor da mensagem para adaptar a resposta
        """
        message_lower = message.lower()
        
        # Indicadores de urgência
        urgency_indicators = ['urgente', 'rápido', 'importante', 'prioridade', 'hoje']
        urgency_level = sum(1 for word in urgency_indicators if word in message_lower)
        
        # Indicadores emocionais
        stress_indicators = ['estressado', 'cansado', 'difícil', 'complicado', 'problema']
        motivation_indicators = ['motivado', 'animado', 'pronto', 'vamos', 'conseguir']
        
        mood = "neutral"
        if any(word in message_lower for word in stress_indicators):
            mood = "stressed"
        elif any(word in message_lower for word in motivation_indicators):
            mood = "motivated"
        
        # Atualiza contexto do usuário
        self.user_context['mood_indicators'].append({
            'timestamp': datetime.now(),
            'mood': mood,
            'urgency': urgency_level
        })
        
        # Mantém apenas os últimos 10 indicadores
        if len(self.user_context['mood_indicators']) > 10:
            self.user_context['mood_indicators'] = self.user_context['mood_indicators'][-10:]
        
        return {
            'mood': mood,
            'urgency_level': urgency_level,
            'message_length': len(message),
            'politeness_level': 1 if any(word in message_lower for word in ['por favor', 'obrigado', 'obrigada']) else 0
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
            title = ' '.join(title_words)
            title = self._clean_task_title(title)
            if len(title) > 3:
                return title
        
        # Como último recurso, usa a mensagem inteira
        fallback_title = self._clean_task_title(message_clean)
        return fallback_title if len(fallback_title) > 3 else "Nova tarefa"

    def _clean_task_title(self, title):
        """
        Limpa o título da tarefa removendo ruídos e formatando adequadamente
        """
        # Remove aspas extras
        title = title.strip('"\'')
        
        # Remove palavras de ruído no início
        words = title.lower().split()
        filtered_words = []
        skip_next = False
        
        for i, word in enumerate(words):
            if skip_next:
                skip_next = False
                continue
                
            if word in self.noise_words and i < 3:  # Remove ruído apenas no início
                if word in ['preciso', 'tenho'] and i + 1 < len(words) and words[i + 1] == 'que':
                    skip_next = True  # Pula "tenho que"
                continue
            filtered_words.append(word)
        
        if filtered_words:
            title = ' '.join(filtered_words)
        
        # Capitalização adequada
        title = title.strip()
        if title:        title = title[0].upper() + title[1:]
        
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
                r"(?:marcar|agendar|anotar)"
            ],
            "listar": [
                r"(?:quais|que|o que) (?:são|tenho|tem)",
                r"(?:mostra|mostre|lista|liste)",
                r"(?:minhas? tarefas?|minha agenda)",
                r"(?:como está|verificar) (?:minha|a) (?:agenda|lista)"
            ],
            "concluir": [
                r"(?:concluí|terminei|acabei|finalizei|completei)",
                r"(?:feito|pronto|done)",
                r"(?:marcar? como) (?:concluída?|feita?)",
                r"(?:está|ficou) (?:pronto|feito)"
            ],
            "remover": [
                r"(?:remove|remova|delete|exclui|cancela)",
                r"(?:apaga|tira|tire) (?:a|da|essa) tarefa",
                r"(?:não precisa|descartar|eliminar)"
            ],
            "saudacao": [
                r"^(?:oi|olá|hey|oie|e aí|salve)",
                r"^(?:bom dia|boa tarde|boa noite)",
                r"^(?:como está|como vai|tudo bem)"
            ],
            "gratidao": [
                r"(?:obrigad[oa]|obrigad[oa] mesmo|muito obrigad[oa])",
                r"(?:valeu|brigadão|vlw)",
                r"(?:você é|és) (?:incrível|ótim[oa]|demais)"
            ]
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
            return detected_actions[0][0]
        
        # Se ainda não detectou nada, tenta inferir pelo contexto
        # Frases declarativas geralmente são tarefas para adicionar
        if len(message.split()) > 2 and not message.endswith('?'):
            return "adicionar"
        
        # Caso contrário, é uma consulta geral
        return "consulta"

    def _call_openrouter_api(self, messages):
        """
        Chama a API do OpenRouter com tratamento de erro humanizado
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
            response = requests.post(self.BASE_URL, headers=headers, json=data, timeout=30)
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
            self.user_context['interaction_count'] += 1
            
            # Analisa contexto e humor
            context = self._analyze_context_and_mood(message)
            
            # Adiciona à memória de conversa
            self.conversation_memory.append({
                'timestamp': datetime.now(),
                'message': message,
                'context': context
            })
            
            # Mantém apenas as últimas 20 interações na memória
            if len(self.conversation_memory) > 20:
                self.conversation_memory = self.conversation_memory[-20:]
            
            # Detecta ação
            action = self._detect_action(message)
            
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
                self.user_context['last_task_added'] = task_title
                self.user_context['current_focus'] = task_title
                
                # Resposta personalizada baseada na personalidade
                response = self._get_personality_response_style("task_added", True).format(task_title)
                
                # Adiciona dica motivacional baseada no contexto
                context = self._analyze_context_and_mood(message)
                if context['mood'] == 'stressed':
                    response += "\n\n💪 Respirar fundo e focar numa tarefa de cada vez. Você consegue!"
                elif context['urgency_level'] > 0:
                    response += "\n\n⚡ Detectei que é importante! Que tal começar por essa?"
                
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
                task_lower = task['title'].lower()
                if any(word in task_lower for word in ['urgente', 'importante', 'prioridade']):
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
                response += "\n\n💡 Dica: Que tal focar nas 3 mais importantes primeiro?"
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
                return "🤔 Qual tarefa você concluiu? Pode me dar o número ou nome dela?"
            
            # Tenta marcar como concluída
            success, task_title = self.task_manager.complete_task(task_identifier)
            
            if success:
                return self._get_personality_response_style("task_completed", True).format(task_title)
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
                return self._get_personality_response_style("task_removed", True).format(task_title)
            else:
                return self._get_personality_response_style("task_removed", False)
                
        except Exception as e:
            return f"😅 Tive dificuldade para remover a tarefa. Pode tentar novamente? (Erro: {str(e)})"

    def _extract_task_identifier(self, message):
        """
        Extrai identificador de tarefa (número ou nome) da mensagem
        """
        # Procura por números
        number_match = re.search(r'\b(\d+)\b', message)
        if number_match:
            return int(number_match.group(1))
        
        # Procura por nomes entre aspas
        quote_match = re.search(r'["\']([^"\']+)["\']', message)
        if quote_match:
            return quote_match.group(1)
        
        # Tenta extrair usando padrões similares ao de adicionar tarefa
        patterns = [
            r'(?:concluir|finalizar|completar|terminar|concluída|feita)\s+(.+?)(?:\s+(?:hoje|agora|já)\s*|$)',
            r'(?:remover|deletar|excluir|tirar)\s+(.+?)(?:\s+(?:da lista|das tarefas)\s*|$)',
            r'(?:tarefa|task)\s+(.+?)(?:\s+(?:concluída|removida|deletada)\s*|$)'
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
            humanized_report += "\n\n✨ Cada número aqui representa seu crescimento e dedicação!"
            
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
                r'\b(oi|olá|hello|hi|ola)\b',
                r'\b(como vai|tudo bem|como está)\b',
                r'\b(obrigad[oa]|thanks|valeu)\b',
                r'\b(tchau|bye|até logo)\b'
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
                    Se a pergunta não for relacionada a produtividade, redirecione gentilmente para suas funcionalidades."""
                },
                {
                    "role": "user", 
                    "content": message
                }
            ]
            
            ai_response = self._call_openrouter_api(messages)
            return ai_response
            
        except Exception as e:
            return "✨ Estou aqui para te ajudar com suas tarefas e produtividade! Que tal começarmos adicionando uma nova tarefa?"

    def _get_casual_response(self, message_lower):
        """
        Respostas para interações casuais e sociais
        """
        if any(word in message_lower for word in ['oi', 'olá', 'hello', 'hi', 'ola']):
            greetings = [
                "✨ Oi! Sou a Lumi, sua assistente de produtividade! Como posso te ajudar hoje?",
                "🌟 Olá! Pronta para tornar seu dia mais produtivo! O que vamos conquistar?",
                "⚡ Oi! Que bom te ver! Vamos organizar suas tarefas e arrasar hoje?",
                "🎯 Olá! Sou a Lumi e estou aqui para te ajudar a ser ainda mais incrível!"
            ]
            import random
            return random.choice(greetings)
            
        elif any(word in message_lower for word in ['como vai', 'tudo bem', 'como está']):
            return "🌟 Estou ótima e super motivada para te ajudar! Como está seu dia produtivo? Posso te ajudar com alguma tarefa?"
            
        elif any(word in message_lower for word in ['obrigad', 'thanks', 'valeu']):
            return "😊 Fico feliz em ajudar! Estou sempre aqui quando precisar. Vamos continuar construindo seu sucesso juntas!"
            
        elif any(word in message_lower for word in ['tchau', 'bye', 'até logo']):
            return "👋 Até logo! Espero te ver em breve para mais conquistas! Lembre-se: você é capaz de coisas incríveis!"
            
        return "✨ Estou aqui para te ajudar com suas tarefas e produtividade! Como posso tornar seu dia melhor?"

    def get_user_stats(self):
        """
        Retorna estatísticas humanizadas do usuário
        """
        stats = {
            'interactions': self.user_context['interaction_count'],
            'tasks_in_memory': len([m for m in self.conversation_memory if 'tarefa' in m.get('message', '').lower()]),
            'last_task': self.user_context.get('last_task_added', 'Nenhuma'),
            'mood_trend': self._analyze_mood_trend(),
            'productivity_level': self._calculate_productivity_level()
        }
        return stats

    def _analyze_mood_trend(self):
        """
        Analisa tendência de humor baseada nas últimas interações
        """
        if not self.user_context['mood_indicators']:
            return "neutral"
        
        recent_moods = [m['mood'] for m in self.user_context['mood_indicators'][-5:]]
        if recent_moods.count('motivated') > recent_moods.count('stressed'):
            return "positive"
        elif recent_moods.count('stressed') > recent_moods.count('motivated'):
            return "needs_support"
        return "balanced"

    def _calculate_productivity_level(self):
        """
        Calcula nível de produtividade baseado em padrões de uso
        """
        if self.user_context['interaction_count'] < 5:
            return "getting_started"
        elif self.user_context['interaction_count'] < 20:
            return "building_momentum"
        elif self.user_context['interaction_count'] < 50:
            return "productive"
        else:
            return "power_user"

    # Mantendo compatibilidade com métodos antigos
    def generate_response(self, message):
        """Método de compatibilidade - redireciona para process_message"""
        return self.process_message(message)

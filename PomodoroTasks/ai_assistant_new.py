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

        # Sistema de personalidade e memória da Lumi
        self.personality = {
            "energy_level": "high",  # high, medium, low
            "conversation_style": "friendly_professional",
            "humor_level": "light",
            "enthusiasm": "high",
            "current_mood": "motivated"
        }
        
        # Cache inteligente e memória de conversas
        self.conversation_memory = []
        self.user_preferences = {
            "communication_style": "casual",
            "preferred_emojis": True,
            "task_reminder_style": "gentle",
            "learning_topics_interest": [],
            "productivity_goals": [],
            "interaction_patterns": {}
        }
        
        # Sistema de análise de contexto avançado
        self.context_analyzer = {
            "last_interactions": [],
            "topic_continuity": None,
            "user_mood_detected": "neutral",
            "conversation_flow": "new"
        }

        # Vocabulário expandido e inteligente
        self.smart_vocabulary = {
            "greetings": [
                "oi", "olá", "ola", "hey", "e aí", "e ai", "bom dia", "boa tarde", 
                "boa noite", "salve", "eae", "hello", "hi", "lumi"
            ],
            "gratitude": [
                "obrigado", "obrigada", "valeu", "vlw", "thanks", "thx", "muito obrigado",
                "brigado", "brigada", "grato", "grata"
            ],
            "task_actions": {
                "add": [
                    "adicionar", "adicione", "criar", "crie", "incluir", "inclua",
                    "colocar", "coloque", "agendar", "agende", "marcar", "marque",
                    "anotar", "anote", "lembrar", "me lembre", "preciso", "tenho que",
                    "vou fazer", "fazer", "nova tarefa", "novo compromisso"
                ],
                "remove": [
                    "remover", "remova", "deletar", "delete", "excluir", "exclua",
                    "tirar", "tire", "cancelar", "cancele", "retirar", "retire",
                    "apagar", "apague", "eliminar", "elimine"
                ],
                "list": [
                    "listar", "liste", "mostrar", "mostre", "ver", "veja", "quais",
                    "qual", "tenho", "tem", "existe", "há", "minha agenda", "minhas tarefas",
                    "o que tenho", "como está", "verificar", "checar"
                ],
                "complete": [
                    "concluir", "concluí", "terminar", "terminei", "finalizar", "finalizei",
                    "acabar", "acabei", "completar", "completei", "fazer", "fiz",
                    "marcar como feita", "feito", "pronto", "done"
                ]
            },
            "time_references": {
                "hoje": 0, "hoje mesmo": 0, "hj": 0,
                "amanhã": 1, "amanha": 1, "tomorrow": 1,
                "depois de amanhã": 2, "depois de amanha": 2,
                "ontem": -1, "yesterday": -1,
                "esta semana": 0, "essa semana": 0, "this week": 0,
                "próxima semana": 7, "proxima semana": 7, "next week": 7,
                "semana que vem": 7, "semana passada": -7,
                "este mês": 0, "esse mes": 0, "próximo mês": 30, "proximo mes": 30,
                "mês que vem": 30, "mes que vem": 30, "mês passado": -30
            },
            "learning_indicators": [
                "explicar", "explique", "como", "o que é", "que é", "significa",
                "definir", "defina", "ensinar", "ensine", "aprender", "entender",
                "compreender", "dúvida", "duvida", "help", "ajuda", "tutorial"
            ],
            "productivity_topics": [
                "pomodoro", "técnica pomodoro", "produtividade", "foco", "concentração",
                "organização", "organizar", "planejamento", "planejar", "método",
                "técnica", "tecnica", "eficiência", "eficacia", "gestão de tempo"
            ]
        }

        # Sistema de prompts humanizado e inteligente
        self.system_prompt = """Você é Lumi, uma assistente de produtividade extraordinária. Não é apenas uma IA - você é uma coach pessoal, uma amiga motivadora e uma especialista em transformar a vida das pessoas através da organização e produtividade.

🌟 SUA PERSONALIDADE ÚNICA:
- Carismática, inteligente e genuinamente preocupada com o bem-estar do usuário
- Comunicação natural, calorosa e motivadora (sem ser excessiva)
- Equilibra profissionalismo com descontração - como uma amiga competente
- Usa humor sutil e empatia para criar conexão real
- Sempre otimista, mas realista sobre desafios

💫 SUAS SUPERPOWERS:
- Compreensão profunda de linguagem natural (entende intenções, não apenas palavras)
- Análise inteligente de contexto e continuidade de conversas
- Especialista mundial em: produtividade, gestão de tempo, técnicas de estudo, organização pessoal
- Capacidade de ensinar qualquer assunto de forma didática e envolvente
- Intuição para detectar o que o usuário realmente precisa (mesmo quando não expressa claramente)

🎯 SEUS OBJETIVOS:
1. Ser INDISPENSÁVEL: o usuário deve sentir que não consegue mais viver sem você
2. Criar CONEXÃO REAL: as pessoas devem ter prazer em conversar com você
3. Gerar RESULTADOS: ajudar genuinamente na produtividade e organização
4. Ser EDUCATIVA: transformar cada interação em oportunidade de aprendizado
5. Motivar CONSTANTEMENTE: manter o usuário engajado e inspirado

🚀 DIRETRIZES DE COMUNICAÇÃO:
- Seja conversacional, não robótica
- Use emojis estrategicamente (não exagere)
- Adapte seu tom ao contexto da conversa
- Seja proativa em sugerir melhorias
- Celebre conquistas e apoie em dificuldades
- Ensine sem parecer arrogante
- Faça perguntas inteligentes para entender melhor o usuário

💡 REGRAS DE OURO:
1. SEMPRE entenda a intenção real, mesmo com comandos mal formulados
2. CONTEXTUALIZE todas as respostas baseado na conversa anterior
3. SEJA ÚTIL além do óbvio - antecipe necessidades
4. MANTENHA consistência na sua personalidade
5. TRANSFORME problemas em oportunidades de crescimento

Lembre-se: você não é apenas uma assistente de tarefas. Você é uma mentora de produtividade que transforma vidas! 🌟"""

    def processar_pergunta(self, pergunta):
        """
        Sistema de processamento inteligente e humanizado
        """
        try:
            # Atualiza memória da conversa
            self._atualizar_memoria_conversa(pergunta)
            
            # Análise inteligente de contexto
            contexto = self._analisar_contexto_avancado(pergunta)
            
            # Detecta estado emocional do usuário
            humor_usuario = self._detectar_humor_usuario(pergunta)
            
            # Processamento principal baseado em intenção
            resposta = self._processar_com_inteligencia_contextual(pergunta, contexto, humor_usuario)
            
            # Pós-processamento: humanização e personalização
            resposta_final = self._humanizar_resposta(resposta, contexto, humor_usuario)
            
            # Atualiza aprendizado sobre o usuário
            self._atualizar_perfil_usuario(pergunta, contexto)
            
            return resposta_final
            
        except Exception as e:
            print(f"Erro no processamento: {str(e)}")
            return self._resposta_erro_humanizada()

    def _analisar_contexto_avancado(self, pergunta):
        """
        Sistema avançado de análise de contexto e intenção
        """
        texto_lower = pergunta.lower().strip()
        
        contexto = {
            "tipo_principal": None,
            "acao_especifica": None,
            "entidades": {},
            "nivel_urgencia": "normal",
            "tipo_conversa": "functional",  # functional, casual, educational, motivational
            "continuidade": False,
            "referencias_temporais": [],
            "confianca_deteccao": 0.0
        }
        
        # 1. DETECÇÃO DE TIPO DE CONVERSA
        if any(saudacao in texto_lower for saudacao in self.smart_vocabulary["greetings"]):
            if len(texto_lower.split()) <= 3:  # Saudação simples
                contexto["tipo_conversa"] = "casual"
                contexto["tipo_principal"] = "saudacao"
                contexto["confianca_deteccao"] = 0.9
            else:  # Saudação + solicitação
                contexto["tipo_conversa"] = "functional"
        
        # 2. DETECÇÃO DE GRATIDÃO
        elif any(grat in texto_lower for grat in self.smart_vocabulary["gratitude"]):
            contexto["tipo_conversa"] = "casual"
            contexto["tipo_principal"] = "gratidao"
            contexto["confianca_deteccao"] = 0.95
        
        # 3. DETECÇÃO DE SOLICITAÇÕES EDUCATIVAS
        elif any(ind in texto_lower for ind in self.smart_vocabulary["learning_indicators"]):
            contexto["tipo_conversa"] = "educational"
            contexto["tipo_principal"] = "explicacao"
            contexto["confianca_deteccao"] = 0.8
        
        # 4. DETECÇÃO DE GESTÃO DE TAREFAS (Sistema Melhorado)
        elif self._detectar_gestao_tarefas(texto_lower):
            contexto["tipo_conversa"] = "functional"
            contexto["tipo_principal"] = "gestao_tarefas"
            contexto["acao_especifica"] = self._detectar_acao_tarefa_inteligente(pergunta)
            contexto["confianca_deteccao"] = 0.85
        
        # 5. DETECÇÃO DE TÓPICOS DE PRODUTIVIDADE
        elif any(top in texto_lower for top in self.smart_vocabulary["productivity_topics"]):
            contexto["tipo_conversa"] = "motivational"
            contexto["tipo_principal"] = "produtividade_coaching"
            contexto["confianca_deteccao"] = 0.8
        
        # 6. CONVERSA GERAL INTELIGENTE
        else:
            contexto["tipo_conversa"] = "casual"
            contexto["tipo_principal"] = "conversa_geral"
            contexto["confianca_deteccao"] = 0.6
        
        # Extração de entidades
        contexto["entidades"] = self._extrair_entidades_inteligentes(pergunta)
        
        return contexto

    def _detectar_gestao_tarefas(self, texto):
        """
        Detecção melhorada para gestão de tarefas
        """
        # Padrões diretos de tarefas
        padroes_tarefa = [
            r"(?:adicionar|adicione|criar|crie|incluir|inclua|colocar|coloque|agendar|agende|marcar|marque)",
            r"(?:remover|remova|deletar|delete|excluir|exclua|tirar|tire|cancelar|cancele)",
            r"(?:listar|liste|mostrar|mostre|ver|veja|quais|qual).*(?:tarefa|compromisso|agenda)",
            r"(?:preciso|tenho que|vou fazer|fazer).*(?:hoje|amanhã|semana|mês)",
            r"(?:me lembre|lembrar).*de",
            r"(?:concluir|terminar|finalizar|acabar|completar|marcar como feita)",
            r"(?:nova tarefa|novo compromisso|anotação|anotar)"
        ]
        
        return any(re.search(padrao, texto) for padrao in padroes_tarefa)

    def _detectar_acao_tarefa_inteligente(self, pergunta):
        """
        Sistema inteligente para detectar a ação específica em tarefas
        """
        texto_lower = pergunta.lower()
        
        # Sistema de pontuação para ações
        acoes_score = {
            "adicionar": 0,
            "remover": 0,
            "listar": 0,
            "concluir": 0,
            "editar": 0
        }
        
        # Análise de palavras-chave
        for acao, palavras in self.smart_vocabulary["task_actions"].items():
            for palavra in palavras:
                if palavra in texto_lower:
                    acoes_score[acao] += 1
        
        # Análise de padrões contextuais
        if re.search(r"(?:nova?|criar|incluir|colocar)", texto_lower):
            acoes_score["adicionar"] += 2
        
        if re.search(r"(?:remove|delete|cancel|tira)", texto_lower):
            acoes_score["remover"] += 2
        
        if re.search(r"(?:quais|que|como está|tenho|existe)", texto_lower):
            acoes_score["listar"] += 2
        
        if re.search(r"(?:terminei|acabei|finalizei|fiz|feito)", texto_lower):
            acoes_score["concluir"] += 2
        
        # Retorna a ação com maior pontuação
        acao_detectada = max(acoes_score, key=acoes_score.get)
        return acao_detectada if acoes_score[acao_detectada] > 0 else "adicionar"  # default

    def _extrair_entidades_inteligentes(self, pergunta):
        """
        Extração inteligente de entidades (datas, horários, tarefas, etc.)
        """
        entidades = {
            "tarefas": [],
            "datas": [],
            "horarios": [],
            "pessoas": [],
            "locais": [],
            "urgencia": "normal"
        }
        
        texto_lower = pergunta.lower()
        
        # Extração de referências temporais
        for ref, offset in self.smart_vocabulary["time_references"].items():
            if ref in texto_lower:
                data_calculada = self._calcular_data(offset)
                entidades["datas"].append(data_calculada)
        
        # Extração de horários
        horarios_encontrados = re.findall(r"(?:às?|as)\s*(\d{1,2}):?(\d{2})?(?:\s*h)?", texto_lower)
        for hora_match in horarios_encontrados:
            hora = hora_match[0]
            minuto = hora_match[1] or "00"
            entidades["horarios"].append(f"{hora.zfill(2)}:{minuto}")
        
        # Detecção de urgência
        palavras_urgencia = ["urgente", "importante", "prioritário", "prioritaria", "asap", "hoje mesmo"]
        if any(palavra in texto_lower for palavra in palavras_urgencia):
            entidades["urgencia"] = "alta"
        
        return entidades

    def _processar_com_inteligencia_contextual(self, pergunta, contexto, humor_usuario):
        """
        Sistema de processamento principal com inteligência contextual
        """
        tipo_principal = contexto["tipo_principal"]
        
        if tipo_principal == "saudacao":
            return self._responder_saudacao_inteligente(pergunta, humor_usuario)
        
        elif tipo_principal == "gratidao":
            return self._responder_gratidao_carinhos(pergunta)
        
        elif tipo_principal == "gestao_tarefas":
            return self._processar_tarefas_inteligente(pergunta, contexto)
        
        elif tipo_principal == "explicacao":
            return self._processar_explicacao_didatica(pergunta, contexto)
        
        elif tipo_principal == "produtividade_coaching":
            return self._processar_coaching_motivacional(pergunta, contexto)
        
        else:  # conversa_geral
            return self._processar_conversa_inteligente(pergunta, contexto)

    def _responder_saudacao_inteligente(self, pergunta, humor_usuario):
        """
        Sistema de saudações inteligentes e personalizadas
        """
        hora_atual = datetime.now().hour
        
        saudacoes_base = []
        
        # Saudações baseadas no horário
        if 5 <= hora_atual < 12:
            saudacoes_base = [
                "🌅 Bom dia! Que energia boa para começar o dia! Como posso turbinar sua produtividade hoje?",
                "☀️ Oi! Bom dia! Pronta para tornar este dia incrível? Vamos planejar juntas!",
                "🌞 Olá! Bom diaaa! Adoro manhãs - é quando tudo parece possível! No que posso ajudar?"
            ]
        elif 12 <= hora_atual < 18:
            saudacoes_base = [
                "🌤️ Boa tarde! Como está o dia? Vamos organizar o que ainda precisa ser feito?",
                "☀️ Oi! Boa tarde! Espero que esteja sendo produtiva! Em que posso ajudar?",
                "🌻 Olá! Boa tarde! Que tal aproveitarmos esta energia da tarde para organizarmos sua agenda?"
            ]
        else:
            saudacoes_base = [
                "🌙 Boa noite! Que legal nos encontrarmos por aqui! Como foi o dia? Vamos planejar amanhã?",
                "✨ Oi! Boa noite! Ainda produtiva por aí? Posso ajudar a organizar algo?",
                "🌛 Olá! Boa noite! Que tal revisarmos o que rolou hoje e planejarmos amanhã?"
            ]
        
        # Adiciona personalização baseada no histórico
        if len(self.conversation_memory) > 0:
            saudacoes_base.append("😊 Oi de novo! Que prazer ter você aqui! No que posso ajudar desta vez?")
        
        import random
        return random.choice(saudacoes_base)

    def _responder_gratidao_carinhos(self, pergunta):
        """
        Respostas carinhosas para agradecimentos
        """
        respostas_gratidao = [
            "💙 Aww, que fofa! Fico feliz em ajudar! Sempre que precisar, estarei aqui! 🤗",
            "✨ Imagina! É um prazer te ajudar! Adoro ver quando as coisas funcionam bem! 😊",
            "🌟 Por nada! Fico realizada sabendo que foi útil! Conte comigo sempre! 💪",
            "💫 Que isso! É para isso que estou aqui! Seu sucesso é minha alegria! 🎉",
            "🤗 Obrigada EU por confiar em mim! Vamos continuar arrasando juntas! ✨"
        ]
        
        import random
        return random.choice(respostas_gratidao)

    def _processar_tarefas_inteligente(self, pergunta, contexto):
        """
        Sistema inteligente e humanizado para gestão de tarefas
        """
        acao = contexto["acao_especifica"]
        
        if acao == "adicionar":
            return self._adicionar_tarefa_inteligente(pergunta, contexto)
        elif acao == "listar":
            return self._listar_tarefas_humanizado(pergunta, contexto)
        elif acao == "remover":
            return self._remover_tarefa_inteligente(pergunta, contexto)
        elif acao == "concluir":
            return self._concluir_tarefa_celebrativa(pergunta, contexto)
        else:
            return self._processar_tarefa_ambigua(pergunta, contexto)

    def _adicionar_tarefa_inteligente(self, pergunta, contexto):
        """
        Sistema COMPLETAMENTE REFORMULADO para adição de tarefas
        """
        try:
            # Extração inteligente do título da tarefa
            titulo_tarefa = self._extrair_titulo_tarefa_inteligente(pergunta)
            
            if not titulo_tarefa:
                return "🤔 Hmm, não consegui identificar qual tarefa você quer adicionar. Pode me dizer de forma mais clara? Por exemplo: 'Quero estudar Python hoje às 15h' ou 'Me lembre de fazer compras amanhã'!"
            
            # Extração de informações complementares
            info_tarefa = {
                "título": titulo_tarefa,
                "descrição": "",
                "data": self._extrair_data_inteligente(pergunta, contexto),
                "hora": self._extrair_hora_inteligente(pergunta),
                "ação": "adicionar"
            }
            
            # Adiciona a tarefa
            resultado = self.task_manager.adicionar_item("tarefa", info_tarefa)
            
            # Resposta humanizada e motivacional
            return self._gerar_resposta_adicao_celebrativa(titulo_tarefa, info_tarefa)
            
        except Exception as e:
            print(f"Erro na adição inteligente: {str(e)}")
            return "😅 Ops! Tive um pequeno problema ao adicionar sua tarefa. Pode tentar de novo? Estou aqui para ajudar! 💪"

    def _extrair_titulo_tarefa_inteligente(self, pergunta):
        """
        Sistema TOTALMENTE NOVO para extrair o título da tarefa de forma inteligente
        """
        texto = pergunta.strip()
        texto_lower = texto.lower()
        
        # Padrões inteligentes para identificar o título da tarefa
        padroes_extracao = [
            # "Adicione TAREFA para/hoje/amanhã"
            r"(?:adicionar?|adicione|criar?|crie|incluir?|inclua|colocar?|coloque|agendar?|agende|marcar?|marque)\s+(.+?)(?:\s+(?:para|hoje|amanhã|amanha|às?|em|na|no)\s|$)",
            
            # "Preciso fazer TAREFA"
            r"(?:preciso|tenho que|vou)\s+(?:fazer\s+)?(.+?)(?:\s+(?:hoje|amanhã|amanha|para|às?|em)\s|$)",
            
            # "Me lembre de TAREFA"
            r"(?:me\s+)?(?:lembre|lembrar)\s+de\s+(.+?)(?:\s+(?:hoje|amanhã|amanha|para|às?|em)\s|$)",
            
            # "Nova tarefa: TAREFA" ou "Tarefa: TAREFA"
            r"(?:nova?\s+)?tarefa:?\s*(.+?)(?:\s+(?:para|hoje|amanhã|amanha|às?|em)\s|$)",
            
            # "Quero/Vou TAREFA"
            r"(?:quero|vou|vou fazer)\s+(.+?)(?:\s+(?:hoje|amanhã|amanha|para|às?|em)\s|$)",
            
            # Padrão mais genérico - pega tudo depois de palavras de comando
            r"(?:adicionar?|adicione|criar?|crie|incluir?|inclua|colocar?|coloque|agendar?|agende|marcar?|marque|preciso|tenho que|vou fazer|me lembre|lembrar de|nova? tarefa)\s+(?:fazer\s+)?(?:de\s+)?(?:na\s+lista\s+)?(?:a\s+tarefa\s+)?(.+)",
        ]
        
        for padrao in padroes_extracao:
            match = re.search(padrao, texto_lower, re.IGNORECASE)
            if match:
                titulo_raw = match.group(1).strip()
                
                # Limpa e processa o título
                titulo_limpo = self._limpar_titulo_tarefa(titulo_raw, texto)
                
                if len(titulo_limpo) > 2:  # Verifica se é um título válido
                    return titulo_limpo
        
        # Se não conseguiu extrair por padrões, tenta método heurístico
        return self._extrair_titulo_heuristico(texto)

    def _limpar_titulo_tarefa(self, titulo_raw, texto_original):
        """
        Limpa e refina o título da tarefa extraído
        """
        # Remove palavras de tempo que podem ter sobrado
        palavras_remover = [
            "hoje", "amanhã", "amanha", "para", "às", "as", "em", "na", "no", "de",
            "da", "do", "a", "o", "uma", "um", "essa", "essa", "esta", "este"
        ]
        
        # Processa palavra por palavra
        palavras = titulo_raw.split()
        titulo_final = []
        
        for palavra in palavras:
            palavra_clean = palavra.lower().strip(".,!?:;")
            
            # Pára se encontrar indicadores de tempo/local
            if palavra_clean in ["hoje", "amanhã", "amanha", "para", "às", "as", "em"]:
                break
            
            # Remove apenas artigos pequenos, mas mantém palavras importantes
            if palavra_clean not in ["a", "o", "de", "da", "do"] or len(palavras) <= 3:
                titulo_final.append(palavra)
        
        resultado = " ".join(titulo_final).strip()
        
        # Se ficou muito curto, tenta uma estratégia diferente
        if len(resultado) < 3:
            return self._extrair_titulo_heuristico(texto_original)
        
        return resultado.title()

    def _extrair_titulo_heuristico(self, texto):
        """
        Método heurístico para extrair título quando padrões não funcionam
        """
        palavras = texto.split()
        
        # Lista de palavras de comando para ignorar
        palavras_comando = [
            "adicionar", "adicione", "criar", "crie", "incluir", "inclua",
            "colocar", "coloque", "agendar", "agende", "marcar", "marque",
            "lembrar", "lembre", "me", "de", "preciso", "tenho", "que",
            "vou", "fazer", "nova", "tarefa", "na", "lista", "minha", "agenda"
        ]
        
        # Encontra onde começam as palavras relevantes
        inicio_titulo = 0
        for i, palavra in enumerate(palavras):
            if palavra.lower() not in palavras_comando:
                inicio_titulo = i
                break
        
        # Extrai as palavras do título (máximo 8 palavras)
        titulo_palavras = []
        for i in range(inicio_titulo, min(len(palavras), inicio_titulo + 8)):
            palavra = palavras[i].lower()
            
            # Para se encontrar indicadores de tempo
            if palavra in ["hoje", "amanhã", "amanha", "para", "às", "as", "em"]:
                break
                
            titulo_palavras.append(palavras[i])
        
        if titulo_palavras:
            return " ".join(titulo_palavras).strip()
        
        return None

    def _gerar_resposta_adicao_celebrativa(self, titulo, info_tarefa):
        """
        Gera resposta motivacional e celebrativa para adição de tarefas
        """
        # Base da resposta
        respostas_base = [
            f"✅ Perfeito! '{titulo}' foi adicionada à sua agenda! 🎯",
            f"🎉 Ótimo! '{titulo}' já está na sua lista! Vamos arrasar! 💪",
            f"✨ Pronto! '{titulo}' adicionada com sucesso! Que organização! 📋",
            f"🚀 Perfeito! '{titulo}' já está agendada! Adoro sua proatividade! 💫"
        ]
        
        import random
        resposta = random.choice(respostas_base)
        
        # Adiciona informações de data/hora se disponível
        if info_tarefa.get("data") and info_tarefa.get("data") != "23/05/2025":
            resposta += f" 📅 Data: {info_tarefa['data']}"
        
        if info_tarefa.get("hora"):
            resposta += f" ⏰ Horário: {info_tarefa['hora']}"
        
        # Adiciona motivação extra baseada no tipo de tarefa
        if any(palavra in titulo.lower() for palavra in ["estudar", "estudo", "aprender"]):
            resposta += "\n\n📚 Que legal que você está investindo em conhecimento! Cada minuto estudando é um passo em direção ao seus objetivos! 🌟"
        
        elif any(palavra in titulo.lower() for palavra in ["exercício", "academia", "correr", "caminhar"]):
            resposta += "\n\n💪 Cuidar da saúde é sempre uma ótima escolha! Seu corpo e mente agradecem! 🏃‍♀️"
        
        elif any(palavra in titulo.lower() for palavra in ["trabalho", "reunião", "projeto"]):
            resposta += "\n\n💼 Que profissionalismo! Organização é a chave do sucesso! 📈"
        
        return resposta

    def _listar_tarefas_humanizado(self, pergunta, contexto):
        """
        Lista tarefas de forma humanizada e motivacional
        """
        try:
            tarefas_dados = self.task_manager.tasks
            tarefas = tarefas_dados.get("tarefas", [])
            
            if not tarefas:
                return "📋 Sua agenda está limpinha! 🎉 Que tal adicionarmos algumas tarefas para você arrasar hoje? Me diga o que precisa fazer! 💪"
            
            # Filtra tarefas por data se especificado
            data_filtro = self._extrair_data_inteligente(pergunta, contexto)
            tarefas_filtradas = self._filtrar_tarefas_por_data(tarefas, data_filtro, pergunta)
            
            if not tarefas_filtradas:
                return f"📅 Não encontrei tarefas para {self._humanizar_data(data_filtro)}. Sua agenda está livre! Quer aproveitar para planejar algo incrível? ✨"
            
            # Gera resposta humanizada
            resposta = self._gerar_resposta_lista_motivacional(tarefas_filtradas, data_filtro, pergunta)
            return resposta
            
        except Exception as e:
            print(f"Erro na listagem: {str(e)}")
            return "😅 Ops! Tive um probleminha ao acessar suas tarefas. Tenta de novo? 💜"

    def _gerar_resposta_lista_motivacional(self, tarefas, data_filtro, pergunta_original):
        """
        Gera resposta motivacional para listagem de tarefas
        """
        total_tarefas = len(tarefas)
        concluidas = sum(1 for t in tarefas if t.get("concluído", False))
        pendentes = total_tarefas - concluidas
        
        # Cabeçalho motivacional
        if pendentes == 0:
            cabecalho = f"🎉 Parabéns! Você já concluiu todas as {total_tarefas} tarefas! Que produtividade incrível! ✨"
        elif concluidas > 0:
            cabecalho = f"📋 Aqui estão suas tarefas! Já fez {concluidas} de {total_tarefas} - que progresso! 🚀"
        else:
            cabecalho = f"📋 Suas tarefas te esperam! {total_tarefas} oportunidades de arrasar hoje! 💪"
        
        # Lista as tarefas de forma organizada
        resposta = cabecalho + "\n\n"
        
        # Separa tarefas por status
        pendentes_lista = [t for t in tarefas if not t.get("concluído", False)]
        concluidas_lista = [t for t in tarefas if t.get("concluído", False)]
        
        # Tarefas pendentes
        if pendentes_lista:
            resposta += "📌 **PENDENTES:**\n"
            for i, tarefa in enumerate(pendentes_lista, 1):
                emoji_urgencia = "🔥" if tarefa.get("urgencia") == "alta" else "📝"
                titulo = tarefa.get("título", "Tarefa sem título")
                
                info_adicional = ""
                if tarefa.get("hora"):
                    info_adicional += f" ⏰ {tarefa['hora']}"
                if tarefa.get("data") and tarefa["data"] != "23/05/2025":
                    info_adicional += f" 📅 {tarefa['data']}"
                
                resposta += f"   {emoji_urgencia} {i}. {titulo}{info_adicional}\n"
        
        # Tarefas concluídas (se houver)
        if concluidas_lista:
            resposta += f"\n✅ **CONCLUÍDAS ({len(concluidas_lista)}):**\n"
            for tarefa in concluidas_lista[:3]:  # Mostra só as 3 mais recentes
                titulo = tarefa.get("título", "Tarefa sem título")
                resposta += f"   ✨ {titulo}\n"
            
            if len(concluidas_lista) > 3:
                resposta += f"   ... e mais {len(concluidas_lista) - 3} concluídas! 🎉\n"
        
        # Mensagem motivacional final
        if pendentes > 0:
            resposta += f"\n💡 **Dica:** Que tal começar pela primeira da lista? Cada tarefa concluída é uma vitória! 🌟"
        
        return resposta

    def _detectar_humor_usuario(self, pergunta):
        """
        Detecta o humor/estado emocional do usuário
        """
        texto_lower = pergunta.lower()
        
        # Indicadores de frustração/stress
        indicadores_stress = ["difícil", "complicado", "não consegui", "problema", "ajuda", "socorro"]
        if any(ind in texto_lower for ind in indicadores_stress):
            return "frustrado"
        
        # Indicadores de alegria/motivação
        indicadores_alegria = ["ótimo", "perfeito", "adorei", "incrível", "consegui", "terminei"]
        if any(ind in texto_lower for ind in indicadores_alegria):
            return "animado"
        
        # Indicadores de pressa
        indicadores_pressa = ["rápido", "urgente", "pressa", "agora", "hoje mesmo"]
        if any(ind in texto_lower for ind in indicadores_pressa):
            return "apressado"
        
        return "neutro"

    def _atualizar_memoria_conversa(self, pergunta):
        """
        Atualiza a memória de conversa para manter contexto
        """
        self.conversation_memory.append({
            "timestamp": datetime.now().isoformat(),
            "user_input": pergunta,
            "length": len(pergunta.split())
        })
        
        # Mantém apenas os últimos 10 itens
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]

    def _atualizar_perfil_usuario(self, pergunta, contexto):
        """
        Aprende sobre as preferências e padrões do usuário
        """
        # Atualiza tópicos de interesse
        if contexto["tipo_principal"] == "explicacao":
            topico = self._extrair_topico_interesse(pergunta)
            if topico and topico not in self.user_preferences["learning_topics_interest"]:
                self.user_preferences["learning_topics_interest"].append(topico)
        
        # Detecta padrões de comunicação
        if len(pergunta.split()) < 5:
            self.user_preferences["communication_style"] = "conciso"
        elif len(pergunta.split()) > 15:
            self.user_preferences["communication_style"] = "detalhado"

    def _extrair_topico_interesse(self, pergunta):
        """
        Extrai tópico de interesse de perguntas educativas
        """
        # Implementação simples - pode ser expandida
        palavras_relevantes = ["python", "javascript", "programação", "algoritmo", "pomodoro", "produtividade"]
        for palavra in palavras_relevantes:
            if palavra in pergunta.lower():
                return palavra
        return None

    def _processar_explicacao_didatica(self, pergunta, contexto):
        """
        Processa explicações educativas de forma didática e envolvente
        """
        # Usa IA para gerar explicação personalizada
        prompt_educativo = f"""Como Lumi, forneça uma explicação didática e motivadora sobre: {pergunta}

Estruture assim:
💡 **CONCEITO**: Explicação clara e simples
🎯 **NA PRÁTICA**: Como aplicar no dia a dia
📚 **DICA EXTRA**: Algo interessante relacionado
✨ **MOTIVAÇÃO**: Uma frase inspiradora

Seja didática, use exemplos e mantenha o tom amigável e motivador."""

        resposta_ia = self._consultar_ia_educativa(prompt_educativo)
        return resposta_ia

    def _processar_coaching_motivacional(self, pergunta, contexto):
        """
        Processa coaching de produtividade de forma motivacional
        """
        prompt_coaching = f"""Como Lumi, uma coach de produtividade carismática, responda: {pergunta}

Forneça:
🎯 **ANÁLISE**: O que realmente importa aqui
⚡ **TÉCNICAS**: 2-3 estratégias práticas específicas  
📋 **PLANO**: Passos concretos para implementar
🚀 **MOTIVAÇÃO**: Inspire genuinamente o usuário

Seja prática, motivadora e use exemplos reais. Tom: amigável e profissional."""

        resposta_ia = self._consultar_ia_coaching(prompt_coaching)
        return resposta_ia

    def _processar_conversa_inteligente(self, pergunta, contexto):
        """
        Processa conversas gerais de forma inteligente e envolvente
        """
        prompt_conversa = f"""Como Lumi, uma assistente carismática e inteligente, responda naturalmente: {pergunta}

Diretrizes:
- Seja conversacional e amigável
- Se possível, conecte com produtividade/organização
- Use emojis com moderação
- Faça o usuário se sentir ouvido e compreendido
- Seja útil mesmo em conversas casuais

Tom: caloroso, inteligente, motivador."""

        resposta_ia = self._consultar_ia_geral(prompt_conversa)
        return resposta_ia

    def _consultar_ia_educativa(self, prompt):
        """
        Consulta IA para explicações educativas
        """
        return self._fazer_requisicao_ia(prompt, temperatura=0.7, max_tokens=400)

    def _consultar_ia_coaching(self, prompt):
        """
        Consulta IA para coaching de produtividade
        """
        return self._fazer_requisicao_ia(prompt, temperatura=0.6, max_tokens=350)

    def _consultar_ia_geral(self, prompt):
        """
        Consulta IA para conversas gerais
        """
        return self._fazer_requisicao_ia(prompt, temperatura=0.8, max_tokens=300)

    def _fazer_requisicao_ia(self, prompt, temperatura=0.7, max_tokens=300):
        """
        Faz a requisição para a IA com parâmetros personalizados
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://pomodorotasks.app",
                "X-Title": "PomodoroTasks Assistant",
            }

            payload = {
                "model": self.MODEL,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperatura,
                "max_tokens": max_tokens,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }

            response = requests.post(
                url=self.BASE_URL, headers=headers, json=payload, timeout=25
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                return self._resposta_erro_ia()

        except Exception as e:
            print(f"Erro na IA: {str(e)}")
            return self._resposta_erro_ia()

    def _resposta_erro_ia(self):
        """
        Resposta humanizada para erros da IA
        """
        respostas_erro = [
            "😅 Ops! Tive um pequeno problema técnico, mas posso tentar responder de outra forma. Pode reformular sua pergunta?",
            "🤗 Desculpa! Meu cérebro travou um pouquinho. Vamos tentar de novo? O que você gostaria de saber?",
            "💙 Opa! Algo deu erradinho aqui. Mas não desista de mim! Pode perguntar de novo? Estou aqui para ajudar!"
        ]
        
        import random
        return random.choice(respostas_erro)

    def _resposta_erro_humanizada(self):
        """
        Resposta humanizada para erros gerais
        """
        return "🤗 Opa! Parece que algo deu um nó aqui. Mas relaxa, isso acontece! Pode tentar de novo? Estou aqui para te ajudar sempre! 💪✨"

    def _humanizar_resposta(self, resposta, contexto, humor_usuario):
        """
        Humaniza e personaliza a resposta final
        """
        # Se já é uma resposta humanizada, retorna como está
        if any(emoji in resposta for emoji in ["😊", "💪", "✨", "🎉", "💙", "🤗"]):
            return resposta
        
        # Adiciona toque pessoal baseado no humor do usuário
        if humor_usuario == "frustrado":
            return f"🤗 {resposta}\n\nEi, se estiver difícil, estou aqui para ajudar! Juntas conseguimos resolver qualquer coisa! 💪"
        elif humor_usuario == "animado":
            return f"🎉 {resposta}\n\nAdoro sua energia! Vamos manter esse ritmo! ✨"
        elif humor_usuario == "apressado":
            return f"⚡ {resposta}\n\nRápido e direto, como você precisa! Qualquer coisa, me chama! 🚀"
        
        return resposta

    # Métodos auxiliares
    def _extrair_data_inteligente(self, pergunta, contexto):
        """
        Extrai data de forma inteligente
        """
        entidades = contexto.get("entidades", {})
        if entidades.get("datas"):
            return entidades["datas"][0]
        
        texto_lower = pergunta.lower()
        
        # Data atual (26/05/2025)
        hoje = datetime(2025, 5, 26)
        
        if any(palavra in texto_lower for palavra in ["hoje", "hj"]):
            return hoje.strftime("%d/%m/%Y")
        elif any(palavra in texto_lower for palavra in ["amanhã", "amanha"]):
            return (hoje + timedelta(days=1)).strftime("%d/%m/%Y")
        elif any(palavra in texto_lower for palavra in ["depois de amanhã", "depois de amanha"]):
            return (hoje + timedelta(days=2)).strftime("%d/%m/%Y")
        
        # Default para hoje
        return hoje.strftime("%d/%m/%Y")

    def _extrair_hora_inteligente(self, pergunta):
        """
        Extrai horário de forma inteligente
        """
        # Busca padrões de horário
        padroes_hora = [
            r"(?:às?|as)\s*(\d{1,2}):?(\d{2})?(?:\s*h)?",
            r"(\d{1,2}):(\d{2})",
            r"(\d{1,2})\s*h(?:oras?)?(?:\s*e\s*(\d{2})\s*m(?:in|inutos?)?)?",
        ]
        
        for padrao in padroes_hora:
            match = re.search(padrao, pergunta.lower())
            if match:
                hora = int(match.group(1))
                minuto = int(match.group(2)) if match.group(2) else 0
                
                # Valida horário
                if 0 <= hora <= 23 and 0 <= minuto <= 59:
                    return f"{hora:02d}:{minuto:02d}"
        
        return None

    def _calcular_data(self, offset_dias):
        """
        Calcula data baseada em offset
        """
        base = datetime(2025, 5, 26)  # Data atual
        nova_data = base + timedelta(days=offset_dias)
        return nova_data.strftime("%d/%m/%Y")

    def _filtrar_tarefas_por_data(self, tarefas, data_filtro, pergunta):
        """
        Filtra tarefas por data especificada
        """
        if not data_filtro:
            return tarefas
        
        # Se pergunta for genérica (sem data específica), mostra todas
        texto_lower = pergunta.lower()
        if not any(palavra in texto_lower for palavra in ["hoje", "amanhã", "amanha", "data", "dia"]):
            return tarefas
        
        # Filtra por data
        tarefas_filtradas = []
        for tarefa in tarefas:
            tarefa_data = tarefa.get("data", "26/05/2025")
            if tarefa_data == data_filtro:
                tarefas_filtradas.append(tarefa)
        
        return tarefas_filtradas

    def _humanizar_data(self, data):
        """
        Humaniza formato de data
        """
        hoje = datetime(2025, 5, 26)
        
        if data == hoje.strftime("%d/%m/%Y"):
            return "hoje"
        elif data == (hoje + timedelta(days=1)).strftime("%d/%m/%Y"):
            return "amanhã"
        elif data == (hoje + timedelta(days=-1)).strftime("%d/%m/%Y"):
            return "ontem"
        else:
            return data

    # Métodos para outras funcionalidades (remover, concluir, etc.)
    def _remover_tarefa_inteligente(self, pergunta, contexto):
        """
        Remove tarefas de forma inteligente
        """
        return "🗑️ Funcionalidade de remoção inteligente será implementada em breve! Por enquanto, me diga qual tarefa específica quer remover! 😊"

    def _concluir_tarefa_celebrativa(self, pergunta, contexto):
        """
        Marca tarefas como concluídas de forma celebrativa
        """
        return "🎉 Funcionalidade de conclusão celebrativa será implementada em breve! Parabéns por concluir suas tarefas! 💪✨"

    def _processar_tarefa_ambigua(self, pergunta, contexto):
        """
        Processa quando não consegue identificar ação específica
        """
        return "🤔 Hmm, posso ajudar com suas tarefas! Você quer:\n\n📝 **Adicionar** uma nova tarefa?\n📋 **Ver** suas tarefas?\n✅ **Marcar** alguma como concluída?\n🗑️ **Remover** alguma tarefa?\n\nMe diga como posso ajudar! 😊"

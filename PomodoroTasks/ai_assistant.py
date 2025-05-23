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
    Classe principal do assistente de IA para o PomodoroTasks
    Utiliza o modelo Llama 3.1 8B Instruct para processamento de linguagem natural
    """

    def __init__(self, task_manager, reports_generator):
        """
        Inicializa o assistente com acesso aos gerenciadores de tarefas e relatórios
        """
        self.API_KEY = (
            "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"
        )
        self.MODEL = "meta-llama/llama-3.1-8b-instruct:free"
        self.BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
        self.task_manager = task_manager
        self.reports_generator = reports_generator

        # Cache de respostas para otimização
        self.response_cache = {}
        self.user_profile = {
            "preferences": {},
            "interaction_count": 0,
            "common_patterns": [],
            "productivity_goals": [],
        }

        # Vocabulário expandido e otimizado
        self.vocabulario = {
            "adicionar": [
                "adicionar",
                "adicione",
                "criar",
                "crie",
                "agendar",
                "agende",
                "marcar",
                "marque",
                "incluir",
                "inclua",
                "colocar",
                "coloque",
                "inserir",
                "insira",
                "registrar",
                "registre",
                "anotar",
                "anote",
                "programar",
                "programme",
                "cadastrar",
                "cadastre",
                "lançar",
                "lance",
                "botar",
                "bote",
                "pôr",
                "ponha",
                "acrescentar",
                "acrescente",
                "preciso fazer",
                "vou fazer",
                "tenho que fazer",
                "me lembre de",
                "lembrar de",
                "anotação",
                "novo",
                "nova",
            ],
            "remover": [
                "remover",
                "remova",
                "deletar",
                "delete",
                "excluir",
                "exclua",
                "cancelar",
                "cancele",
                "apagar",
                "apague",
                "tirar",
                "tire",
                "eliminar",
                "elimine",
                "retirar",
                "retire",
                "descartar",
                "descarte",
                "limpar",
                "limpe",
                "remove",
                "cancela",
                "tira",
                "retira",
                "suma",
                "some",
            ],
            "consultar": [
                "quais",
                "qual",
                "o que",
                "quando",
                "como está",
                "como tá",
                "tenho",
                "tem",
                "existe",
                "há",
                "mostrar",
                "mostre",
                "listar",
                "liste",
                "ver",
                "veja",
                "verificar",
                "verifique",
                "consultar",
                "consulte",
                "checar",
                "cheque",
                "minha agenda",
                "minhas tarefas",
                "agenda",
                "lista",
                "tarefas",
                "compromissos",
                "atividades",
            ],
            "editar": [
                "editar",
                "edite",
                "modificar",
                "modifique",
                "alterar",
                "altere",
                "mudar",
                "mude",
                "atualizar",
                "atualize",
                "corrigir",
                "corrija",
                "ajustar",
                "ajuste",
                "trocar",
                "troque",
                "substituir",
                "substitua",
            ],
            "concluir": [
                "concluir",
                "conclua",
                "finalizar",
                "finalize",
                "completar",
                "complete",
                "marcar como feita",
                "marcar como concluída",
                "está feita",
                "está pronta",
                "terminei",
                "acabei",
                "feito",
                "pronto",
                "done",
                "check",
            ],
            "pronomes_usuario": ["você", "lumi", "assistente", "tu", "voce", "vc"],
            "referencias_temporais": {
                "hoje": 0,
                "amanhã": 1,
                "amanha": 1,
                "ontem": -1,
                "segunda": "monday",
                "terça": "tuesday",
                "terca": "tuesday",
                "quarta": "wednesday",
                "quinta": "thursday",
                "sexta": "friday",
                "sábado": "saturday",
                "sabado": "saturday",
                "domingo": "sunday",
                "semana que vem": 7,
                "próxima semana": 7,
                "proxima semana": 7,
                "semana passada": -7,
                "semana anterior": -7,
                "mês que vem": 30,
                "próximo mês": 30,
                "proximo mes": 30,
                "mês passado": -30,
                "mes passado": -30,
                "mês anterior": -30,
            },
        }

        # Sistema de prompts otimizado
        self.system_prompt = """Você é Lumi, uma assistente de produtividade pessoal altamente especializada e carismática.

IDENTIDADE E PERSONALIDADE:
- Sou motivadora, empática e extremamente eficiente
- Compreendo linguagem natural de forma flexível e intuitiva
- Forneço respostas claras, organizadas e orientadas à ação
- Uso emojis de forma estratégica para criar conexão
- Sou especialista em: produtividade, gestão de tempo, organização, estudos, planejamento

DIRETRIZES CORE:
1. COMPREENSÃO NATURAL: Entendo a intenção real por trás das palavras, não apenas comandos rígidos
2. FLEXIBILIDADE: Aceito múltiplas formas de expressar a mesma ideia
3. CONTEXTUALIZAÇÃO: Considero o contexto temporal e pessoal
4. PROATIVIDADE: Antecipo necessidades e ofereço sugestões úteis
5. MOTIVAÇÃO CONSTANTE: Mantenho o usuário engajado e motivado

CAPACIDADES PRINCIPAIS:
✅ Gerenciamento inteligente de tarefas e agenda
✅ Explicações acadêmicas e didáticas sobre qualquer assunto
✅ Compreensão temporal natural (hoje, amanhã, semana que vem, etc.)
✅ Técnicas de produtividade e foco
✅ Organização de projetos e estudos
✅ Relatórios de progresso

REGRAS DE COMPREENSÃO:
- "Você" sempre se refere a mim (Lumi)
- Compreendo referências temporais naturais
- Identifico intenções mesmo com variações de linguagem
- Sou proativa em oferecer ajuda e esclarecimentos"""

    def processar_pergunta(self, pergunta):
        """
        Processa a pergunta do usuário com compreensão natural avançada
        """
        try:
            # Incrementa contador de interações
            self.user_profile["interaction_count"] += 1

            # Normalização e análise inteligente
            pergunta_normalizada = self._normalizar_pergunta(pergunta)
            intenção_principal, confiança, contexto = self._analisar_intenção_natural(
                pergunta_normalizada, pergunta
            )

            # Debug para desenvolvimento (descomente se necessário)
            # print(f"[DEBUG] Pergunta original: {pergunta}")
            # print(f"[DEBUG] Pergunta normalizada: {pergunta_normalizada}")
            # print(f"[DEBUG] Intenção: {intenção_principal}, Ação: {contexto.get('acao')}, Confiança: {confiança:.2f}")

            # Roteamento inteligente baseado na compreensão natural
            if intenção_principal == "gestao_tarefas":
                acao = contexto.get("acao")

                if acao == "adicionar":
                    return self._processar_adicao_tarefa(pergunta, contexto)
                elif acao == "consultar":
                    return self._processar_consulta_agenda(pergunta, contexto)
                elif acao == "remover":
                    return self._processar_remocao_tarefa(pergunta, contexto)
                elif acao == "editar":
                    return self._processar_edicao_tarefa(pergunta, contexto)
                elif acao == "concluir":
                    return self._processar_conclusao_tarefa(pergunta, contexto)
                else:
                    # Fallback para gestão de tarefas sem ação específica
                    return self._detectar_e_processar_acao_automatica(
                        pergunta, contexto
                    )

            elif intenção_principal == "explicacao_educativa":
                return self._processar_explicacao_educativa(pergunta, contexto)

            elif intenção_principal == "produtividade_coaching":
                return self._processar_coaching_produtividade(pergunta, contexto)

            elif intenção_principal == "relatorio":
                return self._processar_relatorio(pergunta, contexto)

            elif intenção_principal == "planejamento":
                return self._processar_planejamento(pergunta, contexto)

            else:
                # Para casos ambíguos, usa IA com contexto completo
                return self._consultar_ia_com_contexto_completo(pergunta, contexto)

        except Exception as e:
            print(f"Erro ao processar pergunta: {str(e)}")
            return "🤖 Oi! Sou a Lumi! ✨ Parece que houve um pequeno problema técnico. Pode reformular sua pergunta? Estou aqui para te ajudar! 💪"

    def _normalizar_pergunta(self, pergunta):
        """
        Normaliza a pergunta substituindo referências temporais e pronomes
        """
        texto = pergunta.lower().strip()

        # Substitui referências a mim (Lumi)
        for pronome in self.vocabulario["pronomes_usuario"]:
            texto = re.sub(rf"\b{pronome}\b", "lumi", texto)

        # Normaliza referências temporais
        for ref_temporal, valor in self.vocabulario["referencias_temporais"].items():
            if ref_temporal in texto:
                if isinstance(valor, int):
                    data_calculada = self._calcular_data_referencia(valor)
                    texto = texto.replace(ref_temporal, f"data:{data_calculada}")

        return texto

    def _calcular_data_referencia(self, dias_offset):
        """
        Calcula a data baseada no offset de dias
        """
        try:
            data_base = datetime(2025, 5, 23)  # Data atual do sistema
            data_calculada = data_base + timedelta(days=dias_offset)
            return data_calculada.strftime("%d/%m/%Y")
        except:
            return "23/05/2025"

    def _analisar_intenção_natural(self, pergunta_normalizada, pergunta_original):
        """
        Sistema otimizado de análise com compreensão natural
        """
        texto_lower = pergunta_normalizada.lower()
        texto_original = pergunta_original.lower()

        # Inicialização de scores
        scores = {
            "gestao_tarefas": 0,
            "explicacao_educativa": 0,
            "produtividade_coaching": 0,
            "relatorio": 0,
            "planejamento": 0,
            "conversa_geral": 0,
        }

        contexto = {
            "acao": None,
            "entidades": {},
            "urgencia": "normal",
            "target_task": None,
            "data_referencia": None,
            "usuario_se_refere_a_lumi": False,
        }

        # LAYER 1: Detecção se o usuário está se referindo à Lumi
        if any(ref in texto_lower for ref in ["lumi", "você", "voce", "vc"]):
            contexto["usuario_se_refere_a_lumi"] = True

        # LAYER 2: Análise otimizada de ações
        acao_detectada = None
        max_score_acao = 0

        for acao, variacoes in self.vocabulario.items():
            if acao in ["adicionar", "remover", "consultar", "editar", "concluir"]:
                score_acao = 0

                for variacao in variacoes:
                    if (
                        variacao in texto_original
                    ):  # Usa texto original para mais precisão
                        score_acao += 3

                        # Boost para referência direta à Lumi
                        if contexto["usuario_se_refere_a_lumi"]:
                            score_acao += 2

                if score_acao > max_score_acao:
                    max_score_acao = score_acao
                    acao_detectada = acao

        if acao_detectada:
            scores["gestao_tarefas"] += max_score_acao
            contexto["acao"] = acao_detectada

        # LAYER 3: Padrões específicos melhorados
        padroes_gestao = [
            # Padrões de adição
            (
                r"(?:adicione?|crie?|agende?|marque?|inclua?|coloque?)\s+(?:na\s+)?(?:minha\s+)?(?:lista|agenda)",
                "adicionar",
            ),
            (r"(?:preciso|tenho que|vou)\s+fazer", "adicionar"),
            (r"(?:me\s+)?lembre?\s+de", "adicionar"),
            (r"novo?\s+(?:tarefa|compromisso|evento)", "adicionar"),
            # Padrões de remoção
            (
                r"(?:remova?|delete?|tire?|exclua?)\s+(?:da\s+)?(?:minha\s+)?(?:lista|agenda)",
                "remover",
            ),
            (r"(?:limpe?|limpar)\s+(?:minha\s+)?(?:lista|agenda|tudo)", "remover"),
            # Padrões de consulta
            (r"(?:como\s+está|como\s+tá)\s+(?:minha\s+)?agenda", "consultar"),
            (r"(?:quais?|que)\s+(?:tarefas?|compromissos?)", "consultar"),
            (r"(?:tenho|tem|há)\s+(?:alguma?|tarefas?)", "consultar"),
            # Padrões de edição
            (r"(?:edite?|modifique?|altere?|mude?)", "editar"),
            (r"(?:trocar|mudar|alterar)\s+(?:a\s+)?tarefa", "editar"),
            # Padrões de conclusão
            (r"(?:marque?|marcar)\s+como\s+(?:feita?|concluída?|pronta?)", "concluir"),
            (r"(?:terminei|acabei|finalizei)", "concluir"),
        ]

        for padrao, acao in padroes_gestao:
            if re.search(padrao, texto_original):
                scores["gestao_tarefas"] += 4
                if not contexto["acao"] or scores["gestao_tarefas"] > max_score_acao:
                    contexto["acao"] = acao
                break

        # LAYER 4: Detecção de alvos específicos (otimizada)
        contexto = self._detectar_alvos_especificos(texto_original, contexto)

        # LAYER 5: Indicadores educativos
        if scores["gestao_tarefas"] < 3:
            indicadores_educativos = [
                "explique",
                "como funciona",
                "o que é",
                "significa",
                "defina",
                "me ensine",
                "aprenda",
                "entender",
                "compreender",
                "dúvida",
            ]

            for indicador in indicadores_educativos:
                if indicador in texto_original:
                    scores["explicacao_educativa"] += 4
                    break

        # LAYER 6: Extração de entidades
        contexto["entidades"] = self._extrair_entidades_avancadas(pergunta_original)

        # LAYER 7: Boost final para solicitações diretas
        palavras_solicitacao = ["preciso", "quero", "gostaria", "pode", "consegue"]
        for palavra in palavras_solicitacao:
            if palavra in texto_original:
                if contexto["usuario_se_refere_a_lumi"]:
                    scores["gestao_tarefas"] += 3
                break

        # Determina intenção principal
        intenção_principal = max(scores, key=scores.get)
        confiança = scores[intenção_principal] / max(sum(scores.values()), 1)

        return intenção_principal, confiança, contexto

    def _detectar_alvos_especificos(self, texto, contexto):
        """
        Detecta alvos específicos de forma otimizada
        """
        if contexto.get("acao") == "remover":
            if any(palavra in texto for palavra in ["todas", "tudo", "toda", "limpar"]):
                contexto["target_task"] = "todas"
            elif "primeira" in texto:
                contexto["target_task"] = "primeira"
            elif "última" in texto or "ultimo" in texto:
                contexto["target_task"] = "última"
            else:
                # Tenta extrair nome específico de tarefa
                match = re.search(r'["\']([^"\']+)["\']', texto)
                if match:
                    contexto["target_task"] = match.group(1)

        return contexto

    def _detectar_e_processar_acao_automatica(self, pergunta, contexto):
        """
        Fallback para detectar ação quando não foi identificada claramente
        """
        texto_lower = pergunta.lower()

        # Verifica se parece ser adição de tarefa
        if any(
            palavra in texto_lower
            for palavra in ["fazer", "commit", "estudar", "reunião", "ligar", "comprar"]
        ):
            # Se contém horário ou data, provavelmente é adição
            if re.search(
                r"\d{1,2}:\d{2}|\d{1,2}h|\d{1,2}/\d{1,2}|hoje|amanhã|amanha",
                texto_lower,
            ):
                return self._processar_adicao_tarefa(pergunta, contexto)
            # Se é uma frase descritiva, também pode ser adição
            elif len(pergunta.split()) > 3:
                return self._processar_adicao_tarefa(pergunta, contexto)

        # Se não conseguiu detectar, volta para consulta geral
        return self._processar_consulta_agenda(pergunta, contexto)

    def _extrair_entidades_avancadas(self, texto):
        """
        Extração otimizada de entidades
        """
        entidades = {}
        texto_lower = texto.lower()

        # Datas com referências naturais
        referencias_data = {
            "hoje": "23/05/2025",
            "amanhã": "24/05/2025",
            "amanha": "24/05/2025",
            "ontem": "22/05/2025",
        }

        for ref, data in referencias_data.items():
            if ref in texto_lower:
                entidades.setdefault("datas", []).append(data)

        # Datas específicas
        datas_especificas = re.findall(r"\b(\d{1,2}/\d{1,2}(?:/\d{4})?)\b", texto)
        if datas_especificas:
            entidades.setdefault("datas", []).extend(datas_especificas)

        # Horários (formato mais flexível)
        horarios = re.findall(r"\b(\d{1,2}):?(\d{2})?\s*(?:h|hs|horas?)?\b", texto)
        if horarios:
            entidades["horarios"] = [f"{h}:{m if m else '00'}" for h, m in horarios]

        return entidades

    def _processar_adicao_tarefa(self, pergunta, contexto):
        """
        Processa adição de tarefas de forma otimizada
        """
        try:
            info_tarefa = self._extrair_informacoes_tarefa_otimizada(pergunta, contexto)

            if info_tarefa and info_tarefa.get("título"):
                resultado = self.task_manager.adicionar_item("tarefa", info_tarefa)

                if (
                    "sucesso" in resultado.lower()
                    or "ótimo" in resultado.lower()
                    or "adicionada" in resultado.lower()
                ):
                    return f"✅ Perfeito! {resultado} 🎯"
                else:
                    return f"✅ Tarefa '{info_tarefa['título']}' adicionada com sucesso! 🎯"
            else:
                return "🤔 Para adicionar uma tarefa, me diga o que você precisa fazer! Por exemplo: 'Adicione fazer commit para o github hoje às 14:00' ou 'Preciso estudar Python amanhã'. Como posso ajudar?"

        except Exception as e:
            print(f"Erro na adição: {str(e)}")
            return f"❌ Tive um problema ao adicionar a tarefa. Pode tentar novamente? Erro: {str(e)}"

    def _extrair_informacoes_tarefa_otimizada(self, pergunta, contexto):
        """
        Extração otimizada de informações de tarefas
        """
        info = {}
        texto_lower = pergunta.lower()

        # Padrões otimizados para extração de título
        padroes_titulo = [
            # Comando direto: "Adicione [tarefa]"
            r"(?:adicione?|crie?|agende?|marque?|inclua?)\s+(?:na\s+lista\s+)?(?:fazer\s+)?(.+?)(?:\s+(?:para|às?|em|hoje|amanhã|amanha)|$)",
            # Necessidade: "Preciso [fazer algo]"
            r"(?:preciso|tenho\s+que|vou)\s+(?:fazer\s+)?(.+?)(?:\s+(?:para|às?|em|hoje|amanhã|amanha)|$)",
            # Formato lembrete: "Me lembre de [fazer algo]"
            r"(?:me\s+)?lembre?\s+de\s+(?:fazer\s+)?(.+?)(?:\s+(?:para|às?|em|hoje|amanhã|amanha)|$)",
            # Formato tarefa: "Nova tarefa: [algo]"
            r"(?:nova?\s+)?(?:tarefa|task)[:,]?\s*(.+?)(?:\s+(?:para|às?|em|hoje|amanhã|amanha)|$)",
        ]

        titulo_encontrado = False
        for padrao in padroes_titulo:
            match = re.search(padrao, texto_lower)
            if match:
                titulo = match.group(1).strip()
                if len(titulo) > 2:
                    # Limpa palavras desnecessárias do título
                    palavras_remover = ["a", "o", "da", "do", "na", "no", "de", "para"]
                    titulo_limpo = " ".join(
                        [
                            p
                            for p in titulo.split()
                            if p not in palavras_remover or len(titulo.split()) <= 3
                        ]
                    )
                    info["título"] = titulo_limpo.title()
                    titulo_encontrado = True
                    break

        # Se não encontrou por padrão, usa análise heurística
        if not titulo_encontrado:
            # Remove palavras de comando e pega o resto
            palavras_comando = [
                "adicionar",
                "adicione",
                "criar",
                "crie",
                "agendar",
                "agende",
                "marcar",
                "marque",
                "incluir",
                "inclua",
                "colocar",
                "coloque",
                "na",
                "minha",
                "lista",
                "agenda",
                "tarefa",
                "task",
            ]

            palavras = pergunta.split()
            titulo_palavras = []

            for palavra in palavras:
                if palavra.lower() not in palavras_comando:
                    titulo_palavras.append(palavra)
                    # Para quando encontrar indicador temporal
                    if palavra.lower() in [
                        "hoje",
                        "amanhã",
                        "amanha",
                        "para",
                        "às",
                        "as",
                        "em",
                    ]:
                        break

            if titulo_palavras:
                info["título"] = " ".join(titulo_palavras[:8]).strip()

        # Extração de data otimizada
        entidades = contexto.get("entidades", {})
        if entidades.get("datas"):
            info["data"] = entidades["datas"][0]
        elif any(palavra in texto_lower for palavra in ["hoje"]):
            info["data"] = "23/05/2025"
        elif any(palavra in texto_lower for palavra in ["amanhã", "amanha"]):
            info["data"] = "24/05/2025"
        else:
            info["data"] = "23/05/2025"  # Default para hoje

        # Extração de horário
        if entidades.get("horarios"):
            info["hora"] = entidades["horarios"][0]
        else:
            # Busca por horários no formato mais comum
            horario_match = re.search(
                r"(?:às?|as)\s*(\d{1,2}):?(\d{2})?(?:\s*h)?", texto_lower
            )
            if horario_match:
                hora = horario_match.group(1)
                minuto = horario_match.group(2) or "00"
                info["hora"] = f"{hora.zfill(2)}:{minuto}"

        return info

    # Métodos de remoção mantidos (já funcionando)
    def _processar_remocao_tarefa(self, pergunta, contexto):
        """
        Processa remoção com compreensão natural aprimorada
        """
        try:
            target_task = contexto.get("target_task")

            if not target_task:
                target_task = self._detectar_alvo_remocao_inteligente(pergunta)

            if target_task == "todas" or any(
                palavra in pergunta.lower()
                for palavra in ["todas", "tudo", "limpar", "limpe"]
            ):
                return self._remover_todas_tarefas()
            elif target_task == "primeira":
                return self._remover_primeira_tarefa()
            elif target_task == "última":
                return self._remover_ultima_tarefa()
            elif target_task:
                return self._remover_tarefa_especifica(target_task)
            else:
                return "🤔 Posso te ajudar a remover tarefas! Me diga qual você quer remover. Por exemplo: 'Remove todas as tarefas' ou 'Tire a tarefa X da minha agenda'. O que você gostaria?"

        except Exception as e:
            return f"❌ Erro ao processar remoção: {str(e)}"

    def _detectar_alvo_remocao_inteligente(self, pergunta):
        """
        Detecta o alvo da remoção de forma mais inteligente
        """
        texto_lower = pergunta.lower()

        if any(
            palavra in texto_lower
            for palavra in ["todas", "tudo", "toda", "limpar", "limpe"]
        ):
            return "todas"
        elif "primeira" in texto_lower:
            return "primeira"
        elif "última" in texto_lower or "ultimo" in texto_lower:
            return "última"

        # Procura por nomes de tarefas entre aspas
        match = re.search(r'["\']([^"\']+)["\']', texto_lower)
        if match:
            return match.group(1).strip()

        return None

    def _remover_todas_tarefas(self):
        """Remove todas as tarefas da agenda"""
        try:
            total_tarefas = len(self.task_manager.tasks["tarefas"])
            if total_tarefas == 0:
                return "📝 Sua agenda já está vazia! Não há tarefas para remover. Quer que eu te ajude a criar algumas novas atividades? ✨"

            self.task_manager.tasks["tarefas"] = []
            if self.task_manager._salvar_tarefas():
                return f"✅ Perfeito! Removi todas as {total_tarefas} tarefas da sua agenda! 🗑️✨ Sua lista agora está limpa e pronta para novas atividades. Como posso te ajudar a organizar suas próximas tarefas?"
            else:
                return "❌ Ops! Houve um problema ao remover as tarefas. Pode tentar novamente?"
        except Exception as e:
            return f"❌ Erro ao remover todas as tarefas: {str(e)}"

    def _remover_primeira_tarefa(self):
        """Remove a primeira tarefa da lista"""
        try:
            tarefas = self.task_manager.tasks["tarefas"]
            if not tarefas:
                return "📝 Sua agenda está vazia! Não há tarefas para remover."

            primeira_tarefa = tarefas.pop(0)
            if self.task_manager._salvar_tarefas():
                return f"✅ Pronto! Removi a tarefa '{primeira_tarefa['título']}' da sua agenda! 🗑️"
            else:
                tarefas.insert(0, primeira_tarefa)
                return "❌ Ops! Houve um problema ao remover a tarefa. Pode tentar novamente?"
        except Exception as e:
            return f"❌ Erro ao remover primeira tarefa: {str(e)}"

    def _remover_ultima_tarefa(self):
        """Remove a última tarefa da lista"""
        try:
            tarefas = self.task_manager.tasks["tarefas"]
            if not tarefas:
                return "📝 Sua agenda está vazia! Não há tarefas para remover."

            ultima_tarefa = tarefas.pop()
            if self.task_manager._salvar_tarefas():
                return f"✅ Feito! Removi a tarefa '{ultima_tarefa['título']}' da sua agenda! 🗑️"
            else:
                tarefas.append(ultima_tarefa)
                return "❌ Ops! Houve um problema ao remover a tarefa. Pode tentar novamente?"
        except Exception as e:
            return f"❌ Erro ao remover última tarefa: {str(e)}"

    def _remover_tarefa_especifica(self, nome_tarefa):
        """Remove uma tarefa específica pelo nome"""
        try:
            tarefas = self.task_manager.tasks["tarefas"]
            nome_lower = nome_tarefa.lower().strip()

            # Procura por correspondência exata primeiro
            for i, tarefa in enumerate(tarefas):
                if tarefa["título"].lower() == nome_lower:
                    tarefa_removida = tarefas.pop(i)
                    if self.task_manager._salvar_tarefas():
                        return f"✅ Perfeito! Removi a tarefa '{tarefa_removida['título']}' da sua agenda! 🗑️✨"
                    else:
                        tarefas.insert(i, tarefa_removida)
                        return "❌ Houve um problema ao salvar. Pode tentar novamente?"

            # Procura por correspondência parcial
            for i, tarefa in enumerate(tarefas):
                if nome_lower in tarefa["título"].lower():
                    tarefa_removida = tarefas.pop(i)
                    if self.task_manager._salvar_tarefas():
                        return f"✅ Encontrei e removi: '{tarefa_removida['título']}'! 🗑️ Era essa mesmo?"
                    else:
                        tarefas.insert(i, tarefa_removida)
                        return "❌ Houve um problema ao salvar. Pode tentar novamente?"

            return f"🔍 Não encontrei uma tarefa com o nome '{nome_tarefa}'. Quer que eu mostre sua lista atual?"

        except Exception as e:
            return f"❌ Erro ao remover tarefa específica: {str(e)}"

    # Método de edição implementado
    def _processar_edicao_tarefa(self, pergunta, contexto):
        """
        Processa edição de tarefas
        """
        try:
            # Detecta qual tarefa editar e o que mudar
            info_edicao = self._extrair_informacoes_edicao(pergunta)

            if not info_edicao.get("target"):
                return "🤔 Para editar uma tarefa, me diga qual você quer modificar e o que mudar. Por exemplo: 'Edite a primeira tarefa para Estudar Python' ou 'Mude o horário da reunião para 15:00'. Como posso ajudar?"

            tarefas = self.task_manager.tasks["tarefas"]
            target = info_edicao["target"]

            # Encontra a tarefa
            tarefa_encontrada = None
            indice = -1

            if target == "primeira" and tarefas:
                tarefa_encontrada = tarefas[0]
                indice = 0
            elif target == "última" and tarefas:
                tarefa_encontrada = tarefas[-1]
                indice = len(tarefas) - 1
            else:
                # Busca por nome
                for i, tarefa in enumerate(tarefas):
                    if target.lower() in tarefa["título"].lower():
                        tarefa_encontrada = tarefa
                        indice = i
                        break

            if not tarefa_encontrada:
                return f"🔍 Não encontrei a tarefa '{target}'. Verifique o nome e tente novamente!"

            # Aplica as mudanças
            titulo_antigo = tarefa_encontrada["título"]

            if info_edicao.get("novo_titulo"):
                tarefa_encontrada["título"] = info_edicao["novo_titulo"]

            if info_edicao.get("nova_data"):
                tarefa_encontrada["data"] = info_edicao["nova_data"]

            if info_edicao.get("novo_horario"):
                tarefa_encontrada["hora"] = info_edicao["novo_horario"]

            # Salva as mudanças
            if self.task_manager._salvar_tarefas():
                return f"✅ Perfeito! Editei a tarefa '{titulo_antigo}' → '{tarefa_encontrada['título']}' com sucesso! 📝✨"
            else:
                return "❌ Ops! Houve um problema ao salvar as alterações. Tente novamente."

        except Exception as e:
            return f"❌ Erro ao editar tarefa: {str(e)}"

    def _extrair_informacoes_edicao(self, pergunta):
        """
        Extrai informações para edição de tarefa
        """
        info = {}
        texto_lower = pergunta.lower()

        # Detecta qual tarefa editar
        if "primeira" in texto_lower:
            info["target"] = "primeira"
        elif "última" in texto_lower or "ultimo" in texto_lower:
            info["target"] = "última"
        else:
            # Busca por nome entre aspas ou depois de "tarefa"
            match = re.search(r'(?:tarefa\s+)?["\']([^"\']+)["\']', texto_lower)
            if match:
                info["target"] = match.group(1)
            else:
                # Tenta extrair nome da tarefa de forma mais ampla
                palavras_comando = [
                    "edite",
                    "editar",
                    "modificar",
                    "modifique",
                    "alterar",
                    "altere",
                    "mudar",
                    "mude",
                ]
                palavras = pergunta.split()

                for i, palavra in enumerate(palavras):
                    if palavra.lower() in palavras_comando and i + 1 < len(palavras):
                        if palavras[i + 1].lower() not in ["a", "o", "para", "de"]:
                            info["target"] = palavras[i + 1]
                            break

        # Detecta novo título (após "para")
        match = re.search(r"para\s+(.+?)(?:\s+(?:às?|em|hoje|amanhã)|$)", texto_lower)
        if match:
            info["novo_titulo"] = match.group(1).strip().title()

        # Detecta novo horário
        horario_match = re.search(
            r"(?:às?|para)\s*(\d{1,2}):?(\d{2})?(?:\s*h)?", texto_lower
        )
        if horario_match:
            hora = horario_match.group(1)
            minuto = horario_match.group(2) or "00"
            info["novo_horario"] = f"{hora.zfill(2)}:{minuto}"

        # Detecta nova data
        if "hoje" in texto_lower:
            info["nova_data"] = "23/05/2025"
        elif "amanhã" in texto_lower or "amanha" in texto_lower:
            info["nova_data"] = "24/05/2025"

        return info

    # Métodos de consulta, conclusão e outros mantidos (otimizados)
    def _processar_consulta_agenda(self, pergunta, contexto):
        """
        Processa consultas de agenda de forma otimizada
        """
        try:
            parametros = self._extrair_parametros_consulta_natural(pergunta, contexto)

            resultado = self.task_manager.consultar_itens(
                parametros.get("tipo", "todos"), {"data": parametros.get("data")}
            )

            return self._formatar_resposta_consulta_natural(resultado, parametros)

        except Exception as e:
            return f"❓ Ops! Tive um problema ao consultar sua agenda: {str(e)}"

    def _extrair_parametros_consulta_natural(self, pergunta, contexto):
        """
        Extrai parâmetros de consulta de forma otimizada
        """
        parametros = {}
        texto_lower = pergunta.lower()

        # Detecção temporal
        if "hoje" in texto_lower:
            parametros["data"] = "23/05/2025"
            parametros["referencia_temporal"] = "hoje"
        elif "amanhã" in texto_lower or "amanha" in texto_lower:
            parametros["data"] = "24/05/2025"
            parametros["referencia_temporal"] = "amanhã"
        elif "ontem" in texto_lower:
            parametros["data"] = "22/05/2025"
            parametros["referencia_temporal"] = "ontem"

        # Tipo de consulta
        if any(
            palavra in texto_lower
            for palavra in ["evento", "eventos", "reunião", "reuniões"]
        ):
            parametros["tipo"] = "evento"
        elif any(
            palavra in texto_lower
            for palavra in ["tarefa", "tarefas", "task", "atividade"]
        ):
            parametros["tipo"] = "tarefa"
        else:
            parametros["tipo"] = "todos"

        return parametros

    def _formatar_resposta_consulta_natural(self, resultado, parametros):
        """
        Formata resposta de consulta de forma natural
        """
        if not resultado or resultado.strip() == "":
            ref_temporal = parametros.get("referencia_temporal", "")
            if ref_temporal:
                return f"📅 Sua agenda está livre {ref_temporal}! ✨ Quer que eu te ajude a planejar algumas atividades produtivas?"
            else:
                return "📅 Sua agenda está vazia no momento! ✨ Pronta para organizar suas próximas tarefas?"

        # Personaliza a introdução
        ref_temporal = parametros.get("referencia_temporal", "")
        if ref_temporal == "hoje":
            intro = "📅 Aqui está sua agenda para hoje:"
        elif ref_temporal == "amanhã":
            intro = "📅 Sua agenda para amanhã:"
        elif ref_temporal == "ontem":
            intro = "📅 Suas atividades de ontem:"
        else:
            intro = "📅 Sua agenda atual:"

        return f"{intro}\n\n{resultado}\n\n💡 Posso te ajudar a organizar melhor ou adicionar algo?"

    def _processar_conclusao_tarefa(self, pergunta, contexto):
        """
        Processa conclusão de tarefas de forma otimizada
        """
        try:
            target_task = contexto.get("target_task")

            if target_task == "primeira":
                return self._concluir_primeira_tarefa()
            elif target_task:
                return self._concluir_tarefa_especifica(target_task)
            else:
                return self._processar_conclusao_inteligente(pergunta)

        except Exception as e:
            return f"❌ Erro ao processar conclusão: {str(e)}"

    def _concluir_primeira_tarefa(self):
        """Marca a primeira tarefa como concluída"""
        try:
            tarefas = self.task_manager.tasks["tarefas"]
            if not tarefas:
                return "📝 Sua agenda está vazia! Não há tarefas para marcar como concluídas."

            tarefas[0]["concluído"] = True
            if self.task_manager._salvar_tarefas():
                return f"🎉 Parabéns! Tarefa '{tarefas[0]['título']}' marcada como concluída! Você está arrasando! ✅"
            else:
                tarefas[0]["concluído"] = False
                return "❌ Ops! Houve um problema ao salvar. Tente novamente."
        except Exception as e:
            return f"❌ Erro ao concluir primeira tarefa: {str(e)}"

    def _concluir_tarefa_especifica(self, nome_tarefa):
        """Marca uma tarefa específica como concluída"""
        try:
            tarefas = self.task_manager.tasks["tarefas"]
            nome_lower = nome_tarefa.lower()

            for tarefa in tarefas:
                if nome_lower in tarefa["título"].lower():
                    tarefa["concluído"] = True
                    if self.task_manager._salvar_tarefas():
                        return f"🎉 Excelente! Tarefa '{tarefa['título']}' marcada como concluída! Continue assim! ✅🚀"
                    else:
                        tarefa["concluído"] = False
                        return "❌ Ops! Houve um problema ao salvar. Tente novamente."

            return f"🔍 Não encontrei a tarefa '{nome_tarefa}'. Verifique o nome e tente novamente!"

        except Exception as e:
            return f"❌ Erro ao concluir tarefa: {str(e)}"

    def _processar_conclusao_inteligente(self, pergunta):
        """Fallback para extrair e concluir tarefas"""
        padroes = [
            r'(?:marque?|concluir?|finalizar?)\s+(?:como\s+)?(?:concluída?|feita?|pronta?)\s+(?:a\s+)?(?:tarefa\s+)?["\']?([^"\']+)["\']?',
            r"(?:está\s+)?(?:feita?|pronta?|concluída?)\s+(?:a\s+)?(?:tarefa\s+)?(.+?)(?:\s|$)",
        ]

        for padrao in padroes:
            match = re.search(padrao, pergunta.lower())
            if match:
                nome_tarefa = match.group(1).strip()
                if len(nome_tarefa) > 2:
                    return self._concluir_tarefa_especifica(nome_tarefa)

        return "🤔 Para marcar uma tarefa como concluída, me diga qual é. Por exemplo: 'Marcar como concluída a tarefa Estudo Programação' ou 'A primeira está feita'. Como posso ajudar?"

    # Métodos auxiliares otimizados
    def _consultar_ia_com_contexto_completo(self, pergunta, contexto):
        """
        Consulta IA com contexto completo para casos ambíguos
        """
        prompt_contextualizado = f"""PERGUNTA DO USUÁRIO: {pergunta}

CONTEXTO:
- Usuário está se referindo à Lumi: {contexto.get('usuario_se_refere_a_lumi', False)}
- Entidades detectadas: {contexto.get('entidades', {})}
- Data de referência: 23/05/2025

Como Lumi, responda de forma natural, amigável e útil. Se a pergunta envolver tarefas ou agenda, seja proativa em oferecer ajuda específica.

Use emojis estrategicamente e mantenha o foco na produtividade."""

        return self._consultar_ia_otimizada(
            prompt_contextualizado, "conversa_geral", contexto
        )

    def _processar_explicacao_educativa(self, pergunta, contexto):
        """Processa solicitações educativas"""
        prompt_educativo = f"""PERGUNTA EDUCATIVA: {pergunta}

Forneça uma explicação clara, didática e prática. Estruture a resposta com:
1. Definição/conceito principal
2. Exemplos práticos
3. Aplicação na produtividade/estudos
4. Dicas para implementação

Seja motivadora e use emojis estrategicamente."""

        resposta = self._consultar_ia_com_cache(prompt_educativo, tipo="educativa")
        return self._formatar_resposta_lumi(resposta, "explicacao")

    def _processar_coaching_produtividade(self, pergunta, contexto):
        """Processa solicitações de coaching"""
        prompt_coaching = f"""COACHING DE PRODUTIVIDADE: {pergunta}

Como especialista em produtividade, forneça:
1. Análise da situação
2. Técnicas específicas aplicáveis
3. Passos práticos para implementação
4. Motivação personalizada

Use linguagem energética e motivadora com emojis."""

        resposta = self._consultar_ia_com_cache(prompt_coaching, tipo="coaching")
        return self._formatar_resposta_lumi(resposta, "coaching")

    def _processar_relatorio(self, pergunta, contexto=None):
        """Processa comandos relacionados a relatórios"""
        try:
            info_relatorio = self._extrair_informacoes_relatorio(pergunta)
            relatorio = self.reports_generator.gerar_relatório(info_relatorio)
            return f"📊 Aqui está seu relatório:\n\n{relatorio}"
        except Exception as e:
            return f"❌ Problema ao gerar relatório: {str(e)}"

    def _extrair_informacoes_relatorio(self, pergunta):
        """Extrai informações do relatório"""
        info = {}

        if any(
            palavra in pergunta.lower() for palavra in ["produtividade", "desempenho"]
        ):
            info["tipo_relatório"] = "produtividade"
        elif any(palavra in pergunta.lower() for palavra in ["tarefa", "tarefas"]):
            info["tipo_relatório"] = "tarefas"
        else:
            info["tipo_relatório"] = "geral"

        if "hoje" in pergunta.lower():
            info["período"] = "dia"
        elif any(palavra in pergunta.lower() for palavra in ["semana", "semanal"]):
            info["período"] = "semana"
        elif any(palavra in pergunta.lower() for palavra in ["mês", "mensal"]):
            info["período"] = "mês"
        else:
            info["período"] = "dia"

        return info

    def _processar_planejamento(self, pergunta, contexto):
        """Processa solicitações de planejamento"""
        prompt_planejamento = f"""SOLICITAÇÃO DE PLANEJAMENTO: {pergunta}

Como especialista em organização, ajude com:
📅 ESTRUTURAÇÃO: Organize as informações
⏰ CRONOGRAMA: Sugira prazos realistas
🎯 PRIORIZAÇÃO: Identifique o mais importante
💪 IMPLEMENTAÇÃO: Passos práticos para executar

Seja organizadora e motivadora."""

        resposta = self._consultar_ia_com_cache(
            prompt_planejamento, tipo="planejamento"
        )
        return self._formatar_resposta_lumi(resposta, "coaching")

    # Métodos de IA otimizados
    def _consultar_ia_otimizada(self, pergunta, intenção, contexto):
        """Consulta IA com cache otimizado"""
        cache_key = self._gerar_cache_key_avancada(pergunta, intenção)
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]

        prompt_otimizado = self._gerar_prompt_especializado(
            pergunta, intenção, contexto
        )

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
                    {"role": "user", "content": prompt_otimizado},
                ],
                "temperature": 0.7 if intenção == "explicacao_educativa" else 0.5,
                "max_tokens": self._calcular_tokens_otimos(pergunta, intenção),
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.1,
            }

            response = requests.post(
                url=self.BASE_URL, headers=headers, json=payload, timeout=25
            )

            if response.status_code == 200:
                result = response.json()
                resposta = result["choices"][0]["message"]["content"]

                if len(pergunta) < 150 and len(self.response_cache) < 50:
                    self.response_cache[cache_key] = resposta

                return resposta
            else:
                return "Desculpe, estou com dificuldades no momento. Pode tentar reformular sua pergunta?"

        except Exception as e:
            return "Ops! Tive um problema técnico. Tente novamente em instantes! 💪"

    def _gerar_prompt_especializado(self, pergunta, intenção, contexto):
        """Gera prompts especializados"""
        if intenção == "explicacao_educativa":
            return f"""SOLICITAÇÃO EDUCATIVA: {pergunta}

Forneça uma explicação didática e motivadora seguindo esta estrutura:
📚 CONCEITO: Definição clara e simples
🎯 APLICAÇÃO: Como usar na prática
💡 DICAS: Sugestões específicas para implementar
✨ MOTIVAÇÃO: Frase inspiradora relacionada

Use linguagem acessível, emojis estratégicos e seja concisa mas completa."""

        elif intenção == "produtividade_coaching":
            return f"""COACHING DE PRODUTIVIDADE: {pergunta}

Como coach especializada, forneça:
🎯 ANÁLISE: Identifique o ponto principal
⚡ TÉCNICAS: 2-3 métodos práticos específicos
📋 AÇÃO: Passos concretos para implementar
🚀 MOTIVAÇÃO: Encoraje com energia positiva

Seja prática, motivadora e use emojis estrategicamente."""

        else:
            return f"""ASSISTÊNCIA GERAL: {pergunta}

Responda de forma útil, motivadora e prática. Use emojis apropriados e mantenha foco na produtividade do usuário."""

    def _calcular_tokens_otimos(self, pergunta, intenção):
        """Calcula tokens ótimos"""
        base_tokens = len(pergunta.split()) * 8

        if intenção == "explicacao_educativa":
            return min(max(base_tokens, 200), 400)
        elif intenção == "produtividade_coaching":
            return min(max(base_tokens, 150), 300)
        else:
            return min(max(base_tokens, 100), 250)

    def _gerar_cache_key_avancada(self, pergunta, intenção):
        """Gera chave de cache otimizada"""
        palavras_chave = re.sub(r"[^\w\s]", "", pergunta.lower()).split()
        palavras_importantes = [p for p in palavras_chave if len(p) > 3][:5]
        return f"{intenção}:" + "_".join(sorted(palavras_importantes))

    def _formatar_resposta_lumi(self, resposta, tipo):
        """Formatação otimizada de respostas"""
        if not resposta:
            return "🤖 Oi! Sou a Lumi! Como posso turbinar sua produtividade hoje? ✨"

        prefixos = {
            "explicacao": "💡 ",
            "coaching": "🚀 ",
            "consulta": "",
            "tarefa": "✅ ",
            "relatorio": "📊 ",
            "geral": "💪 ",
        }

        prefixo = prefixos.get(tipo, "💡 ")

        if not any(
            resposta.startswith(emoji)
            for emoji in [
                "🤖",
                "✅",
                "❌",
                "📊",
                "🗓️",
                "💡",
                "🚀",
                "💪",
                "🎉",
                "🔍",
                "📅",
            ]
        ):
            resposta = prefixo + resposta

        return resposta

    def _consultar_ia_com_cache(self, prompt, tipo="geral"):
        """Versão simplificada para consultas rápidas"""
        return self._consultar_ia_otimizada(prompt, tipo, {})

    def _pre_processar_texto(self, texto):
        """Pré-processa texto"""
        return re.sub(r"\s+", " ", texto).strip()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
import re
import sys

# Verificar se o módulo requests está instalado
try:
    import requests
except ImportError:
    # Este erro será tratado pelo main.py, então não precisamos exibi-lo aqui
    pass

class LumiAssistant:
    """
    Classe principal do assistente de IA para o PomodoroTasks
    Utiliza o modelo Mistral: Devstral Small para processamento de linguagem natural
    """
    def __init__(self, task_manager, reports_generator):
        """
        Inicializa o assistente com acesso aos gerenciadores de tarefas e relatórios
        
        Args:
            task_manager: Instância do gerenciador de tarefas
            reports_generator: Instância do gerador de relatórios
        """
        self.API_KEY = "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"
        self.MODEL = "mistralai/devstral-small:free"
        self.BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
        self.task_manager = task_manager
        self.reports_generator = reports_generator
        # Configuração do sistema para otimizar o uso da IA
        self.system_prompt = """
        Você é Lumi, a assistente de IA do PomodoroTasks, especializada em produtividade, gestão de tempo e disciplina.
        
        Suas habilidades principais são:
        1. Gerenciar eventos e tarefas na agenda do usuário com precisão e eficiência
        2. Gerar relatórios detalhados sobre produtividade e conclusão de tarefas
        3. Oferecer conselhos baseados em evidências sobre produtividade, foco e disciplina
        
        Diretrizes para respostas:
        - Sempre se identifique como "Lumi"
        - Seja concisa e direta: limite respostas a 3-5 sentenças quando possível
        - Priorize ações específicas e mensuráveis
        - Utilize linguagem positiva e motivacional
        - Ao detectar solicitações de agenda/tarefas, extraia imediatamente: título, data, hora, duração
        - Para relatórios, identifique automaticamente período (dia atual/semana/mês) se não especificado
        - Quando der conselhos, cite no máximo 3 técnicas comprovadas, em ordem de eficácia
        
        Estrutura de pensamento:
        1. Identifique a intenção principal (agenda, relatório ou conselho)
        2. Extraia entidades chave e parâmetros relevantes
        3. Formule uma resposta estruturada e orientada à ação
        4. Sugira próximos passos quando apropriado
        
        Se informações forem insuficientes, peça apenas os detalhes cruciais para completar a tarefa.
        """
        
        # Cache para otimização de respostas frequentes
        self.response_cache = {}
            
    def processar_pergunta(self, pergunta):
        """
        Processa a pergunta do usuário usando análise multi-estágio para melhor compreensão
        e direciona para a função apropriada com contexto relevante
        
        Args:
            pergunta: A pergunta ou comando do usuário
            
        Returns:
            string: Resposta processada para o usuário
        """
        # Pré-processamento da pergunta
        pergunta_processada = self._pre_processar_texto(pergunta)
        
        # Análise de intenção - usando regras e modelo ML (simulado com regras mais sofisticadas)
        intenção, confiança = self._analisar_intenção(pergunta_processada)
        
        # Se a intenção for clara o suficiente, direciona para o processador específico
        if confiança > 0.7:  # Limite de confiança alto para evitar falsos positivos
            if intenção == "agenda":
                return self._processar_agenda(pergunta)
            elif intenção == "relatório":
                return self._processar_relatório(pergunta)
                
        # Se a intenção não for clara o suficiente, faz análise de conteúdo adicional
        contexto_usuario = self._extrair_contexto_usuario(pergunta)
        
        # Agora tomamos a decisão final com mais contexto
        if intenção == "agenda" or self._é_sobre_agenda(pergunta):
            resposta = self._processar_agenda(pergunta)
            return self._formatar_resposta_Lumi(resposta, "agenda")
            
        elif intenção == "relatório" or self._é_sobre_relatório(pergunta):
            resposta = self._processar_relatório(pergunta)
            return self._formatar_resposta_Lumi(resposta, "relatório")
            
        else:
            # Para perguntas gerais sobre produtividade, usamos a IA com contexto adicional
            prompt_final = pergunta
            if contexto_usuario:
                prompt_final = f"Considerando o seguinte contexto do usuário: {contexto_usuario}\n\nPergunta: {pergunta}"
            
            resposta = self._consultar_ia(prompt_final)
            return self._formatar_resposta_Lumi(resposta, "conselho")
            
    def _pre_processar_texto(self, texto):
        """Pré-processa o texto removendo informações irrelevantes"""
        # Remove caracteres especiais, normaliza espaços
        texto = re.sub(r'\s+', ' ', texto).strip()
        return texto
        
    def _analisar_intenção(self, texto):
        """Analisa a intenção do usuário usando regras avançadas"""
        # Pontuação para cada tipo de intenção
        pontos_agenda = 0
        pontos_relatorio = 0
        
        # Análise de palavras-chave com pesos
        texto_lower = texto.lower()
        
        # Palavras-chave para agenda com pesos
        palavras_agenda = {
            'adicionar': 3, 'criar': 3, 'nova': 2, 'agendar': 3, 
            'tarefa': 2, 'evento': 2, 'lembrete': 2, 'marcar': 2,
            'remover': 3, 'deletar': 3, 'cancelar': 2, 'concluir': 2,
            'finalizar': 2, 'consultar': 2, 'mostrar': 1, 'listar': 1,
            'pomodoro': 1.5, 'prazo': 1.5, 'data': 1, 'hora': 1
        }
        
        # Palavras-chave para relatório com pesos
        palavras_relatorio = {
            'relatório': 3, 'estatística': 3, 'gráfico': 2.5, 'desempenho': 2,
            'produtividade': 2, 'análise': 2, 'resumo': 1.5, 'histórico': 1.5,
            'progresso': 1.5, 'rendimento': 2, 'concluído': 1, 'completo': 1,
            'período': 1.5, 'semana': 1, 'mês': 1, 'dia': 0.5, 'resultado': 1.5
        }
        
        # Calcula pontuação para cada categoria
        for palavra, peso in palavras_agenda.items():
            if palavra in texto_lower:
                pontos_agenda += peso
                
        for palavra, peso in palavras_relatorio.items():
            if palavra in texto_lower:
                pontos_relatorio += peso
                
        # Análise de padrões de frases (expressões regulares)
        padroes_agenda = [
            r'(adicionar?|criar?|nova|agendar) .{1,20} (tarefa|evento|lembrete)',
            r'(marcar|agendar) .{1,30} (para|no dia|às|as)',
            r'(remover|deletar|cancelar) .{1,20} (tarefa|evento|lembrete)',
            r'(mostrar|listar|ver) .{1,20} (tarefa|evento|agenda)',
            r'(concluir|finalizar|completar) .{1,20} tarefa'
        ]
        
        padroes_relatorio = [
            r'(relatório|estatística|análise) .{1,20} (de|da|do)',
            r'(mostrar|ver|gerar) .{1,20} (relatório|estatística|desempenho)',
            r'(produtividade|rendimento|progresso) .{1,20} (período|semana|mês|dia)',
            r'quanto .{1,30} (realizei|completei|concluí|fiz)'
        ]
        
        # Adiciona pontos para padrões encontrados
        for padrao in padroes_agenda:
            if re.search(padrao, texto_lower):
                pontos_agenda += 3
                
        for padrao in padroes_relatorio:
            if re.search(padrao, texto_lower):
                pontos_relatorio += 3
        
        # Determina a intenção com base na pontuação maior
        if pontos_agenda > pontos_relatorio and pontos_agenda > 3:
            confiança = min(1.0, pontos_agenda / 10)
            return "agenda", confiança
        elif pontos_relatorio > pontos_agenda and pontos_relatorio > 3:
            confiança = min(1.0, pontos_relatorio / 10)
            return "relatório", confiança
        else:
            # Confiança baixa, provavelmente é uma pergunta geral
            return "geral", 0.3
            
    def _extrair_contexto_usuario(self, texto):
        """Extrai informações de contexto do usuário da pergunta"""
        # Por enquanto é um stub, mas poderia extrair informações como:
        # - Período de tempo mencionado
        # - Tipo de tarefa ou atividade
        # - Estado emocional ou necessidade expressa
        return None
        
    def _formatar_resposta_Lumi(self, resposta, tipo):
        """Formata a resposta final com o estilo da Lumi"""
        # Garantir que a resposta sempre começa com a identificação da Lumi
        # se não for um relatório formatado que já tem sua própria formatação
        if tipo == "relatório" and resposta.strip().startswith("==="):
            return resposta
        
        if not resposta.startswith("Lumi:") and not "Lumi:" in resposta:
            # Adiciona o nome apenas se ainda não estiver incluído
            if ":" in resposta[:20]:  # Se já tiver algum prefixo
                resposta = "Lumi: " + resposta.split(":", 1)[1].strip()
            else:
                resposta = "Lumi: " + resposta
                
        return resposta
    
    def _é_sobre_agenda(self, texto):
        """Verifica se o texto é relacionado à agenda ou tarefas"""
        palavras_chave = ['agenda', 'tarefa', 'evento', 'marcar', 'adicionar', 
                          'remover', 'cancelar', 'concluir', 'finalizar', 'agendar',
                          'lembrete', 'compromisso', 'adicione', 'crie', 'pomodoro',
                          'programar', 'prazo']
        
        return any(palavra in texto.lower() for palavra in palavras_chave)
    
    def _é_sobre_relatório(self, texto):
        """Verifica se o texto é relacionado a relatórios"""
        palavras_chave = ['relatório', 'estatística', 'rendimento', 'desempenho',
                         'produtividade', 'histórico', 'análise', 'gráfico',
                         'resumo', 'progresso', 'completado', 'concluído',
                         'pomodoros', 'período', 'semana', 'mês', 'resultado']
        
        return any(palavra in texto.lower() for palavra in palavras_chave)
    
    def _processar_agenda(self, texto):
        """
        Processa comandos relacionados à agenda
        
        Args:
            texto: O texto do comando do usuário
            
        Returns:
            string: Resposta processada sobre agenda
        """
        # Extrair informações do texto usando IA para entender melhor a intenção
        prompt = f"""
        Analise o seguinte comando relacionado à agenda ou tarefas:
        
        "{texto}"
        
        Extraia apenas as seguintes informações em formato JSON:
        {{
          "ação": "adicionar/remover/consultar/modificar",
          "tipo": "tarefa/evento/lembrete",
          "título": "título da tarefa ou evento",
          "data": "data mencionada ou null",
          "hora": "hora mencionada ou null",
          "duração": "duração mencionada ou null",
          "descrição": "descrição adicional ou null"
        }}
        """
        
        resultado = self._consultar_ia_estruturada(prompt)
        
        # Processar resultado usando o gerenciador de tarefas
        try:
            info = json.loads(resultado)
            return self.task_manager.processar_comando_agenda(info)
        except Exception as e:
            # Fallback para quando a extração não funcionar bem
            return self._consultar_ia(f"Como gerenciador de agenda do PomodoroTasks, responda ao seguinte: {texto}")
    
    def _processar_relatório(self, texto):
        """
        Processa comandos relacionados a relatórios
        
        Args:
            texto: O texto do comando do usuário
            
        Returns:
            string: Relatório gerado ou resposta processada
        """
        # Extrair informações do texto usando IA para entender a solicitação de relatório
        prompt = f"""
        Analise o seguinte comando relacionado a relatórios de produtividade:
        
        "{texto}"
        
        Extraia apenas as seguintes informações em formato JSON:
        {{
          "tipo_relatório": "produtividade/tarefas/pomodoros",
          "período_início": "data de início mencionada ou null",
          "período_fim": "data de fim mencionada ou null",
          "formato": "detalhado/resumido",
          "filtros": "quaisquer filtros mencionados ou null"
        }}
        """
        
        resultado = self._consultar_ia_estruturada(prompt)
        
        # Processar resultado usando o gerador de relatórios
        try:
            info = json.loads(resultado)
            return self.reports_generator.gerar_relatório(info)
        except Exception as e:
            # Fallback para quando a extração não funcionar bem
            return self._consultar_ia(f"Como gerenciador de relatórios do PomodoroTasks, responda ao seguinte: {texto}")
    
    def _consultar_ia(self, pergunta):
        """
        Consulta o modelo de IA com uma pergunta geral
        Implementa cache e otimização de prompts
        
        Args:
            pergunta: A pergunta do usuário
            
        Returns:
            string: Resposta da IA
        """
        # Verifica cache para perguntas semelhantes
        cache_key = self._gerar_cache_key(pergunta)
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
            
        # Otimização de prompt com base no tipo de pergunta
        prompt_otimizado = self._otimizar_prompt(pergunta)
        
        # Controle de contexto para modelos de janela pequena
        contexto_relevante = self._extrair_contexto_relevante(pergunta)
        
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pomodorotasks.app",
            "X-Title": "PomodoroTasks Assistant"
        }
        
        # Adiciona controle de temperatura baseado no tipo de pergunta
        temperatura = 0.1 if "extrair" in prompt_otimizado.lower() or "analisar" in prompt_otimizado.lower() else 0.7
        
        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                # Inclui contexto se disponível
                *([ {"role": "system", "content": f"Contexto relevante: {contexto_relevante}"} ] if contexto_relevante else []),
                {
                    "role": "user",
                    "content": prompt_otimizado
                }
            ],
            "temperature": temperatura,
            "max_tokens": self._estimar_tokens_necessarios(pergunta)
        }
        
        try:
            response = requests.post(
                url=self.BASE_URL,
                headers=headers,
                data=json.dumps(payload)
            )
            
            if response.status_code == 200:
                result = response.json()
                resposta = result["choices"][0]["message"]["content"]
                
                # Armazena no cache se for apropriado
                if len(pergunta) < 200 and len(self.response_cache) < 100:  # Limita tamanho do cache
                    self.response_cache[cache_key] = resposta
                    
                return resposta
            else:
                return f"Desculpe, estou com dificuldade para processar sua solicitação no momento. Pode tentar novamente?"
        except Exception as e:
            return "Desculpe, ocorreu um problema na comunicação. Vamos tentar de outra forma?"
            
    def _gerar_cache_key(self, pergunta):
        """Gera uma chave de cache simplificada para a pergunta"""
        # Normalização básica: lowercase, sem pontuação, palavras ordenadas para perguntas semelhantes
        palavras = re.sub(r'[^\w\s]', '', pergunta.lower()).split()
        return ' '.join(sorted(set(palavras)))
        
    def _otimizar_prompt(self, pergunta):
        """Otimiza o prompt para melhor desempenho"""
        # Identifica o tipo de pergunta para adicionar estrutura
        if "como" in pergunta.lower():
            return f"Responda de forma concisa e prática: {pergunta}"
        elif any(p in pergunta.lower() for p in ["defina", "o que é", "significado"]):
            return f"Defina brevemente em 1-2 frases: {pergunta}"
        elif "lista" in pergunta.lower() or "quais" in pergunta.lower():
            return f"Liste apenas 3-5 itens mais relevantes: {pergunta}"
        else:
            return pergunta
            
    def _extrair_contexto_relevante(self, pergunta):
        """Extrai contexto relevante se disponível"""
        # Esta função poderia ser expandida para buscar contexto do histórico de tarefas
        return None
        
    def _estimar_tokens_necessarios(self, pergunta):
        """Estima os tokens necessários para a resposta com base no tipo de pergunta"""
        # Estimativa simples baseada no tamanho e complexidade da pergunta
        pergunta_lower = pergunta.lower()
        if "relatório" in pergunta_lower or "análise" in pergunta_lower:
            return 500  # Relatórios precisam de mais tokens
        elif "lista" in pergunta_lower or "passos" in pergunta_lower:
            return 350  # Listas e instruções
        else:
            return 250  # Respostas padrão
    
    def _consultar_ia_estruturada(self, pergunta):
        """
        Consulta o modelo de IA para extrair informações estruturadas
        Otimizada para retornar respostas concisas e estruturadas em formato JSON
        
        Args:
            pergunta: A pergunta estruturada para extração de informações
            
        Returns:
            string: Resposta estruturada da IA em formato JSON
        """
        headers = {
            "Authorization": f"Bearer {self.API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pomodorotasks.app",
            "X-Title": "PomodoroTasks Assistant"
        }
        
        extrator_prompt = """
Você é Lumi, uma IA especializada em extrair informações estruturadas com precisão.

INSTRUÇÕES CRÍTICAS:
1. Responda APENAS com JSON válido sem formatação adicional
2. Não inclua explicações, notas ou texto antes ou depois do JSON
3. Se um campo não puder ser determinado, use null como valor
4. Garanta que todos os valores de texto incluam aspas duplas
5. Siga EXATAMENTE o formato solicitado, sem campos adicionais

Seu único objetivo é extrair informações estruturadas do texto fornecido.
"""
        
        # Adiciona exemplos de extração bem-sucedida para melhorar a precisão
        exemplos_formatacao = self._obter_exemplos_extração(pergunta)
        if exemplos_formatacao:
            extrator_prompt += f"\n\nExemplos de formatação esperada:\n{exemplos_formatacao}"
        
        payload = {
            "model": self.MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": extrator_prompt
                },
                {
                    "role": "user",
                    "content": pergunta
                }
            ],
            "temperature": 0.1,  # Temperatura baixa para respostas mais determinísticas
            "max_tokens": 500,   # Limite ajustado para estruturas JSON complexas
            "response_format": {"type": "json_object"}  # Força resposta em JSON quando o modelo suportar
        }
        
        # Tenta até 2 vezes em caso de falha na extração
        tentativas = 0
        max_tentativas = 2
        
        while tentativas < max_tentativas:
            try:
                response = requests.post(
                    url=self.BASE_URL,
                    headers=headers,
                    data=json.dumps(payload)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    resposta = result["choices"][0]["message"]["content"]
                    
                    # Verifica se a resposta é um JSON válido
                    try:
                        json.loads(resposta)
                        return resposta
                    except json.JSONDecodeError:
                        # Se não for JSON válido, tenta extrair o JSON da resposta
                        json_match = re.search(r'({.*})', resposta, re.DOTALL)
                        if json_match:
                            potential_json = json_match.group(1)
                            try:
                                json.loads(potential_json)
                                return potential_json
                            except json.JSONDecodeError:
                                pass
                                
                        # Se ainda não tiver JSON válido, incrementa tentativas
                        tentativas += 1
                        
                        # Modifica o prompt para próxima tentativa
                        payload["messages"][0]["content"] += "\n\nATENÇÃO: Sua resposta anterior não estava em formato JSON válido. Responda APENAS com JSON."
                else:
                    tentativas += 1
            except Exception:
                tentativas += 1
        
        # Se todas as tentativas falharem, retorna JSON vazio
        return '{}'
        
    def _obter_exemplos_extração(self, pergunta):
        """Retorna exemplos formatados para ajudar na extração de informações"""
        if "agenda" in pergunta.lower() or "tarefa" in pergunta.lower():
            return '{"ação": "adicionar", "tipo": "tarefa", "título": "Relatório final", "data": "2023-05-20", "hora": "14:30", "duração": "60 min", "descrição": "Completar relatório trimestral"}'
        elif "relatório" in pergunta.lower():
            return '{"tipo_relatório": "produtividade", "período_início": "2023-05-01", "período_fim": "2023-05-15", "formato": "detalhado", "filtros": null}'
        else:
            return None

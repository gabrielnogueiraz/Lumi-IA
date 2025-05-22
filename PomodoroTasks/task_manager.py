#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime, timedelta
import uuid

class TaskManager:
    """
    Gerenciador de tarefas e eventos do PomodoroTasks
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de tarefas
        """
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tasks.json")
        self._verificar_arquivos()
        self.tasks = self._carregar_tarefas()
    
    def _verificar_arquivos(self):
        """Garante que os arquivos e diretórios necessários existam"""
        data_dir = os.path.dirname(self.data_file)
        
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({"tarefas": [], "eventos": [], "pomodoros": []}, f, ensure_ascii=False, indent=2)
    
    def _carregar_tarefas(self):
        """Carrega as tarefas do arquivo"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar tarefas: {e}")
            return {"tarefas": [], "eventos": [], "pomodoros": []}
    
    def _salvar_tarefas(self):
        """Salva as tarefas no arquivo"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Erro ao salvar tarefas: {e}")
            return False
    
    def processar_comando_agenda(self, info):
        """
        Processa um comando relacionado à agenda
        
        Args:
            info: Dicionário com informações do comando
            
        Returns:
            string: Resposta do processamento
        """
        acao = info.get("ação", "").lower()
        tipo = info.get("tipo", "tarefa").lower()
        
        if acao == "adicionar":
            return self.adicionar_item(tipo, info)
        elif acao == "remover":
            return self.remover_item(tipo, info)
        elif acao == "consultar":
            return self.consultar_itens(tipo, info)
        elif acao == "modificar":
            return self.modificar_item(tipo, info)
        else:
            return f"Não compreendi a ação '{acao}'. Por favor, especifique se deseja adicionar, remover, consultar ou modificar."
    
    def adicionar_item(self, tipo, info):
        """
        Adiciona um novo item (tarefa ou evento)
        
        Args:
            tipo: O tipo do item ("tarefa" ou "evento")
            info: Dicionário com as informações do item
            
        Returns:
            string: Confirmação da adição
        """
        titulo = info.get("título")
        if not titulo:
            return "É necessário fornecer um título para adicionar um item."
        
        # Prepara o novo item
        novo_item = {
            "id": str(uuid.uuid4()),
            "título": titulo,
            "descrição": info.get("descrição") or "",
            "data_criação": datetime.now().isoformat(),
            "concluído": False
        }
        
        # Adiciona campos específicos conforme o tipo
        if info.get("data"):
            novo_item["data"] = info.get("data")
        
        if info.get("hora"):
            novo_item["hora"] = info.get("hora")
        
        if info.get("duração"):
            novo_item["duração"] = info.get("duração")
        
        # Adiciona à lista correspondente
        if tipo == "tarefa":
            self.tasks["tarefas"].append(novo_item)
        elif tipo == "evento":
            self.tasks["eventos"].append(novo_item)
        elif tipo == "pomodoro":
            # Pomodoros são gerenciados de forma diferente
            novo_item["tempo_foco"] = info.get("tempo_foco") or 25
            novo_item["tempo_pausa"] = info.get("tempo_pausa") or 5
            self.tasks["pomodoros"].append(novo_item)
        
        # Salva as alterações
        if self._salvar_tarefas():
            return f"{tipo.capitalize()} '{titulo}' adicionado(a) com sucesso!"
        else:
            return f"Houve um erro ao salvar o(a) {tipo}. Por favor, tente novamente."
    
    def remover_item(self, tipo, info):
        """
        Remove um item existente
        
        Args:
            tipo: O tipo do item ("tarefa" ou "evento")
            info: Dicionário com as informações para identificação
            
        Returns:
            string: Confirmação da remoção
        """
        titulo = info.get("título")
        
        if not titulo:
            return f"É necessário fornecer o título do(a) {tipo} para remover."
        
        # Determina a lista correta com base no tipo
        lista_items = self.tasks.get("tarefas" if tipo == "tarefa" else "eventos" if tipo == "evento" else "pomodoros")
        
        # Procura o item pelo título
        for i, item in enumerate(lista_items):
            if item["título"].lower() == titulo.lower():
                removido = lista_items.pop(i)
                
                if self._salvar_tarefas():
                    return f"{tipo.capitalize()} '{removido['título']}' removido(a) com sucesso!"
                else:
                    lista_items.insert(i, removido)  # restaura o item se não conseguiu salvar
                    return f"Houve um erro ao remover o(a) {tipo}. Por favor, tente novamente."
                
        return f"Não foi encontrado(a) nenhum(a) {tipo} com o título '{titulo}'."
    
    def consultar_itens(self, tipo, info):
        """
        Consulta os itens existentes, possivelmente com filtros
        
        Args:
            tipo: O tipo dos itens ("tarefa", "evento", "todos")
            info: Dicionário com os filtros da consulta
            
        Returns:
            string: Lista formatada dos itens
        """
        # Determina quais listas consultar
        listas = []
        if tipo == "todos" or not tipo:
            listas = [("Tarefas", self.tasks["tarefas"]), ("Eventos", self.tasks["eventos"])]
        elif tipo == "tarefa":
            listas = [("Tarefas", self.tasks["tarefas"])]
        elif tipo == "evento":
            listas = [("Eventos", self.tasks["eventos"])]
        elif tipo == "pomodoro":
            listas = [("Pomodoros", self.tasks["pomodoros"])]
        
        resultado = []
        data_filtro = info.get("data")
        
        # Cria o resultado formatado
        for nome_lista, lista in listas:
            items_filtrados = []
            
            # Aplica filtros se houver
            for item in lista:
                # Filtra por data
                if data_filtro and item.get("data") != data_filtro:
                    continue
                    
                # Adiciona o item se passou pelos filtros
                items_filtrados.append(item)
            
            if items_filtrados:
                resultado.append(f"\n{nome_lista}:")
                for item in items_filtrados:
                    status = "✓" if item.get("concluído") else "□"
                    data_hora = ""
                    if item.get("data"):
                        data_hora += f" - Data: {item['data']}"
                    if item.get("hora"):
                        data_hora += f" - Hora: {item['hora']}"
                        
                    resultado.append(f"  [{status}] {item['título']}{data_hora}")
                
        if not resultado:
            return f"Não há {tipo}s cadastrados" + (f" para a data {data_filtro}" if data_filtro else ".")
        
        return "\n".join(resultado)
    
    def modificar_item(self, tipo, info):
        """
        Modifica um item existente
        
        Args:
            tipo: O tipo do item ("tarefa", "evento", "pomodoro")
            info: Dicionário com as informações da modificação
            
        Returns:
            string: Confirmação da modificação
        """
        titulo = info.get("título")
        
        if not titulo:
            return f"É necessário fornecer o título do(a) {tipo} para modificar."
        
        # Determina a lista correta com base no tipo
        lista_items = self.tasks.get("tarefas" if tipo == "tarefa" else "eventos" if tipo == "evento" else "pomodoros")
        
        # Procura o item pelo título
        for item in lista_items:
            if item["título"].lower() == titulo.lower():
                # Atualiza os campos que foram fornecidos
                for campo in ["descrição", "data", "hora", "duração"]:
                    if info.get(campo):
                        item[campo] = info[campo]
                
                # Campo especial para conclusão
                if "concluído" in info:
                    item["concluído"] = info["concluído"]
                    
                if tipo == "pomodoro" and info.get("tempo_foco"):
                    item["tempo_foco"] = info["tempo_foco"]
                    
                if tipo == "pomodoro" and info.get("tempo_pausa"):
                    item["tempo_pausa"] = info["tempo_pausa"]
                
                if self._salvar_tarefas():
                    return f"{tipo.capitalize()} '{titulo}' atualizado(a) com sucesso!"
                else:
                    return f"Houve um erro ao atualizar o(a) {tipo}. Por favor, tente novamente."
                
        return f"Não foi encontrado(a) nenhum(a) {tipo} com o título '{titulo}'."
    
    def registrar_pomodoro_concluido(self, tarefa_id=None, duracao=25):
        """
        Registra um pomodoro concluído
        
        Args:
            tarefa_id: ID opcional da tarefa associada
            duracao: Duração do pomodoro em minutos
            
        Returns:
            boolean: Sucesso da operação
        """
        pomodoro = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "duracao": duracao,
            "tarefa_id": tarefa_id
        }
        
        self.tasks["pomodoros"].append(pomodoro)
        return self._salvar_tarefas()
        
    def obter_tarefas_periodo(self, data_inicio, data_fim):
        """
        Retorna as tarefas em um determinado período
        
        Args:
            data_inicio: Data de início do período (string ISO)
            data_fim: Data de fim do período (string ISO)
            
        Returns:
            dict: Dicionário com tarefas, eventos e pomodoros do período
        """
        resultado = {
            "tarefas": [],
            "eventos": [],
            "pomodoros": []
        }
        
        # Converte datas para comparação
        try:
            inicio = datetime.fromisoformat(data_inicio) if isinstance(data_inicio, str) else data_inicio
            fim = datetime.fromisoformat(data_fim) if isinstance(data_fim, str) else data_fim
        except ValueError:
            return resultado
            
        # Filtra tarefas e eventos
        for tipo in ["tarefas", "eventos"]:
            for item in self.tasks[tipo]:
                if "data" in item:
                    try:
                        item_data = datetime.fromisoformat(item["data"])
                        if inicio <= item_data <= fim:
                            resultado[tipo].append(item)
                    except ValueError:
                        pass
        
        # Filtra pomodoros
        for pomodoro in self.tasks["pomodoros"]:
            try:
                timestamp = datetime.fromisoformat(pomodoro["timestamp"])
                if inicio <= timestamp <= fim:
                    resultado["pomodoros"].append(pomodoro)
            except ValueError:
                pass
                
        return resultado

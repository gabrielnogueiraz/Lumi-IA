#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import calendar
import json

class ReportsGenerator:
    """
    Gerador de relatórios para o PomodoroTasks
    """
    
    def __init__(self, task_manager):
        """
        Inicializa o gerador de relatórios
        
        Args:
            task_manager: O gerenciador de tarefas para consulta de dados
        """
        self.task_manager = task_manager
    
    def gerar_relatório(self, info):
        """
        Gera um relatório com base nas informações fornecidas
        
        Args:
            info: Dicionário com informações sobre o relatório desejado
            
        Returns:
            string: O relatório gerado
        """
        tipo_relatorio = info.get("tipo_relatório", "").lower()
        
        # Determina o período do relatório
        periodo_inicio, periodo_fim = self._determinar_periodo(info)
        
        if tipo_relatorio == "produtividade":
            return self._relatorio_produtividade(periodo_inicio, periodo_fim, info)
        elif tipo_relatorio == "tarefas":
            return self._relatorio_tarefas(periodo_inicio, periodo_fim, info)
        elif tipo_relatorio == "pomodoros":
            return self._relatorio_pomodoros(periodo_inicio, periodo_fim, info)
        else:
            # Relatório geral por padrão
            return self._relatorio_geral(periodo_inicio, periodo_fim, info)
    
    def _determinar_periodo(self, info):
        """
        Determina o período de início e fim para o relatório
        
        Args:
            info: Dicionário com informações de período
            
        Returns:
            tuple: (data_inicio, data_fim) como objetos datetime
        """
        hoje = datetime.now()
        inicio = None
        fim = None
        
        # Extrai datas específicas se fornecidas
        if info.get("período_início"):
            try:
                inicio = datetime.fromisoformat(info["período_início"].split("T")[0])
            except (ValueError, AttributeError):
                pass
                
        if info.get("período_fim"):
            try:
                fim = datetime.fromisoformat(info["período_fim"].split("T")[0])
            except (ValueError, AttributeError):
                pass
        
        # Se não foram fornecidas datas específicas, usa um período padrão
        if not inicio and not fim:
            # Por padrão, usa a última semana
            inicio = hoje - timedelta(days=7)
            fim = hoje
        elif not inicio:
            # Se só tem fim, assume 7 dias antes
            inicio = fim - timedelta(days=7)
        elif not fim:
            # Se só tem início, assume até hoje
            fim = hoje
        
        # Normaliza para início e fim do dia
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fim = fim.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        return inicio, fim
    
    def _relatorio_produtividade(self, periodo_inicio, periodo_fim, info):
        """
        Gera um relatório de produtividade para o período especificado
        
        Args:
            periodo_inicio: Data de início do período
            periodo_fim: Data de fim do período
            info: Informações adicionais sobre o relatório
            
        Returns:
            string: Relatório formatado de produtividade
        """
        dados = self.task_manager.obter_tarefas_periodo(periodo_inicio, periodo_fim)
        
        total_tarefas = len(dados["tarefas"])
        tarefas_concluidas = sum(1 for t in dados["tarefas"] if t.get("concluído"))
        
        total_pomodoros = len(dados["pomodoros"])
        tempo_pomodoros = sum(p.get("duracao", 25) for p in dados["pomodoros"])
        
        # Calcula a taxa de conclusão
        taxa_conclusao = 0
        if total_tarefas > 0:
            taxa_conclusao = (tarefas_concluidas / total_tarefas) * 100
            
        # Formata o período para exibição
        formato_data = "%d/%m/%Y"
        periodo_str = f"{periodo_inicio.strftime(formato_data)} a {periodo_fim.strftime(formato_data)}"
        
        # Constrói o relatório
        linhas = [
            f"\n=== RELATÓRIO DE PRODUTIVIDADE: {periodo_str} ===\n",
            f"Tarefas no período: {total_tarefas}",
            f"Tarefas concluídas: {tarefas_concluidas} ({taxa_conclusao:.1f}%)",
            f"Pomodoros realizados: {total_pomodoros}",
            f"Tempo total em pomodoros: {tempo_pomodoros} minutos ({tempo_pomodoros/60:.1f} horas)"
        ]
        
        if info.get("formato", "").lower() == "detalhado" and tarefas_concluidas > 0:
            linhas.append("\n--- TAREFAS CONCLUÍDAS ---")
            for tarefa in dados["tarefas"]:
                if tarefa.get("concluído"):
                    data_str = tarefa.get("data", "Sem data")
                    linhas.append(f"✓ {tarefa['título']} - {data_str}")
        
        if info.get("formato", "").lower() == "detalhado" and (total_tarefas - tarefas_concluidas) > 0:
            linhas.append("\n--- TAREFAS PENDENTES ---")
            for tarefa in dados["tarefas"]:
                if not tarefa.get("concluído"):
                    data_str = tarefa.get("data", "Sem data")
                    linhas.append(f"□ {tarefa['título']} - {data_str}")
                    
        return "\n".join(linhas)
    
    def _relatorio_tarefas(self, periodo_inicio, periodo_fim, info):
        """
        Gera um relatório de tarefas para o período especificado
        
        Args:
            periodo_inicio: Data de início do período
            periodo_fim: Data de fim do período
            info: Informações adicionais sobre o relatório
            
        Returns:
            string: Relatório formatado de tarefas
        """
        dados = self.task_manager.obter_tarefas_periodo(periodo_inicio, periodo_fim)
        
        # Formata o período para exibição
        formato_data = "%d/%m/%Y"
        periodo_str = f"{periodo_inicio.strftime(formato_data)} a {periodo_fim.strftime(formato_data)}"
        
        # Constrói o relatório
        linhas = [
            f"\n=== RELATÓRIO DE TAREFAS: {periodo_str} ===\n",
            f"Total de tarefas: {len(dados['tarefas'])}"
        ]
        
        # Adiciona informações detalhadas das tarefas
        if dados["tarefas"]:
            linhas.append("\n--- TAREFAS NO PERÍODO ---")
            
            # Organiza por status
            concluidas = [t for t in dados["tarefas"] if t.get("concluído")]
            pendentes = [t for t in dados["tarefas"] if not t.get("concluído")]
            
            if concluidas:
                linhas.append("\nConcluídas:")
                for tarefa in concluidas:
                    data_str = tarefa.get("data", "Sem data")
                    linhas.append(f"✓ {tarefa['título']} - {data_str}")
            
            if pendentes:
                linhas.append("\nPendentes:")
                for tarefa in pendentes:
                    data_str = tarefa.get("data", "Sem data")
                    linhas.append(f"□ {tarefa['título']} - {data_str}")
        else:
            linhas.append("\nNenhuma tarefa encontrada no período especificado.")
            
        # Adiciona eventos se a formatação for detalhada
        if info.get("formato", "").lower() == "detalhado" and dados["eventos"]:
            linhas.append("\n--- EVENTOS NO PERÍODO ---")
            for evento in dados["eventos"]:
                data_hora = evento.get("data", "Sem data")
                if evento.get("hora"):
                    data_hora += f" às {evento['hora']}"
                linhas.append(f"• {evento['título']} - {data_hora}")
                
        return "\n".join(linhas)
    
    def _relatorio_pomodoros(self, periodo_inicio, periodo_fim, info):
        """
        Gera um relatório de pomodoros para o período especificado
        
        Args:
            periodo_inicio: Data de início do período
            periodo_fim: Data de fim do período
            info: Informações adicionais sobre o relatório
            
        Returns:
            string: Relatório formatado de pomodoros
        """
        dados = self.task_manager.obter_tarefas_periodo(periodo_inicio, periodo_fim)
        
        # Formata o período para exibição
        formato_data = "%d/%m/%Y"
        periodo_str = f"{periodo_inicio.strftime(formato_data)} a {periodo_fim.strftime(formato_data)}"
        
        # Processa os dados dos pomodoros
        total_pomodoros = len(dados["pomodoros"])
        tempo_total = sum(p.get("duracao", 25) for p in dados["pomodoros"])
        media_diaria = 0
        
        # Calcula a média diária
        dias_periodo = (periodo_fim - periodo_inicio).days + 1
        if dias_periodo > 0:
            media_diaria = total_pomodoros / dias_periodo
            
        # Agrupa por dia para análise
        pomodoros_por_dia = {}
        for pomodoro in dados["pomodoros"]:
            try:
                data = datetime.fromisoformat(pomodoro["timestamp"]).date()
                if data not in pomodoros_por_dia:
                    pomodoros_por_dia[data] = []
                pomodoros_por_dia[data].append(pomodoro)
            except (ValueError, KeyError):
                pass
        
        # Constrói o relatório
        linhas = [
            f"\n=== RELATÓRIO DE POMODOROS: {periodo_str} ===\n",
            f"Total de pomodoros: {total_pomodoros}",
            f"Tempo total focado: {tempo_total} minutos ({tempo_total/60:.1f} horas)",
            f"Média diária: {media_diaria:.1f} pomodoros por dia"
        ]
        
        # Adiciona detalhes por dia se solicitado
        if info.get("formato", "").lower() == "detalhado" and pomodoros_por_dia:
            linhas.append("\n--- DETALHAMENTO POR DIA ---")
            
            # Ordena os dias
            dias_ordenados = sorted(pomodoros_por_dia.keys())
            
            for dia in dias_ordenados:
                pomodoros_dia = pomodoros_por_dia[dia]
                tempo_dia = sum(p.get("duracao", 25) for p in pomodoros_dia)
                linhas.append(f"\n{dia.strftime('%d/%m/%Y')}: {len(pomodoros_dia)} pomodoros - {tempo_dia} minutos")
                
                # Mapeia para tarefas se possível
                tarefas_associadas = {}
                for pomodoro in pomodoros_dia:
                    if pomodoro.get("tarefa_id"):
                        tarefa_id = pomodoro["tarefa_id"]
                        if tarefa_id not in tarefas_associadas:
                            tarefas_associadas[tarefa_id] = 0
                        tarefas_associadas[tarefa_id] += 1
                
                # Adiciona informações de tarefas se houver
                if tarefas_associadas:
                    for tarefa_id, contagem in tarefas_associadas.items():
                        # Busca o título da tarefa
                        titulo = "Tarefa não encontrada"
                        for tarefa in dados["tarefas"]:
                            if tarefa.get("id") == tarefa_id:
                                titulo = tarefa["título"]
                                break
                                
                        linhas.append(f"  - {titulo}: {contagem} pomodoros")
        
        return "\n".join(linhas)
    
    def _relatorio_geral(self, periodo_inicio, periodo_fim, info):
        """
        Gera um relatório geral combinando informações de tarefas e pomodoros
        
        Args:
            periodo_inicio: Data de início do período
            periodo_fim: Data de fim do período
            info: Informações adicionais sobre o relatório
            
        Returns:
            string: Relatório geral formatado
        """
        dados = self.task_manager.obter_tarefas_periodo(periodo_inicio, periodo_fim)
        
        # Formata o período para exibição
        formato_data = "%d/%m/%Y"
        periodo_str = f"{periodo_inicio.strftime(formato_data)} a {periodo_fim.strftime(formato_data)}"
        
        # Estatísticas gerais
        total_tarefas = len(dados["tarefas"])
        tarefas_concluidas = sum(1 for t in dados["tarefas"] if t.get("concluído"))
        
        total_pomodoros = len(dados["pomodoros"])
        tempo_pomodoros = sum(p.get("duracao", 25) for p in dados["pomodoros"])
        
        total_eventos = len(dados["eventos"])
        
        # Constrói o relatório
        linhas = [
            f"\n=== RELATÓRIO GERAL: {periodo_str} ===\n",
            "--- RESUMO ---",
            f"Tarefas no período: {total_tarefas} (Concluídas: {tarefas_concluidas})",
            f"Eventos agendados: {total_eventos}",
            f"Pomodoros realizados: {total_pomodoros} ({tempo_pomodoros/60:.1f} horas)",
            "\n--- DETALHES ---"
        ]
        
        # Adiciona percentual de conclusão se houver tarefas
        if total_tarefas > 0:
            taxa_conclusao = (tarefas_concluidas / total_tarefas) * 100
            linhas.append(f"Taxa de conclusão de tarefas: {taxa_conclusao:.1f}%")
            
        # Média diária de pomodoros
        dias_periodo = (periodo_fim - periodo_inicio).days + 1
        if dias_periodo > 0 and total_pomodoros > 0:
            media_pomodoros = total_pomodoros / dias_periodo
            linhas.append(f"Média diária de pomodoros: {media_pomodoros:.1f}")
        
        # Adiciona tarefas pendentes mais próximas
        if dados["tarefas"]:
            pendentes = [t for t in dados["tarefas"] if not t.get("concluído")]
            if pendentes:
                # Ordena por data se disponível
                try:
                    pendentes.sort(key=lambda x: x.get("data", "9999-12-31"))
                except:
                    pass
                    
                linhas.append("\n--- PRÓXIMAS TAREFAS PENDENTES ---")
                for i, tarefa in enumerate(pendentes[:5]):  # Mostra até 5 tarefas
                    data_str = tarefa.get("data", "Sem prazo")
                    linhas.append(f"{i+1}. {tarefa['título']} - {data_str}")
                    
                if len(pendentes) > 5:
                    linhas.append(f"... e mais {len(pendentes) - 5} tarefas pendentes.")
        
        # Adiciona próximos eventos
        if dados["eventos"]:
            try:
                eventos = sorted(dados["eventos"], key=lambda x: (x.get("data", "9999-12-31"), x.get("hora", "23:59")))
            except:
                eventos = dados["eventos"]
                
            if eventos:
                linhas.append("\n--- PRÓXIMOS EVENTOS ---")
                for i, evento in enumerate(eventos[:3]):  # Mostra até 3 eventos
                    data_hora = evento.get("data", "Sem data")
                    if evento.get("hora"):
                        data_hora += f" às {evento['hora']}"
                    linhas.append(f"{i+1}. {evento['título']} - {data_hora}")
                    
                if len(eventos) > 3:
                    linhas.append(f"... e mais {len(eventos) - 3} eventos agendados.")
        
        return "\n".join(linhas)

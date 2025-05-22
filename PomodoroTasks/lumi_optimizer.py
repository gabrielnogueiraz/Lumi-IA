#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Otimizador de Memória para Lumi

Este script monitora e gerencia o uso de memória e desempenho da assistente Lumi.
Ele é executado em paralelo ao processo principal e ajuda a manter o desempenho 
otimizado em sistemas com recursos limitados.
"""

import os
import sys
import time
import psutil
import json
import argparse
from datetime import datetime

class LumiOptimizer:
    """Gerenciador de otimização para Lumi"""
    
    def __init__(self, config_file="lumi_config.json", log_file="lumi_performance.log"):
        """Inicializa o otimizador de memória"""
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file)
        self.log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", log_file)
        self.config = self._load_config()
        self.ensure_log_directory()
        
    def _load_config(self):
        """Carrega ou cria o arquivo de configuração"""
        default_config = {
            "memory_threshold": 75,  # percentual de memória que aciona otimização
            "cache_size_max": 100,   # número máximo de entradas em cache
            "response_cache_ttl": 3600,  # tempo de vida do cache em segundos
            "optimization_level": "auto",  # auto, performance, memory_saving
            "enable_advanced_reasoning": True,  # habilita recursos avançados de raciocínio
            "log_performance": True,  # registra métricas de desempenho
            "last_optimization": None,
            "version": "1.0.0"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            else:
                with open(self.config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
            return default_config
    
    def ensure_log_directory(self):
        """Garante que o diretório de logs existe"""
        log_dir = os.path.dirname(self.log_file)
        if not os.path.exists(log_dir):
            try:
                os.makedirs(log_dir)
            except Exception as e:
                print(f"Erro ao criar diretório de logs: {e}")
    
    def _save_config(self):
        """Salva as configurações atualizadas"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def check_system_resources(self):
        """Verifica os recursos disponíveis do sistema"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.5)
            
            return {
                "memory_percent": memory.percent,
                "memory_available": memory.available / (1024 * 1024),  # MB
                "cpu_percent": cpu_percent,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Erro ao verificar recursos: {e}")
            return None
    
    def log_performance(self, metrics):
        """Registra métricas de desempenho"""
        if not self.config.get("log_performance", True):
            return
        
        try:
            log_entry = f"{metrics['timestamp']} - CPU: {metrics['cpu_percent']}% - RAM: {metrics['memory_percent']}% ({metrics['memory_available']:.2f} MB disponível)\n"
            
            with open(self.log_file, 'a') as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Erro ao registrar desempenho: {e}")
    
    def optimize_if_needed(self):
        """Verifica e aplica otimizações se necessário"""
        metrics = self.check_system_resources()
        if not metrics:
            return False
        
        # Registra métricas
        self.log_performance(metrics)
        
        # Verifica se precisa otimizar
        if metrics["memory_percent"] > self.config["memory_threshold"]:
            print(f"\n[Lumi Optimizer] Aplicando otimizações de memória (uso atual: {metrics['memory_percent']}%)")
            
            # Atualiza configurações para modo econômico
            self.config["cache_size_max"] = max(10, self.config["cache_size_max"] // 2)
            self.config["enable_advanced_reasoning"] = False
            self.config["last_optimization"] = datetime.now().isoformat()
            self._save_config()
            
            return True
        
        # Se a memória estiver OK mas já teve otimização, restaura configurações
        elif metrics["memory_percent"] < (self.config["memory_threshold"] - 20) and self.config["last_optimization"]:
            print(f"\n[Lumi Optimizer] Restaurando configurações (uso atual: {metrics['memory_percent']}%)")
            
            # Restaura configurações padrão
            self.config["cache_size_max"] = 100
            self.config["enable_advanced_reasoning"] = True
            self.config["last_optimization"] = None
            self._save_config()
            
        return False
    
    def run(self, interval=300):
        """Executa o otimizador de forma contínua"""
        print(f"[Lumi Optimizer] Iniciando monitoramento de recursos...")
        
        try:
            while True:
                self.optimize_if_needed()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[Lumi Optimizer] Monitoramento finalizado pelo usuário.")
        except Exception as e:
            print(f"[Lumi Optimizer] Erro: {e}")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Otimizador de Recursos para Lumi")
    parser.add_argument("--diagnose", action="store_true", help="Executa apenas diagnóstico e exibe sugestões")
    parser.add_argument("--interval", type=int, default=300, help="Intervalo entre verificações (segundos)")
    args = parser.parse_args()
    
    optimizer = LumiOptimizer()
    
    if args.diagnose:
        metrics = optimizer.check_system_resources()
        if metrics:
            print("\n" + "="*60)
            print(f"{'DIAGNÓSTICO DE RECURSOS - LUMI':^60}")
            print("="*60)
            print(f"\nUso de CPU: {metrics['cpu_percent']}%")
            print(f"Uso de Memória: {metrics['memory_percent']}% ({metrics['memory_available']:.2f} MB disponível)")
            
            # Recomendações
            if metrics['memory_percent'] > 85:
                print("\nALERTA: Memória muito alta. Recomendações:")
                print("- Feche aplicações não utilizadas")
                print("- Reinicie o computador antes de usar Lumi")
                print("- Use o modo econômico: --optimize memory")
            elif metrics['memory_percent'] > 70:
                print("\nAVISO: Memória moderadamente alta. Recomendações:")
                print("- Considere fechar aplicações pesadas")
                print("- Lumi pode ter desempenho reduzido nessas condições")
            else:
                print("\nBOM: Recursos de sistema adequados para o funcionamento ideal da Lumi.")
                
            print("\nPara monitoramento contínuo, execute sem a flag --diagnose")
    else:
        optimizer.run(args.interval)

if __name__ == "__main__":
    main()

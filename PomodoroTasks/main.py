#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from datetime import datetime
import argparse
import calendar
import sys

def check_dependencies():
    """
    Verifica se todas as dependências necessárias estão instaladas
    """
    missing_modules = []
    
    # Lista de módulos necessários
    required_modules = ["requests"]
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("\n" + "="*60)
        print("ERRO: Dependências ausentes")
        print("="*60)
        print("\nOs seguintes módulos são necessários mas não estão instalados:")
        for module in missing_modules:
            print(f"  - {module}")
        
        print("\nPara instalar todas as dependências, execute um dos comandos:")
        print("  pip install -r requirements.txt")
        print("  pip install " + " ".join(missing_modules))
        print("\nSe o pip não estiver disponível, instale o Python corretamente.")
        return False
    
    return True

# Verificar dependências antes de continuar
if not check_dependencies():
    sys.exit(1)

# Agora que sabemos que requests está instalado, podemos importá-lo
import requests

# Importação dos módulos da aplicação
try:
    from ai_assistant import LumiAssistant
    from task_manager import TaskManager
    from reports_generator import ReportsGenerator
except ImportError as e:
    print(f"\nERRO ao importar módulos da aplicação: {e}")
    print("Verifique se todos os arquivos do projeto estão no local correto.")
    sys.exit(1)

def main():
    """
    Ponto de entrada principal do assistente PomodoroTasks
    """
    print("\n" + "="*60)
    print(f"{'LUMI - ASSISTENTE DE PRODUTIVIDADE':^60}")
    print("="*60)
    
    # Inicializando os componentes principais
    task_manager = TaskManager()
    reports_generator = ReportsGenerator(task_manager)
    assistant = LumiAssistant(task_manager, reports_generator)
    
    parser = argparse.ArgumentParser(description='Lumi - Assistente de Produtividade')
    parser.add_argument('--pergunta', '-p', type=str, help='Faça uma pergunta diretamente')
    args = parser.parse_args()
    
    # Se foi fornecida uma pergunta como argumento, processa e encerra
    if args.pergunta:
        resposta = assistant.processar_pergunta(args.pergunta)
        print(resposta)
        return
    
    # Caso contrário, entra no modo interativo
    print("\nOlá! Sou Lumi, sua assistente pessoal para produtividade e gestão de tarefas.")
    print("Como posso ajudar você a ser mais produtivo hoje?\n")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("\nAté logo! Tenha um dia produtivo!")
                break
                
            # Processando a entrada do usuário
            resposta = assistant.processar_pergunta(user_input)
            print(f"\n{resposta}")
            
        except KeyboardInterrupt:
            print("\nPrograma finalizado pelo usuário.")
            break
        except Exception as e:
            print(f"\nOcorreu um erro: {e}")
            
if __name__ == "__main__":
    main()

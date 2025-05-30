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
    missing_modules = []  # Lista de módulos necessários
    required_modules = ["requests", "flask", "flask_cors", "google.generativeai"]

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print("\n" + "=" * 60)
        print("ERRO: Dependências ausentes")
        print("=" * 60)
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


def exibir_boas_vindas():
    """Exibe mensagem de boas-vindas personalizada"""
    print("\n" + "=" * 70)
    print(f"{'🚀 LUMI - SUA ASSISTENTE DE PRODUTIVIDADE PESSOAL 🚀':^70}")
    print("=" * 70)
    print()
    print("💡 Olá! Sou a Lumi, sua coach de produtividade pessoal!")
    print("✨ Estou aqui para ajudar você a ser mais organizado e eficiente.")
    print()
    print("📋 O que posso fazer por você:")
    print("   • Gerenciar suas tarefas e agenda")
    print("   • Explicar conceitos e tirar dúvidas de estudo")
    print("   • Dar dicas de produtividade e organização")
    print("   • Gerar relatórios do seu progresso")
    print("   • Ajudar no planejamento de projetos")
    print()
    print("🎯 Exemplo de comandos:")
    print("   • 'Adicionar reunião às 14:00 hoje'")
    print("   • 'Como funciona o método Pomodoro?'")
    print("   • 'Quais tarefas tenho para hoje?'")
    print("   • 'Me explique algoritmos de ordenação'")
    print()
    print("💪 Vamos juntos turbinar sua produtividade!")
    print("-" * 70)


def main():
    """
    Ponto de entrada principal do assistente PomodoroTasks
    """

    # Inicializando os componentes principais
    try:
        task_manager = TaskManager()
        reports_generator = ReportsGenerator(task_manager)
        assistant = LumiAssistant(task_manager, reports_generator)
    except Exception as e:
        print(f"Erro ao inicializar componentes: {e}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Lumi - Assistente de Produtividade")
    parser.add_argument(
        "--pergunta", "-p", type=str, help="Faça uma pergunta diretamente"
    )
    parser.add_argument(
        "--silencioso",
        "-s",
        action="store_true",
        help="Modo silencioso (sem boas-vindas)",
    )
    args = parser.parse_args()

    # Se foi fornecida uma pergunta como argumento, processa e encerra
    if args.pergunta:
        print("\n🤖 Lumi processando sua solicitação...")
        resposta = assistant.process_message(args.pergunta)
        print(f"\n{resposta}\n")
        return

    # Exibe boas-vindas se não estiver em modo silencioso
    if not args.silencioso:
        exibir_boas_vindas()

    # Contador de interações
    contador_interacoes = 0

    # Loop principal interativo
    while True:
        try:
            # Prompt dinâmico baseado na quantidade de interações
            if contador_interacoes == 0:
                prompt = "\n💬 Como posso te ajudar hoje? "
            elif contador_interacoes % 5 == 0:
                prompt = f"\n💪 Já são {contador_interacoes} interações! Como posso continuar te ajudando? "
            else:
                prompt = "\n💬 "

            user_input = input(prompt).strip()

            # Comandos especiais
            if user_input.lower() in ["sair", "exit", "quit", "tchau", "bye"]:
                print("\n✨ Até logo! Foi ótimo te ajudar hoje!")
                print(
                    "💪 Continue produtivo(a) e lembre-se: pequenos passos levam a grandes conquistas!"
                )
                break
            elif user_input.lower() in ["ajuda", "help", "?"]:
                print("\n📚 COMANDOS DISPONÍVEIS:")
                print(
                    "   • Para TAREFAS: 'Adicionar [tarefa] para [data/hoje/amanhã] às [hora]'"
                )
                print("   • Para CONSULTAS: 'Quais tarefas tenho hoje?'")
                print(
                    "   • Para ESTUDOS: 'Explique [conceito]' ou 'Como funciona [algo]?'"
                )
                print("   • Para PRODUTIVIDADE: 'Dicas para [situação]'")
                print("   • Para RELATÓRIOS: 'Relatório de produtividade'")
                print("   • Para SAIR: 'sair' ou 'quit'")
                continue
            elif user_input.lower() in ["limpar", "clear", "cls"]:
                os.system("cls" if os.name == "nt" else "clear")
                print("🚀 Lumi pronta para continuar!")
                continue
            elif not user_input:
                print(
                    "💭 Está pensando? Estou aqui quando precisar! Digite 'ajuda' se quiser ver os comandos."
                )
                continue

            # Processa a entrada do usuário
            print("🤖 Processando...")
            resposta = assistant.process_message(user_input)
            print(f"\n{resposta}")

            contador_interacoes += 1

            # Dicas periódicas para engajamento
            if contador_interacoes == 3:
                print(
                    "\n💡 Dica: Você pode me perguntar sobre qualquer assunto de estudo ou pedir dicas de produtividade!"
                )
            elif contador_interacoes == 7:
                print(
                    "\n🎯 Lembra: Para adicionar tarefas, use verbos como 'adicionar', 'criar' ou 'agendar'!"
                )
            elif contador_interacoes % 10 == 0:
                print(
                    f"\n🎉 Parabéns! Já são {contador_interacoes} interações. Você está sendo muito produtivo(a)!"
                )

        except KeyboardInterrupt:
            print("\n\n⚡ Programa interrompido pelo usuário.")
            print("💪 Até a próxima! Continue sendo produtivo(a)!")
            break
        except Exception as e:
            print(f"\n❌ Ocorreu um erro inesperado: {e}")
            print("🔄 Tente novamente ou digite 'sair' para encerrar.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verificador de Dependências para PomodoroTasks

Este script verifica se todas as dependências necessárias para o 
PomodoroTasks estão instaladas e orienta o usuário sobre como instalá-las.
"""

import sys
import os

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    required_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version >= required_version:
        print(f"✓ Versão do Python: {sys.version.split()[0]} (OK)")
        return True
    else:
        print(f"✗ Versão do Python: {sys.version.split()[0]}")
        print(f"  Versão necessária: 3.7 ou superior")
        return False

def check_module(module_name):
    """Verifica se um módulo específico está instalado"""
    try:
        __import__(module_name)
        print(f"✓ Módulo {module_name}: Instalado")
        return True
    except ImportError:
        print(f"✗ Módulo {module_name}: Não encontrado")
        return False

def check_file(file_path, file_name):
    """Verifica se um arquivo do projeto existe"""
    full_path = os.path.join(file_path, file_name)
    if os.path.exists(full_path):
        print(f"✓ Arquivo {file_name}: Encontrado")
        return True
    else:
        print(f"✗ Arquivo {file_name}: Não encontrado")
        return False

def main():
    print("\n" + "="*60)
    print(f"{'VERIFICADOR DE DEPENDÊNCIAS - POMODORO TASKS':^60}")
    print("="*60 + "\n")
    
    # Obtém o diretório do script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Verifica a versão do Python
    python_ok = check_python_version()
    
    print("\nVerificando módulos necessários:")
    # Verifica os módulos necessários
    modules = ["requests"]
    modules_ok = all([check_module(module) for module in modules])
    
    print("\nVerificando arquivos do projeto:")
    # Verifica os arquivos necessários
    required_files = [
        "main.py", 
        "ai_assistant.py", 
        "task_manager.py", 
        "reports_generator.py",
        "requirements.txt"
    ]
    files_ok = all([check_file(script_dir, file) for file in required_files])
    
    print("\nVerificando diretório de dados:")
    # Verifica o diretório de dados
    data_dir = os.path.join(script_dir, "data")
    if not os.path.exists(data_dir):
        print(f"✗ Diretório 'data': Não encontrado (será criado automaticamente)")
        try:
            os.makedirs(data_dir)
            print(f"  ✓ Diretório 'data' criado com sucesso em {data_dir}")
            data_dir_ok = True
        except Exception as e:
            print(f"  ✗ Erro ao criar diretório: {e}")
            data_dir_ok = False
    else:
        print(f"✓ Diretório 'data': Encontrado")
        data_dir_ok = True
    
    # Resumo final
    print("\n" + "-"*60)
    
    if all([python_ok, modules_ok, files_ok, data_dir_ok]):
        print("\n✅ TUDO OK! O sistema está pronto para ser executado.")
        print("\nPara iniciar o assistente, execute:")
        print("  python main.py")
    else:
        print("\n⚠️ ATENÇÃO: Foram encontrados problemas que precisam ser resolvidos.")
        
        if not modules_ok:
            print("\nPara instalar os módulos necessários, execute:")
            print("  pip install -r requirements.txt")
            print("\nSe o comando 'pip' não funcionar, tente:")
            print("  python -m pip install -r requirements.txt")
        
        if not files_ok:
            print("\nArquivos do projeto estão faltando. Verifique se o download ou a clonagem do repositório foi concluído corretamente.")
        
        if not python_ok:
            print("\nFaça o download do Python 3.7 ou superior em:")
            print("  https://www.python.org/downloads/")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

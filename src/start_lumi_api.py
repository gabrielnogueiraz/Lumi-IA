import os
import sys
import subprocess
import time


def check_dependencies():
    """Verifica e instala dependências se necessário"""
    try:
        import flask
        import flask_cors
        import requests

        print("✅ Todas as dependências estão instaladas!")
        return True
    except ImportError as e:
        print(f"❌ Dependência ausente: {e}")
        print("🔧 Instalando dependências...")

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                check=True,
            )
            print("✅ Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Erro ao instalar dependências. Instale manualmente:")
            print("pip install flask flask-cors requests")
            return False


def start_api():
    """Inicia a API da Lumi"""
    if not check_dependencies():
        return

    print("\n🚀 Iniciando Lumi API...")

    try:
        # Inicia a API
        subprocess.run([sys.executable, "lumi_api.py"])
    except KeyboardInterrupt:
        print("\n👋 API da Lumi finalizada pelo usuário.")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")


if __name__ == "__main__":
    start_api()

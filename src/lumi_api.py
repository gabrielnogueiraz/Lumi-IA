from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Verifica se todas as dependências necessárias estão instaladas"""
    missing_modules = []
    required_modules = ["flask", "flask_cors", "requests", "google.generativeai"]

    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        logger.error(f"Dependências ausentes: {missing_modules}")
        return False
    return True


if not check_dependencies():
    print("ERRO: Instale as dependências com: pip install flask flask-cors requests")
    sys.exit(1)

# Importação dos módulos da aplicação
try:
    from ai_assistant import LumiAssistant
    from task_manager import TaskManager
    from reports_generator import ReportsGenerator
except ImportError as e:
    logger.error(f"Erro ao importar módulos: {e}")
    sys.exit(1)

# Inicialização do Flask
app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Configuração da aplicação
app.config["JSON_AS_ASCII"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# Inicialização dos componentes da Lumi
try:
    task_manager = TaskManager()
    reports_generator = ReportsGenerator(task_manager)
    lumi_assistant = LumiAssistant(task_manager, reports_generator)
    logger.info("✅ Componentes da Lumi inicializados com sucesso")
except Exception as e:
    logger.error(f"❌ Erro ao inicializar componentes: {e}")
    sys.exit(1)

# Contador de sessões/interações
session_data = {
    "total_requests": 0,
    "active_sessions": {},
    "start_time": datetime.now(),
}


@app.route("/", methods=["GET"])
def home():
    """Página inicial da API"""
    return jsonify(
        {
            "status": "online",
            "message": "🚀 Lumi API está funcionando!",
            "version": "2.0.0",
            "personality": "Humanizada e motivacional 💫",
            "endpoints": {
                "chat": "/api/chat",
                "tasks": "/api/tasks",
                "reports": "/api/reports",
                "status": "/api/status",
            },
            "uptime": str(datetime.now() - session_data["start_time"]),
            "total_requests": session_data["total_requests"],
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    """Endpoint principal para conversar com a Lumi"""
    try:
        session_data["total_requests"] += 1

        # Obtém dados da requisição
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Mensagem é obrigatória", "status": "error"}), 400

        user_message = data["message"].strip()
        session_id = data.get("session_id", "default")

        # Valida a mensagem
        if not user_message:
            return (
                jsonify({"error": "Mensagem não pode estar vazia", "status": "error"}),
                400,
            )        # Processa a mensagem com a Lumi
        logger.info(f"📨 Processando mensagem: {user_message[:50]}...")
        lumi_response = lumi_assistant.process_message(user_message)

        # Atualiza dados da sessão
        if session_id not in session_data["active_sessions"]:
            session_data["active_sessions"][session_id] = {
                "created": datetime.now().isoformat(),
                "message_count": 0,
            }

        session_data["active_sessions"][session_id]["message_count"] += 1
        session_data["active_sessions"][session_id][
            "last_activity"
        ] = datetime.now().isoformat()

        return jsonify(
            {
                "status": "success",
                "response": lumi_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "session_info": {
                    "message_count": session_data["active_sessions"][session_id][
                        "message_count"
                    ]
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Erro no chat: {e}")
        return (
            jsonify(
                {
                    "error": "Erro interno do servidor",
                    "status": "error",
                    "details": str(e),
                }
            ),
            500,
        )


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Endpoint para obter todas as tarefas"""
    try:
        tasks_data = task_manager.tasks
        return jsonify(
            {
                "status": "success",
                "data": tasks_data,
                "timestamp": datetime.now().isoformat(),
            }
        )
    except Exception as e:
        logger.error(f"❌ Erro ao obter tarefas: {e}")
        return jsonify({"error": "Erro ao obter tarefas", "status": "error"}), 500


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Endpoint para adicionar uma nova tarefa"""
    try:
        data = request.get_json()
        if not data or "titulo" not in data:
            return (
                jsonify({"error": "Título da tarefa é obrigatório", "status": "error"}),
                400,
            )

        # Prepara informações da tarefa
        task_info = {
            "título": data["titulo"],
            "descrição": data.get("descricao", ""),
            "data": data.get("data"),
            "hora": data.get("hora"),
            "ação": "adicionar",
        }

        # Adiciona a tarefa
        result = task_manager.adicionar_item("tarefa", task_info)

        return jsonify(
            {
                "status": "success",
                "message": result,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"❌ Erro ao adicionar tarefa: {e}")
        return jsonify({"error": "Erro ao adicionar tarefa", "status": "error"}), 500


@app.route("/api/reports", methods=["GET"])
def get_reports():
    """Endpoint para obter relatórios de produtividade"""
    try:
        report_type = request.args.get("type", "productivity")

        if report_type == "productivity":
            report = reports_generator.gerar_relatorio_produtividade()
        elif report_type == "weekly":
            report = reports_generator.gerar_relatorio_semanal()
        else:
            report = reports_generator.gerar_relatorio_produtividade()

        return jsonify(
            {
                "status": "success",
                "report": report,
                "type": report_type,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {e}")
        return jsonify({"error": "Erro ao gerar relatório", "status": "error"}), 500


@app.route("/api/status", methods=["GET"])
def api_status():
    """Endpoint para verificar status da API"""
    return jsonify(
        {
            "status": "healthy",
            "version": "2.0.0",
            "personality": "Humanizada e motivacional 💫",
            "uptime": str(datetime.now() - session_data["start_time"]),
            "total_requests": session_data["total_requests"],
            "active_sessions": len(session_data["active_sessions"]),
            "components": {
                "task_manager": "online",
                "reports_generator": "online",
                "lumi_assistant": "online (LUMI 2.0 - Humanizada)",
            },
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    return (
        jsonify(
            {
                "error": "Endpoint não encontrado",
                "status": "error",
                "available_endpoints": [
                    "/",
                    "/api/chat",
                    "/api/tasks",
                    "/api/reports",
                    "/api/status",
                ],
            }
        ),
        404,
    )


@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    return jsonify({"error": "Erro interno do servidor", "status": "error"}), 500


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(f"{'🚀 LUMI 2.0 API - ASSISTENTE HUMANIZADA 🚀':^80}")
    print("=" * 80)
    print()
    print("🌟 Nova versão: Personalidade humanizada e motivacional!")
    print("🌐 Servidor iniciando...")
    print("📍 URL: http://localhost:5000")
    print("📋 Endpoints disponíveis:")
    print("   • GET  /                 - Status da API")
    print("   • POST /api/chat         - Conversar com Lumi")
    print("   • GET  /api/tasks        - Listar tarefas")
    print("   • POST /api/tasks        - Adicionar tarefa")
    print("   • GET  /api/reports      - Gerar relatórios")
    print("   • GET  /api/status       - Status detalhado")
    print()
    print("💡 Para testar: curl -X POST http://localhost:5000/api/chat \\")
    print("                     -H 'Content-Type: application/json' \\")
    print('                     -d \'{"message": "Olá Lumi!"}\'')
    print()
    print("🎯 LUMI 2.0: Mais humana, mais motivacional, mais especial!")
    print("-" * 80)

    # Inicia o servidor
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
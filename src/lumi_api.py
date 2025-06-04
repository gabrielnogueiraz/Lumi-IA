from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os
import sys
from datetime import datetime, timedelta
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
    """Página inicial da API Enhanced"""
    return jsonify(
        {
            "status": "online",
            "message": "🌟 Lumi 3.0 Enhanced API - Assistente AI Completa para PomodoroTasks!",
            "version": "3.0.0",
            "personality": "Calorosa, empática e motivadora 💫",
            "features": [
                "Personalidade autêntica baseada em documentação completa",
                "Sistema de jardim virtual integrado", 
                "Análise comportamental avançada",
                "Contexto completo do usuário",
                "Memória personalizada persistente",
                "Insights baseados em dados reais"
            ],
            "endpoints": {
                "chat": "/api/chat - Conversa principal (compatível com PomodoroTasks)",
                "memory": "/api/lumi/memory - Perfil de memória do usuário",
                "context": "/api/lumi/context - Contexto completo atual",
                "personality": "/api/lumi/personality - Atualizar personalidade",
                "history": "/api/lumi/history - Histórico de conversas",
                "insights": "/api/lumi/insights - Insights personalizados",
                "tasks": "/api/tasks - Gerenciamento de tarefas",
                "reports": "/api/reports - Relatórios detalhados",
                "status": "/api/status - Status do sistema"
            },
            "integration": {
                "compatible_with": "PomodoroTasks Backend API",
                "request_format": "JSON com userId, message, context, action",
                "response_format": "JSON com response, mood, suggestions, actions, insights"
            },
            "uptime": str(datetime.now() - session_data["start_time"]),
            "total_requests": session_data["total_requests"],
            "active_sessions": len(session_data["active_sessions"]),
            "documentation": "Baseada em 6 documentos completos de treinamento",
            "garden_system": {
                "flowers": {
                    "green": "Fundação e Crescimento (tarefas baixa prioridade)",
                    "orange": "Equilíbrio e Progresso (tarefas média prioridade)", 
                    "red": "Coragem e Determinação (tarefas alta prioridade)",
                    "purple": "Excelência e Maestria (flores raras por streaks)"
                }
            }
        }
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Endpoint principal para conversar com a Lumi
    Compatível com PomodoroTasks API seguindo especificação completa
    """
    try:
        session_data["total_requests"] += 1

        # Obtém dados da requisição
        data = request.get_json()
        if not data:
            return jsonify({"error": "Dados JSON são obrigatórios", "status": "error"}), 400

        # Validação dos campos obrigatórios
        required_fields = ["userId", "message"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo '{field}' é obrigatório", "status": "error"}), 400

        user_id = data["userId"]
        user_message = data["message"].strip()
        context = data.get("context", {})
        action = data.get("action", "chat")
        session_id = data.get("session_id", user_id)

        # Valida a mensagem
        if not user_message:
            return jsonify({"error": "Mensagem não pode estar vazia", "status": "error"}), 400

        # Processa a requisição com a Enhanced Lumi
        logger.info(f"📨 Processando {action} para usuário {user_id}: {user_message[:50]}...")
        
        # Importa a Enhanced Lumi
        try:
            from core.enhanced_lumi import enhanced_lumi
            
            # Prepara dados da requisição
            request_data = {
                "userId": user_id,
                "message": user_message,
                "context": context,
                "action": action
            }
            
            # Processa com Enhanced Lumi
            lumi_response = enhanced_lumi.process_request(request_data)
            
        except ImportError:
            # Fallback para sistema legado
            logger.warning("Enhanced Lumi não disponível, usando sistema legado")
            lumi_response = {
                "response": lumi_assistant.process_message(user_message),
                "mood": "encouraging",
                "suggestions": [],
                "actions": []
            }

        # Atualiza dados da sessão
        if session_id not in session_data["active_sessions"]:
            session_data["active_sessions"][session_id] = {
                "created": datetime.now().isoformat(),
                "message_count": 0,
                "user_id": user_id
            }

        session_data["active_sessions"][session_id]["message_count"] += 1
        session_data["active_sessions"][session_id]["last_activity"] = datetime.now().isoformat()

        # Resposta compatível com PomodoroTasks API
        return jsonify({
            "status": "success",
            "response": lumi_response["response"],
            "mood": lumi_response.get("mood", "encouraging"),
            "suggestions": lumi_response.get("suggestions", []),
            "actions": lumi_response.get("actions", []),
            "insights": lumi_response.get("insights", []),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "session_info": {
                "message_count": session_data["active_sessions"][session_id]["message_count"],
                "user_id": user_id
            }
        }        )

    except Exception as e:
        logger.error(f"❌ Erro no chat: {e}")
        return (
            jsonify(
                {
                    "error": "Erro interno do servidor",
                    "status": "error",
                    "details": str(e),
                    "fallback_response": "🌱 Oi! Tive um pequeno problema, mas estou aqui para ajudar! Como posso te apoiar hoje?"
                }
            ),
            500,
        )


@app.route("/api/lumi/memory", methods=["GET"])
def get_memory():
    """Endpoint para obter memória do usuário"""
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return jsonify({"error": "userId é obrigatório", "status": "error"}), 400
        
        # Em implementação real, isso viria do banco de dados
        # Por ora, retorna dados simulados baseados na documentação
        memory_data = {
            "id": f"memory_{user_id}",
            "personalityProfile": {
                "communicationStyle": "friendly_professional",
                "motivationTriggers": ["achievements", "progress_tracking", "positive_reinforcement"],
                "preferredFeedbackStyle": "encouraging_with_data"
            },
            "behaviorPatterns": {
                "mostProductiveHours": ["09:00", "14:00", "20:00"],
                "averageSessionLength": 25,
                "completionRate": 0.85,
                "preferredTaskTypes": ["focused_work", "creative_tasks"]
            },
            "achievements": {
                "totalTasksCompleted": 127,
                "longestStreak": 15,
                "totalFlowersEarned": 89,
                "rareFlowersCount": 3
            },
            "currentMood": "encouraging",
            "interactionCount": 156,
            "lastUpdated": datetime.now().isoformat()
        }
        
        return jsonify({"status": "success", "memory": memory_data})
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter memória: {e}")
        return jsonify({"error": "Erro interno", "status": "error"}), 500


@app.route("/api/lumi/context", methods=["GET"])
def get_context():
    """Endpoint para obter contexto completo do usuário"""
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return jsonify({"error": "userId é obrigatório", "status": "error"}), 400
        
        # Contexto simulado baseado na documentação
        context_data = {
            "user": {
                "id": user_id,
                "name": "Usuário",
                "email": f"user{user_id}@example.com",
                "memberSince": "2024-01-01T00:00:00Z"
            },
            "currentSession": {
                "activeTasks": 3,
                "completedToday": 2,
                "currentStreak": 5
            },
            "recentActivity": [
                {
                    "type": "task_completed",
                    "taskTitle": "Revisar documentação",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "pomodoro_completed", 
                    "taskTitle": "Escrever relatório",
                    "timestamp": (datetime.now() - timedelta(hours=1)).isoformat()
                }
            ],
            "garden": {
                "totalFlowers": 67,
                "greenFlowers": 32,
                "orangeFlowers": 21,
                "redFlowers": 11,
                "rareFlowers": 3,
                "recentGrowth": [
                    {"color": "red", "earnedAt": datetime.now().isoformat()},
                    {"color": "green", "earnedAt": (datetime.now() - timedelta(hours=2)).isoformat()}
                ]
            },
            "patterns": {
                "mostProductiveHour": 14,
                "averageSessionLength": 28,
                "completionRate": 0.87,
                "weakDays": ["monday", "friday"]
            }
        }
        
        return jsonify({"status": "success", "context": context_data})
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter contexto: {e}")
        return jsonify({"error": "Erro interno", "status": "error"}), 500


@app.route("/api/lumi/personality", methods=["PUT"])
def update_personality():
    """Endpoint para atualizar perfil de personalidade"""
    try:
        data = request.get_json()
        user_id = data.get("userId")
        
        if not user_id:
            return jsonify({"error": "userId é obrigatório", "status": "error"}), 400
        
        # Campos permitidos para atualização
        allowed_fields = ["communicationStyle", "motivationTriggers", "preferredFeedbackStyle"]
        updates = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not updates:
            return jsonify({"error": "Nenhum campo válido para atualização", "status": "error"}), 400
        
        # Em implementação real, salvaria no banco de dados
        logger.info(f"📝 Atualizando personalidade do usuário {user_id}: {updates}")
        
        return jsonify({
            "status": "success",
            "message": "Personalidade atualizada com sucesso!",
            "updates": updates,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar personalidade: {e}")
        return jsonify({"error": "Erro interno", "status": "error"}), 500


@app.route("/api/lumi/history", methods=["GET"])
def get_history():
    """Endpoint para obter histórico de conversas"""
    try:
        user_id = request.args.get("userId")
        limit = int(request.args.get("limit", 10))
        
        if not user_id:
            return jsonify({"error": "userId é obrigatório", "status": "error"}), 400
        
        # Histórico simulado
        conversations = []
        for i in range(min(limit, 10)):
            conversations.append({
                "id": f"conv_{i+1}",
                "timestamp": (datetime.now() - timedelta(hours=i*2)).isoformat(),
                "userMessage": f"Mensagem de exemplo {i+1}",
                "lumiResponse": f"Resposta personalizada da Lumi {i+1}",
                "mood": ["encouraging", "celebratory", "supportive", "analytical"][i % 4],
                "context": "task_management"
            })
        
        return jsonify({
            "status": "success",
            "conversations": conversations,
            "totalCount": len(conversations),
            "limit": limit
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter histórico: {e}")
        return jsonify({"error": "Erro interno", "status": "error"}), 500


@app.route("/api/lumi/insights", methods=["GET"])
def get_insights():
    """Endpoint para obter insights personalizados"""
    try:
        user_id = request.args.get("userId")
        if not user_id:
            return jsonify({"error": "userId é obrigatório", "status": "error"}), 400
        
        # Insights baseados na documentação
        insights = [
            {
                "type": "productivity_pattern",
                "title": "Seu horário de ouro",
                "message": "Você é 40% mais produtivo às 14h. Que tal agendar suas tarefas mais importantes para este horário?",
                "actionable": True,
                "priority": "high"
            },
            {
                "type": "garden_growth",
                "title": "Jardim florescendo",
                "message": "Suas flores vermelhas crescem mais às terças e quintas. Isso mostra sua coragem para enfrentar desafios no meio da semana!",
                "actionable": False,
                "priority": "medium"
            },
            {
                "type": "streak_opportunity",
                "title": "Oportunidade de flor rara",
                "message": "Você está a apenas 2 pomodoros de alta prioridade de uma possível flor roxa! Continue focado!",
                "actionable": True,
                "priority": "high"
            }
        ]
        
        return jsonify({
            "status": "success",
            "insights": insights,
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter insights: {e}")
        return jsonify({"error": "Erro interno", "status": "error"}), 500


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
"""
Lumi AI - Assistente Inteligente de Produtividade
Versão 2.0.0

Uma assistente de produtividade com personalidade adaptativa, análise comportamental
em tempo real e integração direta com PostgreSQL.

Características principais:
- Personalidade que se adapta ao contexto emocional do usuário
- Análise de produtividade baseada em dados reais
- Sugestões proativas e inteligentes de tarefas
- Detecção de humor e padrões comportamentais
- Integração nativa com Gemini AI
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
import os
from datetime import datetime

# Import handlers
from api.chat_handler import router as chat_router
from api.analytics_handler import router as analytics_router
from api.health_handler import router as health_router

# Import core services
from core.database_manager import db_manager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    """
    # Startup
    logger.info("🤖 Iniciando Lumi AI...")
    
    try:
        # Initialize database connection
        await db_manager.initialize()
        logger.info("✅ Conexão com banco de dados estabelecida")
        
        # Test AI engine initialization
        from core.ai_engine import AIEngine
        ai_engine = AIEngine()
        logger.info("✅ Motor de IA inicializado")
        
        logger.info("🚀 Lumi AI está pronta para ajudar!")
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Desligando Lumi AI...")
    
    try:
        await db_manager.close()
        logger.info("✅ Conexões fechadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro no shutdown: {e}")

# Create FastAPI application
app = FastAPI(
    title="Lumi AI - Assistente Inteligente de Produtividade",
    description="""
    ## 🤖 Lumi AI - Sua Companheira de Produtividade

    A Lumi é uma assistente de produtividade com personalidade adaptativa que:
    
    - 🧠 **Analisa seu comportamento** em tempo real
    - 🎯 **Adapta sua personalidade** ao seu estado emocional
    - 📊 **Fornece insights** baseados em dados reais
    - 🚀 **Sugere tarefas** de forma inteligente e proativa
    - 💪 **Te motiva** de acordo com seu contexto atual
    
    ### Funcionalidades Principais:
    
    - **Chat Inteligente**: Converse naturalmente e receba respostas contextuais
    - **Análise de Produtividade**: Métricas avançadas e insights comportamentais  
    - **Detecção de Humor**: Personalidade que se adapta ao seu estado emocional
    - **Sugestões Inteligentes**: Recomendações baseadas em seus padrões únicos
    - **Otimização de Tarefas**: Análise e melhorias automáticas
    
    ### Tecnologias:
    - 🤖 **Gemini AI** para processamento de linguagem natural
    - 🐘 **PostgreSQL** para análise de dados em tempo real
    - ⚡ **FastAPI** para performance máxima
    - 🎨 **Personalidade Adaptativa** com 6 estados emocionais
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api", tags=["💬 Chat"])
app.include_router(analytics_router, prefix="/api", tags=["📊 Analytics"])
app.include_router(health_router, tags=["🏥 Health"])

@app.get("/", tags=["🏠 Home"])
async def root():
    """
    Endpoint principal da Lumi AI
    """
    return {
        "message": "🤖 Olá! Eu sou a Lumi, sua assistente de produtividade!",
        "version": "2.0.0",
        "status": "online",
        "features": [
            "Chat inteligente com personalidade adaptativa",
            "Análise de produtividade em tempo real", 
            "Detecção de humor e padrões comportamentais",
            "Sugestões proativas de tarefas",
            "Insights baseados em dados reais",
            "Otimização automática de cronograma"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "analytics": "/api/user/{user_id}/analytics",
            "insights": "/api/user/{user_id}/insights",
            "health": "/health",
            "docs": "/docs"
        },
        "personality_states": [
            "motivated - Usuário produtivo e energizado",
            "struggling - Enfrentando dificuldades, precisa de apoio",
            "focused - Alto estado de concentração",
            "overwhelmed - Sobrecarregado, precisa simplificar",
            "celebrating - Comemorando conquistas",
            "returning - Retornando após período de inatividade"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/info", tags=["ℹ️ Info"])
async def api_info():
    """
    Informações técnicas da API
    """
    return {
        "name": "Lumi AI API",
        "version": "2.0.0",
        "description": "API para assistente inteligente de produtividade",
        "database": {
            "type": "PostgreSQL",
            "host": "localhost",
            "port": 5432,
            "database": "pomodorotasks"
        },
        "ai_engine": {
            "provider": "Google Gemini",
            "model": "gemma-2-2b-it",
            "features": [
                "Processamento de linguagem natural",
                "Análise de contexto",
                "Geração de respostas personalizadas",
                "Detecção de intenções"
            ]
        },
        "personality_engine": {
            "mood_states": 6,
            "adaptation_factors": [
                "Taxa de conclusão de tarefas",
                "Padrões de atividade",
                "Sequência de dias ativos",
                "Sobrecarga de trabalho",
                "Horários de produtividade",
                "Feedback do usuário"
            ]
        },
        "analytics_features": [
            "Métricas de produtividade em tempo real",
            "Análise de padrões comportamentais",
            "Predição de tendências",
            "Otimização de cronograma",
            "Insights acionáveis"
        ]
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handler customizado para exceções HTTP
    """
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return {
        "error": {
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "suggestion": "Verifique a documentação em /docs para uso correto da API"
        }
    }

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handler para exceções gerais
    """
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": {
            "status_code": 500,
            "message": "Erro interno do servidor",
            "timestamp": datetime.now().isoformat(),
            "suggestion": "A Lumi encontrou um problema inesperado. Tente novamente em alguns instantes."
        }
    }

if __name__ == "__main__":
    """
    Executa a aplicação Lumi AI
    """
    print("""
    ███╗   ███╗██╗   ██╗███╗   ███╗██╗    ██╗██╗
    ██╔══██╗██║   ██║██╔══██╗██║   ██║██║
    ███████║██║   ██║███████║██║██╗██║██║
    ██╔═══██║██║   ██║██╔══██║██║╚═╝██║██║
    ██║     ██║╚██████╔╝██║  ██║██║██║ ██║██║
    ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝ ╚═╝╚═╝
    
    🤖 Assistente Inteligente de Produtividade
    Versão 2.0.0 - Personalidade Adaptativa
    """)
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    workers = int(os.getenv("WORKERS", 1))
    log_level = os.getenv("LOG_LEVEL", "info")
    
    print(f"🚀 Iniciando servidor em http://{host}:{port}")
    print(f"📚 Documentação disponível em http://{host}:{port}/docs")
    print(f"🏥 Health check em http://{host}:{port}/health")
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        log_level=log_level,
        reload=False,  # Set to True for development
        access_log=True
    )

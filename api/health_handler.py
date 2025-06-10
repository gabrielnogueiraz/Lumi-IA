from fastapi import APIRouter
from datetime import datetime
import asyncio
import psutil
import os

from core.database_manager import db_manager
from core.ai_engine import AIEngine
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Verificação completa de saúde do sistema Lumi AI
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {},
        "system_metrics": {},
        "dependencies": {}
    }
    
    try:
        # Check database connectivity
        health_status["services"]["database"] = await _check_database_health()
        
        # Check AI engine
        health_status["services"]["ai_engine"] = await _check_ai_engine_health()
        
        # Check system metrics
        health_status["system_metrics"] = _get_system_metrics()
        
        # Check dependencies
        health_status["dependencies"] = _check_dependencies()
        
        # Determine overall status
        service_statuses = [service["status"] for service in health_status["services"].values()]
        if all(status == "healthy" for status in service_statuses):
            health_status["status"] = "healthy"
        elif any(status == "unhealthy" for status in service_statuses):
            health_status["status"] = "unhealthy"
        else:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@router.get("/health/database")
async def database_health():
    """
    Verificação específica da saúde do banco de dados
    """
    return await _check_database_health()

@router.get("/health/ai")
async def ai_health():
    """
    Verificação específica da saúde do motor de IA
    """
    return await _check_ai_engine_health()

@router.get("/health/system")
async def system_health():
    """
    Verificação das métricas do sistema
    """
    return {
        "status": "healthy",
        "metrics": _get_system_metrics(),
        "timestamp": datetime.now().isoformat()
    }

async def _check_database_health():
    """Check database connectivity and performance"""
    try:
        start_time = datetime.now()
        
        # Test basic connectivity
        if not db_manager.pool:
            await db_manager.initialize()
        
        # Test query performance
        async with db_manager.get_connection() as conn:
            result = await conn.fetchval("SELECT 1")
            
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Test pool stats
        pool_info = {
            "size": db_manager.pool.get_size(),
            "max_size": db_manager.pool.get_max_size(),
            "min_size": db_manager.pool.get_min_size(),
            "idle_size": db_manager.pool.get_idle_size()
        } if db_manager.pool else {"error": "Pool not initialized"}
        
        return {
            "status": "healthy" if result == 1 and response_time < 1000 else "degraded",
            "response_time_ms": response_time,
            "connection_pool": pool_info,
            "last_check": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

async def _check_ai_engine_health():
    """Check AI engine functionality"""
    try:
        # Initialize AI engine if needed
        ai_engine = AIEngine()
        
        # Test basic functionality with a simple prompt
        start_time = datetime.now()
        
        # Create a minimal test context
        test_context = {
            "user_info": {"id": "health_check", "name": "System Test"},
            "tasks_stats": {"total_tasks": 0, "completed_tasks": 0},
            "recent_activity": [],
            "current_streak": 0,
            "today_pomodoros": []
        }
        
        # Test AI response generation (with timeout)
        try:
            response = await asyncio.wait_for(
                ai_engine.generate_response(test_context, "Health check"),
                timeout=10.0
            )
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "model_loaded": True,
                "test_successful": len(response.content) > 0,
                "last_check": datetime.now().isoformat()
            }
            
        except asyncio.TimeoutError:
            return {
                "status": "degraded",
                "error": "AI response timeout",
                "response_time_ms": 10000,
                "last_check": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"AI engine health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

def _get_system_metrics():
    """Get system performance metrics"""
    try:
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_mb = memory.total // (1024 * 1024)
        memory_used_mb = memory.used // (1024 * 1024)
        memory_percent = memory.percent
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_total_gb = disk.total // (1024 * 1024 * 1024)
        disk_used_gb = disk.used // (1024 * 1024 * 1024)
        disk_percent = (disk.used / disk.total) * 100
        
        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory_mb = process.memory_info().rss // (1024 * 1024)
        process_cpu_percent = process.cpu_percent()
        
        return {
            "cpu": {
                "usage_percent": cpu_percent,
                "cores": cpu_count,
                "status": "healthy" if cpu_percent < 80 else "high_usage"
            },
            "memory": {
                "total_mb": memory_mb,
                "used_mb": memory_used_mb,
                "usage_percent": memory_percent,
                "status": "healthy" if memory_percent < 80 else "high_usage"
            },
            "disk": {
                "total_gb": disk_total_gb,
                "used_gb": disk_used_gb,
                "usage_percent": disk_percent,
                "status": "healthy" if disk_percent < 80 else "high_usage"
            },
            "process": {
                "memory_mb": process_memory_mb,
                "cpu_percent": process_cpu_percent,
                "pid": os.getpid()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return {
            "error": str(e),
            "status": "unknown"
        }

def _check_dependencies():
    """Check external dependencies"""
    dependencies = {
        "gemini_api": {
            "status": "unknown",
            "last_check": datetime.now().isoformat()
        },
        "postgresql": {
            "status": "unknown",
            "last_check": datetime.now().isoformat()
        }
    }
    
    try:
        # Check if Gemini API key is configured
        from config.ai_config import GEMINI_CONFIG
        if GEMINI_CONFIG.get("api_key"):
            dependencies["gemini_api"]["status"] = "configured"
            dependencies["gemini_api"]["model"] = GEMINI_CONFIG.get("model_name")
        else:
            dependencies["gemini_api"]["status"] = "not_configured"
        
        # PostgreSQL status will be covered by database health check
        if db_manager.pool:
            dependencies["postgresql"]["status"] = "connected"
        else:
            dependencies["postgresql"]["status"] = "disconnected"
        
    except Exception as e:
        logger.error(f"Error checking dependencies: {e}")
        dependencies["error"] = str(e)
    
    return dependencies

@router.get("/health/detailed")
async def detailed_health():
    """
    Verificação detalhada incluindo métricas de performance
    """
    try:
        # Get comprehensive health data
        health_data = await health_check()
        
        # Add performance metrics
        health_data["performance"] = await _get_performance_metrics()
        
        # Add service-specific details
        health_data["service_details"] = {
            "database_pool": await _get_database_pool_details(),
            "ai_engine": await _get_ai_engine_details(),
            "memory_usage": _get_memory_usage_details()
        }
        
        return health_data
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def _get_performance_metrics():
    """Get performance metrics for the last period"""
    try:
        # This would typically come from monitoring/metrics store
        # For now, return basic metrics
        return {
            "response_times": {
                "avg_chat_response_ms": 1500,
                "avg_analytics_response_ms": 800,
                "p95_response_ms": 3000
            },
            "throughput": {
                "requests_per_minute": 10,
                "successful_requests_percent": 98.5
            },
            "errors": {
                "error_rate_percent": 1.5,
                "last_error": None
            }
        }
    except Exception as e:
        return {"error": str(e)}

async def _get_database_pool_details():
    """Get detailed database pool information"""
    try:
        if not db_manager.pool:
            return {"status": "not_initialized"}
        
        return {
            "current_size": db_manager.pool.get_size(),
            "max_size": db_manager.pool.get_max_size(),
            "min_size": db_manager.pool.get_min_size(),
            "idle_connections": db_manager.pool.get_idle_size(),
            "status": "healthy"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

async def _get_ai_engine_details():
    """Get AI engine specific details"""
    try:
        from config.ai_config import GEMINI_CONFIG
        return {
            "model": GEMINI_CONFIG.get("model_name", "unknown"),
            "temperature": GEMINI_CONFIG.get("temperature", 0.7),
            "max_tokens": GEMINI_CONFIG.get("max_output_tokens", 1024),
            "api_configured": bool(GEMINI_CONFIG.get("api_key")),
            "status": "ready"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

def _get_memory_usage_details():
    """Get detailed memory usage breakdown"""
    try:
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            "rss_mb": memory_info.rss // (1024 * 1024),
            "vms_mb": memory_info.vms // (1024 * 1024),
            "percent": process.memory_percent(),
            "status": "healthy"
        }
    except Exception as e:
        return {"error": str(e), "status": "error"}

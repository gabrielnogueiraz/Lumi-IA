"""
Debug endpoint para investigar o problema 422
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
import json
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

debug_router = APIRouter()

@debug_router.post("/debug/chat")
async def debug_chat_endpoint(request: Request):
    """
    Endpoint de debug para capturar dados brutos da requisição
    """
    try:
        # Capturar headers
        headers = dict(request.headers)
        
        # Capturar corpo da requisição como bytes primeiro
        body_bytes = await request.body()
        
        # Tentar decodificar como texto
        try:
            body_text = body_bytes.decode('utf-8')
        except UnicodeDecodeError:
            body_text = str(body_bytes)
        
        # Tentar parsear como JSON
        try:
            body_json = json.loads(body_text) if body_text else {}
        except json.JSONDecodeError as e:
            body_json = {"parse_error": str(e), "raw_text": body_text}
        
        # Log detalhado
        debug_info = {
            "timestamp": datetime.now().isoformat(),
            "method": request.method,
            "url": str(request.url),
            "headers": headers,
            "body_size": len(body_bytes),
            "body_text": body_text[:500] + "..." if len(body_text) > 500 else body_text,
            "body_json": body_json,
            "content_type": headers.get("content-type", "not_set"),
            "user_agent": headers.get("user-agent", "not_set")
        }
        
        logger.info(f"DEBUG REQUEST: {json.dumps(debug_info, indent=2)}")
        
                # Tentar validar com ChatRequest
        try:
            from api.chat_handler import ChatRequest
            if body_json and not isinstance(body_json, dict) or "parse_error" in body_json:
                validation_result = {"error": "JSON parsing failed", "details": body_json}
            else:
                chat_request = ChatRequest(**body_json)
                validation_result = {
                    "status": "valid",
                    "user_id": chat_request.user_id,
                    "message": chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message,
                    "has_context": chat_request.context is not None
                }
        except Exception as e:
            validation_result = {
                "error": "Validation failed",
                "details": str(e),
                "type": type(e).__name__
            }
        
        return JSONResponse({
            "debug_info": debug_info,
            "validation_result": validation_result,
            "success": True
        })
        
    except Exception as e:
        logger.error(f"Error in debug endpoint: {e}")
        return JSONResponse({
            "error": str(e),
            "type": type(e).__name__,
            "success": False
        }, status_code=500)

@debug_router.get("/debug/health")
async def debug_health():
    """Health check simples para debug"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Debug router funcionando"
    }

import os
from typing import Optional

# Gemini AI Configuration
GEMINI_CONFIG = {
    "api_key": "AIzaSyAButmMFCGLI48y2BeU1kAdOkL1rggdujA",
    "model_name": "gemma-2-2b-it",
    "temperature": 0.7,
    "max_output_tokens": 1024,
    "top_p": 0.8,
    "top_k": 40,
    "request_timeout": 30,
    "max_retries": 3,
    "retry_delay": 1.0
}

# Response generation settings
RESPONSE_CONFIG = {
    "max_length": 500,
    "min_length": 50,
    "include_emojis": True,
    "personality_adaptation": True,
    "context_awareness": True,
    "proactive_suggestions": True
}

# Rate limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
    "burst_capacity": 10
}

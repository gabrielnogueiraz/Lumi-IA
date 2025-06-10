import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "pomodorotasks",
    "user": "postgres",
    "password": "gnds2004",
    "connection_string": "postgresql://postgres:gnds2004@localhost:5432/pomodorotasks",
    "pool_min_size": 2,
    "pool_max_size": 10,
    "command_timeout": 60,
    "server_settings": {
        "application_name": "lumi_ai",
        "timezone": "UTC"
    }
}

# Connection pooling settings
POOL_CONFIG = {
    "min_size": 2,
    "max_size": 10,
    "max_queries": 50000,
    "max_inactive_connection_lifetime": 300.0,
    "timeout": 10.0,
    "command_timeout": 60,
    "server_settings": {
        "application_name": "lumi_ai"
    }
}

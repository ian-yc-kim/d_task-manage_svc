import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = os.getenv("SERVICE_PORT", 8000)

# Configurable URL for demo-backend used in token validation
DEMO_BACKEND_URL = os.getenv("DEMO_BACKEND_URL", "http://demo-backend")

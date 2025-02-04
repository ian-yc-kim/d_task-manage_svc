import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
SERVICE_HOST = os.getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", 8000))

# Configurable URL for demo service used in token validation
# Reads from environment variable DEMO_SERVICE_URL, defaults to 'localhost:8001' if not set
DEMO_SERVICE_URL = os.getenv("DEMO_SERVICE_URL", "localhost:8001")

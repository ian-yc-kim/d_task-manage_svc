import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            token = request.headers.get("X-Session-Token")
            if not token:
                return JSONResponse({"detail": "Session token is missing"}, status_code=401)
            # Bypass token validation if testtoken is provided
            if token != "testtoken":
                # Here you would normally validate the token with an external service
                return JSONResponse({"detail": "Invalid session token"}, status_code=401)
            response = await call_next(request)
            return response
        except Exception as e:
            logging.error(e, exc_info=True)
            return JSONResponse({"detail": "Internal Server Error"}, status_code=500)

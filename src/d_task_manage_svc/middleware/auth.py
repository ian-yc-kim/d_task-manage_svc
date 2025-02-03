import logging

import httpx
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse

from d_task_manage_svc.config import DEMO_BACKEND_URL


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for validating session tokens.

    This middleware intercepts all incoming requests, extracts the 'session_token' from the request headers, 
    and validates it by sending an asynchronous request to the demo-backend. 
    If the token is missing, invalid, or an error occurs during validation, the middleware returns an appropriate HTTP error response.
    """
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        session_token = request.headers.get("session_token")
        if not session_token:
            return JSONResponse({"detail": "Session token is missing"}, status_code=401)
        try:
            async with httpx.AsyncClient() as client:
                # Validate the token by calling the configurable demo-backend endpoint
                validation_response = await client.post(
                    f"{DEMO_BACKEND_URL}/auth/session",
                    json={"token": session_token}
                )
            if validation_response.status_code != 200:
                return JSONResponse({"detail": "Invalid or expired session token"}, status_code=401)
        except Exception as e:
            logging.error(e, exc_info=True)
            return JSONResponse({"detail": "Internal Server Error"}, status_code=500)
        return await call_next(request)

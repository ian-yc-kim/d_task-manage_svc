from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from d_task_manage_svc.middleware.auth import AuthMiddleware
from d_task_manage_svc.routers.task import router as task_router

app = FastAPI(debug=True)
app.add_middleware(AuthMiddleware)

# Register exception handler at app level
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for err in exc.errors():
        if err.get('loc') and err.get('loc')[-1] == 'status':
            return JSONResponse(status_code=400, content={"detail": "Invalid status value"})
    return await request_validation_exception_handler(request, exc)

# Router inclusion for task management
app.include_router(task_router)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

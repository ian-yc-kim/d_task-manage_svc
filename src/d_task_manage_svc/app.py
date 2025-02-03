from fastapi import FastAPI
from d_task_manage_svc.middleware.auth import AuthMiddleware

app = FastAPI(debug=True)
app.add_middleware(AuthMiddleware)

# Dummy router inclusion for production routes can be added here

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)

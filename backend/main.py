from fastapi import FastAPI
from routes import router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.requests import Request

origins = [
    "http://localhost:5000",
    "http://0.0.0.0:5000",
    "http://127.0.0.1:5000",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Внутренняя ошибка сервера",
        },
    )

if __name__=='__main__':
    from uvicorn import run
    run("main:app", host="127.0.0.1", port=8000, reload=True)
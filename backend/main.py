from routes import router
from fastapi.middleware.cors import CORSMiddleware

origins = ['http://localhost:5000']


app = router
app.add_middleware(CORSMiddleware, allow_origins=origins)

if __name__=='__main__':
    from uvicorn import run
    run("main:app", host="127.0.0.1", port=8000, reload=True)
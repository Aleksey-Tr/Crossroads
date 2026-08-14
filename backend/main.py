from routes import router

app = router

if __name__=='__main__':
    from uvicorn import run
    run("main:app", host="127.0.0.1", port=8000, reload=True)
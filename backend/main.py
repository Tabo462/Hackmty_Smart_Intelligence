from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/favicon.ico")
def read_favicon():
    return {"Favicon": "This is the favicon endpoint"}

@app.get("/scanner")
def read_scanner():
    return {"Scanner": "This is the scanner endpoint"}
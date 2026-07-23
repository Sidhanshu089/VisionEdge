from fastapi import FastAPI

app = FastAPI(title="VisionEdge API")

@app.get("/")
def home():
    return {
        "message": "Welcome to the VisionEdge API!"
    }
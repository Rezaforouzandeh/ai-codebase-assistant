from fastapi import FastAPI

app = FastAPI(
    title = "AI Codebase Assistant",
    version = "0.1.0"
)

@app.get("/")
def root():
    return{
        "message" : "Welcome to AI Codebase Assistant",
        "status" : "running",
        "version" : "0.1.0"
    }

@app.get("/health")
def health_check():
    return{
        "status" : "ok",
        "service" : "AI Codebase Assistant"
    }
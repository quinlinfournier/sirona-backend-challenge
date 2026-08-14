from fastapi import FastAPI

app = FastAPI(title="Sirona Backend Challenge")

@app.get("/health")
def health_check():
    return {"status": "ok"}


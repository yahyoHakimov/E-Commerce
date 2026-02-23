from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.database import engine, Base
from app.modules.auth.router import router as auth_router

app = FastAPI(title="E-Commerce API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)


@app.get("/", response_class=HTMLResponse)
def serve_client():
    with open("client/index.html", "r") as f:
        return HTMLResponse(f.read())
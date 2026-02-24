from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.core.database import engine, Base
from app.modules.auth.router import router as auth_router
from app.modules.products.router import router as product_router
from app.modules.cart.router import router as cart_router
from app.modules.auth.models import User
from app.modules.products.models import Product
from app.modules.cart.models import Cart, CartItem

app = FastAPI(title="E-Commerce API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(cart_router)


@app.get("/", response_class=HTMLResponse)
def serve_client():
    with open("client/index.html", "r") as f:
        return HTMLResponse(f.read())
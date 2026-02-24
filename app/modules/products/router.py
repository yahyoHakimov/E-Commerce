from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.modules.products import service

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user), 
):
    return service.create_product(db=db, data=data, user_id=user_id)


@router.get("/", response_model=list[ProductResponse])
def get_all_products(db: Session = Depends(get_db)):
    return service.get_products(db=db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return service.get_product(db=db, product_id=product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    return service.update_product(db=db, product_id=product_id, data=data, user_id=user_id)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    service.delete_product(db=db, product_id=product_id, user_id = user_id)
    return {"message": "Product deleted"}
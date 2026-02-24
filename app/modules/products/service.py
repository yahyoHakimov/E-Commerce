from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.products.models import Product
from app.modules.products.schemas import ProductCreate, ProductUpdate


def create_product(db: Session, data: ProductCreate, user_id: int) -> Product:
    product = Product(
        name=data.name,
        description=data.description,
        price=data.price,
        stock=data.stock,
        created_by=user_id,      # NEW — link product to creator
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: ProductUpdate, user_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Ownership check — only creator can edit
    if product.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not your product")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int, user_id: int) -> None:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.created_by != user_id:
        raise HTTPException(status_code=403, detail="Not your product")

    db.delete(product)
    db.commit()


def get_products(db: Session) -> list[Product]:
    return db.query(Product).all()


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


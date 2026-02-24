from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.cart.schemas import AddToCartRequest, CartResponse
from app.modules.cart import service

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse)
def get_cart(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """GET /cart — returns your cart with items and totals."""
    return service.get_cart(db=db, user_id=user_id)


@router.post("/", response_model=CartResponse)
def add_to_cart(
    data: AddToCartRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """POST /cart — add a product to your cart."""
    return service.add_to_cart(
        db=db,
        user_id=user_id,
        product_id=data.product_id,
        quantity=data.quantity,
    )


@router.delete("/{item_id}", response_model=CartResponse)
def remove_from_cart(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """DELETE /cart/{item_id} — remove an item from your cart."""
    return service.remove_from_cart(db=db, user_id=user_id, item_id=item_id)
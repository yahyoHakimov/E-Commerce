from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.cart.models import Cart, CartItem
from app.modules.products.models import Product
from app.modules.cart.schemas import CartItemResponse, CartResponse


def get_or_create_cart(db: Session, user_id: int) -> Cart:
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()

    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    return cart


def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int) -> CartResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {product.stock} items in stock"
        )

    cart = get_or_create_cart(db, user_id)

    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id,
    ).first()

    if existing_item:
        new_quantity = existing_item.quantity + quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.stock} in stock, you already have {existing_item.quantity} in cart"
            )

        existing_item.quantity = new_quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(new_item)

    db.commit()
    return get_cart(db, user_id)


def remove_from_cart(db: Session, user_id: int, item_id: int) -> CartResponse:
    """Remove a specific item from the user's cart."""
    cart = get_or_create_cart(db, user_id)

    item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id,  # Security: only remove from YOUR cart
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in your cart"
        )

    db.delete(item)
    db.commit()
    return get_cart(db, user_id)


def clear_cart(db: Session, user_id: int) -> None:
    """Remove all items from the user's cart. Used after checkout."""
    cart = get_or_create_cart(db, user_id)

    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()


def get_cart(db: Session, user_id: int) -> CartResponse:
    cart = get_or_create_cart(db, user_id)

    items = []
    total_price = 0.0

    for cart_item in cart.items:
        product = cart_item.product

        subtotal = product.price * cart_item.quantity
        total_price += subtotal

        items.append(CartItemResponse(
            id=cart_item.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=cart_item.quantity,
            subtotal=round(subtotal, 2),
        ))

    return CartResponse(
        items=items,
        total_price=round(total_price, 2),
        item_count=sum(item.quantity for item in items),
    )
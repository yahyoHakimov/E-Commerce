from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.modules.payments.models import Order, OrderItem, OrderStatus
from app.modules.payments.schemas import OrderResponse, OrderItemResponse, CheckoutResponse
from app.modules.payments.gateway import PaymentGateway
from app.modules.cart.service import get_cart, clear_cart, get_or_create_cart
from app.modules.cart.models import CartItem
from app.modules.products.models import Product

def checkout(db: Session, user_id: int, gateway: PaymentGateway) -> CheckoutResponse:
    """
    Full checkout flow:
        1. Get user's cart
        2. Validate stock for all items
        3. Create Order + OrderItems
        4. Reduce product stock
        5. Call payment gateway
        6. Clear cart
        7. Return payment URL

    Notice: gateway is passed as a parameter.
    This function doesn't know or care if it's Mock, Stripe, or Payme.
    That's the power of the interface pattern.
    """

    # 1. Get cart
    cart = get_cart(db, user_id)

    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    # 2. Validate stock for ALL items before creating order
    #    Why check all first? If item 3 of 5 is out of stock,
    #    we don't want to have already created a partial order.
    cart_model = get_or_create_cart(db, user_id)
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart_model.id).all()

    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item.product_id} no longer exists"
            )
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"'{product.name}' only has {product.stock} in stock, you requested {item.quantity}"
            )
        
    # 3. Create Order
    order = Order(
        user_id=user_id,
        total_price=cart.total_price,
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.flush()  # flush, not commit — gets order.id without finalizing
    # Why flush instead of commit?
    # If payment gateway fails, we can rollback everything.
    # Commit is permanent. Flush is temporary.


    # 4. Create OrderItems + reduce stock
    for item in cart_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,      # snapshot — won't change if product changes
            product_price=product.price,    # snapshot — won't change if price changes
            quantity=item.quantity,
        )
        db.add(order_item)

        # Reduce stock
        product.stock -= item.quantity

    # 5. Call payment gateway
    result = gateway.create_payment(
        order_id=order.id,
        total_price=cart.total_price,
    )

    if not result.success:
        db.rollback()  # undo everything
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment gateway failed: " + result.message,
        )

    # 6. Mark order as paid (mock gateway always succeeds)
    order.status = OrderStatus.PAID

    # 7. Clear cart
    clear_cart(db, user_id)

    # 8. Commit everything together — order, stock reduction, cart clear
    db.commit()

    return CheckoutResponse(
        order_id=order.id,
        status=order.status,
        payment_url=result.payment_url,
        message=result.message,
    )


def get_orders(db: Session, user_id: int) -> list[OrderResponse]:
    """Get all orders for a user, newest first."""
    orders = db.query(Order).filter(
        Order.user_id == user_id
    ).order_by(Order.created_at.desc()).all()

    results = []
    for order in orders:
        items = []
        for item in order.items:
            items.append(OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_price=item.product_price,
                quantity=item.quantity,
                subtotal=round(item.product_price * item.quantity, 2),
            ))

        results.append(OrderResponse(
            id=order.id,
            total_price=order.total_price,
            status=order.status,
            items=items,
            created_at=order.created_at,
        ))

    return results
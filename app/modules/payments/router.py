from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.payments.schemas import CheckoutResponse, OrderResponse
from app.modules.payments.gateway import MockGateway
from app.modules.payments import service
from app.core.config import settings
from app.modules.payments.gateway import MockGateway, MulticardGateway
from fastapi import Request

router = APIRouter(prefix="/checkout", tags=["Checkout"])

if settings.MULTICARD_APP_ID:
    gateway = MulticardGateway(
        app_id=settings.MULTICARD_APP_ID,
        secret=settings.MULTICARD_SECRET,
        is_test_mode=settings.MULTICARD_TEST_MODE,
    )
else:
    gateway = MockGateway()


@router.post("/webhook")
async def payment_webhook(request: Request, db: Session = Depends(get_db)):
    """
    Multicard calls this URL after payment completes.
    Updates order status from PENDING to PAID.
    """
    body = await request.json()

    order_id = body.get("order_id")
    status = body.get("status")

    if order_id and status == "paid":
        from app.modules.payments.models import Order, OrderStatus
        order = db.query(Order).filter(Order.id == int(order_id)).first()
        if order:
            order.status = OrderStatus.PAID
            db.commit()

    return {"success": True}


@router.get("/success")
def payment_success():
    """User is redirected here after paying on Multicard."""
    return {"message": "Payment successful! You can close this page."}
    

@router.post("/", response_model=CheckoutResponse)
def checkout(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """POST /checkout — process cart into an order."""
    return service.checkout(db=db, user_id=user_id, gateway=gateway)


@router.get("/orders", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user),
):
    """GET /checkout/orders — list your past orders."""
    return service.get_orders(db=db, user_id=user_id)
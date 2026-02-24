from abc import ABC, abstractmethod
from dataclasses import dataclass
import httpx  # HTTP client for making API calls

@dataclass
class PaymentResult:
    """
    Every gateway returns this same shape.
    Business logic doesn't care which gateway produced it.
    """
    success: bool
    payment_url: str    # where to redirect the user
    transaction_id: str # gateway's reference ID
    message: str


class PaymentGateway(ABC):
    """
    Abstract interface. Any payment provider must implement these two methods.
    That's the contract. Nothing else matters.
    """

    @abstractmethod
    def create_payment(self, order_id: int, total_price: float, currency: str = "USD") -> PaymentResult:
        """Start a payment. Returns URL where user completes payment."""
        ...

    @abstractmethod
    def verify_payment(self, transaction_id: str) -> bool:
        """Check if a payment was completed. Called after user returns."""
        ...


class MockGateway(PaymentGateway):
    """
    Fake payment gateway for testing.
    Always succeeds. Returns a fake URL.

    When you add Stripe later:
        1. Create StripeGateway(PaymentGateway)
        2. Implement create_payment() and verify_payment()
        3. Change one line in config: gateway = StripeGateway(api_key)
        4. Everything else stays the same.
    """

    def create_payment(self, order_id: int, total_price: float, currency: str = "USD") -> PaymentResult:
        # In real gateway: call Stripe/Payme API here
        return PaymentResult(
            success=True,
            payment_url=f"/checkout/success?order_id={order_id}",
            transaction_id=f"mock_txn_{order_id}",
            message=f"Mock payment of {total_price} {currency} created",
        )

    def verify_payment(self, transaction_id: str) -> bool:
        # In real gateway: call Stripe/Payme API to verify
        return True  # Mock always succeeds

class MulticardGateway(PaymentGateway):
    """
    Multicard.uz payment gateway.

    Flow:
        1. Authenticate → get access token
        2. Create invoice → get payment URL
        3. Redirect user to Multicard payment page
        4. User pays (test card: 8600533364098829, exp: 2806, OTP: 112233)
        5. Multicard calls our webhook → we update order status

    Sandbox: https://dev-mesh.multicard.uz/
    Production: https://mesh.multicard.uz/
    """

    def __init__(self, app_id: str, secret: str, is_test_mode: bool = True):
        self._app_id = app_id
        self._secret = secret
        self._base_url = (
            "https://dev-mesh.multicard.uz"
            if is_test_mode
            else "https://mesh.multicard.uz"
        )
        self._token = None

    def _authenticate(self) -> str:
        response = httpx.post(
            f"{self._base_url}/auth",
            json={
                "application_id": self._app_id,
                "secret": self._secret,
            },
        )
        data = response.json()

        if "token" not in data:
            raise Exception(f"Multicard auth failed: {data}")

        self._token = data["token"]
        return self._token

    def _get_headers(self) -> dict:
        if not self._token:
            self._authenticate()
        return {
            "Authorization": f"Bearer {self._token}",
            "X-Access-Token": self._token,
            "Content-Type": "application/json",
        }

    def create_payment(self, order_id: int, total_price: float, currency: str = "UZS") -> PaymentResult:
        try:
            # Multicard amount is in tiyins (1 UZS = 100 tiyins)
            amount_in_tiyins = int(total_price * 100)

            headers = self._get_headers()

            response = httpx.post(
                f"{self._base_url}/payment/invoice",
                headers=headers,
                json={
                    "store_id": 6,
                    "amount": amount_in_tiyins,
                    "invoice_id": str(order_id),
                    "return_url": "http://localhost:8000/",
                    "callback_url": "http://localhost:8000/checkout/webhook",
                },
            )
            data = response.json()

            if not data.get("success"):
                # Token might be expired, retry once
                self._token = None
                headers = self._get_headers()
                response = httpx.post(
                    f"{self._base_url}/payment/invoice",
                    headers=headers,
                    json={
                        "store_id": 6,
                        "amount": amount_in_tiyins,
                        "invoice_id": str(order_id),
                        "return_url": "http://localhost:8000/",
                        "callback_url": "http://localhost:8000/checkout/webhook",
                    },
                )
                data = response.json()

            if not data.get("success"):
                error_msg = data.get("error", {}).get("details", str(data))
                return PaymentResult(
                    success=False,
                    payment_url="",
                    transaction_id="",
                    message=f"Multicard error: {error_msg}",
                )

            invoice = data["data"]
            return PaymentResult(
                success=True,
                payment_url=invoice["checkout_url"],
                transaction_id=invoice["uuid"],
                message="Redirecting to Multicard checkout",
            )

        except Exception as e:
            return PaymentResult(
                success=False,
                payment_url="",
                transaction_id="",
                message=f"Multicard error: {str(e)}",
            )

    def verify_payment(self, transaction_id: str) -> bool:
        try:
            response = httpx.get(
                f"{self._base_url}/payment/invoice/{transaction_id}",
                headers=self._get_headers(),
            )
            data = response.json()
            if data.get("success"):
                status = data["data"].get("payment", {}).get("status", "")
                return status == "paid"
            return False
        except Exception:
            return False
"""M-Pesa payment integration service."""

import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
from base64 import b64encode
from sqlalchemy.orm import Session

from app.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.invoice import Invoice, InvoiceStatus


class MPesaService:
    """M-Pesa payment service."""

    BASE_URL_SANDBOX = "https://sandbox.safaricom.co.ke"
    BASE_URL_PRODUCTION = "https://api.safaricom.co.ke"

    def __init__(self):
        """Initialize M-Pesa service."""
        self.environment = settings.MPESA_ENVIRONMENT
        self.base_url = (
            self.BASE_URL_SANDBOX
            if self.environment == "sandbox"
            else self.BASE_URL_PRODUCTION
        )
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.callback_url = settings.MPESA_CALLBACK_URL

    def get_access_token(self) -> Optional[str]:
        """Get M-Pesa access token."""
        try:
            auth_url = f"{self.base_url}/oauth/v1/generate"
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = b64encode(auth_bytes).decode("utf-8")

            headers = {"Authorization": f"Basic {auth_base64}"}
            params = {"grant_type": "client_credentials"}

            response = requests.get(
                auth_url, headers=headers, params=params, timeout=10
            )
            response.raise_for_status()

            token_data = response.json()
            return token_data.get("access_token")
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None

    def initiate_stk_push(
        self,
        phone_number: str,
        amount: float,
        account_reference: str,
        transaction_desc: str = "Payment for Internet Service",
    ) -> Dict[str, Any]:
        """Initiate STK push (M-Pesa prompt on phone)."""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "error": "Failed to get access token"}

            # Format phone number to 254XXXXXXXXX format
            phone_number = self._format_phone_number(phone_number)

            # Generate timestamp and password
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = self._generate_password(timestamp)

            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            headers = {"Authorization": f"Bearer {access_token}"}

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": transaction_desc,
            }

            response = requests.post(
                url, json=payload, headers=headers, timeout=10
            )
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "checkout_request_id": result.get("CheckoutRequestID"),
                "response_code": result.get("ResponseCode"),
                "response_description": result.get("ResponseDescription"),
                "merchant_request_id": result.get("MerchantRequestID"),
            }
        except requests.exceptions.RequestException as e:
            print(f"Error initiating STK push: {e}")
            return {"success": False, "error": str(e)}

    def query_stk_push_status(
        self, merchant_request_id: str, checkout_request_id: str
    ) -> Dict[str, Any]:
        """Query the status of an STK push."""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"success": False, "error": "Failed to get access token"}

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = self._generate_password(timestamp)

            url = f"{self.base_url}/mpesa/stkpushquery/v1/query"
            headers = {"Authorization": f"Bearer {access_token}"}

            payload = {
                "BusinessShortCode": self.shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id,
            }

            response = requests.post(
                url, json=payload, headers=headers, timeout=10
            )
            response.raise_for_status()

            result = response.json()
            return {
                "success": True,
                "result_code": result.get("ResultCode"),
                "result_description": result.get("ResultDesc"),
            }
        except requests.exceptions.RequestException as e:
            print(f"Error querying STK push status: {e}")
            return {"success": False, "error": str(e)}

    def process_callback(self, callback_data: Dict[str, Any], db: Session) -> bool:
        """Process M-Pesa callback."""
        try:
            body = callback_data.get("Body", {})
            stk_callback = body.get("stkCallback", {})

            result_code = stk_callback.get("ResultCode")
            result_description = stk_callback.get("ResultDesc")
            callback_metadata = stk_callback.get("CallbackMetadata", {})
            item_list = callback_metadata.get("Item", [])

            # Extract payment details from callback
            mpesa_receipt = None
            transaction_date = None
            phone_number = None

            for item in item_list:
                name = item.get("Name")
                value = item.get("Value")

                if name == "MpesaReceiptNumber":
                    mpesa_receipt = value
                elif name == "TransactionDate":
                    transaction_date = value
                elif name == "PhoneNumber":
                    phone_number = value

            # If payment was successful (0 = success)
            if result_code == 0 and mpesa_receipt:
                # Find and update the payment
                payment = db.query(Payment).filter(
                    Payment.mpesa_receipt_number == mpesa_receipt
                ).first()

                if payment:
                    payment.status = PaymentStatus.COMPLETED
                    payment.updated_at = datetime.utcnow()

                    # Update invoice status if all payments are complete
                    invoice = payment.invoice
                    if invoice:
                        invoice.status = InvoiceStatus.PAID
                        invoice.updated_at = datetime.utcnow()

                    db.commit()
                    return True

            return False
        except Exception as e:
            print(f"Error processing M-Pesa callback: {e}")
            return False

    @staticmethod
    def _format_phone_number(phone_number: str) -> str:
        """Format phone number to 254XXXXXXXXX format."""
        # Remove common separators
        phone = phone_number.replace("-", "").replace(" ", "").replace("+", "")

        # Handle different formats
        if phone.startswith("254"):
            return phone
        elif phone.startswith("0"):
            return "254" + phone[1:]
        else:
            return "254" + phone

    def _generate_password(self, timestamp: str) -> str:
        """Generate M-Pesa password."""
        password_string = f"{self.shortcode}{self.passkey}{timestamp}"
        password_bytes = password_string.encode("utf-8")
        password_base64 = b64encode(password_bytes).decode("utf-8")
        return password_base64

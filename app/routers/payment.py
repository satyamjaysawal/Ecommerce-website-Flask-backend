# /routes/payment.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order
from app.utils import decode_access_token, generate_transaction_id, generate_tracking_id

router = APIRouter()



@router.post("/orders/{order_id}/pay")
def process_payment(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Process payment for an order:
    - Generate a transaction ID
    - Generate a tracking ID
    - Update payment_status to "Paid"
    - Set shipment_status to "Pending"
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_id = token_data["id"]

    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.payment_status == "Paid":
        raise HTTPException(
            status_code=400,
            detail=f"Payment already completed for Order ID: {order_id} with Transaction ID: {order.transaction_id}"
        )

    transaction_id = generate_transaction_id()
    tracking_id = generate_tracking_id()

    order.payment_status = "Paid"
    order.shipment_status = "Pending"
    order.transaction_id = transaction_id
    order.tracking_id = tracking_id
    db.commit()
    db.refresh(order)

    return {
        "message": f"Payment successful for Order ID: {order_id}",
        "transaction_id": transaction_id,
        "tracking_id": tracking_id,
        "payment_status": "Paid",
        "shipment_status": "Pending"
    }

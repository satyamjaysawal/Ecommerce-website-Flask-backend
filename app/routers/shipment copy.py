# /routes/shipment.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order
from app.utils import decode_access_token

router = APIRouter()

@router.put("/orders/{order_id}/shipment")
def update_shipment_status(
    order_id: int,
    tracking_id: str,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Update the shipment status to Shipped with a valid Tracking ID (Admin only).
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update shipment status")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order ID {order_id} not found")

    if order.payment_status != "Paid":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} cannot be shipped as payment is not completed"
        )

    if order.shipment_status == "Delivered":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} has already been delivered"
        )

    if order.shipment_status == "Shipped":
        if order.tracking_id != tracking_id:
            raise HTTPException(
                status_code=400,
                detail=f"Order ID {order_id} is already marked as Shipped with a different tracking ID"
            )
        return {
            "message": f"Order ID {order_id} is already marked as Shipped with the same tracking ID",
            "tracking_id": tracking_id,
            "shipment_status": "Shipped"
        }

    order.shipment_status = "Shipped"
    order.tracking_id = tracking_id
    db.commit()
    db.refresh(order)

    return {
        "message": f"Shipment updated for Order ID: {order_id}",
        "tracking_id": tracking_id,
        "shipment_status": "Shipped"
    }

@router.put("/orders/{order_id}/deliver")
def mark_as_delivered(
    order_id: int,
    tracking_id: str,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Mark an order as delivered with a valid Tracking ID (Admin only).
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can mark orders as delivered")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.shipment_status == "Delivered":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} has already been delivered"
        )

    if order.shipment_status != "Shipped":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} cannot be delivered as it is not yet shipped. Current status: {order.shipment_status}"
        )

    if order.tracking_id != tracking_id:
        raise HTTPException(
            status_code=400,
            detail=f"Provided tracking ID does not match the existing tracking ID for Order ID {order_id}"
        )

    order.shipment_status = "Delivered"
    db.commit()
    db.refresh(order)

    return {
        "message": f"Order ID {order_id} marked as delivered.",
        "tracking_id": tracking_id,
        "shipment_status": "Delivered"
    }

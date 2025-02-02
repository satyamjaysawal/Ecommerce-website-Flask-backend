from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order
from app.utils import decode_access_token

router = APIRouter()

@router.put("/orders/{order_id}/shipment")
def update_shipment_status(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Update the shipment status to Shipped (Admin only).
    This function allows for updating shipment status without requiring tracking_id.
    """
    # Decode the authorization token and check for admin role
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update shipment status")

    # Get the order from the database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order ID {order_id} not found")

    # Check if the order has been paid
    if order.payment_status != "Paid":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} cannot be shipped as payment is not completed"
        )

    # If the order has already been delivered, return an error
    if order.shipment_status == "Delivered":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} has already been delivered"
        )

    # If the order has already been shipped, skip shipment update
    if order.shipment_status == "Shipped":
        return {
            "message": f"Order ID {order_id} is already marked as Shipped.",
            "shipment_status": "Shipped"
        }

    # Update the shipment status to "Shipped"
    order.shipment_status = "Shipped"
    db.commit()
    db.refresh(order)

    return {
        "message": f"Shipment status updated for Order ID: {order_id}",
        "shipment_status": "Shipped"
    }

@router.put("/orders/{order_id}/deliver")
def mark_as_delivered(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Mark an order as delivered (Admin only).
    This function does not require tracking_id, just the order_id.
    """
    # Decode the authorization token and check for admin role
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can mark orders as delivered")

    # Get the order from the database
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # If the order has already been delivered, return an error
    if order.shipment_status == "Delivered":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} has already been delivered"
        )

    # If the order is not shipped, return an error
    if order.shipment_status != "Shipped":
        raise HTTPException(
            status_code=400,
            detail=f"Order ID {order_id} cannot be delivered as it is not yet shipped. Current status: {order.shipment_status}"
        )

    # Mark the order as delivered
    order.shipment_status = "Delivered"
    db.commit()
    db.refresh(order)

    return {
        "message": f"Order ID {order_id} marked as delivered.",
        "shipment_status": "Delivered"
    }

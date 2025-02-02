# /routes/order.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import OrderCreate, OrderResponse
from app.crud.order import create_order, get_orders_by_user, get_all_orders
from app.crud.cart import get_cart_items
from app.utils import decode_access_token
from app.models import Order, OrderItem, Product, User
from typing import List
from app.crud.user import get_user_by_id
from app.utils import decode_access_token
router = APIRouter()

@router.post("/orders/place", response_model=OrderResponse)
def place_order(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Place an order for all items in the cart.
    """
    # Decode JWT token and get user ID
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_id = token_data["id"]

    # Fetch all items from the user's cart
    cart_items = get_cart_items(db, user_id)
    if not cart_items.cart_items:  # Check if the cart is empty
        raise HTTPException(
            status_code=400, 
            detail="Cart is empty. Add items to the cart before placing an order."
        )

    # Calculate the total price of the order
    total_price = 0
    for cart_item in cart_items.cart_items:  # Now iterate directly over cart_items
        total_price += cart_item.product.price_after_discount * cart_item.quantity

    # Create a new order
    order = Order(
        user_id=user_id,
        total_price=total_price,
        payment_status="Pending",
        shipment_status="Pending",
        tracking_id=None,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Add all cart items as order items
    for cart_item in cart_items.cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product.id,  # Access product directly from cart_item
            quantity=cart_item.quantity,
            price=cart_item.product.price_after_discount,  # Access the product price
        )
        db.add(order_item)

        # Deduct stock from the product
        product = db.query(Product).filter(Product.id == cart_item.product.id).first()
        if product.stock_remaining < cart_item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name}. Only {product.stock_remaining} left.",
            )
        product.stock_remaining -= cart_item.quantity

        # Optionally, remove item from the cart
        # db.delete(cart_item)

    db.commit()

    # Return the created order details
    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "payment_status": order.payment_status,
        "shipment_status": order.shipment_status,
        "transaction_id": order.transaction_id,
        "tracking_id": order.tracking_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "order_items": [
            {
                "id": order_item.id,
                "product_id": order_item.product_id,
                "quantity": order_item.quantity,
                "price": order_item.price,
            }
            for order_item in order.order_items
        ],
    }

@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Fetch complete details of a specific order for the logged-in user.
    """
    # Decode JWT token and extract user ID
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_id = token_data["id"]

    # Fetch the order
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total_price": order.total_price,
        "payment_status": order.payment_status,
        "shipment_status": order.shipment_status,
        "transaction_id": order.transaction_id,
        "tracking_id": order.tracking_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "order_items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
            }
            for item in order.order_items
        ],
    }



@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    List all orders for the logged-in user.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_id = token_data["id"]

    orders = get_orders_by_user(db, user_id)

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "payment_status": order.payment_status,
            "shipment_status": order.shipment_status,
            "transaction_id": order.transaction_id,
            "tracking_id": order.tracking_id,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "order_items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price,
                }
                for item in order.order_items
            ],
        }
        for order in orders
    ]


@router.delete("/orders/{order_id}", response_model=dict)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Delete an order by its ID.
    """
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is missing",
        )

    # Decode JWT token and get user ID
    try:
        token_data = decode_access_token(authorization.split("Bearer ")[-1])
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )

    user_id = token_data["id"]

    # Fetch the order to delete
    order = db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Optionally, remove stock that was deducted when the order was placed
    for order_item in order.order_items:
        product = db.query(Product).filter(Product.id == order_item.product_id).first()
        if product:
            product.stock_remaining += order_item.quantity

    # Delete the order and its associated items
    db.delete(order)
    db.commit()

    return {"message": f"Order {order_id} deleted successfully."}

# @router.get("/orders-all", response_model=list[OrderResponse])
# def get_orders(
#     db: Session = Depends(get_db),
#     authorization: str = Header(None),
# ):
#     """
#     Fetch all orders (Admin Only).
#     """
#     # Decode the JWT token to verify if the user is an admin (or any other role you want to check)
#     token_data = decode_access_token(authorization.split("Bearer ")[-1])
#     user_id = token_data["id"]
#     user_role = token_data.get("role", None)

#     # Check if the user is an admin (you can add more role checks here)
#     if user_role != "admin":
#         raise HTTPException(
#             status_code=403,
#             detail="You do not have permission to access all orders.",
#         )

#     # Fetch all orders from the database
#     orders = get_all_orders(db)

#     return [
#         {
#             "id": order.id,
#             "user_id": order.user_id,
#             "total_price": order.total_price,
#             "payment_status": order.payment_status,
#             "shipment_status": order.shipment_status,
#             "transaction_id": order.transaction_id,
#             "tracking_id": order.tracking_id,
#             "created_at": order.created_at,
#             "updated_at": order.updated_at,
#         }
#         for order in orders
#     ]


@router.get("/orders-all", response_model=list[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Fetch all orders (Admin Only).
    """
    # Decode the JWT token to verify if the user is an admin (or any other role you want to check)
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_id = token_data["id"]
    user_role = token_data.get("role", None)

    # Check if the user is an admin (you can add more role checks here)
    if user_role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access all orders.",
        )

    # Fetch all orders from the database
    orders = get_all_orders(db)

    # Filter orders where the payment_status is "Paid"
    paid_orders = [
        {
            "id": order.id,
            "user_id": order.user_id,
            "total_price": order.total_price,
            "payment_status": order.payment_status,
            "shipment_status": order.shipment_status,
            "transaction_id": order.transaction_id,
            "tracking_id": order.tracking_id,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
        }
        for order in orders if order.payment_status == "Paid"
    ]

    return paid_orders

from sqlalchemy.orm import Session
from app.models import Order, OrderItem
from app.schemas import OrderCreate, OrderItemCreate

# def create_order(db: Session, user_id: int, order_data: OrderCreate, cart_items: list):
#     """
#     Create a new order and initialize the fields.
#     """
#     order = Order(
#         user_id=user_id,
#         total_price=order_data.total_price,
#         payment_status=None,  # Default to NULL
#         shipment_status=None,  # Default to NULL
#         tracking_id=None,  # Default to NULL
#     )
#     db.add(order)
#     db.commit()
#     db.refresh(order)

#     # Add cart items as order items
#     for item in cart_items:
#         order_item = OrderItem(
#             order_id=order.id,
#             product_id=item.product_id,
#             quantity=item.quantity,
#             price=item.product.price_after_discount,
#         )
#         db.add(order_item)

#     # Clear the cart
#     for item in cart_items:
#         db.delete(item)

#     db.commit()
#     return order


def create_order(db: Session, user_id: int, order_data: OrderCreate, cart_items: list):
   pass

def get_orders_by_user(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()




def get_all_orders(db: Session):
   
   return db.query(Order).all()
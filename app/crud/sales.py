from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Order, OrderItem, Product
import logging
from fastapi import Query
from datetime import date

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Testing sqlalchemy.func: {func}")


def get_total_revenue(db: Session):
    try:
        # Get all orders
        all_orders = db.query(Order.id, Order.total_price, Order.payment_status).all()
        logger.debug(f"ALL ORDERS (Unfiltered): {all_orders}")

        # Get only 'Paid' orders for revenue
        revenue = db.query(func.sum(Order.total_price)).filter(Order.payment_status == "Paid").scalar()
        
        logger.debug(f"Total revenue fetched: {revenue}")
        return revenue if revenue else 0
    except Exception as e:
        logger.error(f"Error fetching total revenue: {e}")
        return None



def get_monthly_revenue(db: Session, year: int):
    try:
        # Get all orders in the system before filtering
        all_orders = db.query(Order.id, Order.total_price, Order.payment_status, Order.created_at).all()
        logger.debug(f"ALL ORDERS (Unfiltered for {year}): {all_orders}")

        # Get revenue grouped by month
        results = db.query(
            extract("month", Order.created_at).label("month"),
            func.sum(Order.total_price).label("total_revenue")
        ).filter(
            Order.payment_status == "Paid",
            extract("year", Order.created_at) == year
        ).group_by("month").order_by("month").all()

        logger.debug(f"Monthly revenue data for {year}: {results}")

        return [{"month": result[0], "total_revenue": result[1]} for result in results] if results else []
    except Exception as e:
        logger.error(f"Error fetching monthly revenue for {year}: {e}")
        return None



def get_best_performing_products(db: Session, limit=10):
    try:
        # Get all order items before filtering
        all_order_items = db.query(OrderItem.id, OrderItem.product_id, OrderItem.quantity, OrderItem.price).all()
        logger.debug(f"ALL ORDER ITEMS (Unfiltered): {all_order_items}")

        # Get product sales data
        results = db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.price * OrderItem.quantity).label("total_revenue"),
            func.avg(OrderItem.price).label("average_price")
        ).join(OrderItem, OrderItem.product_id == Product.id)\
         .join(Order, Order.id == OrderItem.order_id)\
         .filter(Order.payment_status == "Paid")\
         .group_by(Product.id, Product.name)\
         .order_by(func.sum(OrderItem.quantity).desc())\
         .limit(limit).all()

        logger.debug(f"Best performing products: {results}")

        return [{"id": r[0], "name": r[1], "units_sold": r[2], "total_revenue": r[3], "average_price": r[4]} for r in results]
    except Exception as e:
        logger.error(f"Error fetching best-performing products: {e}")
        return None




def get_daily_sales_trend(
    db: Session, 
    start_date: date = Query(..., description="Start date in YYYY-MM-DD format"), 
    end_date: date = Query(..., description="End date in YYYY-MM-DD format")
):
    try:
        # Get all orders before filtering
        all_orders = db.query(Order.id, Order.total_price, Order.payment_status, Order.created_at).all()
        logger.debug(f"ALL ORDERS (Unfiltered from {start_date} to {end_date}): {all_orders}")

        results = db.query(
            func.date(Order.created_at).label("date"),
            func.sum(Order.total_price).label("daily_revenue"),
            func.count(Order.id).label("orders_count")
        ).filter(
            Order.payment_status == "Paid",
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).group_by(func.date(Order.created_at)).order_by("date").all()

        logger.debug(f"Daily sales trend: {results}")

        return [{"date": r[0], "daily_revenue": r[1], "orders_count": r[2]} for r in results]
    except Exception as e:
        logger.error(f"Error fetching daily sales trend: {e}")
        return None



def get_popular_products(db: Session, limit=10):
    from app.models import Wishlist, Cart
    try:
        # Get all products before filtering
        all_products = db.query(Product.id, Product.name).all()
        logger.debug(f"ALL PRODUCTS (Unfiltered): {all_products}")

        # Get wishlist popularity
        wishlist_popularity = db.query(
            Product.id,
            Product.name,
            func.coalesce(func.count(Wishlist.product_id), 0).label("wishlist_count")  # Default 0 if no data
        ).outerjoin(Wishlist, Wishlist.product_id == Product.id)\
        .group_by(Product.id, Product.name)\
        .order_by(func.count(Wishlist.product_id).desc())\
        .limit(limit).all()

        logger.debug(f"Wishlist popularity: {wishlist_popularity}")

        # Get cart popularity
        cart_popularity = db.query(
            Product.id,
            Product.name,
            func.count(Cart.product_id).label("cart_count")
        ).join(Cart, Cart.product_id == Product.id)\
        .group_by(Product.id, Product.name)\
        .order_by(func.count(Cart.product_id).desc())\
        .limit(limit).all()

        logger.debug(f"Cart popularity: {cart_popularity}")

        # Combine results manually
        popularity_dict = {}

        for item in wishlist_popularity:
            popularity_dict[item[0]] = {
                "id": item[0],
                "name": item[1],
                "wishlist_count": item[2],
                "cart_count": 0  # Default value
            }

        for item in cart_popularity:
            if item[0] in popularity_dict:
                popularity_dict[item[0]]["cart_count"] = item[2]
            else:
                popularity_dict[item[0]] = {
                    "id": item[0],
                    "name": item[1],
                    "wishlist_count": 0,
                    "cart_count": item[2]
                }

        final_results = sorted(popularity_dict.values(), key=lambda x: x["wishlist_count"], reverse=True)

        # Return top N products or default products if empty
        return final_results[:limit] if final_results else all_products[:limit]
    except Exception as e:
        logger.error(f"Error fetching popular products: {e}")
        return None

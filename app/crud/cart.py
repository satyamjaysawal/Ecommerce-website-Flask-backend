from sqlalchemy.orm import Session
from app.models import Cart, Wishlist, Product
from app.schemas import CartCreate, WishlistCreate, CartListResponse, WishlistResponse, ProductResponse, CartResponse
from fastapi import HTTPException
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def get_cart_items(db: Session, user_id: int) -> CartListResponse:
    """
    Retrieve all cart items for a user, fetch product details, and calculate total cart amount.
    """
    cart_items = db.query(Cart).filter(Cart.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=404, detail="Cart is empty.")

    result = []
    total_amount = 0  # Total cart amount

    for item in cart_items:
        print(f"Processing Cart Item ID: {item.id}, Product ID: {item.product_id}, Quantity: {item.quantity}")
        
        # Fetch product details
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found.")

        # Calculate item total price
        item_total_price = product.price_after_discount * item.quantity
        total_amount += item_total_price

        # Convert timestamps to IST
        created_at_ist = product.created_at.astimezone(IST).isoformat() if product.created_at else None
        updated_at_ist = product.updated_at.astimezone(IST).isoformat() if product.updated_at else None

        # Product response data
        product_data = ProductResponse(
            id=product.id, name=product.name, description=product.description,
            price_before_discount=product.price_before_discount, price_after_discount=product.price_after_discount,
            discount_percentage=product.discount_percentage, category=product.category, image_url=product.image_url,
            stock_remaining=product.stock_remaining, product_rating=product.product_rating, is_active=product.is_active,
            created_at=created_at_ist, updated_at=updated_at_ist
        )

        result.append(CartResponse(
            id=item.id, user_id=item.user_id, product_id=item.product_id, 
            quantity=item.quantity, product=product_data
        ))

    return CartListResponse(cart_items=result, total_amount=total_amount)


def get_wishlist_items(db: Session, user_id: int):
    """
    Retrieve all items in the user's wishlist.
    """
    wishlist_items = db.query(Wishlist).filter(Wishlist.user_id == user_id).all()
    if not wishlist_items:
        raise HTTPException(status_code=200, detail="Your wishlist is empty.")  # Changed 404 to 200

    result = []

    for item in wishlist_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with ID {item.product_id} not found.")

        # Convert timestamps to IST
        created_at_ist = product.created_at.astimezone(IST).isoformat() if product.created_at else None
        updated_at_ist = product.updated_at.astimezone(IST).isoformat() if product.updated_at else None

        product_data = ProductResponse(
            id=product.id, name=product.name, description=product.description,
            price_before_discount=product.price_before_discount, price_after_discount=product.price_after_discount,
            discount_percentage=product.discount_percentage, category=product.category, image_url=product.image_url,
            stock_remaining=product.stock_remaining, product_rating=product.product_rating, is_active=product.is_active,
            created_at=created_at_ist, updated_at=updated_at_ist
        )

        result.append(WishlistResponse(id=item.id, user_id=item.user_id, product_id=item.product_id, product=product_data))

    return result


def add_to_cart(db: Session, user_id: int, cart_data: CartCreate):
    """
    Add a product to the cart.
    """
    product = db.query(Product).filter(Product.id == cart_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if cart_data.quantity > product.stock_remaining:
        raise HTTPException(status_code=400, detail=f"Only {product.stock_remaining} units available")

    cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == cart_data.product_id).first()
    if cart_item:
        raise HTTPException(status_code=400, detail="Product already in cart. Update quantity instead.")

    cart_item = Cart(user_id=user_id, **cart_data.dict())
    db.add(cart_item)
    product.stock_remaining -= cart_data.quantity
    db.commit()
    db.refresh(cart_item)

    return cart_item

def remove_from_cart(db: Session, user_id: int, product_id: int):
    """
    Remove a product from the user's cart.
    """
    cart_item = db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")

    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.stock_remaining += cart_item.quantity

    db.delete(cart_item)
    db.commit()
    return {"message": "Item removed from cart"}
    
def add_to_wishlist(db: Session, user_id: int, wishlist_data: WishlistCreate):
    """
    Add a product to the user's wishlist.
    """
    product = db.query(Product).filter(Product.id == wishlist_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    wishlist_item = db.query(Wishlist).filter(Wishlist.user_id == user_id, Wishlist.product_id == wishlist_data.product_id).first()
    if wishlist_item:
        raise HTTPException(status_code=400, detail="Product already exists in your wishlist")
    wishlist_item = Wishlist(user_id=user_id, **wishlist_data.dict())
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

def remove_from_wishlist(db: Session, user_id: int, product_id: int):
    """
    Remove a specific product from the user's wishlist.
    """
    wishlist_item = db.query(Wishlist).filter(Wishlist.user_id == user_id, Wishlist.product_id == product_id).first()
    if not wishlist_item:
        raise HTTPException(status_code=404, detail="Item not found in wishlist")
    db.delete(wishlist_item)
    db.commit()
    return {"message": "Item removed from wishlist"}

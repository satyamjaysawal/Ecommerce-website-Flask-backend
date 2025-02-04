from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz 
from app.database import Base

IST = pytz.timezone("Asia/Kolkata")
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="customer")
    # Products relationship with cascade delete
    products = relationship("Product", back_populates="vendor", cascade="all, delete")
    # Cart and Wishlist relationships
    cart_items = relationship("Cart", back_populates="user", cascade="all, delete")
    wishlist_items = relationship("Wishlist", back_populates="user", cascade="all, delete")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    price_before_discount = Column(Float) 
    price_after_discount = Column(Float)  
    expenditure_cost_inr = Column(Float)
    discount_percentage = Column(Float)
    profit_per_item_inr = Column(Float)  
    total_stock = Column(Integer)
    stock_remaining = Column(Integer)
    category = Column(String)
    image_url = Column(String)
    vendor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True) 
    deleted_at = Column(DateTime, nullable=True) 
    product_rating = Column(Float, default=0.0) 
    # ✅ Add created_at and updated_at in IST
    created_at = Column(DateTime, default=lambda: datetime.now(IST))
    updated_at = Column(DateTime, default=lambda: datetime.now(IST), onupdate=lambda: datetime.now(IST))
    # Relationships
    vendor = relationship("User", back_populates="products")
    cart_items = relationship("Cart", back_populates="product", cascade="all, delete")
    wishlist_items = relationship("Wishlist", back_populates="product", cascade="all, delete")
    reviews = relationship("Review", back_populates="product", cascade="all, delete")  

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    rating = Column(Float, nullable=False)  # Rating between 0.0 and 5.0
    comment = Column(String, nullable=True)  # Optional review comment
    created_at = Column(DateTime, default=lambda: datetime.now(IST))  # Timestamp in IST

    # Relationships
    user = relationship("User")
    product = relationship("Product", back_populates="reviews")

class Cart(Base):
    __tablename__ = "carts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    quantity = Column(Integer, nullable=False, default=1)
    # Relationships
    user = relationship("User", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class Wishlist(Base):
    __tablename__ = "wishlists"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"))
    # Relationships
    user = relationship("User", back_populates="wishlist_items")
    product = relationship("Product", back_populates="wishlist_items")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    total_price = Column(Float, nullable=False)
    status = Column(String, default="Pending") 
    payment_status = Column(String, nullable=True, default=None)  
    shipment_status = Column(String, nullable=True, default=None) 
    transaction_id = Column(String, nullable=True, unique=True)  
    tracking_id = Column(String, nullable=True, default=None) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_items"  

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"))
    quantity = Column(Integer, nullable=False)
    price = Column(Float) 

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product")




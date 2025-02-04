from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    phone_number: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone_number: str
    role: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    expenditure_cost_inr: float
    discount_percentage: float
    total_stock: int
    category: str
    image_url: Optional[str] = None
    vendor_id: Optional[int] = None

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price_before_discount: float
    price_after_discount: float
    discount_percentage: float
    category: str
    image_url: str
    stock_remaining: int
    is_active: bool
    product_rating: float
    created_at: datetime
    updated_at: datetime
    expenditure_cost_inr: Optional[float] = None
    total_stock: Optional[int] = None
    vendor_id: Optional[int] = None
    profit_per_item_inr: Optional[float] = None

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    product_id: int
    rating: float
    comment: Optional[str] = None

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    rating: float
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProductReviewsResponse(BaseModel):
    product_id: int
    weighted_average_rating: float
    reviews: list[ReviewResponse]

    class Config:
        from_attributes = True
class ProductWithReviewsResponse(BaseModel):
    id: int
    name: str
    category: str
    price_before_discount: float
    price_after_discount: float
    stock_remaining: int
    product_rating: float
    reviews: List[ReviewResponse]

    class Config:
        from_attributes = True
class PurchaseProduct(BaseModel):
    quantity: int

class CartCreate(BaseModel):
    product_id: int
    quantity: int

class CartResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    product: ProductResponse

    class Config:
        from_attributes = True

class CartListResponse(BaseModel):
    cart_items: List[CartResponse]
    total_amount: float

    class Config:
        from_attributes = True

class WishlistCreate(BaseModel):
    product_id: int

class WishlistResponse(BaseModel):
    id: int
    user_id: int
    product_id: int
    product: ProductResponse  

    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    total_price: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    payment_status: Optional[str] = None
    transaction_id: Optional[str]
    shipment_status: Optional[str] = None
    tracking_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: Optional[List[OrderItemResponse]] = None  

    class Config:
        from_attributes = True

class ShipmentUpdate(BaseModel):
    shipment_status: str
    tracking_id: str

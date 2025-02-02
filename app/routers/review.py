from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ReviewCreate, ReviewResponse, ProductReviewsResponse
from app.crud.review import add_review, get_reviews_by_product, update_product_rating
from app.crud.product import get_product_by_id
from app.utils import decode_access_token
import pytz
from datetime import datetime
from app.models import Review
# ✅ Define IST timezone globally
IST = pytz.timezone("Asia/Kolkata")

router = APIRouter()

@router.post("/reviews", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),  # ✅ Header can be None
):
    """
    Create a review for a product.
    - **Only customers can add reviews**.
    - Users **cannot review an inactive product**.
    - Users **cannot review the same product more than once**.
    """
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token_data = decode_access_token(authorization.split("Bearer ")[-1])
    except Exception as e:
        print(f"❌ [ERROR] Token decoding failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication token.")

    user_id = token_data["id"]
    user_role = token_data["role"]

    # ✅ Only customers can add reviews
    if user_role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can add reviews.")

    # ✅ Fetch product details
    product = get_product_by_id(db, review.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # ✅ Prevent reviewing inactive products
    if not product.is_active:
        raise HTTPException(status_code=403, detail="Cannot review an inactive product.")

    # ✅ Check if the user has already reviewed this product
    existing_review = db.query(Review).filter(
        Review.user_id == user_id, Review.product_id == review.product_id
    ).first()

    if existing_review:
        raise HTTPException(status_code=400, detail="You have already reviewed this product.")

    # ✅ Add the new review
    new_review = add_review(db, user_id, review.product_id, review.rating, review.comment)

    return new_review


@router.get("/products/{product_id}/reviews", response_model=ProductReviewsResponse)
def list_reviews(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Retrieve all reviews for a specific product.
    - Customers can **only view reviews for active products**.
    - Admins & Vendors can **view all reviews**.
    - Reviews are **sorted by newest first**.
    - Uses **Weighted Average Approach** for product rating calculation.
    """
    print(f"🔍 [DEBUG] Fetching reviews for product ID: {product_id}")

    # ✅ Decode JWT token
    user_role = "guest"
    if authorization:
        token_data = decode_access_token(authorization.split("Bearer ")[-1])
        user_role = token_data["role"]

    print(f"✅ [DEBUG] User Role: {user_role} fetching reviews.")

    # ✅ Fetch product details
    product = get_product_by_id(db, product_id)
    if not product:
        print("❌ [ERROR] Product not found.")
        raise HTTPException(status_code=404, detail="Product not found.")

    # ✅ Restrict customers from viewing inactive product reviews
    if user_role == "customer" and not product.is_active:
        print("❌ [ERROR] Customer cannot view reviews for an inactive product.")
        raise HTTPException(status_code=403, detail="This product is not available.")

    # ✅ Fetch reviews sorted by newest first
    reviews = get_reviews_by_product(db, product_id)
    if not reviews:
        print(f"❌ [ERROR] No reviews found for product ID {product_id}")
        raise HTTPException(status_code=404, detail="No reviews found for this product.")

    # ✅ Convert timestamps to IST
    for review in reviews:
        if review.created_at:
            review.created_at = review.created_at.astimezone(IST)  # ✅ Convert timestamps to IST

    # ✅ Calculate weighted average rating
    weighted_avg_rating = update_product_rating(db, product_id)
    print(f"✅ [DEBUG] Weighted Average Rating: {weighted_avg_rating}")

    return {
        "product_id": product_id,
        "weighted_average_rating": weighted_avg_rating,
        "reviews": reviews  # ✅ Ensure this matches the expected response model
    }

import pytz
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ReviewCreate, ReviewResponse, ProductReviewsResponse
from app.crud.product import get_product_by_id
from app.crud.review import create_review, get_reviews_for_product
from app.utils import decode_access_token
from app.models import Review

# IST timezone
IST = pytz.timezone("Asia/Kolkata")

router = APIRouter()

@router.get("/products/{product_id}/reviews", response_model=ProductReviewsResponse)
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Get all reviews for a product.
    - Returns a list of reviews with the weighted average rating.
    """
    print(f"Fetching reviews for product ID: {product_id}")  # Debug: product_id being fetched

    # Fetch product to ensure it exists
    product = get_product_by_id(db, product_id)
    if not product:
        print(f"Product with ID {product_id} not found!")  # Debug: product not found
        raise HTTPException(status_code=404, detail="Product not found.")

    # Fetch reviews for the product
    reviews = get_reviews_for_product(db, product_id)
    print(f"Fetched {len(reviews)} reviews for product ID: {product_id}")  # Debug: number of reviews fetched
    
    # Calculate weighted average rating
    if reviews:
        total_rating = sum([review.rating for review in reviews])
        weighted_avg_rating = total_rating / len(reviews)
        print(f"Calculated weighted average rating: {weighted_avg_rating}")  # Debug: average rating
    else:
        weighted_avg_rating = 0.0
        print("No reviews found, setting weighted average rating to 0.0")  # Debug: no reviews found

    return ProductReviewsResponse(
        product_id=product_id,
        weighted_average_rating=weighted_avg_rating,
        reviews=[ReviewResponse.from_orm(review) for review in reviews]
    )


@router.post("/products/{product_id}/reviews", response_model=ReviewResponse)
def add_product_review(
    product_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Add a review for a product (only for customers).
    - Requires user to be authenticated with role "customer".
    """
    print(f"Adding review for product ID: {product_id}")  # Debug: product_id for the review

    # Decode JWT token and get user data
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_role = token_data.get("role")
    user_id = token_data.get("id")

    print(f"User role: {user_role}, User ID: {user_id}")  # Debug: role and ID of the user

    if user_role != "customer":
        print("Permission denied. Only customers can leave reviews.")  # Debug: permission check
        raise HTTPException(status_code=403, detail="Permission denied. Only customers can leave reviews.")

    # Fetch product to ensure it exists
    product = get_product_by_id(db, product_id)
    if not product:
        print(f"Product with ID {product_id} not found!")  # Debug: product not found
        raise HTTPException(status_code=404, detail="Product not found.")

    # Create and save the review
    review = create_review(db, user_id, product_id, review_data)
    print(f"Review created: {review.id}")  # Debug: review ID of the created review

    return ReviewResponse.from_orm(review)

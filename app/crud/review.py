import pytz
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Product, Review  # Make sure Review is imported
from app.schemas import ReviewCreate

# IST timezone
IST = pytz.timezone("Asia/Kolkata")

def create_review(db: Session, user_id: int, product_id: int, review_data: ReviewCreate):
    """
    Create a new review for a product by a customer.
    """
    # Create a new review instance with timestamp in IST
    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=review_data.rating,
        comment=review_data.comment,
        created_at=datetime.now(IST),  # Use IST for timestamp
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

def get_reviews_for_product(db: Session, product_id: int):
    """
    Fetch all reviews for a product.
    """
    return db.query(Review).filter(Review.product_id == product_id).all()


from sqlalchemy.orm import Session
from app.models import Review, Product
from app.schemas import ReviewResponse
from datetime import datetime
import pytz

# ✅ Define IST timezone globally
IST = pytz.timezone("Asia/Kolkata")

def add_review(db: Session, user_id: int, product_id: int, rating: float, comment: str = None):
    """
    Add a new review and update the product's weighted average rating.
    """
    current_time_ist = datetime.now().astimezone(IST)  # ✅ Convert timestamp to IST

    new_review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
        created_at=current_time_ist  # ✅ Store IST timestamp
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    # ✅ Update product rating using weighted average
    update_product_rating(db, product_id)

    return new_review

def get_reviews_by_product(db: Session, product_id: int):
    """
    Retrieve all reviews for a given product, sorted by newest first.
    """
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()

def update_product_rating(db: Session, product_id: int):
    """
    Update the product's rating using a weighted average approach.
    """
    reviews = db.query(Review).filter(Review.product_id == product_id).all()

    if not reviews:
        return 0.0  # No reviews, set rating to 0.0

    total_weight = 0
    weighted_sum = 0

    for review in reviews:
        weight = 1  # Default weight
        if review.rating >= 4:
            weight = 2  # Higher weight for positive reviews

        weighted_sum += review.rating * weight
        total_weight += weight

    weighted_avg = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0

    # ✅ Update the product rating
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.product_rating = weighted_avg
        db.commit()

    return weighted_avg

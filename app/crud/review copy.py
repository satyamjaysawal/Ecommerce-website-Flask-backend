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
    - **user_id**: ID of the user submitting the review.
    - **product_id**: ID of the product being reviewed.
    - **rating**: The rating given by the user (e.g., 1 to 5).
    - **comment**: Optional text comment provided by the user for the review.
    """

    # Step 1: Get the current time in IST
    current_time_ist = datetime.now().astimezone(IST)  # Convert timestamp to IST

    # Step 2: Create a new review instance
    new_review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=rating,
        comment=comment,
        created_at=current_time_ist  # Store the IST timestamp for the review
    )

    # Step 3: Add the review to the session and commit to the database
    db.add(new_review)
    db.commit()
    db.refresh(new_review)  # Refresh the instance to get the latest state (e.g., auto-generated fields like ID)

    # Step 4: Update the product's rating using the weighted average approach
    update_product_rating(db, product_id)

    return new_review  # Return the new review object created

def get_reviews_by_product(db: Session, product_id: int):
    """
    Retrieve all reviews for a given product, sorted by newest first.
    """
    return db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()

def update_product_rating(db: Session, product_id: int):
    """
    Update the product's rating using a weighted average approach.
    The weighted average is calculated based on review ratings, where positive reviews have a higher weight.
    """
    reviews = db.query(Review).filter(Review.product_id == product_id).all()

    if not reviews:
        return 0.0  # No reviews, set rating to 0.0

    total_weight = 0
    weighted_sum = 0

    for review in reviews:
        weight = 1  # Default weight
        if review.rating >= 4:
            weight = 2  # Higher weight for positive reviews (rating 4 or above)

        weighted_sum += review.rating * weight
        total_weight += weight

    weighted_avg = round(weighted_sum / total_weight, 2) if total_weight > 0 else 0.0

    # Update the product's rating in the database
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.product_rating = weighted_avg
        db.commit()

    return weighted_avg  # Return the updated weighted average rating

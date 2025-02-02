from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CartCreate, CartResponse, WishlistCreate, WishlistResponse, CartListResponse
from app.crud.cart import (
    add_to_cart,
    get_cart_items,
    remove_from_cart,
    add_to_wishlist,
    get_wishlist_items,
    remove_from_wishlist,
)
from app.utils import decode_access_token
router = APIRouter()
@router.post("/cart", response_model=CartResponse)
def add_item_to_cart(
    cart_data: CartCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Add a product to the cart for the logged-in customer.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can add to cart")
    return add_to_cart(db, token_data["id"], cart_data)
@router.get("/cart", response_model=CartListResponse)  # Correct response model
def view_cart(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    View all cart items for the logged-in customer.
    """
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Authorization header must start with 'Bearer '")
    
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can view cart")

    return get_cart_items(db, token_data["id"])  # Correct return structure

@router.delete("/cart/{product_id}")
def delete_cart_item(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Remove a product from the cart for the logged-in customer.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can remove items from cart")
    return remove_from_cart(db, token_data["id"], product_id)
@router.post("/wishlist", response_model=WishlistResponse)
def add_item_to_wishlist(
    wishlist_data: WishlistCreate,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Add a product to the wishlist for the logged-in customer.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can add to wishlist")
    return add_to_wishlist(db, token_data["id"], wishlist_data)
@router.get("/wishlist", response_model=list[WishlistResponse])
def view_wishlist(db: Session = Depends(get_db), authorization: str = Header(None)):
    """
    View all wishlist items for the logged-in customer.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can view wishlist")
    return get_wishlist_items(db, token_data["id"])

@router.delete("/wishlist/{product_id}")
def delete_wishlist_item(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Remove a product from the wishlist for the logged-in customer.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "customer":
        raise HTTPException(status_code=403, detail="Only customers can remove items from wishlist")
    return remove_from_wishlist(db, token_data["id"], product_id)

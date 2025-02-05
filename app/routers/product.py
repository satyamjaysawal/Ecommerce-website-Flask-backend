from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from app.database import get_db
from typing import List
from app.schemas import ProductCreate, ProductResponse, ProductWithReviewsResponse
from app.crud.product import (
  get_all_products_with_reviews , add_product, get_products, get_product_by_id, update_product, soft_delete_product, search_products_by_name, get_products_by_category, get_products_by_rating, import_products
)
from app.utils import decode_access_token
import pytz
from app.models import Review
IST = pytz.timezone("Asia/Kolkata")
router = APIRouter()


@router.get("/admin-product-analysis", response_model=list[ProductWithReviewsResponse])
def get_products_for_analysis(
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    print("Received request for /admin-product-analysis")  # Debugging log
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    print("Decoded Token Data:", token_data)  # Debugging log
    
    if token_data["role"] != "admin":
        print("Permission denied. Admins only.")  # Debugging log
        raise HTTPException(status_code=403, detail="Permission denied. Admins only.")
    
    # Fetch products along with reviews and ratings for analysis
    products = get_all_products_with_reviews(db)
    print("Fetched Products for Analysis:", products)  # Debugging log
    
    if not products:
        raise HTTPException(status_code=404, detail="No products found for analysis.")
    
    return products





@router.post("/products", response_model=ProductResponse)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db), 
    authorization: str = Header(None)
):
    """Add a new product (Admin/Vendor only)."""
    token_data = decode_access_token(authorization.split("Bearer ")[-1])

    if token_data["role"] not in ["admin", "vendor"]:
        raise HTTPException(status_code=403, detail="Permission denied.")

    vendor_id = token_data["id"] if token_data["role"] == "vendor" else product.vendor_id
    return add_product(db, product, vendor_id)


@router.get("/products/search", response_model=list[dict])
def search_products_by_name_route(
    name: str = Query(..., min_length=1, description="Enter keyword to search in product names"),  # ✅ Enforce minimum length
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to fetch"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Search products by name where any part of the name matches the input keyword.
    - **Customers** see only active products.
    - **Admins/Vendors** see all products.
    - Supports **pagination** (`skip` & `limit`).
    """
    print(f"🔍 [DEBUG] Received request to search products with name: '{name}'")
    print(f"🔍 [DEBUG] Pagination - Skip: {skip}, Limit: {limit}")

    # ✅ Ensure name is not empty
    if not name.strip():
        print("❌ [ERROR] Empty search term provided")
        raise HTTPException(status_code=400, detail="Search term (name) cannot be empty.")

    # ✅ Handle authentication safely
    user_role = "guest"  # Default role for unauthenticated users
    if authorization:
        parts = authorization.split("Bearer ")
        if len(parts) == 2:
            token = parts[1]
            try:
                token_data = decode_access_token(token)
                user_role = token_data.get("role", "guest")
            except Exception as e:
                print(f"❌ [ERROR] Token decoding failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid authentication token.")

    print(f"✅ [DEBUG] User role: {user_role}")

    # ✅ Fetch products based on role & search query
    products = search_products_by_name(db, name.lower(), user_role, skip, limit)

    if not products:
        print(f"❌ [ERROR] No products found for search query: {name}")
        raise HTTPException(status_code=404, detail="No products found matching the search criteria.")

    # ✅ Convert timestamps to IST
    product_list = []
    for product in products:
        try:
            created_at_ist = product.created_at.astimezone(IST).isoformat() if product.created_at else None
            updated_at_ist = product.updated_at.astimezone(IST).isoformat() if product.updated_at else None

            product_data = {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price_before_discount": product.price_before_discount,
                "price_after_discount": product.price_after_discount,
                "discount_percentage": product.discount_percentage,
                "category": product.category,
                "image_url": product.image_url,
                "stock_remaining": product.stock_remaining,
                "is_active": product.is_active,
                "product_rating": product.product_rating,
                "created_at": created_at_ist,
                "updated_at": updated_at_ist,
            }

            # ✅ Include extra fields for admin and vendors
            if user_role in ["admin", "vendor"]:
                product_data.update({
                    "expenditure_cost_inr": product.expenditure_cost_inr,
                    "total_stock": product.total_stock,
                    "profit_per_item_inr": product.profit_per_item_inr,
                    "vendor_id": product.vendor_id,
                })

            product_list.append(product_data)

        except Exception as e:
            print(f"❌ [ERROR] Failed to process product {product.id}: {e}")

    print(f"✅ [SUCCESS] Returning {len(product_list)} products.")
    return product_list

@router.get("/products/category", response_model=list[dict])
def filter_products_by_category(
    category: str = Query(..., min_length=2, description="Category name to filter products"),  # ✅ Ensure valid string
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to fetch"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Fetch products by category.
    - Customers see **only active products**.
    - Admins & Vendors see **all products**.
    - Supports **pagination** (`skip` & `limit`).
    """
    print(f"🔍 [DEBUG] Received category: {category}")  # 🔍 Check what category is being received

    # ✅ Ensure category is not empty
    if not category or category.strip() == "":
        print("❌ [ERROR] Category is empty.")
        raise HTTPException(status_code=400, detail="Category cannot be empty.")

    # ✅ Handle authentication safely
    user_role = "guest"
    if authorization:
        parts = authorization.split("Bearer ")
        if len(parts) == 2:
            token = parts[1]
            try:
                token_data = decode_access_token(token)
                user_role = token_data.get("role", "guest")
            except Exception as e:
                print(f"❌ [ERROR] Token decoding failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid authentication token.")

    print(f"✅ [DEBUG] User Role: {user_role} is filtering products by category.")

    # ✅ Fetch products based on category
    products = get_products_by_category(db, category, user_role, skip, limit)

    if not products:
        print(f"❌ [ERROR] No products found in category: {category}")
        raise HTTPException(status_code=404, detail=f"No products found in category: {category}")

    # ✅ Convert timestamps to IST
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_before_discount": product.price_before_discount,
            "price_after_discount": product.price_after_discount,
            "discount_percentage": product.discount_percentage,
            "category": product.category,
            "image_url": product.image_url,
            "stock_remaining": product.stock_remaining,
            "is_active": product.is_active,
            "product_rating": product.product_rating,
            "created_at": product.created_at.astimezone(IST).isoformat() if product.created_at else None,
            "updated_at": product.updated_at.astimezone(IST).isoformat() if product.updated_at else None,
            **(
                {  # ✅ Include extra fields for admin and vendors
                    "expenditure_cost_inr": product.expenditure_cost_inr,
                    "total_stock": product.total_stock,
                    "profit_per_item_inr": product.profit_per_item_inr,
                    "vendor_id": product.vendor_id,
                } if user_role in ["admin", "vendor"] else {}
            )
        }
        for product in products
    ]

    print(f"✅ [SUCCESS] Returning {len(product_list)} products.")
    return product_list


@router.get("/products/rating", response_model=list[dict])
def filter_products_by_rating(
    min_rating: float = Query(0, ge=0, le=5, description="Minimum product rating (0-5)"),
    max_rating: float = Query(5, ge=0, le=5, description="Maximum product rating (0-5)"),
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to fetch"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Fetch products by rating range.
    - Customers see **only active products**.
    - Admins & Vendors see **all products**.
    - Supports **pagination** (`skip` & `limit`).
    - Ensures **valid rating input (0-5 range)**.
    """
    print(f"🔍 [DEBUG] Fetching products with rating between {min_rating} - {max_rating}")

    # ✅ Handle authentication safely
    user_role = "guest"
    if authorization:
        parts = authorization.split("Bearer ")
        if len(parts) == 2:
            token = parts[1]
            try:
                token_data = decode_access_token(token)
                user_role = token_data.get("role", "guest")
            except Exception as e:
                print(f"❌ [ERROR] Token decoding failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid authentication token.")

    print(f"✅ [DEBUG] User Role: {user_role} filtering products by rating.")

    # ✅ Fetch products based on rating range
    products = get_products_by_rating(db, min_rating, max_rating, user_role, skip, limit)

    if not products:
        print(f"❌ [ERROR] No products found in rating range {min_rating} - {max_rating}")
        raise HTTPException(status_code=404, detail=f"No products found with rating between {min_rating} and {max_rating}")

    # ✅ Convert timestamps to IST
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_before_discount": product.price_before_discount,
            "price_after_discount": product.price_after_discount,
            "discount_percentage": product.discount_percentage,
            "category": product.category,
            "image_url": product.image_url,
            "stock_remaining": product.stock_remaining,
            "is_active": product.is_active,
            "product_rating": product.product_rating,
            "created_at": product.created_at.astimezone(IST).isoformat() if product.created_at else None,
            "updated_at": product.updated_at.astimezone(IST).isoformat() if product.updated_at else None,
            **(
                {  # ✅ Include extra fields for admin and vendors
                    "expenditure_cost_inr": product.expenditure_cost_inr,
                    "total_stock": product.total_stock,
                    "profit_per_item_inr": product.profit_per_item_inr,
                    "vendor_id": product.vendor_id,
                } if user_role in ["admin", "vendor"] else {}
            )
        }
        for product in products
    ]

    print(f"✅ [SUCCESS] Returning {len(product_list)} products.")
    return product_list











@router.get("/products", response_model=list[dict])
def list_all_products(
    skip: int = Query(0, ge=0, description="Number of products to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to fetch (max 100)"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    List all products with role-based filtering.
    - Customers see only active products.
    - Admins & vendors see all products.
    - Supports pagination with `skip` and `limit`.
    """
    print("🔄 [API CALL] Fetching products...")

    # ✅ Handle authentication (allow guest access)
    user_role = "guest"
    if authorization:
        try:
            token_data = decode_access_token(authorization.split("Bearer ")[-1])
            user_role = token_data.get("role")
        except Exception as e:
            print("❌ [ERROR] Token decoding failed:", e)
            raise HTTPException(status_code=401, detail="Invalid authentication token.")

    print(f"✅ [USER ROLE] {user_role} is accessing products.")

    # ✅ Fetch products based on user role
    products = get_products(db, user_role, skip, limit)

    if not products:
        raise HTTPException(status_code=404, detail="No products found.")

    # ✅ Convert timestamps to IST and prepare response
    product_list = []
    for product in products:
        created_at_ist = product.created_at.astimezone(IST).isoformat() if product.created_at else None
        updated_at_ist = product.updated_at.astimezone(IST).isoformat() if product.updated_at else None

        # ✅ Base product data (for all users)
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_before_discount": product.price_before_discount,
            "price_after_discount": product.price_after_discount,
            "discount_percentage": product.discount_percentage,
            "category": product.category,
            "image_url": product.image_url,
            "stock_remaining": product.stock_remaining,
            "is_active": product.is_active,
            "product_rating": product.product_rating,
            "created_at": created_at_ist,
            "updated_at": updated_at_ist,
        }

        # ✅ Include extra fields for admin and vendors
        if user_role in ["admin", "vendor"]:
            product_data.update({
                "expenditure_cost_inr": product.expenditure_cost_inr,
                "total_stock": product.total_stock,
                "profit_per_item_inr": product.profit_per_item_inr,
                "vendor_id": product.vendor_id,
            })

        product_list.append(product_data)

    print(f"✅ [SUCCESS] Returning {len(product_list)} products.")
    return product_list



#===========================================================#


# @router.get("/products/{product_id}", response_model=ProductResponse)
# def retrieve_product(
#     product_id: int,
#     db: Session = Depends(get_db),
#     authorization: str = Header(None),
# ):
#     """
#     Retrieve product details.
#     - Customers can only see active products.
#     - Admins & vendors can see all products.
#     - Converts timestamps to IST.
#     - Hides sensitive fields for non-admin/vendor users.
#     """
#     print(f"🔍 [API CALL] Fetching product ID: {product_id}")

#     # ✅ Default role for unauthenticated users
#     user_role = "guest"
#     if authorization:
#         try:
#             token_data = decode_access_token(authorization.split("Bearer ")[-1])
#             user_role = token_data["role"]
#             print(f"✅ [DEBUG] Token decoded, user role: {user_role}")
#         except Exception as e:
#             print(f"❌ [ERROR] Token decoding failed: {e}")
#             raise HTTPException(status_code=401, detail="Invalid authentication token.")

#     # ✅ Fetch product from the database
#     product = get_product_by_id(db, product_id)
#     if not product:
#         print(f"❌ [ERROR] Product with ID {product_id} not found.")
#         raise HTTPException(status_code=404, detail="Product not found.")

#     # ✅ Restrict customers from viewing inactive products
#     if user_role == "customer" and not product.is_active:
#         print(f"❌ [ERROR] Product {product_id} is inactive and cannot be viewed by customers.")
#         raise HTTPException(status_code=403, detail="This product is not available.")

#     # ✅ Convert timestamps to IST
#     created_at_ist = product.created_at.astimezone(IST) if product.created_at else None
#     updated_at_ist = product.updated_at.astimezone(IST) if product.updated_at else None

#     # ✅ Prepare base response data (shown to all users)
#     product_data = {
#         "id": product.id,
#         "name": product.name,
#         "description": product.description,
#         "price_before_discount": product.price_before_discount,
#         "price_after_discount": product.price_after_discount,
#         "discount_percentage": product.discount_percentage,
#         "category": product.category,
#         "image_url": product.image_url,
#         "stock_remaining": product.stock_remaining,
#         "is_active": product.is_active,
#         "product_rating": product.product_rating,
#         "created_at": created_at_ist,
#         "updated_at": updated_at_ist,
#     }

#     # ✅ Add extra fields only if user is admin/vendor
#     if user_role in ["admin", "vendor"]:
#         product_data.update({
#             "expenditure_cost_inr": product.expenditure_cost_inr,
#             "total_stock": product.total_stock,
#             "profit_per_item_inr": product.profit_per_item_inr,
#             "vendor_id": product.vendor_id,
#         })
#         print(f"✅ [DEBUG] Admin/Vendor product data: {product_data}")

#     print(f"✅ [SUCCESS] Returning product details: {product_data['name']}")
#     return product_data

# @router.get("/products/{product_id}", response_model=ProductResponse)
# def retrieve_product(
#     product_id: int,
#     db: Session = Depends(get_db),
#     authorization: str = Header(None),
# ):
#     print(f"🔍 [API CALL] Fetching product ID: {product_id}")
    
#     # Handle authorization and user roles
#     user_role = "guest"
#     if authorization:
#         try:
#             token_data = decode_access_token(authorization.split("Bearer ")[-1])
#             user_role = token_data["role"]
#             print(f"✅ [DEBUG] Token decoded, user role: {user_role}")
#         except Exception as e:
#             print(f"❌ [ERROR] Token decoding failed: {e}")
#             raise HTTPException(status_code=401, detail="Invalid authentication token.")

#     # Fetch product from DB
#     print(f"🔍 [DEBUG] Querying database for product with ID: {product_id}")
#     product = get_product_by_id(db, product_id)
#     print("====================]]]]",product)

#     if not product:
#         print(f"❌ [ERROR] Product with ID {product_id} not found.")
#         raise HTTPException(status_code=404, detail="Product not found.")

#     # Handle product visibility based on user role
#     if user_role == "customer" and not product.is_active:
#         print(f"❌ [ERROR] Product {product_id} is inactive and cannot be viewed by customers.")
#         raise HTTPException(status_code=403, detail="This product is not available.")
    
#     # Print product data before processing
#     print(f"🔍 [DEBUG] Product data fetched: {product.__dict__}")  # Print all attributes of the product object

#     # Convert timestamps to IST
#     created_at_ist = product.created_at.astimezone(IST) if product.created_at else None
#     updated_at_ist = product.updated_at.astimezone(IST) if product.updated_at else None

#     # Prepare the product data for response
#     print(f"🔍 [DEBUG] Preparing product data for response...")
#     product_data = {
#         "id": product.id,
#         "name": product.name,
#         "description": product.description,
#         "price_before_discount": product.price_before_discount or 0,  # Default to 0 if NULL
#         "price_after_discount": product.price_after_discount or 0,  # Default to 0 if NULL
#         "discount_percentage": product.discount_percentage or 0,  # Default to 0 if NULL
#         "category": product.category or "Uncategorized",  # Default if NULL
#         "image_url": product.image_url or "",  # Default empty string if NULL
#         "stock_remaining": product.stock_remaining or 0,  # Default to 0 if NULL
#         "is_active": product.is_active,
#         "product_rating": product.product_rating or 0,  # Default to 0 if NULL
#         "created_at": created_at_ist,
#         "updated_at": updated_at_ist,
#     }

#     # Add extra fields for admin/vendor role
#     if user_role in ["admin", "vendor"]:
#         product_data.update({
#             "expenditure_cost_inr": product.expenditure_cost_inr or 0,  # Handle NULL
#             "total_stock": product.total_stock or 0,  # Handle NULL
#             "profit_per_item_inr": product.profit_per_item_inr or 0,  # Handle NULL
#             "vendor_id": product.vendor_id or 0,  # Handle NULL
#         })
#         print(f"✅ [DEBUG] Admin/Vendor product data: {product_data}")

#     # Final response logging
#     print(f"✅ [SUCCESS] Returning product details: {product_data['name']}")

#     return product_data


# Assuming the necessary imports (like decode_access_token, get_db, etc.) are already in place

@router.get("/products/{product_id}", response_model=ProductResponse)
def retrieve_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    print(f"🔍 [API CALL] Fetching product ID: {product_id}")
    
    # Fetch product from DB
    product = get_product_by_id(db, product_id)
    print('=============== Product Data ===============')
    print(f"Product Object: {product}")  # Print the whole product object
    print(f"Product Attributes: {product.__dict__}")  # Print all the attributes of the product object
    print('--------------------------------------------')

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    # Prepare the product data for response
    product_data = {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price_before_discount": product.price_before_discount or 0,  # Default to 0 if NULL
        "price_after_discount": product.price_after_discount or 0,  # Default to 0 if NULL
        "discount_percentage": product.discount_percentage or 0,  # Default to 0 if NULL
        "category": product.category or "Uncategorized",  # Default if NULL
        "image_url": product.image_url or "",  # Default empty string if NULL
        "stock_remaining": product.stock_remaining or 0,  # Default to 0 if NULL
        "is_active": product.is_active,
        "product_rating": product.product_rating or 0,  # Default to 0 if NULL
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "expenditure_cost_inr": product.expenditure_cost_inr or 0,  # Handle NULL
        "total_stock": product.total_stock or 0,  # Handle NULL
        "vendor_id": product.vendor_id or 0,  # Handle NULL
        "profit_per_item_inr": product.profit_per_item_inr or 0,  # Handle NULL
    }

    # Debug log: show product data before returning
    # print(f"✅ [DEBUG] Returning product data: {product_data}")

    return product_data




@router.put("/products/{product_id}", response_model=ProductResponse)
def edit_product(
    product_id: int,
    product_data: dict,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Update product details.
    - Admins can update any product.
    - Vendors can update only their own products.
    - Automatically updates calculated fields and timestamps.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_role = token_data["role"]
    user_id = token_data["id"]

    # ✅ Fetch the product
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # ✅ Ensure only the vendor or admin can edit the product
    if user_role == "vendor" and product.vendor_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to edit this product.")

    return update_product(db, product, product_data)

@router.delete("/products/{product_id}/delete")
def remove_product(
    product_id: int,
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Soft delete a product by marking it as inactive and setting the deleted_at timestamp.
    - Only **admins** or the **vendor who owns the product** can delete it.
    """
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    user_role = token_data["role"]
    user_id = token_data["id"]

    # ✅ Fetch the product from the database
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    # ✅ Ensure only the vendor or admin can delete the product
    if user_role == "vendor" and product.vendor_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this product.")

    # ✅ Soft delete the product
    return soft_delete_product(db, product)


#==================================================================#
@router.post("/products/import")
def import_products_route(
    products: List[ProductCreate],  # ✅ Accepts a list of products
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Import a list of products (Admin only) with timestamps in IST.
    - **Admins** can import multiple products.
    - Ensures **each product has a valid vendor_id**.
    - Stores timestamps in **IST timezone**.
    """
    # ✅ Decode JWT token & ensure the user is an admin
    token_data = decode_access_token(authorization.split("Bearer ")[-1])
    if token_data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can import products.")

    return import_products(db, products)



#==============================================================#

@router.get("/products/category", response_model=list[dict])
def filter_products_by_category(
    category: str = Query(..., min_length=2, description="Category name to filter products"),  # ✅ Ensure valid string
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to fetch"),
    db: Session = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Fetch products by category.
    - Customers see **only active products**.
    - Admins & Vendors see **all products**.
    - Supports **pagination** (`skip` & `limit`).
    """
    print(f"🔍 [DEBUG] Received category: {category}")  # 🔍 Check what category is being received

    # ✅ Ensure category is not empty
    if not category or category.strip() == "":
        print("❌ [ERROR] Category is empty.")
        raise HTTPException(status_code=400, detail="Category cannot be empty.")

    # ✅ Handle authentication safely
    user_role = "guest"
    if authorization:
        parts = authorization.split("Bearer ")
        if len(parts) == 2:
            token = parts[1]
            try:
                token_data = decode_access_token(token)
                user_role = token_data.get("role", "guest")
            except Exception as e:
                print(f"❌ [ERROR] Token decoding failed: {e}")
                raise HTTPException(status_code=401, detail="Invalid authentication token.")

    print(f"✅ [DEBUG] User Role: {user_role} is filtering products by category.")

    # ✅ Fetch products based on category
    products = get_products_by_category(db, category, user_role, skip, limit)

    if not products:
        print(f"❌ [ERROR] No products found in category: {category}")
        raise HTTPException(status_code=404, detail=f"No products found in category: {category}")

    # ✅ Convert timestamps to IST
    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price_before_discount": product.price_before_discount,
            "price_after_discount": product.price_after_discount,
            "discount_percentage": product.discount_percentage,
            "category": product.category,
            "image_url": product.image_url,
            "stock_remaining": product.stock_remaining,
            "is_active": product.is_active,
            "product_rating": product.product_rating,
            "created_at": product.created_at.astimezone(IST).isoformat() if product.created_at else None,
            "updated_at": product.updated_at.astimezone(IST).isoformat() if product.updated_at else None,
            **(
                {  # ✅ Include extra fields for admin and vendors
                    "expenditure_cost_inr": product.expenditure_cost_inr,
                    "total_stock": product.total_stock,
                    "profit_per_item_inr": product.profit_per_item_inr,
                    "vendor_id": product.vendor_id,
                } if user_role in ["admin", "vendor"] else {}
            )
        }
        for product in products
    ]

    print(f"✅ [SUCCESS] Returning {len(product_list)} products.")
    return product_list













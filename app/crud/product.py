from sqlalchemy.orm import Session
from app.models import Product, User
from app.schemas import ProductCreate
from datetime import datetime
from fastapi import HTTPException

import pytz

IST = pytz.timezone("Asia/Kolkata")

def add_product(db: Session, product_data, vendor_id=None):
    """Add a new product with calculated fields."""
    
    last_product = db.query(Product).order_by(Product.id.desc()).first()
    next_product_id = last_product.id + 1 if last_product else 1

    price_before_discount = product_data.price
    price_after_discount = price_before_discount - (price_before_discount * product_data.discount_percentage / 100)
    profit_per_item_inr = price_after_discount - product_data.expenditure_cost_inr

    current_time_ist = datetime.now().astimezone(IST)

    new_product = Product(
        id=next_product_id,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        expenditure_cost_inr=product_data.expenditure_cost_inr,
        discount_percentage=product_data.discount_percentage,
        total_stock=product_data.total_stock,
        stock_remaining=product_data.total_stock,
        category=product_data.category,
        image_url=product_data.image_url,
        price_before_discount=price_before_discount,
        price_after_discount=price_after_discount,
        profit_per_item_inr=profit_per_item_inr,
        vendor_id=vendor_id or product_data.vendor_id,
        is_active=True,
        product_rating=0.0,
        created_at=current_time_ist,
        updated_at=current_time_ist,
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product



def get_products(db: Session, user_role: str, skip: int = 0, limit: int = 10):
    """
    Fetch all products with role-based filtering.
    - Customers see only active products.
    - Admins & vendors see all products.
    - Supports pagination.
    """
    query = db.query(Product)
    # ✅ Customers see only active products
    if user_role == "customer":
        query = query.filter(Product.is_active == True)
    # ✅ Apply pagination
    products = query.offset(skip).limit(limit).all()
    return products


# def get_product_by_id(db: Session, product_id: int):
#     """Fetch a product by its ID."""
#     return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_id(db: Session, product_id: int):
    """Fetch a product by its ID."""
    print(f"[get_product_by_id] Fetching product with ID: {product_id}")
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            print(f"[get_product_by_id] Product found: {product.__dict__}")  
            print(f"[get_product_by_id] No product found with ID: {product_id}")
        return product
    except Exception as e:
        print(f"[get_product_by_id] Error occurred: {e}")
        raise e



# def update_product(db: Session, product, product_data):
#     """
#     Update product details with validation.
#     - Ensures price-related updates recalculate derived fields.
#     - Updates timestamps in IST.
#     """
#     allowed_fields = [
#         "name", "description", "price", "expenditure_cost_inr", "discount_percentage",
#         "total_stock", "category", "image_url", "is_active"
#     ]

#     # ✅ Validate and update fields
#     for field, value in product_data.items():
#         if field not in allowed_fields:
#             raise HTTPException(status_code=400, detail=f"Field '{field}' is not editable.")
#         setattr(product, field, value)

#     # ✅ Recalculate derived fields if price is updated
#     if "price" in product_data or "discount_percentage" in product_data:
#         product.price_before_discount = product.price
#         product.price_after_discount = product.price - (float(product.discount_percentage) * product.price / 100)
#         product.profit_per_item_inr = product.price_after_discount - product.expenditure_cost_inr

#     if "total_stock" in product_data:
#         product.stock_remaining = product.total_stock  # Optionally reset stock_remaining

#     # ✅ Update timestamp in IST
#     product.updated_at = datetime.now().astimezone(IST)

#     db.commit()
#     db.refresh(product)

#     return product
def update_product(db, product, product_data):
    try:
        print(f"Updating product with data: {product_data}")

        if 'name' in product_data:
            product.name = product_data['name']
        if 'description' in product_data:
            product.description = product_data['description']
        if 'category' in product_data:
            product.category = product_data['category']
        if 'image_url' in product_data:
            product.image_url = product_data['image_url']
        
        if 'price' in product_data:
            print(f"Original price: {product.price}")
            product.price = float(product_data['price'])
        
        if 'expenditure_cost_inr' in product_data and product_data['expenditure_cost_inr'] is not None:
            print(f"Original expenditure cost: {product.expenditure_cost_inr}")
            product.expenditure_cost_inr = float(product_data['expenditure_cost_inr']) if product_data['expenditure_cost_inr'] else 0
        
        if 'discount_percentage' in product_data and product_data['discount_percentage'] is not None:
            print(f"Original discount percentage: {product.discount_percentage}")
            product.discount_percentage = float(product_data['discount_percentage'])
        
        if 'total_stock' in product_data and product_data['total_stock'] is not None:
            print(f"Original total stock: {product.total_stock}")
            product.total_stock = int(product_data['total_stock'])

        print(f"Price after conversion: {product.price}")
        print(f"Discount after conversion: {product.discount_percentage}")

        # Calculate price after discount
        product.price_after_discount = product.price - (product.discount_percentage * product.price / 100)
        print(f"Price after discount: {product.price_after_discount}")

        db.commit()
        return product
    
    except Exception as e:
        print(f"An error occurred while updating the product: {str(e)}")
        db.rollback()
        return None



def soft_delete_product(db: Session, product):
    """
    Soft delete a product by marking it as inactive.
    - Sets `is_active = False` and adds a `deleted_at` timestamp.
    """
    product.is_active = False
    product.deleted_at = datetime.now().astimezone(IST)  # ✅ Store IST timestamp

    db.commit()
    db.refresh(product)

    return {"message": f"Product '{product.name}' has been deactivated (soft deleted)."}




def search_products_by_name(db: Session, keyword: str, user_role: str, skip: int = 0, limit: int = 10):
    """
    Search products by name containing a given keyword.
    - Customers see only active products.
    - Admins/Vendors see all products.
    - Supports pagination.
    """
    print(f"🔍 [DEBUG] Searching products with keyword: {keyword}")
    print(f"🔍 [DEBUG] User Role: {user_role}, Skip: {skip}, Limit: {limit}")

    if not keyword or keyword.strip() == "":
        print("❌ [ERROR] No valid search keyword provided.")
        return []

    try:
        # ✅ Use `ILIKE` for case-insensitive search and match any part of the name
        query = db.query(Product).filter(Product.name.ilike(f"%{keyword}%"))

        # ✅ Restrict "customer" users to only active products
        if user_role == "customer":
            query = query.filter(Product.is_active == True)

        # ✅ Apply pagination
        products = query.offset(skip).limit(limit).all()
        print(f"✅ [DEBUG] Found {len(products)} products matching the keyword: {keyword}")
        return products

    except Exception as e:
        print(f"❌ [ERROR] Database query failed: {e}")
        return []

#=====================================================================#


def import_products(db: Session, products):
    """
    Bulk import multiple products.
    - Validates each product's vendor_id.
    - Calculates derived fields (`price_after_discount`, `profit_per_item_inr`).
    - Uses a **soft auto-increment strategy** for product IDs.
    - Stores timestamps in **IST timezone**.
    """

    # ✅ Fetch the last product ID
    last_product = db.query(Product).order_by(Product.id.desc()).first()
    next_product_id = last_product.id + 1 if last_product else 1

    imported_products = []

    for product_data in products:
        # ✅ Validate vendor_id is provided
        if not product_data.vendor_id:
            raise HTTPException(status_code=400, detail="Vendor ID is required for importing products.")

        # ✅ Ensure vendor exists
        vendor = db.query(User).filter(User.id == product_data.vendor_id).first()
        if not vendor:
            raise HTTPException(status_code=404, detail=f"Vendor with ID {product_data.vendor_id} does not exist.")

        # ✅ Calculate derived fields
        price_before_discount = product_data.price
        price_after_discount = price_before_discount - (price_before_discount * product_data.discount_percentage / 100)
        profit_per_item_inr = price_after_discount - product_data.expenditure_cost_inr

        # ✅ Get current timestamp in IST
        current_time_ist = datetime.now(IST)

        # ✅ Create new product instance
        new_product = Product(
            id=next_product_id,
            name=product_data.name,
            description=product_data.description,
            price = float(product_data.price) ,
            expenditure_cost_inr=product_data.expenditure_cost_inr,
            discount_percentage = float(product_data.discount_percentage) , # Ensure it's a float
            total_stock=product_data.total_stock,
            stock_remaining=product_data.total_stock,
            category=product_data.category,
            image_url=product_data.image_url,
            price_before_discount=price_before_discount,
            price_after_discount=price_after_discount,
            profit_per_item_inr=profit_per_item_inr,
            vendor_id=product_data.vendor_id,
            is_active=True,  # ✅ Default to active upon import
            product_rating=0.0,  # ✅ New products have no ratings initially
            created_at=current_time_ist,
            updated_at=current_time_ist,
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        imported_products.append(new_product)
        next_product_id += 1  # ✅ Increment for the next product

    return {
        "message": "Products imported successfully.",
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat(),
            }
            for p in imported_products
        ],
    }


#===================================================#

def get_products_by_category(db: Session, category: str, user_role: str, skip: int = 0, limit: int = 10):
    """
    Fetch products by category.
    - Customers see only active products.
    - Admins/Vendors see all products.
    - Supports pagination.
    """
    print(f"🔍 [DEBUG] Searching for category: {category}")

    if not category or category.strip() == "":
        print("❌ [ERROR] No category provided.")
        return []

    try:
        # ✅ Use case-insensitive filtering with partial match
        query = db.query(Product).filter(Product.category.ilike(f"%{category}%"))

        # ✅ Restrict "customer" users to only active products
        if user_role == "customer":
            query = query.filter(Product.is_active == True)

        # ✅ Apply pagination
        products = query.offset(skip).limit(limit).all()

        print(f"✅ [DEBUG] Found {len(products)} products in category: {category}")
        return products

    except Exception as e:
        print(f"❌ [ERROR] Database query failed: {e}")
        return []


def get_products_by_rating(db: Session, min_rating: float, max_rating: float, user_role: str, skip: int = 0, limit: int = 10):
    """
    Fetch products by rating range.
    - Customers see only active products.
    - Admins/Vendors see all products.
    - Supports pagination.
    """
    print(f"🔍 [DEBUG] Searching for products with rating {min_rating} - {max_rating}")

    if min_rating > max_rating:
        print("❌ [ERROR] min_rating cannot be greater than max_rating")
        return []

    try:
        # ✅ Use rating filter
        query = db.query(Product).filter(Product.product_rating.between(min_rating, max_rating))

        # ✅ Restrict "customer" users to only active products
        if user_role == "customer":
            query = query.filter(Product.is_active == True)

        # ✅ Apply pagination
        products = query.offset(skip).limit(limit).all()

        print(f"✅ [DEBUG] Found {len(products)} products in rating range {min_rating} - {max_rating}")
        return products

    except Exception as e:
        print(f"❌ [ERROR] Database query failed: {e}")
        return []
















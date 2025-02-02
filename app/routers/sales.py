from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from app.database import get_db
from app.crud.sales import (
    get_total_revenue,
    get_monthly_revenue,
    get_best_performing_products,
    get_daily_sales_trend,
    get_popular_products,
)
from sqlalchemy import func, extract
from app.models import Order  # Add this import

router = APIRouter()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Total Revenue
@router.get("/total-revenue")
def total_revenue(db: Session = Depends(get_db)):
    logger.debug("Fetching total revenue...")
    revenue = get_total_revenue(db)
    if revenue is None:
        raise HTTPException(status_code=500, detail="Error fetching total revenue")
    return {"total_revenue": revenue}

# Monthly Revenue (Trends)
@router.get("/monthly-revenue")
def monthly_revenue(year: int, db: Session = Depends(get_db)):
    logger.debug(f"Fetching monthly revenue for year {year}...")
    
    # Ensure query year is valid
    available_years = db.query(func.distinct(extract("year", Order.created_at))).all()
    available_years = [int(y[0]) for y in available_years]  # Convert to list

    logger.debug(f"Available years in database: {available_years}")

    if year not in available_years:
        return {"year": year, "monthly_revenue": []}  # Return empty list instead of 404

    revenue = get_monthly_revenue(db, year)
    if revenue is None:
        raise HTTPException(status_code=500, detail="Error fetching monthly revenue")

    return {"year": year, "monthly_revenue": revenue}


# Daily Sales Trend
@router.get("/daily-sales-trend")
def daily_sales_trend(start_date: str, end_date: str, db: Session = Depends(get_db)):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        logger.error("Invalid date format in daily sales trend request.")
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    logger.debug(f"Fetching daily sales trend from {start_date} to {end_date}...")
    trends = get_daily_sales_trend(db, start_date, end_date)
    if trends is None:
        raise HTTPException(status_code=500, detail="Error fetching daily sales trend")
    return {"sales_trend": trends}

# Best Performing Products
@router.get("/best-products")
def best_performing_products(limit: int = 10, db: Session = Depends(get_db)):
    logger.debug(f"Fetching best performing products with limit {limit}...")
    products = get_best_performing_products(db, limit)
    if products is None:
        raise HTTPException(status_code=500, detail="Error fetching best-performing products")
    return {"best_performing_products": products}

# Popular Products
@router.get("/popular-products")
def popular_products(limit: int = 10, db: Session = Depends(get_db)):
    logger.debug(f"Fetching popular products with limit {limit}...")
    products = get_popular_products(db, limit)
    if products is None:
        raise HTTPException(status_code=500, detail="Error fetching popular products")
    return {"popular_products": products}

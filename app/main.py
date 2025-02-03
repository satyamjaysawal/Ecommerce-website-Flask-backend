import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.database import engine, Base
from app.routers import auth, product, user, cart, order, sales, review, payment, shipment
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# ✅ Implement CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:5173")],  # Frontend allowed origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Home route to check if the server is running
@app.get("/")
def read_root():
    return {"message": "Server is running!"}

# Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/user", tags=["Users"])
app.include_router(product.router, prefix="/product", tags=["Products"])
app.include_router(review.router, prefix="/reviews", tags=["Reviews"])  
app.include_router(cart.router, prefix="/cart", tags=["Cart"])
app.include_router(order.router, prefix="/orders", tags=["Orders"])
app.include_router(payment.router, prefix="/payment", tags=["Payment"])
app.include_router(shipment.router, prefix="/shipment", tags=["Shipment"])  
app.include_router(sales.router, prefix="/sales", tags=["Sales Analysis"])

# Create tables on startup
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)

# Add security scheme for Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="E-commerce API",
        version="1.0.0",
        description="E-commerce API with role-based authentication",
        routes=app.routes,
    )
    security_scheme = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["components"]["securitySchemes"] = security_scheme
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Override the OpenAPI schema
app.openapi = custom_openapi

# # ✅ Explicitly Bind to 0.0.0.0 and Use Render's Assigned Port
# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))  # Use PORT from environment, fallback to 8000
#     print(f"🚀 Starting server on 0.0.0.0:{port} ...")  # Debugging output
#     uvicorn.run(app, host="0.0.0.0", port=port, reload=False)  # Bind to 0.0.0.0

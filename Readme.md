

  [**Frontent - E-Commerce Website**](https://ecommerce-website-reactjs-vite-frontend.onrender.com)
`https://ecommerce-website-reactjs-vite-frontend.onrender.com`

[**Frontend - GitHub Link**](https://github.com/satyamjaysawal/Ecommerce-website-Reactjs-Vite-frontend.git)
`https://github.com/satyamjaysawal/Ecommerce-website-Reactjs-Vite-frontend.git`


![image](https://github.com/user-attachments/assets/eb668367-0843-465d-8472-05224d53e9a8)


![image](https://github.com/user-attachments/assets/d6fc6ffe-34c3-415f-aec3-75043a45a246)



List of all the API URLs:

### 1. **Authentication**
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`

### 2. **User Profile**
- `GET /user/profile`
- `PUT /user/profile`
- `GET /user/{user_id}`
- `PUT /user/{user_id}`
- `DELETE /user/{user_id}`

### 3. **Product Management**
- `POST /product/products`
- `GET /product/products`
- `GET /product/products/{product_id}`
- `PUT /product/products/{product_id}`
- `DELETE /product/products/{product_id}`
- `GET /product/products/search`
- `GET /product/products/category`
- `GET /product/products/rating`

### 4. **Cart & Wishlist**
- `POST /cart/cart`
- `GET /cart/cart`
- `DELETE /cart/cart/{product_id}`
- `POST /cart/wishlist`
- `GET /cart/wishlist`
- `DELETE /cart/wishlist/{product_id}`

### 5. **Orders**
- `POST /orders/place`
- `GET /orders/orders/{order_id}`
- `GET /orders/orders`

### 6. **Reviews**
- `POST /reviews/reviews`
- `GET /reviews/products/{product_id}/reviews`

### 7. **Sales Analytics (Admin only)**
- `GET /sales/total-revenue`
- `GET /sales/monthly-revenue`
- `GET /sales/daily-sales-trend`
- `GET /sales/best-products`
- `GET /sales/popular-products`

### 8. **Shipment (Admin only)**
- `PUT /shipment/orders/{order_id}/shipment`
- `PUT /shipment/orders/{order_id}/deliver`

### 9. **Payment**
- `POST /payment/create-order`
- `POST /payment/confirm-payment`



## Installation

To run this project locally, follow the steps below:

### Backend Setup (FastAPI)
1. Clone this repository:
   ```bash
   git clone https://github.com/your-repository-url.git
   cd your-repository-directory
   ```

2. Create a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the environment variables:
   - **DATABASE_URL**: PostgreSQL connection URL
   - **SECRET_KEY**: A secure key for JWT token encoding
   - **RAZORPAY_API_KEY**: API key for Razorpay

   Example `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@localhost/ecommerce_db
   DATABASE_URL=postgresql://xxxxxxxxxxxxxxxxxxxxxxxxxxxx?sslmode=require
   FRONTEND_URL=https://ecommerce-website-reactjs-vite-frontend.onrender.com
   FRONTEND_URL=http://localhost:5173
   PORT=8080
   RAZORPAY_API_KEY=your_razorpay_api_key
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup (React)
1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install frontend dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### Database Setup
Ensure you have a PostgreSQL database running. You can use Docker to set up the database easily:
```bash
docker-compose up -d
```

This will start the PostgreSQL container.

### Docker Setup
You can use Docker to run both the frontend and backend services in containers. The project contains a `docker-compose.yml` file to handle both services.

To run the project using Docker:
```bash
docker-compose up --build
```

## Deployment

The frontend of the project has been deployed and is accessible through the following URL:
[**E-Commerce Website**](https://ecommerce-website-reactjs-vite-frontend.onrender.com)

## API Documentation

The API follows a RESTful design and provides endpoints for product management, user authentication, order management, and more.




















****
****




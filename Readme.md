

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

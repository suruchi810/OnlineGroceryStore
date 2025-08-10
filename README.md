# 🛒 Online Grocery Store Backend – Django REST API

## 📌 Project Overview
This project is a **Django REST Framework**-based backend for an **Online Grocery Store**.  
It allows customers to browse and purchase products while store managers manage inventory and view sales data.  

---

## 🎯 Key Features

### **User Authentication & Roles**
- User registration & login
- JWT-based authentication
- Two roles:
  - **Customer** – can browse, shop, and manage their cart/wishlist
  - **Store Manager** – can manage products and view sales reports

### **Store Manager Capabilities**
- Add, edit, and delete products *(manager only)*
- View sales reports with filters:
  - Most sold products
  - Least sold products
  - Products by category
  
### **Customer Capabilities**
- Browse products with category & popularity filters
- Add/remove products from cart
- Checkout with bill summary and purchase date
- Save items to wishlist

---

## 🏗 Tech Stack
- **Backend Framework:** Django, Django REST Framework
- **Authentication:** JWT via `djangorestframework-simplejwt`
- **Database:** PostgreSQL database (Neon)
- **API Documentation:** via Postman collection
---

## ⚙️ How to Run the Project

1. **Clone the Repository**
   ```bash
   https://github.com/suruchi810/OnlineGroceryStore.git
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate      
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the Server**
   ```bash
   python manage.py runserver
   ```

---

## API Endpoints

| Method | Endpoint                                                     | Description                      
|--------|--------------------------------------------------------------|----------------------------------------------|
| POST   | `/api/auth/register/`                                        | User registration                            |
| POST   | `/api/auth/login/`                                           | User login (JWT token)                       |
| GET    | `/api/products/`                                             | Browse products                              |
| POST   | `/api/products/`                                             | Add product *(Manager only)*                 |
| PUT    | `/api/products/{id}/`                                        | Edit product *(Manager only)*                |   
| DELETE | `/api/products/{id}/`                                        | Delete product *(Manager only)*              |
| GET    | `/api/cart/list_items`                                       | View cart                                    |
| POST   | `/api/cart/add/`                                             | Add product to cart                          |
| POST   | `/api/cart/remove/`                                          | Remove product from cart                     |
| GET    | `/api/wishlist/my_list/`                                     | View wishlist                                |
| POST   | `/api/wishlist/toggle/`                                      | add / remove item from wishlist              |
| POST   | `/api/checkout/`                                             | Checkout and get bill summary                |
| GET    | `/api/sales-report/`                                         | View full sales report *(Manager only)*      |
| GET    | `/api/sales-report/?category={category_slug}`                | View sales report filtered bycategory        |
| GET    | `/api/sales-report/?sort=most_sold`                          | View most sold products in sales report      |
| GET    | `/api/sales-report/?sort=least_sold`                         | View least sold products in sales report     |
| GET    | `/api/sales-report/?category={category_slug}&sort=most_sold` | View most sold products filtered by category |
| GET    | `/api/sales-report/?category={category_slug}&sort=least_sold`| View least sold products filtered by category|
| GET    | `/api/low-stock-alert/`                                      | View low-stock products (10<=)               |


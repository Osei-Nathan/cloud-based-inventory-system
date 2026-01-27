STEP 1: SYSTEM BLUEPRINT
Project Name

Cloud-Based Inventory, Sales, and Analytics System

Core Goal

Track products, stock movement, sales, and generate basic analytics for small businesses, deployed on the cloud.

STEP 2: DATABASE DESIGN (THIS IS FOUNDATION)
Entities and Relationships
1. User

id

name

email

password

role (ADMIN, STAFF, VIEWER)

is_active

created_at

2. Category

id

name

description

3. Supplier

id

name

contact_info

4. Product

id

name

category (FK)

supplier (FK)

unit_price

stock_quantity

low_stock_threshold

created_at

5. Sale

id

staff (FK → User)

total_amount

created_at

6. SaleItem

id

sale (FK)

product (FK)

quantity

price_at_sale

Rules

Stock reduces only through SaleItem

No direct stock editing except ADMIN

STEP 3: DJANGO APP STRUCTURE

Create separate apps. This signals seriousness.

inventory_system/
├── accounts/
├── products/
├── sales/
├── analytics/
├── config/

App responsibilities

accounts: auth, roles, permissions

products: categories, suppliers, products

sales: sales & sale items

analytics: reports & summaries

STEP 4: API ENDPOINTS (MINIMUM SET)
Auth

POST /api/auth/register/

POST /api/auth/login/

POST /api/auth/refresh/

Products

GET /api/products/

POST /api/products/ (ADMIN)

PATCH /api/products/{id}/

DELETE /api/products/{id}/

Sales

POST /api/sales/

GET /api/sales/

GET /api/sales/{id}/

Analytics

GET /api/analytics/sales-summary/

GET /api/analytics/top-products/


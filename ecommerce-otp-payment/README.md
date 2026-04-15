# 🛍️ NexusShop — E-Commerce with OTP Payment Verification

> **Shop Smarter. Pay Safer.**  
> A full-stack Indian e-commerce platform with real-time OTP verification for secure checkout, built with Flask + Socket.IO + SQLAlchemy.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [OTP System](#otp-system)
- [Admin Dashboard](#admin-dashboard)
- [API Reference](#api-reference)
- [User Flow](#user-flow)
- [Default Credentials](#default-credentials)
- [Troubleshooting](#troubleshooting)

---

## 🌟 Overview

NexusShop is a feature-rich e-commerce web application built for the Indian market. It integrates a dual-channel OTP (One-Time Password) verification system — via **Gmail Email** and **SMS (Fast2SMS)** — to authenticate payments before any order is placed. The platform supports real-time cart updates via WebSockets, an admin dashboard, product reviews, wishlists, and full order management.

---

## ✨ Features

### 🛒 Storefront
- Product listing with category filters and search
- Product detail pages with image, specs, rating, and reviews
- Add to Cart / Wishlist toggle
- Related products suggestions
- Real-time cart count updates (Socket.IO)

### 🔐 OTP-Secured Checkout
- Dual-channel OTP delivery: **Email (Gmail SMTP)** + **SMS (Fast2SMS)**
- 8-character alphanumeric OTP with 5-minute expiry
- OTP resend with 30-second cooldown
- Client IP detection (multi-source, including ipify fallback)
- Detailed OTP email with order summary, product images, and payment details

### 📦 Order Management
- Order placement only after OTP verification
- Order confirmation email sent automatically
- Real-time order status updates via Socket.IO (Confirmed → Processing → Dispatched)
- "Order Received" confirmation button via email redirect
- Order history page (last 10 orders)

### 👤 User Accounts
- Register / Login / Logout
- Password hashing (secure storage)
- Pre-filled checkout form for logged-in users

### 🛠️ Admin Dashboard (`/admin`)
- Secure admin login
- Stats: Total Orders, Revenue, Products, Customers, Pending, Low Stock
- Category revenue breakdown
- Payment method analytics (Card, UPI, Net Banking, COD)
- Top products by revenue
- Order status distribution
- Manage products: add, update stock
- Manage orders: view, update status
- Low stock alerts

---

## 📁 Project Structure

```
ecommerce-otp-payment/
├── app.py              # Main Flask application — all routes & logic
├── config.py           # All configuration (email, SMS, OTP, store info, DB)
├── models.py           # SQLAlchemy models: Product, Order, User, Review, Wishlist
├── otp_service.py      # OTP generation, email (Gmail SMTP), SMS (Fast2SMS)
├── fix_bugs.py         # Utility script for hotfixes
├── requirements.txt    # Python dependencies
├── instance/
│   └── shopzen.db      # SQLite database (auto-created on first run)
├── static/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Product & UI images
└── templates/
    ├── base.html        # Base layout template
    ├── index.html       # Homepage / product listing
    ├── product.html     # Product detail page
    ├── cart.html        # Shopping cart
    ├── checkout.html    # Checkout with OTP flow
    ├── success.html     # Order success page
    ├── orders.html      # Order history
    ├── order_received.html  # Order received confirmation
    ├── login.html       # User login
    ├── register.html    # User registration
    └── admin/
        ├── login.html   # Admin login
        ├── dashboard.html   # Admin analytics dashboard
        ├── products.html    # Admin product management
        └── orders.html      # Admin order management
```

---

## 🧰 Tech Stack

| Layer        | Technology                          |
|--------------|--------------------------------------|
| Backend      | Python 3.10+ · Flask 3.0            |
| Database     | SQLite (via Flask-SQLAlchemy 3.1)   |
| Real-time    | Flask-SocketIO 5.3 · Eventlet 0.35  |
| Email OTP    | Gmail SMTP (smtplib — built-in)     |
| SMS OTP      | Fast2SMS REST API (free trial)      |
| Frontend     | Jinja2 · Vanilla HTML/CSS/JS        |
| HTTP Client  | Requests 2.31                       |
| Config       | python-dotenv 1.0                   |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip
- A Gmail account (for email OTP)
- *(Optional)* Fast2SMS account (for SMS OTP)

### 1. Clone / Navigate to the Project

```bash
cd ecommerce-otp-payment
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy and edit `config.py` or create a `.env` file (see [Configuration](#configuration) below).

---

## 🔧 Configuration

All settings live in `config.py`. You can override them with environment variables or a `.env` file.

### Required — Gmail Email OTP

```python
# config.py
EMAIL_ADDRESS  = "your-gmail@gmail.com"
EMAIL_PASSWORD = "your-app-password"   # 16-char Gmail App Password
```

> **How to get a Gmail App Password:**  
> Google Account → Security → 2-Step Verification → App Passwords → Generate

### Optional — SMS OTP (Fast2SMS)

```python
FAST2SMS_API_KEY = "your-fast2sms-api-key"
```

> Sign up free at [fast2sms.com](https://fast2sms.com) → API → Dev API Key.  
> Free trial credits (~150 SMS) are given on signup.  
> If no key is set, the OTP is printed to the terminal for testing.

### Key Settings Reference

| Setting              | Default                         | Description                        |
|----------------------|---------------------------------|------------------------------------|
| `SECRET_KEY`         | `ecom-otp-super-secret-key-2024`| Flask session secret               |
| `OTP_EXPIRY_SECONDS` | `300` (5 min)                   | OTP validity window                |
| `OTP_LENGTH`         | `6`                             | OTP character length               |
| `OTP_RESEND_WAIT`    | `30` seconds                    | Cooldown before resend             |
| `TAX_RATE`           | `0.18` (18%)                    | GST tax rate                       |
| `CURRENCY`           | `₹`                             | Currency symbol                    |
| `DATABASE_URL`       | `sqlite:///shopzen.db`          | SQLite DB path                     |
| `ADMIN_USERNAME`     | `nexusshop`                     | Admin login username               |
| `ADMIN_PASSWORD`     | `12345678`                      | Admin login password               |

---

## 🚀 Running the App

```bash
python app.py
```

The app starts on **http://localhost:5000** by default.

On first run, the database is automatically created and seeded with sample products.

---

## 🔑 OTP System

The OTP flow works as follows:

```
Customer fills checkout form
        ↓
[Send OTP] → OTP generated (8-char alphanumeric)
        ↓
Sent via Email (Gmail SMTP) + SMS (Fast2SMS)
        ↓
Customer enters OTP on checkout page
        ↓
[Verify OTP] → Session flagged as verified
        ↓
[Place Order] → Stock deducted, order saved to DB
        ↓
Order confirmation email sent (background thread)
        ↓
Real-time status: Confirmed → Processing → Dispatched (Socket.IO)
```

**OTP Email includes:**
- Order summary with product names, quantities, prices
- Tax and total breakdown
- Payment method details
- Customer delivery address
- Client IP address and phone number
- "Order Received" confirmation button

---

## 🛠️ Admin Dashboard

Access the admin panel at: **http://localhost:5000/admin**

### Default Credentials
| Field    | Value        |
|----------|--------------|
| Username | `nexusshop`  |
| Password | `12345678`   |

> ⚠️ **Change these credentials before deploying to production!**

### Admin Capabilities
- 📊 View live analytics (revenue, orders, products, customers)
- 📦 Manage product inventory and stock levels
- 🧾 View and update order statuses
- 🔔 Low stock alerts
- 🏷️ Add new products with category, specs, images

---

## 📡 API Reference

| Method | Endpoint                             | Description                    |
|--------|--------------------------------------|--------------------------------|
| GET    | `/`                                  | Homepage / product listing     |
| GET    | `/product/<id>`                      | Product detail page            |
| GET    | `/cart`                              | View shopping cart             |
| POST   | `/cart/add`                          | Add item to cart               |
| POST   | `/cart/update`                       | Update cart quantity           |
| POST   | `/cart/remove`                       | Remove item from cart          |
| POST   | `/cart/clear`                        | Clear entire cart              |
| GET    | `/checkout`                          | Checkout page                  |
| POST   | `/send-otp`                          | Generate & send OTP            |
| POST   | `/verify-otp`                        | Verify entered OTP             |
| POST   | `/place-order`                       | Place order (requires OTP)     |
| GET    | `/success`                           | Order success page             |
| GET    | `/orders`                            | Order history                  |
| POST   | `/api/product/<id>/review`           | Submit product review          |
| POST   | `/api/wishlist/toggle`               | Toggle wishlist item           |
| GET    | `/api/wishlist`                      | Get wishlist                   |
| GET    | `/api/products`                      | Get all products (JSON)        |
| GET    | `/admin`                             | Admin dashboard                |
| GET    | `/admin/orders`                      | Admin orders list              |
| POST   | `/admin/orders/<id>/status`          | Update order status            |
| GET    | `/admin/products`                    | Admin products list            |
| POST   | `/admin/products/<id>/stock`         | Update product stock           |
| GET    | `/admin/products/add`                | Add new product form           |

### Socket.IO Events

| Event          | Direction      | Description                        |
|----------------|----------------|------------------------------------|
| `connect`      | Client → Server| Join personal room, get cart count |
| `ping_stock`   | Client → Server| Request real-time stock for item   |
| `cart_update`  | Server → Client| Live cart count & subtotal         |
| `stock_update` | Server → Client| Live stock level for a product     |
| `order_status` | Server → Client| Live order status change           |

---

## 🧑‍💼 User Flow

### Customer Journey
1. Browse products on the homepage → Filter by category or search
2. View product detail → Add to cart
3. Go to cart → Proceed to checkout
4. Fill in name, email, phone, address, and payment details
5. Click **"Send OTP"** → Receive OTP via Email/SMS
6. Enter OTP → Click **"Verify & Pay"**
7. Order is placed → Receive confirmation email
8. Track order status in real time or from **Orders** page

### Admin Journey
1. Login at `/admin/login`
2. View dashboard analytics
3. Manage orders (update status: Confirmed → Processing → Dispatched → Delivered)
4. Manage products (update stock, add new products)

---

## 🐛 Troubleshooting

### OTP not received via Email
- Check that `EMAIL_ADDRESS` and `EMAIL_PASSWORD` in `config.py` are correct.
- Make sure you are using a **Gmail App Password**, not your regular Gmail password.
- Check your spam/junk folder.
- Look at the terminal — the OTP is always printed there for debugging.

### SMS not received
- Ensure `FAST2SMS_API_KEY` is set in `config.py`.
- Free trial credits may be exhausted — check your Fast2SMS dashboard.
- If key is missing, OTP falls back to terminal output only.

### Database errors on first run
```bash
# Delete the DB and let it recreate
del instance\shopzen.db    # Windows
python app.py
```

### Port already in use
```bash
# Change port in app.py (last line):
socketio.run(app, host="0.0.0.0", port=5001, debug=True)
```

### Category filter shows encoded URL characters
- This was a known bug — URL encoding for categories with special characters (e.g., `&`) has been fixed.

---

## 📄 License

This project is for educational and demonstration purposes.

---

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/) — Web framework
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) — Real-time WebSocket support
- [Fast2SMS](https://fast2sms.com/) — Free SMS API for India
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM for database management

"""
NexusShop — Advanced E-Commerce with OTP Payment Verification
Flask + Socket.IO + SQLAlchemy + Email OTP + SMS OTP (Fast2SMS)
"""

import json
import uuid
import time
from datetime import datetime, timedelta
from functools import wraps
from threading import Timer

from flask import (Flask, render_template, request, session,redirect, url_for, jsonify, flash)
from flask_socketio import SocketIO, emit, join_room
from flask_sqlalchemy import SQLAlchemy

import config
from models import db, Product, Order, User, Review, Wishlist, seed_products
from otp_service import generate_otp, send_both_otp, send_order_confirmation_email

# ── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config["SQLALCHEMY_DATABASE_URI"] = config.DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
socketio = SocketIO(app, async_mode="gevent", cors_allowed_origins="*")

# ── DB Init ──────────────────────────────────────────────────────────────────
with app.app_context():
    db.create_all()
    seed_products(app, db)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_cart():
    return session.get("cart", {})

def save_cart(cart):
    session["cart"] = cart
    session.modified = True

def cart_total(cart):
    total = 0.0
    for item_id, item in cart.items():
        total += item["price"] * item["qty"]
    return round(total, 2)

def generate_order_id():
    return "SZ" + str(int(time.time()))[-8:].upper()

def get_logged_in_user():
    uid = session.get("user_id")
    return User.query.get(uid) if uid else None


# ══════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("index"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return redirect(url_for("login"))
        session["user_id"]   = user.id
        session["user_name"] = user.name
        session["user_email"]= user.email
        session.modified = True
        flash(f"Welcome back, {user.name}! 👋", "success")
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("index"))
    if request.method == "POST":
        name     = request.form.get("name", "").strip()
        email    = request.form.get("email", "").strip().lower()
        phone    = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        address  = request.form.get("address", "").strip()

        if not name or not email or not password:
            flash("Name, email and password are required.", "error")
            return redirect(url_for("register"))
        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("register"))
        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("register"))

        user = User(name=name, email=email, phone=phone, address=address)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["user_id"]    = user.id
        session["user_name"]  = user.name
        session["user_email"] = user.email
        session.modified = True
        flash(f"Account created! Welcome, {name}! 🎉", "success")
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("user_email", None)
    flash("You've been signed out.", "success")
    return redirect(url_for("index"))


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES — STORE
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    category = request.args.get("category", "All")
    search   = request.args.get("q", "")
    query    = Product.query
    if category != "All":
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products   = query.all()
    categories = ["All"] + sorted(set(p.category for p in Product.query.all()))
    cart_count = sum(i["qty"] for i in get_cart().values())
    current_user = get_logged_in_user()
    return render_template("index.html",
                           products=products,
                           categories=categories,
                           active_category=category,
                           search=search,
                           cart_count=cart_count,
                           current_user=current_user)


@app.route("/api/products")
def api_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])


# ── Cart ─────────────────────────────────────────────────────────────────────

@app.route("/cart")
def cart():
    cart_data = get_cart()
    subtotal  = cart_total(cart_data)
    tax       = round(subtotal * config.TAX_RATE, 2)
    total     = round(subtotal + tax, 2)
    return render_template("cart.html",
                           cart=cart_data,
                           subtotal=subtotal,
                           tax=tax,
                           total=total)


@app.route("/cart/add", methods=["POST"])
def cart_add():
    data       = request.get_json()
    product_id = str(data.get("product_id"))
    qty        = int(data.get("qty", 1))
    product    = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    cart = get_cart()
    if product_id in cart:
        cart[product_id]["qty"] = min(cart[product_id]["qty"] + qty, product.stock)
    else:
        cart[product_id] = {
            "id":    product.id,
            "name":  product.name,
            "price": product.price,
            "emoji": product.image_emoji,
            "color": product.image_color,
            "qty":   qty,
            "stock": product.stock,
        }
    save_cart(cart)

    cart_count = sum(i["qty"] for i in cart.values())
    subtotal   = cart_total(cart)
    # Broadcast live cart count to this session
    socketio.emit("cart_update", {"count": cart_count, "subtotal": subtotal},
                  room=session.get("sid", ""))
    return jsonify({"success": True, "cart_count": cart_count, "subtotal": subtotal})


@app.route("/cart/update", methods=["POST"])
def cart_update():
    data       = request.get_json()
    product_id = str(data.get("product_id"))
    qty        = int(data.get("qty", 1))
    cart       = get_cart()
    if product_id in cart:
        if qty <= 0:
            del cart[product_id]
        else:
            cart[product_id]["qty"] = qty
    save_cart(cart)
    subtotal = cart_total(cart)
    tax      = round(subtotal * config.TAX_RATE, 2)
    total    = round(subtotal + tax, 2)
    return jsonify({
        "success": True,
        "cart_count": sum(i["qty"] for i in cart.values()),
        "subtotal": subtotal, "tax": tax, "total": total,
    })


@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    data       = request.get_json()
    product_id = str(data.get("product_id"))
    cart       = get_cart()
    cart.pop(product_id, None)
    save_cart(cart)
    subtotal = cart_total(cart)
    tax      = round(subtotal * config.TAX_RATE, 2)
    total    = round(subtotal + tax, 2)
    return jsonify({
        "success": True,
        "cart_count": sum(i["qty"] for i in cart.values()),
        "subtotal": subtotal, "tax": tax, "total": total,
    })


@app.route("/cart/clear", methods=["POST"])
def cart_clear():
    save_cart({})
    return jsonify({"success": True})


# ── Checkout ─────────────────────────────────────────────────────────────────

@app.route("/checkout")
def checkout():
    cart_data    = get_cart()
    if not cart_data:
        return redirect(url_for("index"))
    subtotal     = cart_total(cart_data)
    tax          = round(subtotal * config.TAX_RATE, 2)
    total        = round(subtotal + tax, 2)
    current_user = get_logged_in_user()   # pre-fill form if logged in
    banks = [
        "State Bank of India", "HDFC Bank", "ICICI Bank", "Axis Bank",
        "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda",
        "Canara Bank", "Union Bank of India", "IndusInd Bank",
        "Yes Bank", "Federal Bank", "IDFC First Bank", "RBL Bank",
        "South Indian Bank", "Karnataka Bank", "UCO Bank",
        "Bank of India", "Central Bank of India", "Indian Bank",
    ]
    return render_template("checkout.html",
                           cart=cart_data,
                           subtotal=subtotal,
                           tax=tax,
                           total=total,
                           banks=banks,
                           currency=config.CURRENCY,
                           current_user=current_user)


@app.route("/send-otp", methods=["POST"])
def send_otp():
    data   = request.get_json()
    name   = data.get("name", "").strip()
    email  = data.get("email", "").strip()
    phone  = data.get("phone", "").strip()
    amount = data.get("amount", "0")
    payment_method = data.get("payment_method", "").strip()
    payment_detail = data.get("payment_detail", "").strip()

    if not name or not email or not phone:
        return jsonify({"success": False, "message": "Name, email and phone are required."}), 400

    # Phone validation
    phone_clean = phone.replace("+91", "").replace(" ", "").replace("-", "")
    if not phone_clean.isdigit() or len(phone_clean) != 10:
        return jsonify({"success": False, "message": "Enter a valid 10-digit Indian mobile number."}), 400

    otp = generate_otp()
    session["otp"]            = otp
    session["otp_expires_at"] = (datetime.utcnow() + timedelta(seconds=config.OTP_EXPIRY_SECONDS)).isoformat()
    session["otp_email"]      = email
    session["otp_phone"]      = phone_clean
    session["checkout_name"]  = name
    session["checkout_amount"]= amount
    session.modified          = True

    # ── Capture real public IP (multi-source) ──
    js_ip      = (data.get("ip") or "").strip()
    forwarded  = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    real_ip    = request.headers.get("X-Real-IP", "").strip()
    remote     = request.remote_addr or ""

    def _is_private(ip):
        return not ip or ip in ("Unknown","Unavailable") or \
               ip.startswith(("127.","10.","192.168.","::1","fc","fd"))

    client_ip = js_ip if not _is_private(js_ip) else \
                forwarded if not _is_private(forwarded) else \
                real_ip   if not _is_private(real_ip)   else \
                remote    if not _is_private(remote)     else ""

    # Last resort: fetch from ipify server-side
    if not client_ip or _is_private(client_ip):
        try:
            import urllib.request
            with urllib.request.urlopen("https://api.ipify.org", timeout=3) as resp:
                client_ip = resp.read().decode().strip()
        except Exception:
            client_ip = remote or "Unknown"

    session["client_ip"] = client_ip
    session.modified = True
    print(f"[IP] js={js_ip!r} fwd={forwarded!r} remote={remote!r} → final={client_ip!r}")

    # ── Build rich cart items for email ──
    cart = get_cart()
    cart_items_for_email = []
    subtotal = 0.0
    for pid_str, item in cart.items():
        try:
            prod = Product.query.get(int(pid_str))
            specs_dict = prod.specs if prod else {}
        except Exception:
            prod = None
            specs_dict = {}
        price = float(item.get('price', 0))
        qty   = int(item.get('qty', 1))
        subtotal += price * qty
        cart_items_for_email.append({
            'name':      item.get('name', 'Product'),
            'brand':     item.get('brand', prod.brand if prod else ''),
            'price':     price,
            'qty':       qty,
            'emoji':     item.get('emoji', '📦'),
            'image_url': prod.image_url if prod and prod.image_url else None,
            'specs':     specs_dict,
        })

    tax_amt  = subtotal * config.TAX_RATE
    address  = data.get('address', '').strip()

    result = send_both_otp(email, phone_clean, otp, name, amount, client_ip,
                           cart_items=cart_items_for_email,
                           address=address,
                           subtotal=subtotal,
                           tax=tax_amt,
                           payment_method=payment_method,
                           payment_detail=payment_detail)
    print(f"\n[OTP GENERATED] {otp} — email:{email} phone:+91{phone_clean} ip:{client_ip}\n")

    channels = []
    if result["email"]["success"]:
        channels.append("Email")
    if result["sms"]["success"]:
        channels.append("SMS")
    channel_str = " & ".join(channels) if channels else "Terminal (check console)"

    return jsonify({
        "success": True,
        "message": f"OTP sent via {channel_str}",
        "expires_in": config.OTP_EXPIRY_SECONDS,
        "email_masked": email[:2] + "***@" + email.split("@")[-1],
        "phone_masked": "+91" + phone_clean[:2] + "XXXXX" + phone_clean[-3:],
    })


@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data      = request.get_json()
    user_otp  = data.get("otp", "").strip()
    stored    = session.get("otp")
    expires   = session.get("otp_expires_at")

    if not stored:
        return jsonify({"success": False, "message": "No OTP found. Please resend."}), 400

    # Expiry check
    if expires:
        exp_dt = datetime.fromisoformat(expires)
        if datetime.utcnow() > exp_dt:
            session.pop("otp", None)
            return jsonify({"success": False, "message": "OTP has expired. Please resend."}), 400

    user_otp_upper = user_otp.upper().strip()
    stored_upper   = (stored or "").upper().strip()
    print(f"[OTP VERIFY] entered={user_otp_upper!r} stored={stored_upper!r} match={user_otp_upper==stored_upper}")

    if user_otp_upper != stored_upper:
        return jsonify({"success": False, "message": f"Incorrect OTP. Please try again."}), 400

    # OTP verified — store approval in session
    session["otp_verified"] = True
    session.pop("otp", None)
    session.modified = True
    return jsonify({"success": True, "message": "OTP verified! Processing payment…"})


@app.route("/place-order", methods=["POST"])
def place_order():
    if not session.get("otp_verified"):
        return jsonify({"success": False, "message": "OTP not verified."}), 403

    data           = request.get_json()
    cart_data      = get_cart()
    if not cart_data:
        return jsonify({"success": False, "message": "Cart is empty."}), 400

    subtotal       = cart_total(cart_data)
    tax            = round(subtotal * config.TAX_RATE, 2)
    total          = round(subtotal + tax, 2)
    order_id       = generate_order_id()

    order = Order(
        order_id        = order_id,
        customer_name   = data.get("name", session.get("checkout_name", "")),
        customer_email  = data.get("email", session.get("otp_email", "")),
        customer_phone  = data.get("phone", session.get("otp_phone", "")),
        address         = data.get("address", ""),
        payment_method  = data.get("payment_method", ""),
        payment_detail  = data.get("payment_detail", ""),
        items_json      = json.dumps(list(cart_data.values())),
        subtotal        = subtotal,
        tax             = tax,
        total           = total,
        status          = "Confirmed",
    )
    db.session.add(order)

    # Reduce stock
    for pid, item in cart_data.items():
        product = Product.query.get(int(pid))
        if product:
            product.stock = max(0, product.stock - item["qty"])
    db.session.commit()

    # Clear cart & OTP flag
    save_cart({})
    session.pop("otp_verified", None)
    session["last_order_id"] = order_id
    session.modified = True

    # Send order confirmation email (in background thread)
    def send_confirm():
        send_order_confirmation_email(order.customer_email, order)
    Timer(1, send_confirm).start()

    # Emit live order status events via threading timers
    def emit_processing():
        socketio.emit("order_status", {"order_id": order_id, "status": "Processing"})
    def emit_dispatched():
        socketio.emit("order_status", {"order_id": order_id, "status": "Dispatched"})
    Timer(3, emit_processing).start()
    Timer(8, emit_dispatched).start()

    return jsonify({"success": True, "order_id": order_id, "redirect": url_for("success")})


@app.route("/success")
def success():
    order_id = session.get("last_order_id")
    if not order_id:
        return redirect(url_for("index"))
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return redirect(url_for("index"))
    return render_template("success.html", order=order, currency=config.CURRENCY)


@app.route("/orders")
def orders():
    """Order history — shows last 10 orders."""
    all_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template("orders.html", orders=all_orders, currency=config.CURRENCY)


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCT DETAIL + REVIEWS + WISHLIST
# ══════════════════════════════════════════════════════════════════════════════

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product      = Product.query.get_or_404(product_id)
    reviews_list = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    related      = Product.query.filter(Product.category == product.category, Product.id != product_id).limit(6).all()

    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews_list:
        rating_counts[r.rating] = rating_counts.get(r.rating, 0) + 1
    total_reviews    = len(reviews_list)
    rating_breakdown = {k: (v / total_reviews * 100 if total_reviews else 0) for k, v in rating_counts.items()}

    sid        = session.get("sid", request.remote_addr)
    in_wishlist = Wishlist.query.filter_by(session_id=sid, product_id=product_id).first() is not None
    cart_count = sum(i["qty"] for i in get_cart().values())
    return render_template(
        "product.html",
        product=product, reviews=reviews_list, related=related,
        rating_breakdown=rating_breakdown, rating_counts=rating_counts,
        total_reviews=total_reviews, in_wishlist=in_wishlist,
        cart_count=cart_count, currency=config.CURRENCY
    )


@app.route("/api/product/<int:product_id>/review", methods=["POST"])
def add_review(product_id):
    product   = Product.query.get_or_404(product_id)
    data      = request.get_json()
    user_name = data.get("user_name", "").strip()
    rating    = int(data.get("rating", 0))
    title     = data.get("title", "").strip()
    body      = data.get("body", "").strip()
    if not user_name or not body or rating < 1 or rating > 5:
        return jsonify({"success": False, "message": "Please provide your name, rating, and review."}), 400
    review = Review(product_id=product_id, user_name=user_name, rating=rating, title=title, body=body)
    db.session.add(review)
    db.session.flush()
    all_r          = Review.query.filter_by(product_id=product_id).all()
    product.rating = round(sum(r.rating for r in all_r) / len(all_r), 1)
    product.reviews = len(all_r)
    db.session.commit()
    return jsonify({"success": True, "review": review.to_dict()})


@app.route("/api/wishlist/toggle", methods=["POST"])
def wishlist_toggle():
    data       = request.get_json()
    product_id = data.get("product_id")
    sid        = session.get("sid", request.remote_addr)
    existing   = Wishlist.query.filter_by(session_id=sid, product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"success": True, "in_wishlist": False})
    db.session.add(Wishlist(session_id=sid, product_id=product_id))
    db.session.commit()
    return jsonify({"success": True, "in_wishlist": True})


@app.route("/api/wishlist")
def get_wishlist():
    sid   = session.get("sid", request.remote_addr)
    items = Wishlist.query.filter_by(session_id=sid).all()
    return jsonify({"product_ids": [i.product_id for i in items], "count": len(items)})


# ══════════════════════════════════════════════════════════════════════════════
# SOCKET.IO EVENTS
# ══════════════════════════════════════════════════════════════════════════════

@socketio.on("connect")
def on_connect():
    session["sid"] = request.sid
    join_room(request.sid)
    cart_count = sum(i["qty"] for i in get_cart().values())
    emit("cart_update", {"count": cart_count})


@socketio.on("ping_stock")
def on_ping_stock(data):
    product_id = data.get("product_id")
    product    = Product.query.get(product_id)
    if product:
        emit("stock_update", {"product_id": product_id, "stock": product.stock})



# ══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def _pending_orders():
    return Order.query.filter(Order.status.in_(['Confirmed','Processing'])).count()

@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username','').strip()
        password = request.form.get('password','').strip()
        if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user'] = username
            return redirect(url_for('admin_dashboard'))
        error = "Invalid username or password."
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_user', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    from datetime import datetime as dt
    all_orders      = Order.query.all()
    total_orders    = len(all_orders)
    total_revenue   = sum(o.total for o in all_orders)
    total_products  = Product.query.count()
    total_customers = User.query.count()
    pending_orders  = _pending_orders()
    low_stock       = Product.query.filter(Product.stock <= 10).count()
    avg_val         = (total_revenue / total_orders) if total_orders else 0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    for o in recent_orders:
        pass


    low_stock_products = Product.query.filter(Product.stock <= 10).order_by(Product.stock.asc()).limit(8).all()

    # ── Category revenue (from order items) ──
    cat_colors = ['#6366f1','#8b5cf6','#06b6d4','#22c55e','#f97316','#ec4899','#fbbf24','#a855f7','#14b8a6','#ef4444']
    cat_rev = {}
    for o in all_orders:
        try:
            items = json.loads(o.items_json or '[]')
            for item in items:
                cat = item.get('category', 'Other')
                cat_rev[cat] = cat_rev.get(cat, 0) + float(item.get('price', 0)) * int(item.get('qty', 1))
        except: pass

    # Fallback: use product counts if no orders
    if not cat_rev:
        cats = db.session.query(Product.category, db.func.count(Product.id)).group_by(Product.category).all()
        for c, n in cats:
            cat_rev[c] = n * 1000.0

    max_rev = max(cat_rev.values()) if cat_rev else 1
    category_stats = [
        {'name': c, 'revenue': rev, 'rev_pct': int(rev / max_rev * 100), 'color': cat_colors[i % len(cat_colors)]}
        for i, (c, rev) in enumerate(sorted(cat_rev.items(), key=lambda x: -x[1])[:10])
    ]

    # ── Payment method breakdown ──
    pay_icons  = {'card': '💳', 'upi': '📱', 'netbanking': '🏦', 'cod': '💵', '': '💳'}
    pay_colors = {'card': '#6366f1', 'upi': '#22c55e', 'netbanking': '#06b6d4', 'cod': '#fbbf24', '': '#6366f1'}
    pay_data = {}
    for o in all_orders:
        m = (o.payment_method or 'card').lower()
        if m not in pay_data: pay_data[m] = {'count': 0, 'revenue': 0.0}
        pay_data[m]['count']   += 1
        pay_data[m]['revenue'] += o.total
    tot_pay = total_orders or 1
    payment_stats = [
        {'method': m, 'icon': pay_icons.get(m, '💳'), 'color': pay_colors.get(m, '#6366f1'),
         'count': d['count'], 'revenue': d['revenue'], 'pct': int(d['count'] / tot_pay * 100)}
        for m, d in sorted(pay_data.items(), key=lambda x: -x[1]['count'])
    ]

    # ── Top products by revenue ──
    prod_rev = {}
    prod_meta = {}
    for o in all_orders:
        try:
            items = json.loads(o.items_json or '[]')
            for item in items:
                pid = item.get('id', item.get('name', '?'))
                rev = float(item.get('price', 0)) * int(item.get('qty', 1))
                prod_rev[pid] = prod_rev.get(pid, 0) + rev
                prod_meta[pid] = {'name': item.get('name', 'Unknown'), 'category': item.get('category', '—'),
                                  'units': prod_meta.get(pid, {}).get('units', 0) + int(item.get('qty', 1))}
        except: pass
    top_products = [
        {'name': prod_meta[p]['name'], 'category': prod_meta[p]['category'],
         'units': prod_meta[p]['units'], 'revenue': prod_rev[p]}
        for p in sorted(prod_rev, key=lambda x: -prod_rev[x])[:8]
    ]

    # ── Order status breakdown ──
    status_colors = {'Confirmed':'#6366f1','Processing':'#fbbf24','Dispatched':'#06b6d4','Delivered':'#22c55e','Cancelled':'#ef4444'}
    statuses = db.session.query(Order.status, db.func.count(Order.id)).group_by(Order.status).all()
    order_status_stats = [{'status': s, 'count': n, 'pct': int(n/(total_orders or 1)*100), 'color': status_colors.get(s,'#6366f1')}
                          for s, n in statuses]

    return render_template('admin/dashboard.html',
        active='dashboard', pending_orders=pending_orders,
        now=dt.now().strftime('%d %b %Y, %I:%M %p'),
        stats={
            'total_orders': total_orders, 'total_revenue': total_revenue,
            'total_products': total_products, 'total_customers': total_customers,
            'pending_orders': pending_orders, 'low_stock': low_stock,
            'avg_order_value': avg_val
        },
        recent_orders=recent_orders,
        low_stock_products=low_stock_products,
        category_stats=category_stats,
        payment_stats=payment_stats,
        top_products=top_products,
        order_status_stats=order_status_stats
    )

@app.route('/admin/orders')
@admin_required
def admin_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', active='orders',
                           orders=orders, pending_orders=_pending_orders())

@app.route('/admin/orders/<int:order_id>/status', methods=['POST'])
@admin_required
def admin_update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status','').strip()
    allowed = ['Confirmed','Processing','Dispatched','Delivered','Cancelled']
    if new_status not in allowed:
        return jsonify({'success': False, 'error': 'Invalid status'})
    order = Order.query.get_or_404(order_id)
    order.status = new_status
    db.session.commit()
    return jsonify({'success': True, 'status': new_status})

@app.route('/admin/orders/<int:order_id>')
@admin_required
def admin_order_detail(order_id):
    return redirect(url_for('admin_orders'))

@app.route('/admin/products')
@admin_required
def admin_products():
    products = Product.query.order_by(Product.category, Product.name).all()
    categories = sorted(set(p.category for p in products))
    return render_template('admin/products.html', active='products',
                           products=products, categories=categories,
                           pending_orders=_pending_orders())

@app.route('/admin/products/<int:product_id>/stock', methods=['POST'])
@admin_required
def admin_update_stock(product_id):
    data = request.get_json()
    new_stock = data.get('stock')
    if new_stock is None or int(new_stock) < 0:
        return jsonify({'success': False, 'error': 'Invalid stock'})
    product = Product.query.get_or_404(product_id)
    product.stock = int(new_stock)
    db.session.commit()
    return jsonify({'success': True, 'stock': product.stock})

@app.route('/admin/products/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    categories = sorted(set(p.category for p in Product.query.all()))
    success = None
    error   = None

    if request.method == 'POST':
        try:
            name          = request.form.get('name','').strip()
            brand         = request.form.get('brand','NexusShop').strip()
            category      = request.form.get('category','').strip()
            new_category  = request.form.get('new_category','').strip()
            description   = request.form.get('description','').strip()
            price         = float(request.form.get('price', 0))
            original_price= request.form.get('original_price','').strip()
            stock         = int(request.form.get('stock', 50))
            rating        = float(request.form.get('rating', 4.5))
            image_url     = request.form.get('image_url','').strip()
            image_emoji   = request.form.get('image_emoji','📦').strip()
            badge         = request.form.get('badge','').strip() or None
            highlights    = [h.strip() for h in request.form.getlist('highlights[]') if h.strip()]
            spec_keys     = request.form.getlist('spec_keys[]')
            spec_vals     = request.form.getlist('spec_vals[]')

            if not name:   raise ValueError("Product name is required.")
            if not category: raise ValueError("Category is required.")
            if price <= 0: raise ValueError("Price must be greater than 0.")
            if category == '__new__':
                if not new_category: raise ValueError("Please enter the new category name.")
                category = new_category

            specs = {k.strip(): v.strip() for k,v in zip(spec_keys, spec_vals) if k.strip() and v.strip()}

            product = Product(
                name           = name,
                brand          = brand,
                category       = category,
                description    = description,
                price          = price,
                original_price = float(original_price) if original_price else None,
                stock          = stock,
                rating         = min(5.0, max(1.0, rating)),
                reviews        = 0,
                image_url      = image_url if image_url else None,
                image_emoji    = image_emoji or '📦',
                image_color    = '#6366f1',
                badge          = badge,
                highlights     = json.dumps(highlights) if highlights else None,
                specs_json     = json.dumps(specs) if specs else None,
            )
            db.session.add(product)
            db.session.commit()
            success = name
            categories = sorted(set(p.category for p in Product.query.all()))
        except ValueError as e:
            error = str(e)
        except Exception as e:
            error = f"Unexpected error: {e}"

    return render_template('admin/add_product.html',
                           active='add_product',
                           categories=categories,
                           pending_orders=_pending_orders(),
                           success=success, error=error)

@app.route('/admin/products/<int:product_id>/edit')
@admin_required
def admin_edit_product(product_id):
    return redirect(url_for('admin_products'))

@app.route('/admin/customers')
@admin_required
def admin_customers():
    users = User.query.order_by(User.created_at.desc()).all()
    customers = []
    for u in users:
        orders = Order.query.filter_by(customer_email=u.email).all()
        spent  = sum(o.total for o in orders)
        u.order_count = len(orders)
        u.total_spent = spent
        customers.append(u)
    return render_template('admin/customers.html', active='customers',
                           customers=customers, pending_orders=_pending_orders())


# ══════════════════════════════════════════════════════════════════════════════

@app.route('/admin/users')
@admin_required
def admin_users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    for u in all_users:
        orders = Order.query.filter_by(customer_email=u.email).all()
        u.order_count = len(orders)
        u.total_spent = sum(o.total for o in orders)
    return render_template('admin/users.html', active='users',
                           users=all_users, pending_orders=_pending_orders())

@app.route('/admin/users/<int:user_id>/detail')
@admin_required
def admin_user_detail(user_id):
    u = User.query.get_or_404(user_id)
    orders = Order.query.filter_by(customer_email=u.email).order_by(Order.created_at.desc()).all()
    total_spent = sum(o.total for o in orders)
    order_list = []
    for o in orders:
        try: items = json.loads(o.items_json or '[]')
        except: items = []
        order_list.append({
            'order_id': o.order_id, 'item_count': len(items),
            'payment_method': o.payment_method or '---',
            'total': round(o.total, 2), 'status': o.status,
            'date': o.created_at.strftime('%d %b %Y, %H:%M'),
        })
    return jsonify({
        'id': u.id, 'name': u.name, 'email': u.email,
        'phone': u.phone or '', 'address': u.address or '',
        'password_hash': u.password,
        'joined': u.created_at.strftime('%d %b %Y, %I:%M %p'),
        'order_count': len(orders), 'total_spent': round(total_spent, 2),
        'avg_order': round(total_spent / len(orders), 2) if orders else 0,
        'orders': order_list,
    })

@app.route("/order/received/<order_id>")
def order_received(order_id):
    from datetime import datetime as dt
    order = Order.query.filter_by(order_id=order_id).first()
    if not order:
        return render_template("order_received.html",
                               success=False, already=False, order=None,
                               now=dt.now().strftime("%d %b %Y, %I:%M %p"))
    # Parse items handled by models.py property

    already = (order.status == "Delivered")
    if not already:
        order.status = "Delivered"
        db.session.commit()
        # Notify admin via socket
        try:
            socketio.emit("order_update", {"order_id": order_id, "status": "Delivered"})
        except Exception:
            pass

    return render_template("order_received.html",
                           success=True, already=already, order=order,
                           now=dt.now().strftime("%d %b %Y, %I:%M %p"))


# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print(f"\n{'='*55}")
    print(f"  [SHOP]  NexusShop -- Advanced E-Commerce + OTP Payment")
    print(f"{'='*55}")
    print(f"  [WEB]   http://localhost:5000")
    print(f"  [ADMIN] Admin:  http://localhost:5000/admin")
    print(f"  [EMAIL] Email OTP: {'OK - Configured' if config.EMAIL_ENABLED else 'WARN - Terminal fallback (set EMAIL_ADDRESS in config.py)'}")
    print(f"  [SMS]   SMS OTP:   {'OK - Configured' if config.SMS_ENABLED   else 'WARN - Terminal fallback (set FAST2SMS_API_KEY in config.py)'}")
    print(f"{'='*55}\n")
    socketio.run(app, debug=config.DEBUG, host="0.0.0.0", port=5000, use_reloader=False, allow_unsafe_werkzeug=True)

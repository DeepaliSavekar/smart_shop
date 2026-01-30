from flask import Flask, request, jsonify, render_template, flash, session
from flask_cors import CORS
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for
from datetime import datetime
import random
from twilio.rest import Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', os.urandom(32))
app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access to session cookie
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes session timeout

# MySQL CONNECTION
db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME', 'smartshopping')
)

cursor = db.cursor(dictionary=True)

# TWILIO CONFIG
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')

client = Client(ACCOUNT_SID, AUTH_TOKEN) if ACCOUNT_SID and AUTH_TOKEN else None

# CREATE TABLES
def create_tables():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(15),
            password VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            price INT,
            img VARCHAR(255),
            category VARCHAR(50)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            price INT,
            img VARCHAR(255),
            quantity INT DEFAULT 1
        )
    """)

    # E-WALLET TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallet (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE,
            balance DECIMAL(10, 2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # CREDIT CARDS TABLE - Note: Card numbers are masked, CVV is NOT stored
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS credit_cards (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            card_number_last4 VARCHAR(4),
            card_holder_name VARCHAR(100),
            expiry_date VARCHAR(7),
            card_type VARCHAR(20),
            is_default BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # TRANSACTIONS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            transaction_type ENUM('credit', 'debit', 'deposit') NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            description VARCHAR(255),
            payment_method VARCHAR(50),
            status ENUM('success', 'failed', 'pending') DEFAULT 'success',
            balance_after DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # ORDERS TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            total_amount DECIMAL(10, 2),
            payment_method VARCHAR(50),
            order_status VARCHAR(50) DEFAULT 'Processing',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    db.commit()

# SEED PRODUCTS
def seed_products():
    cursor.execute("SELECT COUNT(*) AS total FROM products")
    count = cursor.fetchone()['total']

    if count == 0:
        products_list = [
            ("Pampers Diapers (Pack of 40)", 650, "/images/diapers.png", "baby"),
            ("Baby Lotion (Himalaya, 200ml)", 180, "/images/babylotion.jpg", "baby"),
            ("Baby Shampoo (Johnson's, 100ml)", 120, "/images/babyshampoo.jpg", "baby"),
            ("Baby Soap (Dove, 4 pcs)", 150, "/images/babysoap.jpg", "baby"),
            ("Baby Powder (Johnson's, 200g)", 160, "/images/babypowder.jpg", "baby"),
            ("Baby Oil (Johnson's, 200ml)", 140, "/images/babyoil.jpg", "baby"),
            ("Feeding Bottle (Philips Avent, 250ml)", 499, "/images/feeding-bottle.jpg", "baby"),
            ("Baby Toothbrush (Pigeon Soft Grip)", 120, "/images/brush.jpg", "baby"),
            ("Baby Cream (Himalaya, 50g)", 90, "/images/babycream.jpg", "baby"),
            ("Baby Cloth Set", 400, "/images/babycloth.jpg", "baby"),
            ("Lipstick (Lakme, 4g)", 350, "/images/lipstick.jpg", "beauty"),
            ("Eyeliner (Maybelline, 3ml)", 220, "/images/eyeliner.jpg", "beauty"),
            ("Foundation (L'Oréal, 30ml)", 450, "/images/foundation.jpg", "beauty"),
            ("Compact Powder (Lakme, 9g)", 250, "/images/compact.jpg", "beauty"),
            ("Nail Polish (Colorbar, 6ml)", 180, "/images/nailpolish.jpg", "beauty"),
            ("Makeup Brush Set", 300, "/images/brushset.jpg", "beauty"),
            ("Perfume (Fogg, 100ml)", 320, "/images/perfume.jpg", "beauty"),
            ("Face Mask (Sheet, Pack of 3)", 150, "/images/facemask.jpg", "beauty"),
            ("Makeup Remover (Garnier, 125ml)", 190, "/images/remover.jpg", "beauty"),
            ("Kajal (Himalaya, 1.2g)", 120, "/images/kajal.jpg", "beauty")
        ]

        cursor.executemany("""
            INSERT INTO products (name, price, img, category)
            VALUES (%s, %s, %s, %s)
        """, products_list)
        db.commit()
        print("✅ Products inserted successfully!")

# ========== BASIC ROUTES ==========

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/home')
def home():
    return render_template("home.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get("fullname")
        email = request.form.get("email")
        phone = request.form.get("mobile")
        password = request.form.get("password")

        if not name or not email or not password:
            return "All fields are required!", 400

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return "Email already registered!", 400

        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (name, email, phone, password) VALUES (%s, %s, %s, %s)",
            (name, email, phone, hashed_password)
        )
        db.commit()
        
        # Create wallet for new user
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO wallet (user_id, balance) VALUES (%s, 0.00)", (user_id,))
        db.commit()

        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect("/home")
        else:
            return "Invalid credentials!", 401

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/send_otp", methods=["POST"])
def send_otp():
    phone = request.form.get("phone")

    if not phone:
        flash("Phone number required")
        return redirect(url_for("index"))

    # Rate limiting check (basic implementation)
    if 'last_otp_time' in session:
        from datetime import datetime, timedelta
        last_time = datetime.fromisoformat(session['last_otp_time'])
        if datetime.now() - last_time < timedelta(seconds=60):
            flash("Please wait 60 seconds before requesting another OTP")
            return redirect(url_for("index"))

    otp = random.randint(100000, 999999)
    session["otp"] = str(otp)
    session["phone"] = phone
    session["last_otp_time"] = datetime.now().isoformat()

    if client:  # Only send if Twilio is configured
        try:
            client.messages.create(
                body=f"Your OTP for Smart Shopping System is {otp}",
                from_=TWILIO_PHONE,
                to=phone
            )
            flash("OTP sent successfully")
        except Exception as e:
            flash("Failed to send OTP")
            print(f"Twilio error: {e}")
    else:
        # For development without Twilio
        print(f"Development mode - OTP: {otp}")
        flash("OTP sent (check console in development mode)")

    return redirect(url_for("index"))

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    entered_otp = request.form.get("otp")
    session_otp = session.get("otp")

    if entered_otp == session_otp:
        session.pop("otp", None)
        session.pop("phone", None)
        return redirect(url_for("login"))
    else:
        flash("Invalid OTP")
        return redirect(url_for("register"))

# ========== PAGE ROUTES ==========

@app.route("/category.html")
def category():
    return render_template("category.html")

@app.route('/offers')
def offers():
    return render_template("offers.html")

@app.route('/stores')
def stores():
    return render_template("stores.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/help-centre')
def help_centre():
    return render_template("Help_centre.html")

@app.route('/delivery-info')
def delivery_info():
    return render_template("delivery_info.html")

@app.route('/returns-policy')
def returns_policy():
    return render_template("Return_policy.html")

@app.route('/cart')
def cart():
    return render_template("cart.html")

@app.route('/wallet')
def wallet():
    return render_template("wallet.html")

@app.route('/grocery')
def grocery():
    return render_template("grocery.html")

@app.route('/fruits')
def fruits():
    return render_template("fruits.html")

@app.route('/dairy')
def dairy():
    return render_template("dairy.html")

@app.route('/snacks')
def snacks():
    return render_template("snacks.html")

@app.route('/household')
def household():
    return render_template("household.html")

@app.route('/personal')
def personal():
    return render_template("personal.html")

@app.route('/baby')
def baby():
    return render_template("baby.html")

@app.route('/beauty')
def beauty():
    return render_template("beauty.html")

@app.route('/stationery')
def stationery():
    return render_template("stationery.html")

@app.route('/pooja')
def pooja():
    return render_template("pooja.html")

@app.route('/buy_to_get_one')
def buy_to_get_one():
    return render_template("buy_to_get_one.html")

@app.route('/cleaning_essentials')
def cleaning_essentials():
    return render_template("cleaning_essentials.html")

@app.route('/fresh_fruits')
def fresh_fruits():
    return render_template("fresh_fruits.html")

@app.route('/Milk_Dairy_Products')
def Milk_Dairy_Products():
    return render_template("Milk_Dairy_Products.html")

@app.route('/fresh_vegetables')
def fresh_vegetables():
    return render_template("fresh_vegetables.html")

# ========== PRODUCT & CART API ==========

@app.route('/api/products/<category_name>', methods=['GET'])
def get_products(category_name):
    cursor.execute("SELECT * FROM products WHERE category=%s", (category_name,))
    products = cursor.fetchall()
    return jsonify(products)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    name = data['name']

    cursor.execute("SELECT * FROM cart WHERE name=%s", (name,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE name=%s",
            (name,)
        )
    else:
        cursor.execute(
            "INSERT INTO cart (name, price, img, quantity) VALUES (%s, %s, %s, 1)",
            (data['name'], data['price'], data['img'])
        )

    db.commit()
    return jsonify({"message": "Item added/updated"})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    cursor.execute("SELECT * FROM cart")
    items = cursor.fetchall()
    return jsonify(items)

@app.route('/api/cart/update/<int:item_id>', methods=['PUT'])
def update_cart(item_id):
    data = request.json
    change = data['change']

    cursor.execute("UPDATE cart SET quantity = quantity + %s WHERE id=%s",
                   (change, item_id))
    db.commit()

    cursor.execute("DELETE FROM cart WHERE quantity <= 0")
    db.commit()

    return jsonify({"message": "Cart updated"})

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_item(item_id):
    cursor.execute("DELETE FROM cart WHERE id=%s", (item_id,))
    db.commit()
    return jsonify({"message": "Item removed"})

# ========== E-WALLET API ==========

@app.route('/api/wallet/balance', methods=['GET'])
def get_wallet_balance():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    cursor.execute("SELECT balance FROM wallet WHERE user_id=%s", (user_id,))
    wallet = cursor.fetchone()
    
    if wallet:
        return jsonify({"balance": float(wallet['balance'])})
    return jsonify({"balance": 0.00})

@app.route('/api/wallet/deposit', methods=['POST'])
def deposit_to_wallet():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    amount = float(data.get('amount', 0))
    card_id = data.get('card_id')

    if amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    # Get current balance
    cursor.execute("SELECT balance FROM wallet WHERE user_id=%s", (user_id,))
    wallet = cursor.fetchone()
    
    if wallet:
        current_balance = float(wallet['balance'])
        new_balance = current_balance + amount
        cursor.execute("UPDATE wallet SET balance=%s WHERE user_id=%s", (new_balance, user_id))
    else:
        current_balance = 0.00
        new_balance = amount
        cursor.execute("INSERT INTO wallet (user_id, balance) VALUES (%s, %s)", (user_id, new_balance))
    
    # Record transaction
    cursor.execute("""
        INSERT INTO transactions (user_id, transaction_type, amount, description, payment_method, balance_after)
        VALUES (%s, 'deposit', %s, %s, %s, %s)
    """, (user_id, amount, f"Deposit to wallet", "Credit Card", new_balance))
    
    db.commit()

    return jsonify({
        "success": True,
        "message": "Amount deposited successfully",
        "new_balance": new_balance
    })

@app.route('/api/wallet/pay', methods=['POST'])
def pay_from_wallet():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    amount = float(data.get('amount', 0))
    description = data.get('description', 'Purchase')

    # Check wallet balance
    cursor.execute("SELECT balance FROM wallet WHERE user_id=%s", (user_id,))
    wallet = cursor.fetchone()
    current_balance = float(wallet['balance']) if wallet else 0.00

    if current_balance < amount:
        return jsonify({"error": "Insufficient balance", "current_balance": current_balance}), 400

    new_balance = current_balance - amount

    # Update wallet
    cursor.execute("UPDATE wallet SET balance=%s WHERE user_id=%s", (new_balance, user_id))
    
    # Record transaction
    cursor.execute("""
        INSERT INTO transactions (user_id, transaction_type, amount, description, payment_method, balance_after)
        VALUES (%s, 'debit', %s, %s, 'E-Wallet', %s)
    """, (user_id, amount, description, new_balance))
    
    # Create order
    cursor.execute("""
        INSERT INTO orders (user_id, total_amount, payment_method)
        VALUES (%s, %s, 'E-Wallet')
    """, (user_id, amount))
    
    db.commit()

    return jsonify({
        "success": True,
        "message": "Payment successful",
        "new_balance": new_balance
    })

# ========== CREDIT CARD API ==========

@app.route('/api/cards', methods=['GET'])
def get_cards():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    cursor.execute("SELECT * FROM credit_cards WHERE user_id=%s ORDER BY is_default DESC", (user_id,))
    cards = cursor.fetchall()
    
    # Format card display (already only storing last 4 digits)
    for card in cards:
        card['card_number'] = '**** **** **** ' + card.get('card_number_last4', '****')
    
    return jsonify(cards)

@app.route('/api/cards/add', methods=['POST'])
def add_card():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.json
    card_number = data.get('card_number', '').replace(' ', '')
    card_holder = data.get('card_holder_name')
    expiry = data.get('expiry_date')
    # Note: CVV is NOT stored for security reasons
    
    # Basic validation
    if len(card_number) < 13 or len(card_number) > 19:
        return jsonify({"error": "Invalid card number"}), 400
    
    # Determine card type
    card_type = "Unknown"
    if card_number.startswith('4'):
        card_type = "Visa"
    elif card_number.startswith('5'):
        card_type = "Mastercard"
    elif card_number.startswith('3'):
        card_type = "Amex"

    # Only store last 4 digits for security
    last4 = card_number[-4:]

    cursor.execute("""
        INSERT INTO credit_cards (user_id, card_number_last4, card_holder_name, expiry_date, card_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (user_id, last4, card_holder, expiry, card_type))
    
    db.commit()

    return jsonify({"success": True, "message": "Card added successfully"})

@app.route('/api/cards/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    cursor.execute("DELETE FROM credit_cards WHERE id=%s AND user_id=%s", (card_id, user_id))
    db.commit()

    return jsonify({"success": True, "message": "Card deleted"})

# ========== TRANSACTION HISTORY ==========

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    cursor.execute("""
        SELECT * FROM transactions 
        WHERE user_id=%s 
        ORDER BY created_at DESC 
        LIMIT 50
    """, (user_id,))
    
    transactions = cursor.fetchall()
    
    # Format dates
    for txn in transactions:
        txn['created_at'] = txn['created_at'].strftime('%Y-%m-%d %H:%M:%S')
        txn['amount'] = float(txn['amount'])
        txn['balance_after'] = float(txn['balance_after'])
    
    return jsonify(transactions)

# ========== START SERVER ==========

if __name__ == '__main__':
    create_tables()
    seed_products()
    
    # Get environment settings
    flask_env = os.getenv('FLASK_ENV', 'production')
    debug_mode = flask_env == 'development'
    
    if debug_mode:
        print("⚠️  Running in DEVELOPMENT mode")
    print("🚀 Flask running on http://127.0.0.1:5000/")
    
    app.run(debug=debug_mode, host='127.0.0.1')
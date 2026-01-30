# Smart Shopping System 🛒

A secure e-commerce web application built with Flask, featuring user authentication, shopping cart, e-wallet, and payment processing.

## Features

- 🔐 Secure user authentication with password hashing
- 📱 OTP verification via Twilio
- 🛍️ Product catalog with multiple categories
- 🛒 Shopping cart functionality
- 💳 E-wallet system
- 💰 Credit card management (PCI-compliant - only stores last 4 digits)
- 📊 Transaction history
- 🔒 Session management with security best practices

## Security Features

- ✅ Environment-based configuration (no hardcoded credentials)
- ✅ Password hashing with Werkzeug
- ✅ Secure session cookies (HTTPOnly, Secure, SameSite)
- ✅ Session timeout (30 minutes)
- ✅ Rate limiting on OTP requests
- ✅ PCI-compliant card storage (only last 4 digits, no CVV storage)
- ✅ SQL injection protection with parameterized queries
- ✅ Debug mode disabled in production

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- Twilio account (for OTP functionality)

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd Final_Project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up MySQL database**
   ```sql
   CREATE DATABASE smartshopping;
   ```

6. **Configure environment variables**
   - Copy `.env.example` to `.env`
     ```bash
     copy .env.example .env
     ```
   - Edit `.env` and fill in your actual credentials:
     ```env
     # Twilio Configuration
     TWILIO_ACCOUNT_SID=your_actual_twilio_sid
     TWILIO_AUTH_TOKEN=your_actual_twilio_token
     TWILIO_PHONE=your_twilio_phone_number
     
     # Database Configuration
     DB_HOST=localhost
     DB_USER=root
     DB_PASSWORD=your_mysql_password
     DB_NAME=smartshopping
     
     # Flask Configuration
     SECRET_KEY=generate_a_random_secret_key_here
     FLASK_ENV=development
     ```

7. **Generate a secure SECRET_KEY**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and paste it as your `SECRET_KEY` in `.env`

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Access the application**
   Open your browser and navigate to: `http://127.0.0.1:5000/`

## Project Structure

```
Final_Project/
├── app.py                  # Main application file
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (NOT in git)
├── .env.example           # Example environment file
├── .gitignore             # Git ignore rules
├── static/                # Static files (CSS, JS, images)
│   └── images/           # Product images
└── templates/            # HTML templates
    ├── index.html
    ├── home.html
    ├── login.html
    ├── register.html
    ├── cart.html
    ├── wallet.html
    └── ...
```

## Database Schema

The application automatically creates the following tables:
- `users` - User accounts
- `products` - Product catalog
- `cart` - Shopping cart items
- `wallet` - E-wallet balances
- `credit_cards` - Saved payment methods (PCI-compliant)
- `transactions` - Transaction history
- `orders` - Order records

## Security Best Practices

### For Developers

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use strong SECRET_KEY** - Generate using `secrets.token_hex(32)`
3. **Keep dependencies updated** - Run `pip list --outdated` regularly
4. **Use HTTPS in production** - Set `SESSION_COOKIE_SECURE = True`
5. **Review code for SQL injection** - Always use parameterized queries
6. **Limit sensitive data** - Never store full card numbers or CVVs

### For Production Deployment

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Enable HTTPS with SSL certificates
4. Set up proper firewall rules
5. Use environment-specific `.env` files
6. Enable database backups
7. Implement proper logging and monitoring

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout
- `POST /send_otp` - Send OTP for verification
- `POST /verify-otp` - Verify OTP

### Products
- `GET /api/products/<category>` - Get products by category

### Cart
- `GET /api/cart` - Get cart items
- `POST /api/cart/add` - Add item to cart
- `PUT /api/cart/update/<id>` - Update cart item quantity
- `DELETE /api/cart/<id>` - Remove item from cart

### Wallet
- `GET /api/wallet/balance` - Get wallet balance
- `POST /api/wallet/deposit` - Deposit to wallet
- `POST /api/wallet/pay` - Pay from wallet

### Cards
- `GET /api/cards` - Get saved cards
- `POST /api/cards/add` - Add new card
- `DELETE /api/cards/<id>` - Delete card

### Transactions
- `GET /api/transactions` - Get transaction history

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- Flask framework
- MySQL database
- Twilio API for OTP
- All contributors and testers

---

**⚠️ IMPORTANT SECURITY NOTICE**

Before deploying to production:
1. ✅ Ensure `.env` is in `.gitignore`
2. ✅ Use strong, unique passwords and keys
3. ✅ Enable HTTPS
4. ✅ Set `FLASK_ENV=production`
5. ✅ Review all security configurations
6. ✅ Never commit sensitive credentials to version control

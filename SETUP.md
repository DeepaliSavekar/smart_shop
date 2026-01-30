# Setup Instructions for Smart Shopping System

## Quick Setup Guide

Follow these steps to set up your project securely:

### 1. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install required packages
pip install -r requirements.txt
```

### 2. Generate Secure Keys

```bash
python generate_keys.py
```

Copy the generated `SECRET_KEY` for the next step.

### 3. Configure Environment Variables

```bash
# Copy the example file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
```

Edit `.env` and fill in your actual credentials:

```env
# Twilio Configuration (get from https://www.twilio.com/console)
TWILIO_ACCOUNT_SID=your_actual_account_sid
TWILIO_AUTH_TOKEN=your_actual_auth_token
TWILIO_PHONE=your_twilio_phone_number

# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smartshopping

# Flask Configuration
SECRET_KEY=paste_the_generated_key_here
FLASK_ENV=development
```

### 4. Set Up MySQL Database

```sql
CREATE DATABASE smartshopping;
```

### 5. Run the Application

```bash
python app.py
```

The application will:
- Automatically create all required database tables
- Seed initial product data
- Start the Flask development server

### 6. Access the Application

Open your browser and go to: `http://127.0.0.1:5000/`

## Security Checklist

Before pushing to GitHub:

- [x] `.env` file is in `.gitignore`
- [x] No hardcoded credentials in code
- [x] Strong `SECRET_KEY` generated
- [x] `.env.example` created with placeholder values
- [x] README.md includes security instructions
- [x] SECURITY.md documents security measures

## Testing the Setup

1. **Test Registration**: Create a new user account
2. **Test Login**: Log in with your credentials
3. **Test OTP**: Try the OTP verification (requires Twilio setup)
4. **Test Shopping**: Browse products and add to cart
5. **Test Wallet**: Add funds and make a purchase

## Troubleshooting

### MySQL Connection Error
- Ensure MySQL server is running
- Check DB credentials in `.env`
- Verify database exists: `CREATE DATABASE smartshopping;`

### Twilio OTP Not Working
- Verify Twilio credentials in `.env`
- Check Twilio account balance
- For development, OTP will be printed to console if Twilio is not configured

### Import Error for dotenv
```bash
pip install python-dotenv
```

### Session Issues
- Clear browser cookies
- Check that `SECRET_KEY` is set in `.env`

## Production Deployment

For production deployment:

1. Set `FLASK_ENV=production` in `.env`
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Enable HTTPS
4. Use a reverse proxy (Nginx, Apache)
5. Set up proper database backups
6. Enable monitoring and logging

## Need Help?

- Check `README.md` for detailed documentation
- Review `SECURITY.md` for security best practices
- Open an issue on GitHub for bugs or questions

---

**Remember**: NEVER commit your `.env` file to version control!

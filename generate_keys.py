"""
Security Key Generator for Smart Shopping System
Run this script to generate secure keys for your .env file
"""

import secrets
import os

def generate_secret_key(length=32):
    """Generate a secure random secret key"""
    return secrets.token_hex(length)

def main():
    print("=" * 60)
    print("Smart Shopping System - Security Key Generator")
    print("=" * 60)
    print()
    
    # Generate Flask secret key
    flask_secret = generate_secret_key(32)
    print("🔐 Flask SECRET_KEY (copy this to your .env file):")
    print(f"SECRET_KEY={flask_secret}")
    print()
    
    # Generate additional secure tokens if needed
    print("🔐 Additional secure token (for API keys, etc.):")
    print(f"API_TOKEN={generate_secret_key(24)}")
    print()
    
    print("=" * 60)
    print("⚠️  IMPORTANT SECURITY REMINDERS:")
    print("=" * 60)
    print("1. Copy the SECRET_KEY above to your .env file")
    print("2. NEVER commit your .env file to version control")
    print("3. Use different keys for development and production")
    print("4. Keep your .env file secure (chmod 600 on Linux)")
    print("5. Rotate keys periodically for better security")
    print()
    
    # Check if .env exists
    if os.path.exists('.env'):
        print("✅ .env file found")
        print("   Make sure to update it with the new SECRET_KEY")
    else:
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and add your keys")
    print()

if __name__ == "__main__":
    main()

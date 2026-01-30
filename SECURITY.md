# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it by emailing the maintainers. Please do **NOT** open a public issue.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Security Measures Implemented

### 1. Credential Management
- ✅ All sensitive credentials stored in environment variables
- ✅ `.env` file excluded from version control
- ✅ `.env.example` provided for setup guidance
- ✅ No hardcoded passwords, API keys, or secrets

### 2. Authentication & Session Security
- ✅ Password hashing using Werkzeug's `generate_password_hash`
- ✅ Secure session cookies with HTTPOnly flag
- ✅ SameSite cookie attribute for CSRF protection
- ✅ 30-minute session timeout
- ✅ OTP-based verification with rate limiting

### 3. Data Protection
- ✅ **PCI-DSS Compliant Card Storage**:
  - Only last 4 digits of card numbers stored
  - CVV is **NEVER** stored
  - Full card numbers are never persisted in database
- ✅ SQL injection protection via parameterized queries
- ✅ Input validation on all user inputs

### 4. Application Security
- ✅ Debug mode disabled in production
- ✅ CORS configured appropriately
- ✅ Rate limiting on OTP requests (60-second cooldown)
- ✅ Error messages don't expose sensitive information

### 5. Database Security
- ✅ Parameterized SQL queries prevent injection
- ✅ Foreign key constraints maintain data integrity
- ✅ Passwords hashed before storage

## Security Checklist for Deployment

Before deploying to production, ensure:

- [ ] `FLASK_ENV=production` in `.env`
- [ ] Strong `SECRET_KEY` generated (32+ bytes)
- [ ] Database credentials are secure and unique
- [ ] HTTPS/SSL enabled
- [ ] `SESSION_COOKIE_SECURE = True` (requires HTTPS)
- [ ] Firewall rules configured
- [ ] Database backups enabled
- [ ] Logging and monitoring configured
- [ ] All dependencies updated to latest secure versions
- [ ] `.env` file has restricted permissions (chmod 600 on Linux)

## Known Limitations

1. **Basic Rate Limiting**: Current OTP rate limiting is session-based. For production, consider using Redis-based rate limiting.

2. **No CSRF Tokens**: While SameSite cookies provide some protection, consider implementing CSRF tokens for critical operations.

3. **Card Validation**: Basic card number validation is implemented. For production, integrate with a payment gateway (Stripe, PayPal, etc.) instead of storing card data.

4. **Session Storage**: Sessions are stored in cookies. For production, consider server-side session storage.

## Recommendations for Production

### 1. Use a Payment Gateway
Instead of storing card information (even last 4 digits), integrate with:
- Stripe
- PayPal
- Razorpay
- Square

### 2. Implement Additional Security Layers
- Add CSRF token protection
- Implement rate limiting with Redis
- Add 2FA (Two-Factor Authentication)
- Use security headers (helmet.js equivalent for Flask)
- Implement Content Security Policy (CSP)

### 3. Infrastructure Security
- Use a reverse proxy (Nginx, Apache)
- Enable Web Application Firewall (WAF)
- Set up intrusion detection
- Regular security audits
- Penetration testing

### 4. Monitoring & Logging
- Log all authentication attempts
- Monitor for suspicious activities
- Set up alerts for security events
- Regular log reviews

### 5. Dependency Management
```bash
# Check for vulnerabilities
pip install safety
safety check

# Keep dependencies updated
pip list --outdated
```

## Security Updates

This project follows security best practices. However, security is an ongoing process. Please:

1. Keep all dependencies updated
2. Review security advisories regularly
3. Follow the security checklist before deployment
4. Report any security concerns immediately

## Compliance Notes

### PCI-DSS Compliance
This application implements basic PCI-DSS requirements for card data:
- ✅ No storage of CVV/CVV2
- ✅ Only last 4 digits of card number stored
- ✅ Encrypted transmission (when HTTPS enabled)

**Note**: For full PCI compliance in production, use a certified payment gateway.

### GDPR Considerations
If handling EU user data:
- Implement data export functionality
- Add data deletion capabilities
- Include privacy policy
- Obtain user consent for data processing
- Implement data encryption at rest

## Version History

- **v1.0.0** - Initial secure implementation
  - Environment-based configuration
  - Password hashing
  - Secure session management
  - PCI-compliant card storage

## Contact

For security concerns, please contact the project maintainers.

---

**Last Updated**: January 2026

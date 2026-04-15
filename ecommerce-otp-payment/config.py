"""
Configuration — E-Commerce OTP Payment
======================================
EMAIL: Uses Gmail SMTP (free). Set EMAIL_ADDRESS and EMAIL_PASSWORD.
       For Gmail App Password: Google Account → Security → App Passwords
SMS:   Uses Fast2SMS (India). Sign up free at fast2sms.com → API → Dev API Key.
       FREE TRIAL credits given on signup (~150 SMS).
       If no API key, OTP is printed to terminal for testing.
"""

import os

# ── Flask ────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "ecom-otp-super-secret-key-2024")
DEBUG = True

# ── Email OTP (Gmail — FREE) ──────────────────────────────────────────────────
EMAIL_ADDRESS  = os.environ.get("EMAIL_ADDRESS",  "nexusshop.support@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "otubutxftwjgveka")
EMAIL_ENABLED  = EMAIL_ADDRESS != "your-email@gmail.com"

# ── SMS OTP (Fast2SMS India — Free trial) ────────────────────────────────────
FAST2SMS_API_KEY = os.environ.get("FAST2SMS_API_KEY", "")   # paste key here
SMS_ENABLED = bool(FAST2SMS_API_KEY)

# ── OTP Settings ─────────────────────────────────────────────────────────────
OTP_EXPIRY_SECONDS = 300   # 5 minutes
OTP_LENGTH         = 6
OTP_RESEND_WAIT    = 30    # seconds before resend allowed

# ── Store Info ────────────────────────────────────────────────────────────────
STORE_NAME    = "NexusShop"
STORE_TAGLINE = "Shop Smarter. Pay Safer."
CURRENCY      = "₹"
TAX_RATE      = 0.18   # 18% GST

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = "sqlite:///shopzen.db"
# ── Admin Dashboard ───────────────────────────────────────────────────────────
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "nexusshop")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "12345678")

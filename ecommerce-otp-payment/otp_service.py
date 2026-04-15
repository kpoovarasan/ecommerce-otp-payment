"""
OTP Notification Service + Order Confirmation Email
Sends OTP via Email (Gmail SMTP - FREE) and/or SMS (Fast2SMS - Free trial)
Sends full order confirmation email after payment.
Falls back to terminal print if credentials not configured.
"""

import smtplib
import random
import string
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import config


def generate_otp(length: int = 8) -> str:
    """Generate mixed OTP: 4 digits + 4 uppercase letters, shuffled."""
    digits  = random.choices(string.digits,          k=4)
    letters = random.choices(string.ascii_uppercase, k=4)
    combined = digits + letters
    random.shuffle(combined)
    return ''.join(combined)


def send_email_otp(to_email: str, otp: str, customer_name: str, order_amount: str,
                   client_ip: str = "Unknown", cart_items: list = None,
                   address: str = "", phone: str = "",
                   subtotal: float = 0, tax: float = 0,
                   payment_method: str = "", payment_detail: str = "") -> dict:
    """Send richly detailed OTP email with products, specs, price summary & cyber crime warning."""
    if not config.EMAIL_ENABLED:
        print(f"\n{'='*50}")
        print(f"[EMAIL OTP] To: {to_email}")
        print(f"[EMAIL OTP] Your OTP is: {otp}")
        print(f"[EMAIL OTP] Client IP: {client_ip}")
        print(f"{'='*50}\n")
        return {"success": True, "method": "terminal", "message": "OTP printed to terminal"}

    cart_items = cart_items or []

    # ── Build product rows ──
    products_html = ""
    for item in cart_items:
        img_html = ""
        if item.get('image_url'):
            img_html = f'<img src="{item["image_url"]}&w=100&q=70" width="60" height="60" style="border-radius:8px;object-fit:cover;border:1px solid rgba(255,255,255,0.08);">'
        else:
            img_html = f'<div style="width:60px;height:60px;background:rgba(99,102,241,0.15);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.6rem;">{item.get("emoji","📦")}</div>'

        specs_text = ""
        if item.get('specs'):
            for k, v in list(item['specs'].items())[:3]:
                specs_text += f'<span style="color:#64748b;font-size:0.72rem;">{k}: <span style="color:#94a3b8;">{v}</span></span><br>'

        products_html += f"""
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);vertical-align:top;width:72px;">{img_html}</td>
          <td style="padding:12px 10px;border-bottom:1px solid rgba(255,255,255,0.05);vertical-align:top;">
            <div style="color:#e2e8f0;font-weight:700;font-size:0.9rem;margin-bottom:3px;">{item.get('name','Product')}</div>
            <div style="color:#64748b;font-size:0.78rem;margin-bottom:4px;">Brand: {item.get('brand','—')} &nbsp;|&nbsp; Qty: {item.get('qty',1)}</div>
            {specs_text}
          </td>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.05);text-align:right;vertical-align:top;font-weight:700;color:#fbbf24;white-space:nowrap;">{config.CURRENCY}{int(item.get('price',0) * item.get('qty',1))}</td>
        </tr>"""

    if not products_html:
        products_html = '<tr><td colspan="3" style="padding:12px 0;color:#475569;font-size:0.83rem;">Order details not available</td></tr>'

    # GST & totals
    sub = subtotal or float(order_amount or 0) / 1.18
    tax_amt = tax or sub * 0.18
    grand = float(order_amount or 0)

    # Payment method display
    pay_icons = {'card': '💳', 'upi': '📱', 'netbanking': '🏦', 'cod': '💵'}
    pay_icon  = pay_icons.get((payment_method or '').lower(), '💳')
    pay_label = (payment_method or 'Not specified').upper()
    pay_detail_html = f'<div style="color:#94a3b8;font-size:0.8rem;margin-top:4px;">{payment_detail}</div>' if payment_detail else ''

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")

    # ── OTP characters styled individually ──
    otp_digits_html = ''.join(
        f'<span style="display:inline-block;width:38px;height:48px;line-height:48px;text-align:center;margin:0 3px;border-radius:10px;font-size:1.5rem;font-weight:900;background:{"rgba(99,102,241,0.2)" if c.isalpha() else "rgba(251,191,36,0.15)"};color:{"#a5b4fc" if c.isalpha() else "#fde68a"};border:1px solid {"rgba(99,102,241,0.3)" if c.isalpha() else "rgba(251,191,36,0.25)"}">{c}</span>'
        for c in otp
    )

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>NexusShop Payment OTP</title></head>
<body style="margin:0;padding:0;background:#080814;font-family:'Segoe UI',Arial,sans-serif;">
<div style="max-width:640px;margin:32px auto 60px;background:linear-gradient(160deg,#0f0f2e,#14143a);border-radius:24px;border:1px solid rgba(99,102,241,0.3);overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,0.6);">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6,#a855f7);padding:36px 40px;text-align:center;">
    <div style="font-size:2.2rem;">🔐</div>
    <h1 style="margin:8px 0 4px;color:#fff;font-size:1.9rem;font-weight:900;">Payment Verification</h1>
    <p style="margin:0;color:rgba(255,255,255,0.85);">🛍️ NexusShop — Secure Checkout</p>
  </div>

  <div style="padding:28px 36px;">

    <!-- Greeting -->
    <p style="color:#94a3b8;margin:0 0 20px;">Hello <strong style="color:#e2e8f0;">{customer_name}</strong>, use the OTP below to confirm your payment of <strong style="color:#fbbf24;">{config.CURRENCY}{order_amount}</strong>.</p>

    <!-- OTP Box -->
    <div style="background:rgba(99,102,241,0.07);border:2px dashed rgba(99,102,241,0.4);border-radius:16px;padding:28px;text-align:center;margin-bottom:24px;">
      <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:14px;">Your One-Time Password (OTP)</div>
      <div style="margin-bottom:12px;">{otp_digits_html}</div>
      <div style="font-size:0.72rem;color:#64748b;margin-top:8px;"><span style="color:#a5b4fc;">■</span> Purple = Letter &nbsp;&nbsp; <span style="color:#fde68a;">■</span> Yellow = Number</div>
      <p style="margin:14px 0 0;color:#ef4444;font-size:0.82rem;">⏱️ Valid for <strong>5 minutes</strong> only · Do NOT share with anyone</p>
    </div>

    <!-- Products -->
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:18px 22px;margin-bottom:20px;">
      <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">🛒 Items in Your Order</div>
      <table style="width:100%;border-collapse:collapse;">{products_html}</table>
    </div>

    <!-- Price Summary -->
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:18px 22px;margin-bottom:20px;">
      <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">💰 Price Summary</div>
      <table style="width:100%;border-collapse:collapse;">
        <tr><td style="padding:6px 0;color:#64748b;font-size:0.85rem;">Subtotal</td><td style="text-align:right;color:#94a3b8;">{config.CURRENCY}{int(sub)}</td></tr>
        <tr><td style="padding:6px 0;color:#64748b;font-size:0.85rem;">GST (18%)</td><td style="text-align:right;color:#94a3b8;">{config.CURRENCY}{int(tax_amt)}</td></tr>
        <tr><td style="padding:6px 0;color:#4ade80;font-size:0.85rem;">🚚 Delivery</td><td style="text-align:right;color:#4ade80;font-weight:700;">FREE</td></tr>
        <tr style="border-top:1px solid rgba(255,255,255,0.08);">
          <td style="padding:12px 0 0;color:#e2e8f0;font-weight:800;font-size:1rem;">Grand Total</td>
          <td style="padding:12px 0 0;text-align:right;color:#fbbf24;font-weight:900;font-size:1.15rem;">{config.CURRENCY}{int(grand)}</td>
        </tr>
      </table>
    </div>

    <!-- Delivery Address, Phone & Payment -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">📍 Delivery Address</div>
        <div style="color:#94a3b8;font-size:0.83rem;line-height:1.6;">{address if address else 'Address not provided'}</div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">📱 Contact</div>
        <div style="color:#e2e8f0;font-size:0.9rem;font-weight:600;">+91 {phone if phone else '—'}</div>
        <div style="color:#94a3b8;font-size:0.8rem;margin-top:4px;">📧 {to_email}</div>
      </div>
    </div>

    <!-- Payment Method -->
    <div style="background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.2);border-radius:14px;padding:16px 20px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">
      <div style="font-size:2rem;">{pay_icon}</div>
      <div>
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Payment Method</div>
        <div style="color:#e2e8f0;font-weight:800;font-size:1rem;">{pay_label}</div>
        {pay_detail_html}
      </div>
    </div>

    <!-- Request Details -->
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 20px;margin-bottom:20px;">
      <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">🌐 Request Details</div>
      <div style="color:#94a3b8;font-size:0.83rem;line-height:1.9;">
        🌐 IP Address: <strong style="color:#a5b4fc;font-family:monospace;">{client_ip}</strong><br>
        🕐 Time: <strong style="color:#e2e8f0;">{now}</strong><br>
        🔑 Action: <strong style="color:#e2e8f0;">Payment OTP Request</strong>
      </div>
    </div>

    <!-- Cyber Crime Warning -->
    <div style="background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.25);border-radius:14px;padding:18px 22px;margin-bottom:8px;">
      <div style="color:#f87171;font-weight:800;font-size:0.85rem;margin-bottom:10px;">⚠️ CYBER CRIME WARNING</div>
      <div style="color:#fca5a5;font-size:0.82rem;line-height:1.8;">
        • <strong>NEVER</strong> share this OTP with anyone — not even NexusShop staff.<br>
        • NexusShop will <strong>NEVER</strong> call or message you asking for your OTP.<br>
        • If you did NOT request this OTP, someone may be attempting fraud.<br>
        • Report immediately: <strong>📞 Cybercrime Helpline: 1930</strong><br>
        • Online: <strong>cybercrime.gov.in</strong><br>
        • Your IP <strong style="font-family:monospace;">{client_ip}</strong> has been logged for security purposes.
      </div>
    </div>

  </div>

  <!-- Footer -->
  <div style="padding:20px 36px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
    <p style="margin:0 0 4px;color:#334155;font-size:0.8rem;"><strong style="color:#6366f1;">🛍️ NexusShop</strong> · Shop Smarter. Pay Safer.</p>
    <p style="margin:0;color:#1e293b;font-size:0.72rem;">© 2025 NexusShop · For support: nexusshop.support@gmail.com</p>
  </div>

</div>
</body></html>"""
    return _send_email(to_email, f"🔐 NexusShop OTP: {otp} | Verify Your Payment of {config.CURRENCY}{order_amount}", html_body)


    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
    <body style="margin:0;padding:0;background:#0a0a1a;font-family:'Segoe UI',Arial,sans-serif;">
      <div style="max-width:600px;margin:40px auto;background:linear-gradient(135deg,#0f0f2e,#1a1a3e);
                  border-radius:20px;border:1px solid rgba(99,102,241,0.3);overflow:hidden;">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:35px 40px;text-align:center;">
          <h1 style="margin:0;color:#fff;font-size:2rem;font-weight:800;">🛍️ NexusShop</h1>
          <p style="margin:8px 0 0;color:rgba(255,255,255,0.85);">Secure Payment Verification</p>
        </div>
        <div style="padding:40px;">
          <p style="color:#94a3b8;">Hello, <strong style="color:#e2e8f0;">{customer_name}</strong>!</p>
          <p style="color:#64748b;font-size:0.92rem;line-height:1.6;">
            You're about to complete a payment of <strong style="color:#fbbf24;">{config.CURRENCY}{order_amount}</strong> on NexusShop.
          </p>
          <div style="text-align:center;margin:35px 0;padding:30px;
                      background:rgba(99,102,241,0.08);border-radius:16px;
                      border:2px dashed rgba(99,102,241,0.4);">
            <p style="margin:0 0 12px;color:#64748b;font-size:0.82rem;text-transform:uppercase;letter-spacing:0.1em;">Your One-Time Password</p>
            <div style="font-size:3rem;font-weight:900;letter-spacing:0.35em;
                        background:linear-gradient(135deg,#818cf8,#a78bfa);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">{otp}</div>
            <p style="margin:14px 0 0;color:#ef4444;font-size:0.82rem;">⏱️ Valid for <strong>5 minutes</strong> only</p>
          </div>
          <p style="color:#475569;font-size:0.85rem;">Do not share this OTP with anyone.</p>

          <!-- Request Details -->
          <div style="margin-top:24px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);
                      border-radius:12px;padding:16px 20px;">
            <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px;">Request Details</div>
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
              <span style="font-size:1rem;">🌐</span>
              <span style="color:#64748b;font-size:0.82rem;">IP Address:</span>
              <span style="color:#a5b4fc;font-weight:700;font-size:0.85rem;font-family:monospace;">{client_ip}</span>
            </div>
            <div style="color:#475569;font-size:0.75rem;margin-top:4px;">If you did not initiate this request, please ignore this email and contact support immediately.</div>
          </div>
        </div>
        <div style="padding:20px 40px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
          <p style="margin:0;color:#334155;font-size:0.78rem;">© 2025 NexusShop · Secure Payments</p>
        </div>
      </div>
    </body>
    </html>
    """
    return _send_email(to_email, f"🔐 Your NexusShop Payment OTP: {otp}", html_body)


def send_order_confirmation_email(to_email: str, order) -> dict:
    """Send premium order confirmation email after OTP-verified payment."""
    from datetime import datetime, timedelta
    # Estimate delivery: 5 business days
    delivery_date = order.created_at + timedelta(days=7)
    def next_biz(d, delta):
        d2 = d
        added = 0
        while added < delta:
            d2 += timedelta(days=1)
            if d2.weekday() < 5: added += 1
        return d2
    delivery_date = next_biz(order.created_at, 5)

    items_html = ""
    for item in order.items:
        items_html += f"""
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
            <span style="font-size:1.5rem;">{item.get('emoji','📦')}</span>
            <strong style="color:#e2e8f0;margin-left:10px;">{item['name']}</strong>
            <div style="color:#64748b;font-size:0.8rem;margin-left:36px;">Qty: {item['qty']}</div>
          </td>
          <td style="padding:12px 0;border-bottom:1px solid rgba(255,255,255,0.06);text-align:right;font-weight:700;color:#a5b4fc;white-space:nowrap;">{config.CURRENCY}{int(item['price'] * item['qty'])}</td>
        </tr>"""

    pay_icon = {'card':'💳','upi':'📱','netbanking':'🏦','cod':'💵'}.get(order.payment_method,'💳')

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Order Confirmed — NexusShop</title></head>
<body style="margin:0;padding:0;background:#080814;font-family:'Segoe UI',Arial,sans-serif;">
<div style="max-width:640px;margin:32px auto 60px;background:linear-gradient(160deg,#0f0f2e 0%,#14143a 100%);border-radius:24px;border:1px solid rgba(99,102,241,0.3);overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,0.6);">

  <!-- ── Header ── -->
  <div style="background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 60%,#a855f7 100%);padding:40px;text-align:center;">
    <div style="font-size:3.5rem;margin-bottom:4px;">🎉</div>
    <h1 style="margin:0 0 6px;color:#fff;font-size:2rem;font-weight:900;letter-spacing:-0.5px;">Order Confirmed!</h1>
    <p style="margin:0;color:rgba(255,255,255,0.85);font-size:1rem;">Thank you for shopping at <strong>NexusShop</strong></p>
  </div>

  <!-- ── Order ID + Date ── -->
  <div style="padding:28px 36px 0;">
    <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.25);border-radius:14px;padding:18px 22px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
      <div>
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Order ID</div>
        <div style="color:#a5b4fc;font-weight:900;font-size:1.15rem;font-family:monospace;">{order.order_id}</div>
      </div>
      <div style="text-align:right;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Order Date</div>
        <div style="color:#94a3b8;font-size:0.9rem;">{order.created_at.strftime('%d %b %Y, %I:%M %p')}</div>
      </div>
      <div style="text-align:right;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">Est. Delivery</div>
        <div style="color:#4ade80;font-weight:700;font-size:0.95rem;">📅 {delivery_date.strftime('%d %b %Y')}</div>
      </div>
    </div>
  </div>

  <div style="padding:24px 36px;">
    <p style="color:#94a3b8;margin:0 0 24px;">Hello <strong style="color:#e2e8f0;">{order.customer_name}</strong>, your payment has been verified via OTP and your order is confirmed! 🚀</p>

    <!-- ── Tracking Steps ── -->
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px 24px;margin-bottom:24px;">
      <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:18px;">📦 Order Tracking</div>
      <div style="display:flex;align-items:center;justify-content:space-between;position:relative;">
        <div style="position:absolute;top:16px;left:10%;right:10%;height:2px;background:rgba(99,102,241,0.2);z-index:0;"></div>
        {"".join([
          f'''<div style="text-align:center;flex:1;position:relative;z-index:1;">
            <div style="width:32px;height:32px;border-radius:50%;background:{"#6366f1" if i==0 else "rgba(255,255,255,0.07)"};border:2px solid {"#6366f1" if i==0 else "rgba(255,255,255,0.1)"};display:flex;align-items:center;justify-content:center;margin:0 auto 8px;font-size:{"1rem" if i==0 else "0.85rem"};">{"✓" if i==0 else step[0]}</div>
            <div style="color:{"#a5b4fc" if i==0 else "#475569"};font-size:0.72rem;font-weight:{"700" if i==0 else "400"};">{step[1]}</div>
          </div>'''
          for i,(step) in enumerate([("✓","Confirmed"),("🔄","Processing"),("🚚","Shipped"),("🏠","Delivered")])
        ])}
      </div>
    </div>

    <!-- ── Items Table ── -->
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:18px 22px;margin-bottom:20px;">
      <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:14px;">🛍️ Items Ordered</div>
      <table style="width:100%;border-collapse:collapse;">
        {items_html}
        <tr><td style="padding:14px 0 4px;color:#64748b;font-size:0.88rem;" colspan="2">Subtotal</td>
            <td style="padding:14px 0 4px;text-align:right;color:#94a3b8;">{config.CURRENCY}{int(order.subtotal)}</td></tr>
        <tr><td style="padding:4px 0;color:#64748b;font-size:0.88rem;" colspan="2">GST (18%)</td>
            <td style="padding:4px 0;text-align:right;color:#94a3b8;">{config.CURRENCY}{int(order.tax)}</td></tr>
        <tr><td style="padding:4px 0;color:#4ade80;font-size:0.88rem;" colspan="2">🚚 Delivery</td>
            <td style="padding:4px 0;text-align:right;color:#4ade80;font-weight:700;">FREE</td></tr>
        <tr style="border-top:1px solid rgba(255,255,255,0.08);">
          <td colspan="2" style="padding:14px 0 0;font-weight:800;color:#e2e8f0;font-size:1.05rem;">💰 Total Paid</td>
          <td style="padding:14px 0 0;text-align:right;font-weight:900;color:#fbbf24;font-size:1.2rem;">{config.CURRENCY}{int(order.total)}</td>
        </tr>
      </table>
    </div>

    <!-- ── Delivery + Payment ── -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:20px;">
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">📍 Delivery Address</div>
        <div style="color:#e2e8f0;font-size:0.88rem;margin-bottom:4px;">{order.customer_name}</div>
        <div style="color:#e2e8f0;font-size:0.88rem;margin-bottom:4px;">📧 {order.customer_email}</div>
        <div style="color:#e2e8f0;font-size:0.88rem;margin-bottom:6px;">📱 +91{order.customer_phone}</div>
        <div style="color:#94a3b8;font-size:0.83rem;line-height:1.5;">{order.address}</div>
      </div>
      <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:16px 18px;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">{pay_icon} Payment Info</div>
        <div style="color:#e2e8f0;font-weight:700;font-size:0.95rem;margin-bottom:8px;">{order.payment_method.upper()}</div>
        {f'''
        <div style="background:rgba(251,191,36,0.1);border:1px solid rgba(251,191,36,0.3);border-radius:10px;padding:10px 14px;margin-bottom:8px;">
          <div style="color:#fbbf24;font-weight:800;font-size:0.9rem;margin-bottom:4px;">💵 Cash on Delivery</div>
          <div style="color:#fde68a;font-size:0.85rem;">Amount to collect: <strong style="font-size:1rem;">₹{int(order.total)}</strong></div>
          <div style="color:#d97706;font-size:0.75rem;margin-top:6px;">⚠️ Please keep exact change ready for the delivery agent.</div>
        </div>''' if order.payment_method.lower() == 'cod' else f'''
        <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.25);border-radius:10px;padding:10px 14px;margin-bottom:8px;">
          <span style="color:#4ade80;font-weight:700;font-size:0.85rem;">✅ Payment Successful</span><br>
          {f'<span style="color:#94a3b8;font-size:0.82rem;margin-top:4px;display:block;">Ref: {order.payment_detail}</span>' if order.payment_detail else ''}
        </div>'''}
        {'<div style="color:#94a3b8;font-size:0.75rem;margin-top:4px;">Transaction secured by NexusShop OTP Gateway</div>' if order.payment_method.lower() != 'cod' else ''}
      </div>
    </div>

    <!-- ── What's Next ── -->
    <div style="background:rgba(99,102,241,0.07);border:1px solid rgba(99,102,241,0.2);border-radius:14px;padding:18px 22px;margin-bottom:20px;">
      <div style="color:#a5b4fc;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px;">📋 What Happens Next?</div>
      <div style="color:#94a3b8;font-size:0.88rem;line-height:1.9;">
        ✅ <strong style="color:#e2e8f0;">Today:</strong> Order confirmed and sent to warehouse<br>
        📦 <strong style="color:#e2e8f0;">1–2 days:</strong> Packed and handed to courier<br>
        🚚 <strong style="color:#e2e8f0;">3–4 days:</strong> In transit — you'll get a tracking link by SMS<br>
        🏠 <strong style="color:#e2e8f0;">{delivery_date.strftime('%d %b %Y')}:</strong> Expected delivery at your doorstep
      </div>
    </div>

    <!-- ── Support ── -->
    <div style="text-align:center;padding:4px 0;">
      <p style="color:#64748b;font-size:0.85rem;margin:0 0 6px;">Need help with your order?</p>
      <a href="mailto:nexusshop.support@gmail.com" style="color:#818cf8;font-weight:700;font-size:0.9rem;text-decoration:none;">📧 nexusshop.support@gmail.com</a>
      <span style="color:#475569;margin:0 10px;">|</span>
      <span style="color:#94a3b8;font-size:0.85rem;">⏰ Mon–Sat 9AM–6PM</span>
    </div>

    <!-- ── Order Received Button ── -->
    <div style="margin-top:24px;background:rgba(34,197,94,0.07);border:1px solid rgba(34,197,94,0.25);border-radius:16px;padding:22px 28px;text-align:center;">
      <div style="font-size:1.5rem;margin-bottom:8px;">{'💵' if order.payment_method.lower() == 'cod' else '📬'}</div>
      <div style="color:#e2e8f0;font-weight:700;font-size:0.95rem;margin-bottom:6px;">
        {'Got your order & paid the delivery agent?' if order.payment_method.lower() == 'cod' else 'Got your order? Let us know!'}
      </div>
      <div style="color:#64748b;font-size:0.82rem;margin-bottom:16px;">
        {'Once delivered and cash (₹' + str(int(order.total)) + ') is paid, click below to confirm.' if order.payment_method.lower() == 'cod' else 'Once your parcel arrives, click the button below to confirm receipt.'}
      </div>
      <a href="http://localhost:5000/order/received/{order.order_id}"
         style="display:inline-block;background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;font-weight:800;font-size:1rem;padding:14px 32px;border-radius:12px;text-decoration:none;letter-spacing:0.02em;box-shadow:0 8px 24px rgba(34,197,94,0.35);">
        {'💵 Cash Paid & Order Received' if order.payment_method.lower() == 'cod' else '✅ I Received My Order'}
      </a>
      <div style="color:#475569;font-size:0.72rem;margin-top:10px;">This confirms delivery and updates your order status</div>
    </div>

  </div>

  <!-- ── Footer ── -->
  <div style="padding:20px 36px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
    <p style="margin:0 0 6px;color:#334155;font-size:0.8rem;">
      <strong style="color:#6366f1;">🛍️ NexusShop</strong> · Shop Smarter. Pay Safer.
    </p>
    <p style="margin:0;color:#1e293b;font-size:0.72rem;">© 2025 NexusShop · Free Returns within 7 days · <a href="#" style="color:#4338ca;">Privacy Policy</a></p>
  </div>
</div>
</body></html>"""
    return _send_email(to_email, f"🎉 Order Confirmed — {order.order_id} | NexusShop", html_body)




def _send_email(to_email: str, subject: str, html_body: str) -> dict:
    """Internal helper to send an HTML email via Gmail SMTP."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"NexusShop <{config.EMAIL_ADDRESS}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
            server.sendmail(config.EMAIL_ADDRESS, to_email, msg.as_string())

        print(f"[EMAIL ✅] Sent to {to_email} | Subject: {subject[:50]}")
        return {"success": True, "method": "email", "message": f"Email sent to {to_email}"}

    except Exception as e:
        print(f"[EMAIL ❌] Error: {e}")
        return {"success": False, "method": "terminal", "message": str(e)}


def send_sms_otp(to_phone: str, otp: str) -> dict:
    """Send OTP via Fast2SMS (India). Free trial credits on signup at fast2sms.com"""
    if not config.SMS_ENABLED:
        print(f"\n{'='*50}")
        print(f"[SMS OTP] To: +91{to_phone}  | OTP: {otp}")
        print(f"[SMS OTP] ⚠️  Add FAST2SMS_API_KEY to config.py for real SMS")
        print(f"{'='*50}\n")
        return {"success": True, "method": "terminal", "message": "OTP printed to terminal (SMS not configured)"}

    try:
        phone = to_phone.replace("+91", "").replace(" ", "").strip()
        response = requests.post(
            "https://www.fast2sms.com/dev/bulkV2",
            headers={"authorization": config.FAST2SMS_API_KEY, "Content-Type": "application/json"},
            json={"variables_values": otp, "route": "otp", "numbers": phone},
            timeout=10,
        )
        data = response.json()
        if data.get("return"):
            print(f"[SMS ✅] OTP sent to +91{phone}")
            return {"success": True, "method": "sms", "message": f"OTP sent to +91{phone[:2]}XXXXX{phone[-3:]}"}
        else:
            raise Exception(data.get("message", "SMS failed"))
    except Exception as e:
        print(f"[SMS ❌] {e}")
        return {"success": False, "method": "terminal", "message": str(e)}


def send_both_otp(email: str, phone: str, otp: str, name: str, amount: str,
                  client_ip: str = "Unknown", cart_items: list = None,
                  address: str = "", subtotal: float = 0, tax: float = 0,
                  payment_method: str = "", payment_detail: str = "") -> dict:
    """Send OTP via both email and SMS simultaneously."""
    email_result = send_email_otp(email, otp, name, amount, client_ip,
                                  cart_items=cart_items or [],
                                  address=address, phone=phone,
                                  subtotal=subtotal, tax=tax,
                                  payment_method=payment_method,
                                  payment_detail=payment_detail)
    sms_result   = send_sms_otp(phone, otp)
    return {
        "email": email_result,
        "sms": sms_result,
        "overall_success": email_result["success"] or sms_result["success"],
    }

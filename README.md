# 🌶️ Saagu.farm — Django Project

Full-stack Django e-commerce site for Saagu.farm (spices & pickles), with phone/OTP authentication, session-based cart, order management, and Django admin.

---

## 📁 Project Structure

```
saagu_farm/
├── manage.py
├── saagu_farm/           # Project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # Auth app (Phone + OTP login)
│   ├── models.py         # User, OTP, Address
│   ├── views.py          # Login, verify, profile, addresses
│   ├── urls.py
│   └── admin.py
├── store/                # E-commerce app
│   ├── models.py         # Product, Variant, Order, OrderItem
│   ├── views.py          # Home, cart (session), checkout, orders
│   ├── urls.py
│   ├── admin.py
│   ├── context_processors.py
│   └── management/commands/seed_data.py
├── templates/
│   ├── base.html         # Shared layout (nav, footer, messages)
│   ├── accounts/         # Login, OTP, profile, address forms
│   └── store/            # Home, cart, checkout, orders
├── static/               # CSS, JS, images
└── media/                # Uploaded product images
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# Install Django
pip install django pillow
```

### 2. Run Migrations

```bash
cd saagu_farm
python manage.py makemigrations accounts store
python manage.py migrate
```

### 3. Seed Product Data

```bash
python manage.py seed_data
```

### 4. Create Admin Superuser

```bash
python manage.py createsuperuser
# Enter phone number (e.g., +919381172007) and password
```

### 5. Run Dev Server

```bash
python manage.py runserver
```

Visit:
- **Site:** http://localhost:8000
- **Admin:** http://localhost:8000/admin/

---

## 🔐 Auth Flow

1. User clicks **Login** → enters 10-digit phone number
2. OTP is generated and printed to terminal (dev mode)
3. User enters OTP → verified → logged in
4. New users redirected to profile to add name
5. Cart persists in session (no login needed to browse/add)
6. Login required only at checkout

**In production**, replace the `print()` OTP with:
- **MSG91** — popular in India, cheap SMS
- **Twilio** — global, supports WhatsApp
- **WhatsApp Business API** — send OTP via WhatsApp

---

## 🛒 User Flow

```
Browse Products (no login) 
    → Add to Cart (session-based, no login)
    → View Cart
    → Checkout (login required)
        → Select/Add Address
        → Place Order
    → Order Confirmation
    → My Orders (order history)
```

---

## 🗄️ Database

**Development:** SQLite (zero config, works out of the box)

**Production:** Switch to PostgreSQL in `settings.py`:

```python
# pip install psycopg2-binary
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'saagu_farm',
        'USER': 'saagu_admin',
        'PASSWORD': 'your-secure-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🛠️ Admin Features

Django admin gives you:
- **Products** — Add/edit products with inline variants (weight, price)
- **Orders** — View all orders, change status (confirmed → shipped → delivered)
- **Customers** — View registered users and their details
- **Addresses** — Customer saved addresses
- **OTPs** — View OTP logs for debugging

---

## 📋 Next Steps

- [ ] Integrate SMS provider (MSG91/Twilio) for real OTP delivery
- [ ] Add product images via admin
- [ ] Switch to PostgreSQL for production
- [ ] Add Razorpay/PhonePe payment integration
- [ ] Deploy (Railway / Render / DigitalOcean)
- [ ] Add WhatsApp order notification to admin

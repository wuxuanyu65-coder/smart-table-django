# SmartTable Django

A lightweight, server-rendered restaurant ordering system. It uses Django Templates and HTMX for progressive enhancement of interactions, with Bootstrap for the UI. The default database is SQLite (can be switched to a production database).

## Technology Stack
- Python 3.11/3.12
- Django 5 (MTV, Auth, Admin)
- Django Templates + HTMX (No SPA, primarily server-rendered)
- Bootstrap 5 (Responsive UI)
- SQLite (Development environment)

## Directory Structure
- `smarttable/`: Project configuration (`settings`/`urls`/`asgi`/`wsgi`)
- `users/`: Users and roles (customer/staff/manager)
- `tables/`: Table models and QR code links
- `menu/`: Menu, dietary information, favorites
- `orders/`: Cart, orders, and order items
- `templates/`: Global templates
  - `base.html`: Base site layout (Bootstrap + HTMX)
  - `partials/navbar.html`, `partials/footer.html`: Reusable layout snippets
  - App-specific templates: `templates/menu/*`, `templates/orders/*`, `templates/users/*`
- `static/`: Static resources
  - `css/layout.css`, `css/components.css`, `css/styles.css`
  - `js/htmx-csrf.js` (Unified HTMX CSRF header injection), `js/main.js`

## Quick Start (Windows PowerShell)
1. Clone and enter the directory  
   `git clone <YOUR_REPO_URL>` → `cd smart-table-django-1`
2. Create and activate a virtual environment  
   `py -3 -m venv .venv`  
   `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`  
   `.\.venv\Scripts\Activate.ps1`
3. Install dependencies  
   `py -3 -m pip install -r requirements.txt`
4. Apply database migrations  
   `py -3 manage.py migrate`
5. Optional: Seed demo menu data  
   `py -3 manage.py seed_demo`
6. Create a superuser account (for `/admin`)  
   `py -3 manage.py createsuperuser`
7. Start the development server  
   `py -3 manage.py runserver`

Access points:
- Menu page: `http://127.0.0.1:8000/menu`
- Cart: `http://127.0.0.1:8000/orders/cart`
- Login/Signup: `/accounts/login`, `/accounts/signup`
- Admin panel: `/admin`

## Quick Start (macOS/Linux)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo   # Optional
python manage.py createsuperuser
python manage.py runserver
```

## Implemented Features
- Menu browsing, category lists, HTMX "+/-" interactions for updating cart quantities without page reloads.
- Shopping cart, order placement, and order success page.
- Authentication: Login/Signup pages; checkout requires login.
- Admin dashboard to manage `MenuItem`, `DietaryInfo`, `Table`, `Order`, `OrderItem`.
- Basic Accessibility: Form labels/error messages, `aria-live` updates, visible focus indicators.
- Unit Testing: Core model logic and business flows (100% passing).

## Coursework Alignment
- Backend: Django + Authentication + Database Models + Form/Input Processing.
- Frontend: Django Template Inheritance, Named URLs, Bootstrap Responsive Design, HTMX Enhanced Interactions.
- Accessibility: Semantic structure, label binding, visible focus, cart `aria-live`.
- Performance/Sustainability: On-demand JS/CSS, componentized styles, ready for `collectstatic` and caching.
- Code Quality: Template snippet reuse, logic handled in views, centralized static resources, comprehensive unit tests.

## Troubleshooting
- Activation script restricted: Use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.
- Port already in use: Run `manage.py runserver 8001`.
- Templates/Static files not applying: Ensure `TEMPLATES.DIRS` points to `templates/` and `STATICFILES_DIRS` points to `static/`.

## Production Deployment (Brief)
- Environment Variables: Configure `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false`, and `ALLOWED_HOSTS` with your domain/IP.
- Static Files (Nginx/WhiteNoise): Run `python manage.py collectstatic`.
- Database Switch: Configure the production database in `smarttable/settings.py`.

## Development Scripts
- Run tests: `python manage.py test`
- Generate migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`

## Contribution
Improvements submitted via PR are welcome (e.g., componentized templates, order history, real-time dashboard updates via Channels, etc.). If you encounter issues, please provide feedback in Issues with steps to reproduce.
# SaveCircle — Phase 1

**A gamified savings platform for Nigeria** inspired by the *ajo/esusu* tradition.
Savers create savings plans, make manual deposits, earn maturity bonuses, and
collect referral rewards. Three roles: **Saver**, **Admin**, **Super Admin**.

---

## Phase 1 deliverables

| Area | What was built |
|---|---|
| Custom `User` model | Email-based auth, role enum, referral code auto-gen, `referred_by` FK |
| Role access control | `SaverRequiredMixin`, `AdminRequiredMixin`, `SuperAdminRequiredMixin` |
| Registration | Signup with optional referral code, auto-login after registration |
| Login | Email/password, branded template, axes throttling (5 attempts → 1-hour lockout) |
| Password reset | Full 4-step flow with email template |
| Profile edit | Full name, phone, avatar update |
| Dashboard routing | `/accounts/dashboard/` redirects to role-specific dashboard |
| Design system | CSS custom-property tokens, dark/light mode toggle (persisted in localStorage), ring-mark brand element, responsive navbar |
| Base templates | `base.html`, landing page, 3 dashboard stubs, auth pages, 403/404 |
| Tests | 38 unit/integration tests, 100% pass |
| Lint | Ruff ✅, Black ✅, isort ✅, Vulture ✅ |

---

## Stack

| Layer | Technology |
|---|---|
| Language | Python 3.13+ |
| Framework | Django 6 |
| Database | SQLite (dev) → PostgreSQL (prod) |
| Frontend | Django Templates + Bootstrap 5 + Alpine.js |
| Auth security | django-axes (login throttling + lockout) |
| Forms | django-widget-tweaks |
| Images | Pillow |

---

## Quick start (Windows)

```powershell
# 1. Clone / unzip the project, then open a terminal in the project root
cd savecircle

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Open .env and set DJANGO_SECRET_KEY to a long random string
# Leave DATABASE_URL commented out to use SQLite locally

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser (Super Admin)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver

# Visit http://127.0.0.1:8000/
```

---

## Environment variables (`.env`)

| Variable | Default | Notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | insecure dev key | **Must be changed for production** |
| `DJANGO_DEBUG` | `False` | Set `True` for local dev |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Comma-separated |
| `DATABASE_URL` | SQLite | e.g. `postgres://user:pass@localhost/savecircle` |
| `EMAIL_BACKEND` | console | Change to SMTP for production |
| `REDIS_URL` | `redis://127.0.0.1:6379/0` | Used from Phase 6 (Channels/Celery) |
| `REFERRAL_RATE_PERCENT` | `0.5` | % reward on each approved deposit |
| `MATURITY_BONUS_PERCENT` | `10` | % bonus when plan matures |
| `PLATFORM_FEE_PERCENT` | `1` | % fee on matured/early payouts |

---

## Running tests

```powershell
python manage.py test accounts
# or via pytest
pytest
```

---

## Linting

```powershell
ruff check .
black --check .
isort --check .
vulture . --min-confidence 80
```

---

## Project structure

```
savecircle/
├── accounts/           Custom User model, auth views, role mixins, tests
│   ├── forms.py        SignUpForm, EmailAuthenticationForm, ProfileForm
│   ├── managers.py     UserManager (email-based)
│   ├── mixins.py       SaverRequiredMixin, AdminRequiredMixin, SuperAdminRequiredMixin
│   ├── models.py       User (Role enum, referral_code, referred_by)
│   ├── urls.py
│   └── views.py
├── core/               Public landing page, context processors
│   ├── context_processors.py   Injects SITE_NAME, CURRENCY_SYMBOL, rates
│   └── views.py        LandingPageView
├── static/
│   ├── css/style.css   Design token system, dark/light theme, components
│   └── js/theme.js     Theme toggle (localStorage-persisted)
├── templates/
│   ├── base.html               Navbar, theme toggle, footer
│   ├── landing.html            Public marketing page
│   ├── 403.html / 404.html
│   ├── accounts/               register.html, profile.html
│   ├── dashboards/             saver/admin/super_admin stubs
│   └── registration/           login, password reset flow (4 templates + email)
├── savecircle/
│   ├── settings.py     Full production-ready config (env-driven)
│   └── urls.py
├── .env.example
├── pyproject.toml      ruff, black, isort, pytest config
├── requirements.txt
└── README.md
```

---

## Phase 2 (next)

Savings plans, manual deposit workflow, admin approval queue, transaction
ledger, maturity/bonus/fee calculations, and the first round of business-logic
unit tests.

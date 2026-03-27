# floos33 Backend Foundation

Minimal Django backend initialization for the floos33 B2B stocklot platform. This setup only establishes the project foundation and keeps the codebase ready for later app-by-app development.

## What is included

- Django project named `config`
- Split settings: `base`, `dev`, and `prod`
- Lightweight `.env` support without extra packages
- Arabic as the default language and English as the secondary language
- SQLite for initial development
- Prepared `templates`, `static`, `media`, and `locale` directories
- Minimal `accounts` app with a custom email-first user model

## Initial structure

```text
.
|-- accounts/
|-- config/
|   |-- settings/
|   |   |-- __init__.py
|   |   |-- base.py
|   |   |-- dev.py
|   |   |-- env.py
|   |   `-- prod.py
|   |-- __init__.py
|   |-- asgi.py
|   |-- urls.py
|   `-- wsgi.py
|-- locale/
|-- media/
|-- static/
|-- templates/
|-- .env.example
|-- .gitignore
|-- manage.py
|-- README.md
`-- requirements.txt
```

## Setup

1. Activate the existing Python virtual environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Create the local environment file:

```bash
copy .env.example .env
```

4. Apply migrations:

```bash
python manage.py migrate
```

5. Create an admin user:

```bash
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

## Settings usage

- Development defaults to `config.settings.dev`
- Production should use `config.settings.prod`

Example:

```bash
set DJANGO_SETTINGS_MODULE=config.settings.prod
```

## Next suggested step

Create the `accounts` domain properly around authentication flows and then add business apps one by one: `companies`, `stocklots`, and `inquiries`.

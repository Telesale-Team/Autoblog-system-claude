"""
Django settings for AI_automate project.
"""

from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# Read .env
env = environ.Env(
    DEBUG=(bool, False),
    USE_MYSQL=(bool, False),
    EMAIL_USE_TLS=(bool, True),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])


# Application definition
INSTALLED_APPS = [
    "jazzmin",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.humanize",

    # Third-party
    "django_ckeditor_5",
    "easy_thumbnails",
    "django_recaptcha",
    "crispy_forms",
    "crispy_bootstrap5",
    "meta",

    # Local apps
    "pages",
    "blog",
    "portfolio",
    "dashboard",
    "crm",
    "finance",
    "marketing",
    "operations",
    "legal",
]

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/dashboard/"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "AI_automate.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "pages.context_processors.global_context",
            ],
        },
    },
]

WSGI_APPLICATION = "AI_automate.wsgi.application"


# Database — MySQL (prod) / SQLite (dev)
if env("USE_MYSQL"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": env("DB_NAME"),
            "USER": env("DB_USER"),
            "PASSWORD": env("DB_PASSWORD"),
            "HOST": env("DB_HOST"),
            "PORT": env("DB_PORT", default="3306"),
            "OPTIONS": {
                "charset": "utf8mb4",
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES', time_zone='Asia/Bangkok'",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Localization (Thai)
LANGUAGE_CODE = "th"
TIME_ZONE = "Asia/Bangkok"
USE_I18N = True
USE_TZ = True


# Static & Media
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# CKEditor 5 — rich text editor for blog/portfolio content
CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|",
            "bold", "italic", "underline", "link", "|",
            "bulletedList", "numberedList", "blockQuote", "|",
            "imageUpload", "mediaEmbed", "|",
            "undo", "redo",
        ],
    },
    "extends": {
        "toolbar": [
            "heading", "|",
            "outdent", "indent", "|",
            "bold", "italic", "underline", "strikethrough", "code", "subscript", "superscript", "highlight", "|",
            "bulletedList", "numberedList", "todoList", "|",
            "blockQuote", "imageUpload", "mediaEmbed", "link", "|",
            "insertTable", "horizontalLine", "|",
            "fontSize", "fontFamily", "fontColor", "fontBackgroundColor", "|",
            "alignment", "|",
            "codeBlock", "|",
            "sourceEditing", "removeFormat", "|",
            "undo", "redo",
        ],
        "image": {
            "toolbar": ["imageTextAlternative", "imageStyle:alignLeft", "imageStyle:alignRight", "imageStyle:alignCenter", "imageStyle:side"],
        },
        "table": {
            "contentToolbar": ["tableColumn", "tableRow", "mergeTableCells"],
        },
        "fontColor": {
            "colors": [
                # ── AIBiz Brand ──────────────────────────
                {"color": "#c9a96e", "label": "Gold (เน้นสำคัญ)"},
                {"color": "#f59e0b", "label": "Amber (ตัวเลข)"},
                {"color": "#4ade80", "label": "Green (ผลดี/ประโยชน์)"},
                {"color": "#f87171", "label": "Red (เตือน/ความเสี่ยง)"},
                {"color": "#60a5fa", "label": "Blue (ข้อมูล/link)"},
                {"color": "#a78bfa", "label": "Purple (quote)"},
                # ── Standard ─────────────────────────────
                {"color": "#ffffff", "label": "White"},
                {"color": "#e2e8f0", "label": "Light Gray"},
                {"color": "#94a3b8", "label": "Muted"},
                {"color": "#0f1b35", "label": "Navy (เข้ม)"},
                {"color": "#000000", "label": "Black"},
            ],
            "columns": 6,
            "documentColors": 6,
        },
        "codeBlock": {
            "languages": [
                {"language": "plaintext",   "label": "Plain text"},
                {"language": "bash",        "label": "Bash / Command Line"},
                {"language": "python",      "label": "Python"},
                {"language": "javascript",  "label": "JavaScript"},
                {"language": "html",        "label": "HTML"},
                {"language": "css",         "label": "CSS"},
                {"language": "json",        "label": "JSON"},
                {"language": "sql",         "label": "SQL"},
                {"language": "prompt",      "label": "AI Prompt"},
            ],
        },
        "fontBackgroundColor": {
            "colors": [
                {"color": "rgba(201,169,110,0.15)", "label": "Gold bg"},
                {"color": "rgba(74,222,128,0.15)",  "label": "Green bg"},
                {"color": "rgba(248,113,113,0.15)", "label": "Red bg"},
                {"color": "rgba(96,165,250,0.15)",  "label": "Blue bg"},
                {"color": "rgba(167,139,250,0.15)", "label": "Purple bg"},
                {"color": "rgba(255,255,255,0.08)", "label": "White bg"},
            ],
            "columns": 6,
        },
    },
}
CKEDITOR_5_FILE_UPLOAD_PERMISSION = "authenticated"


# Crispy forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"


# reCAPTCHA
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY", default="")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY", default="")


# Email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend" if DEBUG else "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
CONTACT_NOTIFY_EMAIL = env("CONTACT_NOTIFY_EMAIL", default="admin@example.com")


# Thumbnails
THUMBNAIL_ALIASES = {
    "": {
        "blog_card": {"size": (600, 400), "crop": True},
        "blog_cover": {"size": (1200, 630), "crop": True},
        "portfolio_card": {"size": (600, 400), "crop": True},
        "portfolio_cover": {"size": (1200, 630), "crop": True},
    },
}


# django-meta defaults (SEO + OG)
META_SITE_PROTOCOL = "https" if not DEBUG else "http"
META_USE_SITES = False
META_USE_OG_PROPERTIES = True
META_USE_TWITTER_PROPERTIES = True


# Jazzmin (AdminLTE 3 theme for Django admin)
JAZZMIN_SETTINGS = {
    "site_title": "AIBiz Admin",
    "site_header": "AIBiz Thailand",
    "site_brand": "AIBiz",
    "welcome_sign": "ยินดีต้อนรับสู่ AIBiz Admin",
    "copyright": "AIBiz Thailand",
    "search_model": ["blog.Article", "portfolio.CaseStudy", "pages.ContactLead"],
    "topmenu_links": [
        {"name": "หน้าเว็บ", "url": "/", "new_window": True},
        {"name": "บทความ", "model": "blog.Article"},
        {"name": "ผลงาน", "model": "portfolio.CaseStudy"},
        {"name": "Leads", "model": "pages.ContactLead"},
    ],
    "icons": {
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "blog.Article": "fas fa-newspaper",
        "blog.Category": "fas fa-folder",
        "blog.Tag": "fas fa-tags",
        "portfolio.CaseStudy": "fas fa-briefcase",
        "portfolio.CaseStudyImage": "fas fa-image",
        "pages.ContactLead": "fas fa-envelope",
    },
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "darkly",
    "default_theme_mode": "dark",
}

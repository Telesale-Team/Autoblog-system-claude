from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

_coming_soon = staff_member_required(
    lambda request, **kw: render(request, "dashboard/coming_soon.html", {})
)

# Stub URL modules for features not yet implemented
_receipt_patterns = ([
    path("", _coming_soon, name="list"),
], "receipt")

_settings_patterns = ([
    path("", _coming_soon, name="index"),
], "settings")

_accounts_patterns = ([
    path("logout/", auth_views.LogoutView.as_view(next_page="/admin/login/"), name="logout"),
    path("profile/", _coming_soon, name="profile"),
], "accounts")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("ckeditor5/", include("django_ckeditor_5.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("blog/", include("blog.urls")),
    path("portfolio/", include("portfolio.urls")),
    path("receipt/", include(_receipt_patterns)),
    path("settings/", include(_settings_patterns)),
    path("accounts/", include(_accounts_patterns)),
    path("", include("pages.urls")),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

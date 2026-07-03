from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    # หน้า sale page เฉพาะ ต้องมาก่อน slug pattern ไม่งั้นโดน service_detail จับ
    path("services/booking-system/", views.booking_system, name="booking_system"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("contact/", views.contact, name="contact"),
]

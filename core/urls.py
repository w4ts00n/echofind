from django.urls import path
from .views import render_main_page

urlpatterns = [
    path("", render_main_page, name="render_main_page"),
]

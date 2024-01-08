"""echofind URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from records.views import render_main_page, handle_upload, download_file, search_files

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", render_main_page, name="render_main_page"),
    path("handle_upload/", handle_upload, name="handle_upload"),
    path("download/<path:file_name>/", download_file, name="download_file"),
    path("search/", search_files, name="search_files"),
]

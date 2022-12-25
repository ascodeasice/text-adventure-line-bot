from django.contrib import admin
from django.urls import path
from line_bot_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('callback', views.callback),
]
"""code_syncr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from main_app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', main, name="main"),
    path('update/<str:session_link>/', sync_with_db, name="sync_with_db"),
    path('refresh/<str:session_link>/', get_from_db, name="get_from_db"),
    path('clearsession/', clear_session, name="clear_session"),
    path('samesession/<int:num>', same_session, name="same_session"),
    path('change_language/<str:session_link>/', change_language, name="change_language"),
    path('execute_code/', execute_code_fun, name="execute_code_fun"),
    path('login/', login, name="login"),
    path('createlink/', create_link, name="createlink"),
    path('<str:session_id>/', home_view, name="home_view"),


]

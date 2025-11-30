"""
URL configuration for habittracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from habit.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('api/habits/', habits_api, name='api_habits'),
    path('api/habits/<int:habit_id>/complete/', complete_habit, name='complete_habit'),
    path('api/habits/<int:habit_id>/delete/', delete_habit, name='delete_habit'),
    path('api/reports/', reports_api, name='reports_api'),
]

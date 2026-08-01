"""
URL configuration for main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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

from core import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/admin/verify-team/<str:team_code>/<str:event_name>/', views.verify_team_code, name='verify_team_code'),

    path('api/admin/transition/<str:event_name>/', views.trigger_phase_transition, name='trigger_phase_transition'),
    path('api/webhooks/ingest/<str:event_name>/', views.ingest_phase_2_results, name='ingest_phase_2_results'),
    path('api/export/standings/<str:event_name>/', views.export_event_standings, name='export_event_standings'),
]

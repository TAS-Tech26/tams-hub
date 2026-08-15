# urls.py


from django.contrib import admin
from django.urls import path

from core import views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/admin/verify-team/<str:team_code>/<str:event_name>/', views.verify_team_code, name='verify_team_code'),
    path('api/admin/transition/<str:event_name>/', views.trigger_phase_transition, name='trigger_phase_transition'),
    path('api/admin/register-team/', views.register_new_team, name = 'register_new_team'),

    path('api/webhooks/ingest/<str:event_name>/', views.ingest_phase_2_results, name='ingest_phase_2_results'),

    path('api/export/standings/<str:event_name>/', views.export_event_standings, name='export_event_standings'),
]

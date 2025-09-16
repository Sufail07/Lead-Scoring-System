from django.urls import include, path
from .views import export_result, offer, upload_leads, get_leads_score, result, view_leads, view_offers
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('offer/', offer, name='offer'),
    path('upload_leads/<int:offer_id>/', upload_leads, name='upload_leads'),
    path('score/<int:offer_id>/', get_leads_score, name='get_leads_score'),
    path('result/', result, name='result'),
    path('view_leads/', view_leads, name='view_leads'),
    path('view_offers/', view_offers, name='view_offers'),
    path('export/', export_result, name='export_result'),
]


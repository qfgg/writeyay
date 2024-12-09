from django.urls import path
from .views import AnalyzeEssayView, export_pdf, privacy, terms


urlpatterns = [
    path('analyze/', AnalyzeEssayView.as_view(), name='analyze'),
    path('export_pdf/', export_pdf, name='export_pdf'),
    path('privacy/', privacy, name='privacy'),
    path('terms/', terms, name='terms'),
]

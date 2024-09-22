from django.urls import path
from .views import AnalyzeEssayView, export_pdf


urlpatterns = [
    path('analyze/', AnalyzeEssayView.as_view(), name='analyze'),
    path('export_pdf/', export_pdf, name='export_pdf'),
]

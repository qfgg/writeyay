from django.urls import path
from .views import AnalyzeEssayView


urlpatterns = [
    path('analyze/', AnalyzeEssayView.as_view(), name='analyze'),
]

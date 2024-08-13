from django.urls import path
from . import views


urlpatterns = [
    path('pricing/', views.pricing, name='pricing'),
    path('pricing/create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('subscribe_success/', views.subscribe_success, name='subscribe_success'),
    path('subscribe_cancel/', views.subscribe_cancel, name='subscribe_cancel'),
    path('create_portal_session/', views.create_portal_session, name='create_portal_session'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('subscription', views.subscription_management, name='subscription'),
]

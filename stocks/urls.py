from django.urls import path
from . import views

urlpatterns = [
    path('stocks/<str:symbol>/', views.stock_detail, name='stock_detail'),
]

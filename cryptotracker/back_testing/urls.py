from django.urls import path
from . import views

app_name = 'back_testing'
urlpatterns = [
    path('strategies/', views.StrategyView.as_view(), name="strategies")
]
from django.urls import path, reverse_lazy
from . import views

app_name = 'tracker'
urlpatterns = [
    #path('', views.SymbolListView.as_view(), name='all'),
    #path('symbol/<int:pk>/', views.SymbolDetailView.as_view(), name='symbol_detail'),
    path('', views.Chart.as_view(), name="all"),
]
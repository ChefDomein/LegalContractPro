from django.urls import path
from .views import compare_contracts

urlpatterns = [
    path('api/compare-contracts/', compare_contracts, name='compare_contracts'),
]

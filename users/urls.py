from django.urls import path

from .views import CreateUserView,MockPurchaseView

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('purchase/mock/', MockPurchaseView.as_view(), name='purchase'),
]
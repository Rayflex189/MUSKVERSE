from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView.as_view()),
    path('auth/verify-otp/', VerifyOTPView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('auth/refresh/', TokenRefreshView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('cars/', CarListView.as_view()),
    path('fancards/', FanCardListView.as_view()),
    path('membership/', MembershipCardListView.as_view()),
    path('stocks/', StockListView.as_view()),
    path('crypto/', CryptoListView.as_view()),
    path('investments/', InvestmentPlanListView.as_view()),
    path('purchase/', PurchaseView.as_view()),
    path('transactions/', UserTransactionListView.as_view()),
]

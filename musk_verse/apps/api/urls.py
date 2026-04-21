from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

#router = DefaultRouter()
#router.register(r'api-keys', APIKeyViewSet)
#router.register(r'webhooks', WebhookViewSet)

urlpatterns = [
    #path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view()),
    path('auth/verify-otp/', VerifyOTPView.as_view()),
    path('auth/login/', LoginView.as_view()),
    path('profile/', ProfileView.as_view()),
    path('cars/', CarListView.as_view()),
    path('fancards/', FanCardListView.as_view()),
    path('membership/', MembershipCardListView.as_view()),
    path('stocks/', StockListView.as_view()),
    path('crypto/', CryptoListView.as_view()),
    path('investments/', InvestmentPlanListView.as_view()),
    path('purchase/', PurchaseView.as_view()),
    path('transactions/', UserTransactionListView.as_view()),
    
    # API Management Endpoints (Admin only)
    path('admin/api-keys/', APIKeyListCreateView.as_view()),
    path('admin/api-keys/<int:pk>/', APIKeyDetailView.as_view()),
    path('admin/api-usage/', APIUsageStatsView.as_view()),
    path('admin/api-rate-limits/', APIRateLimitView.as_view()),
]

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .serializers import *
from apps.accounts.models import User, Profile
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from .models import APIKey, APIUsageLog, APIRateLimit
from .serializers import APIKeySerializer, APIUsageLogSerializer, APIRateLimitSerializer
from django.db.models import Count, Avg, Sum
from datetime import datetime, timedelta
from apps.transactions.models import Transaction
from django.utils import timezone
from apps.products.models import Car, FanCard, MembershipCard, Stock, CryptoAsset, InvestmentPlan

# ========== Admin API Management Views ==========

class APIKeyListCreateView(generics.ListCreateAPIView):
    """List all API keys or create a new one (Admin only)"""
    permission_classes = [IsAdminUser]
    serializer_class = APIKeySerializer
    queryset = APIKey.objects.all().select_related('user')

class APIKeyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an API key (Admin only)"""
    permission_classes = [IsAdminUser]
    serializer_class = APIKeySerializer
    queryset = APIKey.objects.all()

class APIUsageStatsView(APIView):
    """Get API usage statistics (Admin only)"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Time filters
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        stats = {
            'total_requests': APIUsageLog.objects.count(),
            'requests_last_24h': APIUsageLog.objects.filter(timestamp__gte=last_24h).count(),
            'requests_last_7d': APIUsageLog.objects.filter(timestamp__gte=last_7d).count(),
            'avg_response_time_ms': APIUsageLog.objects.aggregate(Avg('response_time'))['response_time__avg'],
            'error_rate': (
                APIUsageLog.objects.filter(status_code__gte=400).count() / 
                max(APIUsageLog.objects.count(), 1) * 100
            ),
            'top_endpoints': list(
                APIUsageLog.objects.values('endpoint')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            ),
            'status_code_breakdown': list(
                APIUsageLog.objects.values('status_code')
                .annotate(count=Count('id'))
                .order_by('-count')
            ),
        }
        return Response(stats)

class APIRateLimitView(generics.ListCreateAPIView):
    """List or create rate limit rules (Admin only)"""
    permission_classes = [IsAdminUser]
    serializer_class = APIRateLimitSerializer
    queryset = APIRateLimit.objects.all().select_related('api_key')

class FanCardListView(generics.ListAPIView):
    queryset = FanCard.objects.all()
    serializer_class = FanCardSerializer

class MembershipCardListView(generics.ListAPIView):
    queryset = MembershipCard.objects.all()
    serializer_class = MembershipCardSerializer

class StockListView(generics.ListAPIView):
    queryset = Stock.objects.filter(available_quantity__gt=0)
    serializer_class = StockSerializer

class CryptoListView(generics.ListAPIView):
    queryset = CryptoAsset.objects.all()
    serializer_class = CryptoSerializer

class InvestmentPlanListView(generics.ListAPIView):
    queryset = InvestmentPlan.objects.all()
    serializer_class = InvestmentPlanSerializer

class UserTransactionListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer  # You'll need to create this serializer
    
    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')

class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    def perform_create(self, serializer):
        user = serializer.save()
        # Send OTP email
        send_mail(
            'Your Musk Verse OTP',
            f'Your OTP code is {user.otp_code}. Valid for 10 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPVerifySerializer
    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=ser.validated_data['email'])
        if user.verify_otp(ser.validated_data['otp_code']):
            return Response({'message': 'Account verified'}, status=200)
        return Response({'error': 'Invalid or expired OTP'}, status=400)

class LoginView(generics.GenericAPIView):
    serializer_class = serializers.Serializer
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = get_object_or_404(User, email=email)
        if user.check_password(password) and user.is_verified:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'profile_completed': hasattr(user, 'profile')
            })
        return Response({'error': 'Invalid credentials'}, status=401)

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

# Product listing views (similar for all)
class CarListView(generics.ListAPIView):
    queryset = Car.objects.filter(availability=True)
    serializer_class = CarSerializer

# Purchase endpoint
class PurchaseView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PurchaseSerializer
    def post(self, request):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        product_type = ser.validated_data['product_type']
        product_id = ser.validated_data['product_id']
        quantity = ser.validated_data['quantity']

        # Map product type to model and price logic (simplified)
        model_map = {
            'car': Car, 'fancard': FanCard, 'membership': MembershipCard,
            'stock': Stock, 'crypto': CryptoAsset, 'investment': InvestmentPlan
        }
        model = model_map.get(product_type)
        if not model:
            return Response({'error': 'Invalid product type'}, status=400)

        product = get_object_or_404(model, id=product_id)
        if product_type in ['stock', 'crypto']:
            if quantity > getattr(product, 'available_quantity', 0):
                return Response({'error': 'Not enough quantity'}, status=400)
            total = product.price * quantity
        else:
            total = product.price

        # Create transaction
        tx = Transaction.objects.create(
            user=request.user,
            product_type=product_type,
            product_id=product_id,
            amount=total,
            status='completed'  # In real app, integrate payment gateway
        )
        # Deduct stock quantity if needed
        if product_type == 'stock':
            product.available_quantity -= quantity
            product.save()
        return Response({'message': 'Purchase successful', 'transaction_id': tx.id}, status=201)

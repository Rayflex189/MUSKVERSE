from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .serializers import *
from apps.accounts.models import User, Profile
from apps.transactions.models import Transaction
from apps.products.models import Car, FanCard, MembershipCard, Stock, CryptoAsset, InvestmentPlan

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

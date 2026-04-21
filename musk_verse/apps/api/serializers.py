from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile
from apps.products.models import Car, FanCard, MembershipCard, Stock, CryptoAsset, InvestmentPlan
from apps.transactions.models import Transaction
# Add these imports at the top
from .models import APIKey, APIUsageLog, APIRateLimit

User = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.set_otp()  
        return user

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = ('user',)

# Product serializers (basic)
class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class FanCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FanCard
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class MembershipCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipCard
        fields = '__all__'

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = '__all__'

class CryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CryptoAsset
        fields = '__all__'

class InvestmentPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentPlan
        fields = '__all__'

class PurchaseSerializer(serializers.Serializer):
    product_type = serializers.ChoiceField(choices=Transaction.PRODUCT_TYPES)
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)  # for stocks/crypto fractional



# Add these serializer classes
class APIKeySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = APIKey
        fields = '__all__'
        read_only_fields = ('key', 'created_at', 'last_used')

class APIUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIUsageLog
        fields = '__all__'

class APIRateLimitSerializer(serializers.ModelSerializer):
    api_key_name = serializers.CharField(source='api_key.name', read_only=True)
    
    class Meta:
        model = APIRateLimit
        fields = '__all__'

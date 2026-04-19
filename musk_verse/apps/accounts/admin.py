from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Personal Information', {
            'fields': ('full_name', 'profile_image_preview', 'phone', 'date_of_birth')
        }),
        ('Location Information', {
            'fields': ('address', 'country', 'currency')
        }),
    )
    readonly_fields = ('profile_image_preview',)
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="100" height="100" style="border-radius: 50%;" />', obj.profile_image.url)
        return "No Image"
    profile_image_preview.short_description = 'Profile Image'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email',)
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Verification Status', {'fields': ('is_verified', 'otp_code', 'otp_created_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('otp_code', 'otp_created_at', 'date_joined', 'last_login')
    inlines = [ProfileInline]
    
    actions = ['verify_users', 'unverify_users']
    
    def verify_users(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} users verified successfully.")
    verify_users.short_description = "Mark selected users as verified"
    
    def unverify_users(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"{queryset.count()} users unverified.")
    unverify_users.short_description = "Mark selected users as unverified"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'full_name', 'country', 'currency', 'profile_thumbnail')
    list_filter = ('country', 'currency')
    search_fields = ('full_name', 'user__email', 'phone', 'address')
    readonly_fields = ('profile_image_preview',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name')
        }),
        ('Contact Details', {
            'fields': ('phone', 'address')
        }),
        ('Location & Currency', {
            'fields': ('country', 'currency', 'date_of_birth')
        }),
        ('Profile Image', {
            'fields': ('profile_image', 'profile_image_preview')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def profile_thumbnail(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%;" />', obj.profile_image.url)
        return "No Image"
    profile_thumbnail.short_description = 'Thumbnail'
    
    def profile_image_preview(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="200" height="200" style="border-radius: 10px;" />', obj.profile_image.url)
        return "No Image Uploaded"
    profile_image_preview.short_description = 'Profile Image Preview'

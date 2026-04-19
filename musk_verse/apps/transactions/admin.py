from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'product_type_badge', 'amount_display', 'status_badge', 'created_at')
    list_filter = ('product_type', 'status', 'created_at')
    search_fields = ('user__email', 'product_id')
    readonly_fields = ('created_at', 'transaction_details')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('User Information', {
            'fields': ('user_link', 'user_email_field')
        }),
        ('Transaction Details', {
            'fields': ('product_type', 'product_id', 'amount', 'status', 'transaction_details')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def amount_display(self, obj):
        return format_html('<span style="font-weight: bold;">${:,.2f}</span>', obj.amount)
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="background-color: {}; padding: 3px 8px; border-radius: 12px; color: white;">{}</span>', 
                          color, obj.status.upper())
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def product_type_badge(self, obj):
        icons = {
            'car': '🚗',
            'fancard': '💳',
            'membership': '👑',
            'stock': '📈',
            'crypto': '₿',
            'investment': '💰'
        }
        icon = icons.get(obj.product_type, '📦')
        return format_html('{} {}', icon, obj.product_type.title())
    product_type_badge.short_description = 'Product Type'
    
    def user_link(self, obj):
        url = reverse('admin:accounts_user_change', args=[obj.user.id])
        return format_html('<a href="{}">View User Profile</a>', url)
    user_link.short_description = 'User Actions'
    
    def user_email_field(self, obj):
        return obj.user.email
    user_email_field.short_description = 'User Email'
    
    def transaction_details(self, obj):
        return format_html("""
            <div style="background-color: #f5f5f5; padding: 10px; border-radius: 5px;">
                <strong>Transaction ID:</strong> {}<br>
                <strong>Product ID:</strong> {}<br>
                <strong>User ID:</strong> {}
            </div>
        """, obj.id, obj.product_id, obj.user.id)
    transaction_details.short_description = 'Additional Details'
    
    actions = ['mark_as_completed', 'mark_as_failed']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"{queryset.count()} transactions marked as completed.")
    mark_as_completed.short_description = "Mark selected as completed"
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"{queryset.count()} transactions marked as failed.")
    mark_as_failed.short_description = "Mark selected as failed"

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import APIKey, APIUsageLog, APIRateLimit, APIWebhook
from .serializers import APIKeySerializer

# Create these models in apps/api/models.py first
# I'll include the model definitions below

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_preview', 'user_email', 'status_badge', 'last_used', 'expiry_badge', 'created_at')
    list_filter = ('status', 'created_at', 'expires_at')
    search_fields = ('name', 'key', 'user__email', 'user__username')
    readonly_fields = ('key_display', 'key_preview_full', 'created_at', 'last_used')
    actions = ['activate_keys', 'deactivate_keys', 'revoke_keys', 'extend_expiry']
    
    fieldsets = (
        ('API Key Information', {
            'fields': ('name', 'user', 'key_display', 'status')
        }),
        ('Permissions', {
            'fields': ('permissions', 'allowed_ips')
        }),
        ('Rate Limits', {
            'fields': ('rate_limit_per_minute', 'rate_limit_per_hour', 'rate_limit_per_day')
        }),
        ('Timing', {
            'fields': ('expires_at', 'created_at', 'last_used')
        }),
    )
    
    def key_preview(self, obj):
        if obj.key:
            masked = obj.key[:8] + '...' + obj.key[-4:] if len(obj.key) > 12 else '****'
            return format_html('<code style="background: #f0f0f0; padding: 2px 6px; border-radius: 4px;">{}</code>', masked)
        return 'No Key'
    key_preview.short_description = 'API Key'
    
    def key_display(self, obj):
        if obj.key:
            return format_html("""
                <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                    <strong>API Key:</strong> 
                    <code style="background: #e9ecef; padding: 4px 8px; border-radius: 3px; user-select: all;">{}</code>
                    <br>
                    <small style="color: #6c757d;">⚠️ Copy this key now. You won't be able to see it again!</small>
                </div>
            """, obj.key)
        return 'No Key Generated'
    key_display.short_description = 'API Key Details'
    
    def key_preview_full(self, obj):
        if obj.key:
            return format_html('<code style="background: #f0f0f0; padding: 4px 8px;">{}</code>', obj.key)
        return 'No Key'
    key_preview_full.short_description = 'Full API Key'
    
    def user_email(self, obj):
        if obj.user:
            url = reverse('admin:accounts_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return 'System Key'
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def status_badge(self, obj):
        if obj.status == 'active':
            if obj.expires_at and obj.expires_at < timezone.now():
                return format_html('<span style="background-color: #dc3545; padding: 3px 8px; border-radius: 12px; color: white;">⚠️ Expired</span>')
            return format_html('<span style="background-color: #28a745; padding: 3px 8px; border-radius: 12px; color: white;">● Active</span>')
        elif obj.status == 'inactive':
            return format_html('<span style="background-color: #ffc107; padding: 3px 8px; border-radius: 12px; color: black;">○ Inactive</span>')
        elif obj.status == 'revoked':
            return format_html('<span style="background-color: #dc3545; padding: 3px 8px; border-radius: 12px; color: white;">✕ Revoked</span>')
        return format_html('<span style="background-color: #6c757d; padding: 3px 8px; border-radius: 12px; color: white;">?</span>')
    status_badge.short_description = 'Status'
    
    def expiry_badge(self, obj):
        if not obj.expires_at:
            return format_html('<span style="color: #28a745;">Never</span>')
        
        days_left = (obj.expires_at - timezone.now()).days
        if days_left < 0:
            return format_html('<span style="color: #dc3545;">Expired</span>')
        elif days_left < 7:
            return format_html('<span style="color: #ffc107;">{} days left</span>', days_left)
        else:
            return format_html('<span style="color: #28a745;">{} days left</span>', days_left)
    expiry_badge.short_description = 'Expiry'
    
    def activate_keys(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} API keys activated.")
    activate_keys.short_description = "Activate selected keys"
    
    def deactivate_keys(self, request, queryset):
        queryset.update(status='inactive')
        self.message_user(request, f"{queryset.count()} API keys deactivated.")
    deactivate_keys.short_description = "Deactivate selected keys"
    
    def revoke_keys(self, request, queryset):
        queryset.update(status='revoked')
        self.message_user(request, f"{queryset.count()} API keys revoked.")
    revoke_keys.short_description = "Revoke selected keys"
    
    def extend_expiry(self, request, queryset):
        for key in queryset:
            if key.expires_at:
                key.expires_at += timedelta(days=30)
            else:
                key.expires_at = timezone.now() + timedelta(days=30)
            key.save()
        self.message_user(request, f"Extended expiry by 30 days for {queryset.count()} keys.")
    extend_expiry.short_description = "Extend expiry by 30 days"

@admin.register(APIUsageLog)
class APIUsageLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'api_key_name', 'endpoint_short', 'method_badge', 'status_code_badge', 'response_time_display', 'timestamp_relative')
    list_filter = ('method', 'status_code', 'timestamp', 'api_key__status')
    search_fields = ('endpoint', 'api_key__name', 'api_key__user__email', 'ip_address')
    readonly_fields = ('request_details', 'response_details', 'timestamp')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('API Key Information', {
            'fields': ('api_key_link', 'api_key_name_field')
        }),
        ('Request Details', {
            'fields': ('method', 'endpoint', 'ip_address', 'user_agent', 'request_details')
        }),
        ('Response Details', {
            'fields': ('status_code', 'response_time', 'response_size', 'response_details')
        }),
        ('Timing', {
            'fields': ('timestamp', 'timestamp_relative_field')
        }),
    )
    
    def api_key_name(self, obj):
        if obj.api_key:
            return format_html('<strong>{}</strong>', obj.api_key.name)
        return 'No API Key'
    api_key_name.short_description = 'API Key'
    api_key_name.admin_order_field = 'api_key__name'
    
    def endpoint_short(self, obj):
        max_length = 50
        if len(obj.endpoint) > max_length:
            return obj.endpoint[:max_length] + '...'
        return obj.endpoint
    endpoint_short.short_description = 'Endpoint'
    
    def method_badge(self, obj):
        colors = {
            'GET': '#28a745',
            'POST': '#007bff',
            'PUT': '#ffc107',
            'DELETE': '#dc3545',
            'PATCH': '#17a2b8'
        }
        color = colors.get(obj.method, '#6c757d')
        return format_html('<span style="background-color: {}; padding: 2px 8px; border-radius: 4px; color: white; font-weight: bold;">{}</span>', 
                          color, obj.method)
    method_badge.short_description = 'Method'
    
    def status_code_badge(self, obj):
        if 200 <= obj.status_code < 300:
            bg = '#28a745'
        elif 300 <= obj.status_code < 400:
            bg = '#17a2b8'
        elif 400 <= obj.status_code < 500:
            bg = '#ffc107'
            text_color = 'black'
        elif 500 <= obj.status_code < 600:
            bg = '#dc3545'
            text_color = 'white'
        else:
            bg = '#6c757d'
            text_color = 'white'
        
        return format_html('<span style="background-color: {}; padding: 2px 8px; border-radius: 4px; color: {}; font-weight: bold;">{}</span>', 
                          bg, text_color if 'text_color' in locals() else 'white', obj.status_code)
    status_code_badge.short_description = 'Status'
    
    def response_time_display(self, obj):
        if obj.response_time < 100:
            color = '#28a745'
        elif obj.response_time < 500:
            color = '#ffc107'
        else:
            color = '#dc3545'
        return format_html('<span style="color: {}; font-weight: bold;">{}ms</span>', color, obj.response_time)
    response_time_display.short_description = 'Response Time'
    response_time_display.admin_order_field = 'response_time'
    
    def timestamp_relative(self, obj):
        now = timezone.now()
        diff = now - obj.timestamp
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return f"{diff.seconds} seconds ago"
    timestamp_relative.short_description = 'Time'
    timestamp_relative.admin_order_field = 'timestamp'
    
    def api_key_link(self, obj):
        if obj.api_key:
            url = reverse('admin:api_apikey_change', args=[obj.api_key.id])
            return format_html('<a href="{}">View API Key</a>', url)
        return 'No API Key'
    api_key_link.short_description = 'API Key Actions'
    
    def api_key_name_field(self, obj):
        return obj.api_key.name if obj.api_key else 'No API Key'
    api_key_name_field.short_description = 'API Key Name'
    
    def request_details(self, obj):
        return format_html("""
            <details>
                <summary style="cursor: pointer; color: #007bff;">View Request Details</summary>
                <pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px;">{}</pre>
            </details>
        """, obj.request_data[:1000] if obj.request_data else 'No data captured')
    request_details.short_description = 'Request Data'
    
    def response_details(self, obj):
        return format_html("""
            <details>
                <summary style="cursor: pointer; color: #007bff;">View Response Details</summary>
                <pre style="background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 5px;">{}</pre>
            </details>
        """, obj.response_data[:1000] if obj.response_data else 'No data captured')
    response_details.short_description = 'Response Data'
    
    def timestamp_relative_field(self, obj):
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    timestamp_relative_field.short_description = 'Full Timestamp'
    
    actions = ['clear_old_logs', 'analyze_slow_requests']
    
    def clear_old_logs(self, request, queryset):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        old_logs = APIUsageLog.objects.filter(timestamp__lt=thirty_days_ago)
        count = old_logs.count()
        old_logs.delete()
        self.message_user(request, f"Deleted {count} logs older than 30 days.")
    clear_old_logs.short_description = "Delete logs older than 30 days"
    
    def analyze_slow_requests(self, request, queryset):
        slow_requests = queryset.filter(response_time__gt=1000)
        self.message_user(request, f"Found {slow_requests.count()} requests slower than 1000ms.")
    analyze_slow_requests.short_description = "Analyze slow requests (>1000ms)"

@admin.register(APIRateLimit)
class APIRateLimitAdmin(admin.ModelAdmin):
    list_display = ('api_key_name', 'endpoint_pattern', 'method', 'limit_per_minute_badge', 'current_usage_display', 'reset_time')
    list_filter = ('method', 'endpoint_pattern')
    search_fields = ('api_key__name', 'endpoint_pattern')
    readonly_fields = ('current_usage', 'last_reset', 'usage_percentage')
    
    fieldsets = (
        ('Rate Limit Configuration', {
            'fields': ('api_key', 'endpoint_pattern', 'method')
        }),
        ('Limits', {
            'fields': ('limit_per_minute', 'limit_per_hour', 'limit_per_day')
        }),
        ('Current Usage', {
            'fields': ('current_usage', 'last_reset', 'usage_percentage', 'reset_time')
        }),
    )
    
    def api_key_name(self, obj):
        return obj.api_key.name if obj.api_key else 'Global Rule'
    api_key_name.short_description = 'API Key'
    
    def limit_per_minute_badge(self, obj):
        if obj.limit_per_minute == 0:
            return format_html('<span style="color: #dc3545;">Unlimited</span>')
        return format_html('<span style="color: #28a745;">{} req/min</span>', obj.limit_per_minute)
    limit_per_minute_badge.short_description = 'Per Minute Limit'
    
    def current_usage_display(self, obj):
        minute_usage = obj.current_usage.get('minute', 0)
        minute_limit = obj.limit_per_minute
        
        if minute_limit > 0:
            percentage = (minute_usage / minute_limit) * 100
            if percentage > 90:
                color = '#dc3545'
            elif percentage > 75:
                color = '#ffc107'
            else:
                color = '#28a745'
            return format_html('<span style="color: {};">{} / {} ({:.1f}%)</span>', color, minute_usage, minute_limit, percentage)
        return f"{minute_usage} requests"
    current_usage_display.short_description = 'Current Usage'
    
    def usage_percentage(self, obj):
        minute_usage = obj.current_usage.get('minute', 0)
        minute_limit = obj.limit_per_minute
        
        if minute_limit > 0:
            percentage = (minute_usage / minute_limit) * 100
            bar_width = min(percentage, 100)
            color = '#28a745' if percentage < 75 else '#ffc107' if percentage < 90 else '#dc3545'
            return format_html("""
                <div style="background: #e9ecef; border-radius: 10px; overflow: hidden; width: 200px;">
                    <div style="background: {}; width: {}%; height: 20px; text-align: center; color: white; line-height: 20px;">
                        {:.1f}%
                    </div>
                </div>
            """, color, bar_width, percentage)
        return 'No limit set'
    usage_percentage.short_description = 'Usage Percentage'
    
    def reset_time(self, obj):
        next_reset = obj.last_reset + timedelta(minutes=1) if obj.last_reset else timezone.now()
        time_until_reset = (next_reset - timezone.now()).total_seconds()
        
        if time_until_reset > 0:
            return format_html('<span style="color: #17a2b8;">Resets in {} seconds</span>', int(time_until_reset))
        return format_html('<span style="color: #28a745;">Ready to reset</span>')
    reset_time.short_description = 'Reset Timer'

@admin.register(APIWebhook)
class APIWebhookAdmin(admin.ModelAdmin):
    list_display = ('name', 'url_short', 'event_type_badge', 'status_badge', 'last_triggered', 'success_rate')
    list_filter = ('status', 'event_type', 'created_at')
    search_fields = ('name', 'url', 'secret')
    readonly_fields = ('last_triggered', 'last_response', 'created_at', 'updated_at')
    actions = ['test_webhook', 'enable_webhooks', 'disable_webhooks']
    
    fieldsets = (
        ('Webhook Configuration', {
            'fields': ('name', 'url', 'secret', 'event_type', 'status')
        }),
        ('Retry Settings', {
            'fields': ('retry_count', 'timeout_seconds')
        }),
        ('Status', {
            'fields': ('last_triggered', 'last_response', 'success_count', 'failure_count', 'success_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def url_short(self, obj):
        max_length = 50
        if len(obj.url) > max_length:
            return obj.url[:max_length] + '...'
        return obj.url
    url_short.short_description = 'URL'
    
    def event_type_badge(self, obj):
        colors = {
            'user_registered': '#28a745',
            'purchase_completed': '#007bff',
            'investment_matured': '#ffc107',
            'api_key_created': '#17a2b8',
            'transaction_failed': '#dc3545'
        }
        color = colors.get(obj.event_type, '#6c757d')
        return format_html('<span style="background-color: {}; padding: 3px 8px; border-radius: 12px; color: white;">{}</span>', 
                          color, obj.event_type.replace('_', ' ').title())
    event_type_badge.short_description = 'Event Type'
    
    def status_badge(self, obj):
        if obj.status == 'active':
            return format_html('<span style="background-color: #28a745; padding: 3px 8px; border-radius: 12px; color: white;">● Active</span>')
        return format_html('<span style="background-color: #6c757d; padding: 3px 8px; border-radius: 12px; color: white;">○ Inactive</span>')
    status_badge.short_description = 'Status'
    
    def success_rate(self, obj):
        total = obj.success_count + obj.failure_count
        if total == 0:
            return format_html('<span style="color: #6c757d;">N/A</span>')
        
        rate = (obj.success_count / total) * 100
        if rate > 90:
            color = '#28a745'
        elif rate > 70:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html("""
            <div>
                <span style="color: {}; font-weight: bold;">{:.1f}%</span>
                <br>
                <small>Success: {} | Failed: {}</small>
            </div>
        """, color, rate, obj.success_count, obj.failure_count)
    success_rate.short_description = 'Success Rate'
    
    def test_webhook(self, request, queryset):
        import requests
        for webhook in queryset:
            try:
                response = requests.post(webhook.url, json={'test': True}, timeout=webhook.timeout_seconds)
                if response.status_code == 200:
                    self.message_user(request, f"Webhook '{webhook.name}' test successful!")
                else:
                    self.message_user(request, f"Webhook '{webhook.name}' returned {response.status_code}", level='ERROR')
            except Exception as e:
                self.message_user(request, f"Webhook '{webhook.name}' failed: {str(e)}", level='ERROR')
    test_webhook.short_description = "Test selected webhooks"
    
    def enable_webhooks(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"Enabled {queryset.count()} webhooks.")
    enable_webhooks.short_description = "Enable selected webhooks"
    
    def disable_webhooks(self, request, queryset):
        queryset.update(status='inactive')
        self.message_user(request, f"Disabled {queryset.count()} webhooks.")
    disable_webhooks.short_description = "Disable selected webhooks"

# Dashboard Widget for API Analytics
class APIAnalyticsDashboard(admin.ModelAdmin):
    change_list_template = 'admin/api_analytics_dashboard.html'
    
    def changelist_view(self, request, extra_context=None):
        from django.db.models import Count, Avg, Sum
        from datetime import datetime, timedelta
        
        last_24h = timezone.now() - timedelta(hours=24)
        last_7d = timezone.now() - timedelta(days=7)
        
        extra_context = extra_context or {}
        extra_context.update({
            'total_requests': APIUsageLog.objects.count(),
            'requests_last_24h': APIUsageLog.objects.filter(timestamp__gte=last_24h).count(),
            'avg_response_time': APIUsageLog.objects.aggregate(Avg('response_time'))['response_time__avg'],
            'error_rate': APIUsageLog.objects.filter(status_code__gte=400).count() / max(APIUsageLog.objects.count(), 1) * 100,
            'top_endpoints': APIUsageLog.objects.values('endpoint').annotate(count=Count('id')).order_by('-count')[:10],
            'active_keys': APIKey.objects.filter(status='active').count(),
            'total_keys': APIKey.objects.count(),
            'recent_logs': APIUsageLog.objects.order_by('-timestamp')[:50],
        })
        return super().changelist_view(request, extra_context=extra_context)

# Register the analytics dashboard
admin.site.register_view('api-analytics', view=APIAnalyticsDashboard, name='API Analytics')

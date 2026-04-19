from django.contrib import admin
from django.utils.html import format_html
from .models import Car, FanCard, MembershipCard, Stock, CryptoAsset, InvestmentPlan

class BaseProductAdmin(admin.ModelAdmin):
    list_per_page = 25
    actions = ['make_available', 'make_unavailable']
    
    def make_available(self, request, queryset):
        queryset.update(availability=True)
        self.message_user(request, f"{queryset.count()} products marked as available.")
    make_available.short_description = "Mark selected as available"
    
    def make_unavailable(self, request, queryset):
        queryset.update(availability=False)
        self.message_user(request, f"{queryset.count()} products marked as unavailable.")
    make_unavailable.short_description = "Mark selected as unavailable"

@admin.register(Car)
class CarAdmin(BaseProductAdmin):
    list_display = ('name', 'price_display', 'availability', 'car_thumbnail')
    list_filter = ('availability',)
    search_fields = ('name', 'description')
    fieldsets = (
        ('Car Information', {
            'fields': ('name', 'description', 'price', 'availability')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
    )
    readonly_fields = ('image_preview',)
    
    def price_display(self, obj):
        return f"${obj.price:,.2f}"
    price_display.short_description = 'Price'
    price_display.admin_order_field = 'price'
    
    def car_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    car_thumbnail.short_description = 'Image'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="300" height="200" style="object-fit: cover;" />', obj.image.url)
        return "No Image Uploaded"
    image_preview.short_description = 'Image Preview'

@admin.register(FanCard)
class FanCardAdmin(BaseProductAdmin):
    list_display = ('name', 'price_display', 'card_thumbnail')
    search_fields = ('name', 'benefits')
    fieldsets = (
        ('Fan Card Details', {
            'fields': ('name', 'benefits', 'price')
        }),
        ('Media', {
            'fields': ('image', 'image_preview')
        }),
    )
    readonly_fields = ('image_preview',)
    
    def price_display(self, obj):
        return f"${obj.price:,.2f}"
    price_display.short_description = 'Price'
    
    def card_thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "No Image"
    card_thumbnail.short_description = 'Image'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" />', obj.image.url)
        return "No Image Uploaded"
    image_preview.short_description = 'Preview'

@admin.register(MembershipCard)
class MembershipCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier_badge', 'price_display', 'benefits_summary')
    list_filter = ('tier',)
    search_fields = ('name', 'benefits')
    
    fieldsets = (
        ('Membership Information', {
            'fields': ('name', 'tier', 'benefits', 'price')
        }),
    )
    
    def tier_badge(self, obj):
        colors = {
            'bronze': '#cd7f32',
            'silver': '#c0c0c0',
            'gold': '#ffd700',
            'platinum': '#e5e4e2'
        }
        color = colors.get(obj.tier, '#000000')
        return format_html('<span style="background-color: {}; padding: 3px 8px; border-radius: 12px; color: white;">{}</span>', 
                          color, obj.tier.upper())
    tier_badge.short_description = 'Tier'
    
    def price_display(self, obj):
        return f"${obj.price:,.2f}"
    price_display.short_description = 'Price'
    
    def benefits_summary(self, obj):
        return obj.benefits[:100] + '...' if len(obj.benefits) > 100 else obj.benefits
    benefits_summary.short_description = 'Benefits'

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price_display', 'available_quantity', 'stock_status')
    list_filter = ('available_quantity',)
    search_fields = ('name', 'symbol')
    actions = ['add_stock', 'reduce_stock']
    
    def price_display(self, obj):
        return f"${obj.price:,.2f}"
    price_display.short_description = 'Price'
    
    def stock_status(self, obj):
        if obj.available_quantity > 1000:
            return format_html('<span style="color: green;">● High</span>')
        elif obj.available_quantity > 100:
            return format_html('<span style="color: orange;">● Medium</span>')
        else:
            return format_html('<span style="color: red;">● Low</span>')
    stock_status.short_description = 'Status'
    
    def add_stock(self, request, queryset):
        for stock in queryset:
            stock.available_quantity += 100
            stock.save()
        self.message_user(request, f"Added 100 shares to {queryset.count()} stocks.")
    add_stock.short_description = "Add 100 shares to selected stocks"
    
    def reduce_stock(self, request, queryset):
        for stock in queryset:
            if stock.available_quantity >= 100:
                stock.available_quantity -= 100
                stock.save()
        self.message_user(request, f"Reduced 100 shares from selected stocks.")
    reduce_stock.short_description = "Reduce 100 shares from selected stocks"

@admin.register(CryptoAsset)
class CryptoAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'symbol', 'price_display', 'fractional_allowed_icon')
    search_fields = ('name', 'symbol')
    
    def price_display(self, obj):
        return f"${obj.price:,.8f}"
    price_display.short_description = 'Price'
    
    def fractional_allowed_icon(self, obj):
        if obj.fractional_allowed:
            return format_html('✅ Allowed')
        return format_html('❌ Not Allowed')
    fractional_allowed_icon.short_description = 'Fractional Trading'

@admin.register(InvestmentPlan)
class InvestmentPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'roi_percentage_display', 'duration_days', 'minimum_amount_display')
    list_filter = ('duration',)
    search_fields = ('name', 'description')
    
    def roi_percentage_display(self, obj):
        return format_html('<span style="color: green; font-weight: bold;">{}%</span>', obj.roi_percentage)
    roi_percentage_display.short_description = 'ROI'
    
    def duration_days(self, obj):
        return f"{obj.duration} days"
    duration_days.short_description = 'Duration'
    
    def minimum_amount_display(self, obj):
        return f"${obj.minimum_amount:,.2f}"
    minimum_amount_display.short_description = 'Minimum Investment'

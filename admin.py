from django.contrib import admin
from .models import Category, MenuItem, Cart, CartItem, Order, OrderItem, Feedback, NewsletterSubscriber, PromoCode, UserProfile

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'is_popular', 'is_new', 'rating']
    list_filter = ['category', 'is_veg', 'is_available', 'is_popular', 'is_new']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_popular', 'is_new']
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discounted_price')
        }),
        ('Product Details', {
            'fields': ('is_veg', 'calories', 'prep_time')
        }),
        ('Status', {
            'fields': ('is_available', 'is_popular', 'is_new', 'is_bestseller')
        }),
        ('Ratings', {
            'fields': ('rating', 'total_reviews')
        }),
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'created_at', 'get_item_count']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_id']
    readonly_fields = ['created_at', 'updated_at']

    def get_item_count(self, obj):
        return obj.get_item_count()
    get_item_count.short_description = 'Total Items'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'menu_item', 'quantity', 'price', 'get_total']
    list_filter = ['cart__user']
    search_fields = ['menu_item__name']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['name', 'price', 'quantity', 'get_total']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'phone', 'total', 'status', 'payment_method', 'order_date']
    list_filter = ['status', 'payment_method', 'order_date']
    search_fields = ['name', 'email', 'phone', 'id']
    readonly_fields = ['subtotal', 'tax', 'delivery_fee', 'discount', 'total', 'order_date', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status']
    date_hierarchy = 'order_date'
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Delivery Address', {
            'fields': ('address', 'city', 'pincode')
        }),
        ('Order Details', {
            'fields': ('status', 'payment_method')
        }),
        ('Financial Summary', {
            'fields': ('subtotal', 'tax', 'delivery_fee', 'discount', 'total')
        }),
        ('Timestamps', {
            'fields': ('order_date', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'name', 'quantity', 'price', 'get_total']
    list_filter = ['order__status']
    search_fields = ['name', 'order__id']

    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Total'

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['name', 'email', 'comments']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'name', 'email', 'phone')
        }),
        ('Feedback Details', {
            'fields': ('rating', 'comments', 'photo')
        }),
        ('Status', {
            'fields': ('is_approved', 'created_at')
        }),
    )

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    readonly_fields = ['subscribed_at']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'is_active', 'used_count']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code', 'description']
    list_editable = ['is_active']
    readonly_fields = ['used_count', 'created_at']
    
    fieldsets = (
        ('Promo Code Information', {
            'fields': ('code', 'description', 'discount_type', 'discount_value')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'used_count', 'min_order_value')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'email_notifications', 'sms_notifications', 'total_orders', 'total_spent']
    list_filter = ['email_notifications', 'sms_notifications']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['total_orders', 'total_spent', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'default_address', 'default_city', 'default_pincode')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Profile', {
            'fields': ('avatar',)
        }),
        ('Statistics', {
            'fields': ('total_orders', 'total_spent')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
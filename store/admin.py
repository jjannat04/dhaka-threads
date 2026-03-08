from django.contrib import admin
from .models import User, Category, Product, Order, Review, Wishlist, OrderItem


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Wishlist)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'full_name', 'total_amount', 'created_at', 'is_paid']
    list_filter = ['is_paid', 'created_at']
    inlines = [OrderItemInline]
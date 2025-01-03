from django.contrib import admin
from .models import Book, Order, Cart, CartItem, PaymentDetail

admin.site.register(Book)
admin.site.register(Order)
# admin.py

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_amount')

    def total_items(self, obj):
        return obj.cart_items.count()
    total_items.short_description = 'Total Items'

    def total_amount(self, obj):
        return obj.total_amount
    total_amount.short_description = 'Total Amount'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'book', 'quantity', 'total_price')
    list_filter = ('cart',)

@admin.register(PaymentDetail)
class PaymentDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'contact', 'amount', 'payment_status', 'created_at')
    search_fields = ('name', 'email', 'contact')
    list_filter = ('payment_status', 'created_at')

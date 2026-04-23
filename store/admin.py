from django.contrib import admin
from .models import Product, ProductVariant, Order, OrderItem


class VariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_available', 'is_featured', 'sort_order')
    list_filter = ('category', 'is_available', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariantInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product_name', 'weight', 'price', 'quantity', 'line_total')
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'delivery_name', 'total', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'delivery_name', 'delivery_phone')
    readonly_fields = ('order_id', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

    actions = ['mark_confirmed', 'mark_shipped', 'mark_delivered']

    def mark_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_confirmed.short_description = 'Mark as Confirmed'

    def mark_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_shipped.short_description = 'Mark as Shipped'

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_delivered.short_description = 'Mark as Delivered'

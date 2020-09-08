from django.contrib import admin
from .models import Item, OrderItem, Order, Address, Payment, Discount, Refund
# Register your models here.

def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(
        refund_requested=False, refund_granted=True
    )
make_refund_accepted.short_description = 'Update orders to refund granted'
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered', 'being_delivered',
                    'recieved', 'refund_requested', 'refund_granted', 'billing_address', 'shippings_address', 'payment', 'discount']
    list_display_links = ['user', 'billing_address',
                          'shippings_address', 'payment', 'discount']
    list_filter = ['ordered', 'being_delivered',
                   'recieved', 'refund_requested', 'refund_granted']

    search_fields = [
        'user__username',
        'ref_code'
    ]

    actions = [make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'shipping_address',
        'shipping_address2',
        'shipping_country',
        'shipping_zip',
        'address_type',
        'default'
    ]

    list_filter = [
        'shipping_country',
        'default', 
        'address_type'
    ]

    search_fields = [
        'user',
        'shipping_address',
        'shipping_address2',
        'shipping_country',
        'shipping_zip',
        'address_type',
        'default'
    ]

admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Payment)
admin.site.register(Discount)
admin.site.register(Refund)

from django.urls import path

from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product/<slug>/', DetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-single-from-cart/<slug>/',
         remove_single_from_cart, name='remove-single-from-cart'),
    path('remove-from-cart/<slug>/',
         remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('add-discount/', AddDiscount.as_view(), name='add-discount'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),

]

from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.home_view, name='home'),

    # Cart (AJAX endpoints)
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Orders
    path('checkout/',                   views.checkout_view,          name='checkout'),
    path('place-order/',                views.place_order,             name='place_order'),
    path('razorpay/create/',            views.razorpay_create_order,   name='razorpay_create'),
    path('razorpay/verify/',            views.razorpay_verify_payment, name='razorpay_verify'),
    path('order/<str:order_id>/',       views.order_confirmation_view, name='order_confirmation'),
    path('my-orders/',                  views.my_orders_view,          name='my_orders'),
]

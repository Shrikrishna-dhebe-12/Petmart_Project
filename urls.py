from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # About
    path('about/', views.about, name='about'),
    
    # Menu
    path('menu/', views.menu, name='menu'),
    path('menu/<slug:slug>/', views.menu_item_detail, name='menu_item_detail'),
    
    # Feedback
    path('feedback/', views.feedback, name='feedback'),
    path('feedback/success/', views.feedback_success, name='feedback_success'),
    
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/data/', views.get_cart, name='get_cart'),
    
    # Checkout & Orders
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.orders, name='orders'),
    
    # User Profile
    path('profile/', views.profile, name='profile'),
    
    # Newsletter
    path('newsletter/', views.newsletter_signup, name='newsletter'),
    
    # Promo Code
    path('validate-promo/', views.validate_promo, name='validate_promo'),
]
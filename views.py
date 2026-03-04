from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from datetime import datetime
from .models import Feedback, Cart, CartItem, MenuItem, PromoCode, Order, OrderItem, UserProfile, NewsletterSubscriber

# ==================== HOME PAGE ====================
def home(request):
    return render(request, 'home.html')

# ==================== ABOUT PAGE ====================
def about(request):
    return render(request, 'about.html')

# ==================== MENU PAGE ====================
def menu(request):
    return render(request, 'menu.html')

def menu_item_detail(request, slug):
    return render(request, 'menu_item_detail.html', {'slug': slug})

# ==================== FEEDBACK ====================
def feedback(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        rating = request.POST.get('rating')
        comments = request.POST.get('comments')
        
        if not name or not email:
            messages.error(request, 'Name and email are required.')
            return render(request, 'feedback.html')
        
        try:
            feedback_entry = Feedback.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone if phone else '',
                rating=int(rating) if rating else 5,
                comments=comments if comments else ''
            )
            request.session['last_feedback_id'] = feedback_entry.id
            messages.success(request, 'Thank you for your feedback!')
            return redirect('feedback_success')
        except Exception as e:
            messages.error(request, f'Error saving feedback: {str(e)}')
            return render(request, 'feedback.html')
    
    context = {}
    if request.user.is_authenticated:
        context = {
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        }
    return render(request, 'feedback.html', context)

def feedback_success(request):
    feedback_id = request.session.get('last_feedback_id')
    feedback_entry = None
    if feedback_id:
        try:
            feedback_entry = Feedback.objects.get(id=feedback_id)
        except Feedback.DoesNotExist:
            pass
    return render(request, 'feedback_success.html', {'feedback': feedback_entry})

# ==================== AUTHENTICATION ====================
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'signup.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return render(request, 'signup.html')
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created! Please login.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')
    
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('home')

# ==================== PROFILE ====================
@login_required
def profile(request):
    # Get user's orders only (remove service bookings)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')[:5]
    
    # Get counts
    total_orders = Order.objects.filter(user=request.user).count()
    total_spent = sum(order.total for order in Order.objects.filter(user=request.user))
    
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        # No booking-related context
    }
    return render(request, 'profile.html', context)

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders.html', {'orders': user_orders})

# ==================== CART FUNCTIONS ====================
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    return cart

def cart_view(request):
    return render(request, 'cart.html')

def add_to_cart(request, item_id):
    if request.method == 'POST':
        try:
            menu_item = get_object_or_404(MenuItem, id=item_id, is_available=True)
            cart = get_or_create_cart(request)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                defaults={'quantity': 1, 'price': menu_item.get_price()}
            )
            
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': f'{menu_item.name} added to cart!',
                'cart_count': cart.get_item_count()
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def update_cart(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            quantity = int(data.get('quantity', 1))
            
            cart = get_or_create_cart(request)
            
            try:
                cart_item = CartItem.objects.get(cart=cart, menu_item_id=item_id)
                
                if quantity <= 0:
                    cart_item.delete()
                    message = 'Item removed from cart'
                else:
                    cart_item.quantity = quantity
                    cart_item.save()
                    message = 'Cart updated'
                
                return JsonResponse({
                    'success': True,
                    'message': message,
                    'cart_count': cart.get_item_count(),
                    'cart_total': float(cart.get_total())
                })
            except CartItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Item not found in cart'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def remove_from_cart(request, item_id):
    if request.method == 'POST':
        try:
            cart = get_or_create_cart(request)
            deleted = CartItem.objects.filter(cart=cart, menu_item_id=item_id).delete()
            
            if deleted[0] > 0:
                return JsonResponse({
                    'success': True,
                    'message': 'Item removed from cart',
                    'cart_count': cart.get_item_count()
                })
            else:
                return JsonResponse({'success': False, 'error': 'Item not found in cart'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def get_cart(request):
    try:
        cart = get_or_create_cart(request)
        
        items = []
        for item in cart.items.all():
            items.append({
                'id': item.menu_item.id,
                'name': item.menu_item.name,
                'price': float(item.price),
                'quantity': item.quantity,
                'total': float(item.get_total()),
                'image': item.menu_item.image.url if item.menu_item.image else None,
                'category': item.menu_item.category.name if item.menu_item.category else 'Food'
            })
        
        subtotal = float(cart.get_total())
        tax = round(subtotal * 0.05, 2)
        delivery_fee = 40
        total = subtotal + tax + delivery_fee
        
        return JsonResponse({
            'success': True,
            'items': items,
            'subtotal': subtotal,
            'tax': tax,
            'delivery_fee': delivery_fee,
            'total': total,
            'count': cart.get_item_count()
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# ==================== CHECKOUT ====================
def checkout(request):
    if request.method == 'POST':
        cart_data = request.POST.get('cart_data')
        if cart_data:
            try:
                cart_items = json.loads(cart_data)
                request.session['checkout_cart'] = cart_items
            except Exception as e:
                print(f"Error: {e}")
    
    return render(request, 'checkout.html')

def place_order(request):
    if request.method == 'POST':
        cart_items = request.session.get('checkout_cart', [])
        
        if not cart_items:
            try:
                cart_data = request.POST.get('cart_data')
                if cart_data:
                    cart_items = json.loads(cart_data)
            except:
                cart_items = []
        
        if not cart_items:
            messages.error(request, 'Your cart is empty!')
            return redirect('menu')
        
        name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address', '')
        city = request.POST.get('city', '')
        pincode = request.POST.get('pincode', '')
        payment_method = request.POST.get('payment_method', 'cod')
        
        if not name or not email or not phone or not address:
            messages.error(request, 'Please fill all fields')
            return redirect('checkout')
        
        try:
            subtotal = 0
            order_items_data = []
            
            for item in cart_items:
                quantity = int(item.get('quantity', 1))
                price = float(item.get('price', 0))
                subtotal += price * quantity
                
                order_items_data.append({
                    'name': item.get('name', 'Unknown Item'),
                    'price': price,
                    'quantity': quantity
                })
            
            tax = round(subtotal * 0.05, 2)
            delivery_fee = 40
            total = subtotal + tax + delivery_fee
            
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                pincode=pincode,
                payment_method=payment_method,
                status='confirmed',
                subtotal=subtotal,
                tax=tax,
                delivery_fee=delivery_fee,
                discount=0,
                total=total,
            )
            
            for item_data in order_items_data:
                OrderItem.objects.create(
                    order=order,
                    name=item_data['name'],
                    price=item_data['price'],
                    quantity=item_data['quantity']
                )
            
            if request.user.is_authenticated:
                try:
                    cart = Cart.objects.get(user=request.user)
                    cart.items.all().delete()
                except:
                    pass
            
            if 'checkout_cart' in request.session:
                del request.session['checkout_cart']
            
            messages.success(request, f'Order #{order.id} placed!')
            return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return redirect('checkout')
    
    return redirect('checkout')

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_confirmation.html', {'order': order})

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})

# ==================== NEWSLETTER ====================
def newsletter_signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            # Check if already subscribed
            if not NewsletterSubscriber.objects.filter(email=email).exists():
                NewsletterSubscriber.objects.create(email=email)
                messages.success(request, f'Successfully subscribed with {email}!')
            else:
                messages.info(request, 'Email already subscribed!')
        else:
            messages.error(request, 'Please enter email.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect('home')

# ==================== PROMO CODE ====================
def validate_promo(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').upper()
            
            try:
                promo = PromoCode.objects.get(code=code, is_active=True)
                
                if promo.is_valid():
                    return JsonResponse({
                        'success': True,
                        'discount': float(promo.discount_value),
                        'message': f'Promo applied! You saved ₹{promo.discount_value}'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Promo code expired'
                    })
            except PromoCode.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid promo code'
                })
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request'})
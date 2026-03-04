# restaurant_app/context_processors.py
from .models import Cart

def cart_count(request):
    """Add cart count to all templates"""
    count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            count = cart.get_item_count()
    else:
        session_id = request.session.session_key
        if session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
            if cart:
                count = cart.get_item_count()
    
    return {'cart_count': count}
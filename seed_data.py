from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from Petmart_Project.models import Category, MenuItem, PromoCode

class Command(BaseCommand):
    help = 'Seed database with initial data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Create categories
        categories = [
            {'name': 'Burgers', 'slug': 'burgers', 'order': 1, 'description': 'Delicious burgers made with 100% pure beef'},
            {'name': 'Chicken', 'slug': 'chicken', 'order': 2, 'description': 'Crispy and juicy chicken items'},
            {'name': 'Fries & Sides', 'slug': 'fries', 'order': 3, 'description': 'Perfect sides to complete your meal'},
            {'name': 'Beverages', 'slug': 'drinks', 'order': 4, 'description': 'Refreshing drinks and shakes'},
            {'name': 'Desserts', 'slug': 'desserts', 'order': 5, 'description': 'Sweet treats to end your meal'},
            {'name': 'Happy Meal', 'slug': 'happy-meal', 'order': 6, 'description': 'Specially designed for kids'},
        ]
        
        for cat_data in categories:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'Created category: {cat.name}')
        
        # Create promo codes
        promos = [
            {'code': 'WELCOME50', 'discount_type': 'percentage', 'discount_value': 50, 
             'max_discount_amount': 100, 'min_order_value': 199, 'description': '50% off up to ₹100 on first order'},
            {'code': 'SAVE20', 'discount_type': 'percentage', 'discount_value': 20, 
             'max_discount_amount': 150, 'min_order_value': 299, 'description': '20% off up to ₹150'},
            {'code': 'FLAT100', 'discount_type': 'fixed', 'discount_value': 100, 
             'min_order_value': 399, 'description': 'Flat ₹100 off on orders above ₹399'},
        ]
        
        for promo_data in promos:
            promo_data['valid_from'] = timezone.now()
            promo_data['valid_to'] = timezone.now() + timedelta(days=30)
            
            promo, created = PromoCode.objects.get_or_create(
                code=promo_data['code'],
                defaults=promo_data
            )
            if created:
                self.stdout.write(f'Created promo: {promo.code}')
        
        self.stdout.write(self.style.SUCCESS('Data seeded successfully!'))
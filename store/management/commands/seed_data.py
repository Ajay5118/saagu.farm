"""
Seed initial product data for Saagu.farm
Run: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from store.models import Product, ProductVariant


class Command(BaseCommand):
    help = 'Seed initial products and variants'

    def handle(self, *args, **kwargs):
        products_data = [
            {
                'name': 'Signature Chilli Powder',
                'slug': 'chilli-powder',
                'description': 'The pride of Saagu.farm. Grown in our own local fields, sun-dried for 15 days.',
                'category': 'spice',
                'badge': 'PURE VEG',
                'is_featured': True,
                'sort_order': 1,
                'variants': [
                    {'weight': '250g', 'weight_grams': 250, 'price': 99, 'mrp': 125},
                    {'weight': '500g', 'weight_grams': 500, 'price': 199, 'mrp': 229},
                ],
            },
            {
                'name': 'Authentic Veg Pickle',
                'slug': 'veg-pickle',
                'description': 'Homemade style with premium oils and our own spice blend.',
                'category': 'pickle_veg',
                'badge': 'PURE VEG',
                'is_featured': True,
                'sort_order': 2,
                'variants': [
                    {'weight': '250g', 'weight_grams': 250, 'price': 200, 'mrp': 200},
                    {'weight': '500g', 'weight_grams': 500, 'price': 400, 'mrp': 400},
                ],
            },
            {
                'name': 'Spicy Chicken Pickle',
                'slug': 'chicken-pickle',
                'description': 'Tender chunks marinated in our signature fiery chilli base.',
                'category': 'pickle_nv',
                'badge': 'Non-Veg',
                'is_featured': True,
                'sort_order': 3,
                'variants': [
                    {'weight': '250g', 'weight_grams': 250, 'price': 250, 'mrp': 250},
                    {'weight': '500g', 'weight_grams': 500, 'price': 450, 'mrp': 450},
                ],
            },
        ]

        for data in products_data:
            variants = data.pop('variants')
            product, created = Product.objects.get_or_create(
                slug=data['slug'],
                defaults=data,
            )
            action = 'Created' if created else 'Already exists'
            self.stdout.write(f"  {action}: {product.name}")

            for v in variants:
                variant, v_created = ProductVariant.objects.get_or_create(
                    product=product,
                    weight=v['weight'],
                    defaults=v,
                )
                if v_created:
                    self.stdout.write(f"    + {variant}")

        self.stdout.write(self.style.SUCCESS('\nDone! Products seeded successfully.'))

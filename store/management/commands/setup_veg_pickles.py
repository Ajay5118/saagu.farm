from django.core.management.base import BaseCommand
from store.models import Product, ProductVariant

PICKLES = [
    {
        'name': 'Mango Pickle',
        'slug': 'mango-pickle',
        'description': 'Raw mango pieces slow-cooked in sesame oil with traditional Andhra spices. Bold, tangy, and irresistibly spicy.',
        'badge': 'PURE VEG',
        'sort_order': 2,
    },
    {
        'name': 'Red Chilli Pickle',
        'slug': 'red-chilli-pickle',
        'description': 'Whole red chillies marinated in mustard oil and spices — a fiery favourite straight from the farm.',
        'badge': 'PURE VEG',
        'sort_order': 3,
    },
    {
        'name': 'Tomato Pickle',
        'slug': 'tomato-pickle',
        'description': 'Sun-ripened tomatoes cooked down with tamarind and spices into a rich, tangy relish.',
        'badge': 'PURE VEG',
        'sort_order': 4,
    },
    {
        'name': 'Amla Pickle',
        'slug': 'amla-pickle',
        'description': 'Fresh Indian gooseberry preserved in a blend of spices and oils. Tart, nourishing, and deeply flavourful.',
        'badge': 'PURE VEG',
        'sort_order': 5,
    },
]

VARIANTS = [
    {'weight': '250g', 'weight_grams': 250, 'price': 200, 'mrp': 200},
    {'weight': '500g', 'weight_grams': 500, 'price': 400, 'mrp': 400},
]


class Command(BaseCommand):
    help = 'Replace generic Veg Pickle with 4 variety-specific veg pickle products'

    def handle(self, *args, **options):
        # Remove the generic veg pickle
        deleted, _ = Product.objects.filter(slug='authentic-veg-pickle').delete()
        if deleted:
            self.stdout.write('  Removed: Authentic Veg Pickle')

        # Push Chicken Pickle sort_order down so it stays last
        Product.objects.filter(category='pickle_nv').update(sort_order=6)

        for data in PICKLES:
            product, created = Product.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'description': data['description'],
                    'category': 'pickle_veg',
                    'badge': data['badge'],
                    'is_available': True,
                    'sort_order': data['sort_order'],
                },
            )
            if not created:
                self.stdout.write(f'  Already exists: {product.name}')
                continue

            for v in VARIANTS:
                ProductVariant.objects.create(product=product, **v)

            self.stdout.write(self.style.SUCCESS(f'  Created: {product.name}'))

        self.stdout.write(self.style.SUCCESS('Done. Assign images via admin or assign_images command.'))

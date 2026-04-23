from django.core.management.base import BaseCommand
from store.models import Product

IMAGE_MAP = {
    'chilli_powder_glass.png': ['spice', 'chilli powder', 'chilli', 'powder'],
    'chicken_pickel.png':      ['pickle_nv', 'chicken', 'non-veg', 'nonveg'],
    'veg_pickel.png':          ['pickle_veg', 'veg pickle', 'vegetable'],
    'c_chillies_2.png':        ['chillies', 'dry chilli', 'red chilli'],
    'c_local_3.png':           ['local', 'guntur', 'byadgi'],
}


class Command(BaseCommand):
    help = 'Assign product images based on product name/category'

    def handle(self, *args, **options):
        products = Product.objects.all()
        if not products.exists():
            self.stderr.write('No products found. Add products via admin first.')
            return

        for product in products:
            if product.image:
                self.stdout.write(f'  Skip {product.name} — already has image')
                continue

            name_lower = product.name.lower()
            category = product.category
            matched = None

            for filename, keywords in IMAGE_MAP.items():
                if category in keywords or any(k in name_lower for k in keywords):
                    matched = filename
                    break

            if matched:
                product.image = f'products/{matched}'
                product.save(update_fields=['image'])
                self.stdout.write(self.style.SUCCESS(f'  {product.name} -> {matched}'))
            else:
                self.stdout.write(self.style.WARNING(f'  {product.name} — no match found'))

"""
Management command to populate the database with realistic sample data
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Brand, Product, Supplier, Competitor, ScrapedData, MarginSetting
from decimal import Decimal
import random
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Populate database with sample cigar data for portfolio demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data for MF Benchmarker...\n')
        
        # Create Brands
        brand_names = [
            'Cohiba',
            'Montecristo', 
            'Romeo y Julieta',
            'Davidoff',
            'Arturo Fuente',
            'Padron',
            'Oliva',
            'Ashton',
        ]
        
        brands = []
        for brand_name in brand_names:
            brand, created = Brand.objects.get_or_create(
                name=brand_name
            )
            brands.append(brand)
            if created:
                self.stdout.write(f'✓ Created brand: {brand.name}')
        
        # Create Suppliers
        suppliers_data = [
            {'code': 'TA', 'name': 'Tobacco Associates'},
            {'code': 'CI', 'name': 'Corona Imports'},
            {'code': 'IR', 'name': 'Iwan Ries & Co.'},
            {'code': 'CH', 'name': 'Cigar Hub'},
            {'code': 'NT', 'name': 'Neptune Tobacco'},
        ]
        
        suppliers = []
        for supplier_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                code=supplier_data['code'],
                defaults=supplier_data
            )
            suppliers.append(supplier)
            if created:
                self.stdout.write(f'✓ Created supplier: {supplier.name}')
        
        # Create Competitors
        competitors_data = [
            {'code': 'TA', 'name': 'Tobacco Associates', 'website_url': 'https://tobaccoassoc.com'},
            {'code': 'CI', 'name': 'Corona Imports', 'website_url': 'https://coronaimports.com'},
            {'code': 'IR', 'name': 'Iwan Ries & Co.', 'website_url': 'https://iwanries.com'},
            {'code': 'CH', 'name': 'Cigar Hub', 'website_url': 'https://cigarhub.com'},
            {'code': 'NT', 'name': 'Neptune Tobacco', 'website_url': 'https://neptunetobacco.com'},
        ]
        
        competitors = []
        for comp_data in competitors_data:
            competitor, created = Competitor.objects.get_or_create(
                code=comp_data['code'],
                defaults=comp_data
            )
            competitors.append(competitor)
            if created:
                self.stdout.write(f'✓ Created competitor: {competitor.name}')
        
        # Create Products
        products_data = [
            # Cohiba products
            {'sku': 'COH-SIG-6', 'name': 'Cohiba Siglo VI (6x52)'},
            {'sku': 'COH-SIG-4', 'name': 'Cohiba Siglo IV (5.5x46)'},
            {'sku': 'COH-ROB', 'name': 'Cohiba Robusto (4.9x50)'},
            
            # Montecristo products
            {'sku': 'MON-NO2', 'name': 'Montecristo No. 2 (6.1x52)'},
            {'sku': 'MON-NO4', 'name': 'Montecristo No. 4 (5.1x42)'},
            {'sku': 'MON-EDM', 'name': 'Montecristo Edmundo (5.3x52)'},
            
            # Romeo y Julieta products
            {'sku': 'RYJ-CHU', 'name': 'Romeo y Julieta Churchill (7x47)'},
            {'sku': 'RYJ-BEL', 'name': 'Romeo y Julieta Belicosos (5.5x52)'},
            
            # Davidoff products
            {'sku': 'DAV-SIG2K', 'name': 'Davidoff Signature 2000 (5x43)'},
            {'sku': 'DAV-MIL', 'name': 'Davidoff Millennium Blend (6x48)'},
            
            # Arturo Fuente products
            {'sku': 'AF-OX858', 'name': 'Arturo Fuente Opus X No. 4 (5.6x48)'},
            {'sku': 'AF-HEM', 'name': 'Arturo Fuente Hemingway (7x48)'},
            
            # Padron products
            {'sku': 'PAD-1964', 'name': 'Padron 1964 Anniversary (6.5x42)'},
            {'sku': 'PAD-2K', 'name': 'Padron 2000 (5x50)'},
            
            # Oliva products
            {'sku': 'OLI-SV', 'name': 'Oliva Serie V (6x60)'},
            {'sku': 'OLI-SG', 'name': 'Oliva Serie G (5x50)'},
            
            # Ashton products
            {'sku': 'ASH-CAB', 'name': 'Ashton Cabinet Selection (6x52)'},
            {'sku': 'ASH-VSG', 'name': 'Ashton Virgin Sun Grown (5.5x50)'},
        ]
        
        products = []
        for i, product_data in enumerate(products_data):
            brand = brands[i % len(brands)]  # Distribute products across brands
            supplier = suppliers[i % len(suppliers)]  # Distribute across suppliers
            
            # Calculate realistic cost prices
            base_cost = Decimal(str(random.uniform(8.50, 45.00)))
            
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults={
                    'name': product_data['name'],
                    'brand': brand,
                    'supplier': supplier,
                    'cost_with_tax': base_cost,
                    'stock_status': random.choice(['instock', 'outofstock', 'neversold']),
                }
            )
            products.append(product)
            if created:
                self.stdout.write(f'✓ Created product: {product.name} (${product.cost_with_tax:.2f})')
        
        # Create realistic scraped data for competitors
        self.stdout.write('\nGenerating competitor price data...')
        for product in products[:10]:  # Create data for first 10 products
            for competitor in competitors:
                # Create realistic competitor prices (some higher, some lower)
                price_variation = random.uniform(0.85, 1.25)
                competitor_price = product.cost_with_tax * Decimal(str(price_variation))
                
                ScrapedData.objects.get_or_create(
                    product=product,
                    competitor=competitor,
                    extraction_date=timezone.now().date(),
                    defaults={
                        'product_name': product.name,
                        'product_type': product.name.split()[-1] if product.name.split() else 'Cigar',
                        'price': competitor_price,
                    }
                )
        
        # Create margin settings (if superuser exists)
        from django.contrib.auth.models import User
        try:
            admin_user = User.objects.get(username='admin')
            
            MarginSetting.objects.get_or_create(
                user=admin_user,
                margin_percentage=40,
                defaults={
                    'is_active': True,
                }
            )
        except User.DoesNotExist:
            self.stdout.write('⚠️ Skipping margin settings (no admin user found)')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created sample data:'))
        self.stdout.write(f'   • {Brand.objects.count()} brands')
        self.stdout.write(f'   • {Supplier.objects.count()} suppliers') 
        self.stdout.write(f'   • {Competitor.objects.count()} competitors')
        self.stdout.write(f'   • {Product.objects.count()} products')
        self.stdout.write(f'   • {ScrapedData.objects.count()} price comparisons')
        self.stdout.write(f'   • {MarginSetting.objects.count()} margin settings')
        
        self.stdout.write(self.style.SUCCESS('\n🎯 Your portfolio demo data is ready!'))
        self.stdout.write('Visit http://127.0.0.1:8001/ to see the dashboard')
        self.stdout.write('Visit http://127.0.0.1:8001/admin/ to manage data')
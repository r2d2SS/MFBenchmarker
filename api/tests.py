import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date

from .models import Brand, Supplier, Product, Competitor, ScrapedData, MarginSetting


class ModelTests(TestCase):
    """Test cases for model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.brand = Brand.objects.create(name='Test Brand')
        self.supplier = Supplier.objects.create(code='TS', name='Test Supplier')
        self.competitor = Competitor.objects.create(
            code='TC', 
            name='Test Competitor',
            website_url='https://test.com'
        )
    
    def test_brand_creation(self):
        """Test brand model creation"""
        self.assertEqual(str(self.brand), 'Test Brand')
        self.assertTrue(isinstance(self.brand.name, str))
    
    def test_product_creation(self):
        """Test product model creation"""
        product = Product.objects.create(
            sku='TEST-001',
            name='Test Product',
            brand=self.brand,
            supplier=self.supplier,
            cost_with_tax=Decimal('10.50'),
            stock_status='instock'
        )
        
        self.assertEqual(str(product), 'TEST-001 - Test Product')
        self.assertEqual(product.brand, self.brand)
        self.assertEqual(product.stock_status, 'instock')
    
    def test_margin_setting_functionality(self):
        """Test margin setting model"""
        margin1 = MarginSetting.objects.create(
            user=self.user,
            margin_percentage=40,
            is_active=True
        )
        
        # Create another margin - should deactivate the first one
        margin2 = MarginSetting.objects.create(
            user=self.user,
            margin_percentage=35,
            is_active=True
        )
        
        # Refresh from database
        margin1.refresh_from_db()
        
        self.assertFalse(margin1.is_active)
        self.assertTrue(margin2.is_active)
        self.assertEqual(MarginSetting.get_current_margin(), 35)


class APITests(APITestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='apipass')
        self.brand = Brand.objects.create(name='API Brand')
        self.supplier = Supplier.objects.create(code='AS', name='API Supplier')
        
        self.product = Product.objects.create(
            sku='API-001',
            name='API Product',
            brand=self.brand,
            supplier=self.supplier,
            cost_with_tax=Decimal('15.00'),
            stock_status='instock'
        )
    
    def test_product_list_api(self):
        """Test product list API endpoint"""
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


# Pytest fixtures for more advanced testing
@pytest.fixture
def api_client():
    """Fixture for API client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    """Fixture for authenticated user"""
    user = User.objects.create_user(username='pytest_user', password='pytest_pass')
    return user

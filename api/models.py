from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class Brand(models.Model):
    """Cigar brand model"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Supplier(models.Model):
    """Supplier/Provider model"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Product(models.Model):
    """Product Master model"""
    sku = models.CharField(max_length=50, unique=True)
    simple_sku = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    cost_with_tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_status = models.CharField(max_length=20, default='instock')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.sku} - {self.name}"
    
    class Meta:
        ordering = ['brand__name', 'name']


class Competitor(models.Model):
    """Competitor websites model"""
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    website_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ScrapedData(models.Model):
    """Scraped price data from competitors"""
    extraction_date = models.DateField(default=date.today)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    product_type = models.CharField(max_length=100, blank=True)
    competitor = models.ForeignKey(Competitor, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.product_name} - {self.competitor.code} - ${self.price}"
    
    class Meta:
        ordering = ['-extraction_date', 'product_name']


class MarginSetting(models.Model):
    """Margin settings history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    margin_percentage = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Margin: {self.margin_percentage}% - {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Deactivate other margin settings when creating a new one
        if self.is_active:
            MarginSetting.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_current_margin(cls):
        """Get the current active margin"""
        current = cls.objects.filter(is_active=True).first()
        return current.margin_percentage if current else 40  # Default to 40%
    
    class Meta:
        ordering = ['-created_at']


class ExchangeRate(models.Model):
    """Exchange rate tracking"""
    from_currency = models.CharField(max_length=3, default='EUR')
    to_currency = models.CharField(max_length=3, default='USD')
    rate = models.DecimalField(max_digits=10, decimal_places=6)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.from_currency}/{self.to_currency}: {self.rate} ({self.date})"
    
    @classmethod
    def get_current_rate(cls, from_curr='EUR', to_curr='USD'):
        """Get the most recent exchange rate"""
        rate = cls.objects.filter(
            from_currency=from_curr, 
            to_currency=to_curr
        ).order_by('-date').first()
        return float(rate.rate) if rate else 1.0533  # Fallback rate
    
    class Meta:
        ordering = ['-date']
        unique_together = ['from_currency', 'to_currency', 'date']

from django.db import models
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone


class Customer(models.Model):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone=models.CharField(max_length=20,unique=True)
    email=models.EmailField(unique=True,blank=True,null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    category=models.ForeignKey(Category,on_delete=models.PROTECT,related_name="products")
    name=models.CharField(max_length=150)
    description=models.TextField(blank=True,null=True)
    price=models.DecimalField(max_digits=12,decimal_places=2)
    stock_quantity=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.category} {self.price}"
class Sale(models.Model):
    STATUS_CHOICES=(
        ('PENDING','Pending'),
        ('COMPLETE','Complete'),
        ('PARTIAL','Partial paid'),
        ('CANCELLED','Cancelled'),
    )
    customer=models.ForeignKey(Customer,on_delete=models.PROTECT,related_name="sales",null=True,blank=True)
    sale_date=models.DateTimeField(default=timezone.now)
    total_amount=models.DecimalField(max_digits=12,decimal_places=2,default=0)
    status=models.CharField(choices=STATUS_CHOICES,max_length=20,default="PENDING")
    def update_total(self):
                   total=sum((item.subtotal for item in self.items.all()),Decimal("0.00"))
                   self.total_amount=total
                   self.save(update_fields=["total_amount"])
                   self.update_payment_status()

    def __str__(self):
        return f"Sale #{self.id}"

    @property
    def amount_paid(self):
         return self.payments.aggregate(total=Sum('amount'))['total'] or Decimal("0.00")
    @property
    def balance(self):
         return max(self.total_amount-self.amount_paid,Decimal('0.00'))

    @property
    def change(self):
         return max(self.amount_paid-self.total_amount,Decimal("0.00"))
    @property
    def payment_status(self):
         paid=self.amount_paid

         if paid==0:
              return "PENDING"
         elif self.balance>0:
              return "PARTIAL"
         else:
              return "PAID"
    def update_payment_status(self):
         if self.status=="CANCELLED":
              return
         if self.amount_paid==0:
              self.status="PENDING"
         elif self.balance>0:
              self.status="PARTIAL"
         else:
              self.status="COMPLETE"
         self.save(update_fields=["status"])

    
class SaleItem(models.Model):
    sale=models.ForeignKey(Sale,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.PROTECT)
    quantity=models.PositiveIntegerField()
    unit_price=models.DecimalField(max_digits=10,decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def save(self,*args,**kwargs):
         if not self.pk:
          self.unit_price=self.product.price

         super().save(*args,**kwargs)

    def __str__(self):
        return  f"{self.product} {self.quantity}"

class Payment(models.Model):
    METHOD_CHOICES=(
        ('CASH','Cash'),
        ('MPESA','Mpesa'),
        ('BANK','Bank Transfer'),
    )
    sale=models.ForeignKey(Sale,on_delete=models.PROTECT,related_name="payments")
    amount=models.DecimalField(max_digits=12,decimal_places=2)
    payment_method=models.CharField(choices=METHOD_CHOICES,max_length=30)
    payment_date=models.DateTimeField(auto_now_add=True)
    reference=models.CharField(max_length=100,blank=True,unique=True,null=True)


    def __str__(self):
        return f" Payment #{self.id}"


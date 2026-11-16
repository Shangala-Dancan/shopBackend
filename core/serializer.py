from rest_framework import serializers
from decimal import Decimal

from .models import Category,Customer,Payment,Product,Sale,SaleItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"
class CustomerSerialaizer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields="__all__"

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields="__all__"
        read_only_fields=["payment_date","amount"]

class ProductSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source="category.name", read_only=True)
    class Meta:
        model=Product
        fields="__all__"


class SaleItemSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(source="product.name",read_only=True)
    class Meta:
        model=SaleItem
        fields=[
            "id",
            "sale",
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields=["unit_price"]
    def get_subtotal(self,obj):
        return obj.quantity*obj.unit_price
class SaleSeriralizer(serializers.ModelSerializer):
    customer_name=serializers.CharField(source="customer.name",read_only=True)
    items=SaleItemSerializer(many=True,read_only=True)
    payments=PaymentSerializer(many=True,read_only=True)
    amount_paid=serializers.SerializerMethodField()
    balance=serializers.SerializerMethodField()
    change=serializers.SerializerMethodField()
    class Meta:
        model=Sale
        fields="__all__"

    def get_amount_paid(self,obj):
        return sum((p.amount for p in obj.payments.all()),Decimal("0.00"))

    def get_balance(self,obj):
        return max(obj.total_amount -self.get_amount_paid(obj),Decimal("0.00"))
    def get_change(self,obj):
        return max(self.get_amount_paid(obj)-obj.total_amount,Decimal("0.00"))
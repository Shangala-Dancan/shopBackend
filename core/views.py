from django.shortcuts import render
from rest_framework import viewsets
from django.db.models import ProtectedError
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from .models import Category,Product,Sale,SaleItem,Payment,Customer
from rest_framework.response import Response
from rest_framework.decorators import permission_classes,api_view
from decimal import Decimal
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, F
from rest_framework.permissions import AllowAny
from .serializer import CustomerSerialaizer,CategorySerializer,PaymentSerializer,ProductSerializer,SaleSeriralizer,SaleItemSerializer


# Create your views here.
@api_view(["POST"])
def addCategory(request):
    serializer=CategorySerializer(data=request.data)
    if serializer.is_valid():
          serializer.save()

          return Response({"message":"category created","data":serializer.data},status=201)
    return Response({"error":"failed to add category","details":serializer.errors})
    

@api_view(["GET"])
def getCategory(request):

        categories=Category.objects.all()

        serializer=CategorySerializer(categories,many=True)

        return Response(serializer.data)
@api_view(["PATCH"])
def updateCategory(request,id):
      try:
          categories=Category.objects.get(id=id)
          serializer=CategorySerializer(categories,data=request.data,partial=True)

          if serializer.is_valid():
               serializer.save()
               return Response({"message":"Updated"})
      except Category.DoesNotExist:
       return ({"error":"Category not found"})
@api_view(["DELETE"])
def deleteCategory(request,id):
      try:
        category=Category.objects.get(id=id)
        category.delete()
        return Response({"message":"category deleted successfully"})
        
      except Category.DoesNotExist:
           return Response({"error":"Category doesnt exists"})
@api_view(["POST"])
def addCustomer(request):

     serializer=CustomerSerialaizer(data=request.data)
     if serializer.is_valid():
          serializer.save()
          return Response({"message":"Customer added"})
     return Response({"error":"failed","details":serializer.errors},status=201)
@api_view(["GET"])
def getCustomers(request):

     customers=Customer.objects.all()
     serializer=CustomerSerialaizer(customers,many=True)

     return Response(serializer.data)
@api_view(["PATCH"])
def updateCustomer(request,id):

     try:
        customer=Customer.objects.get(id=id)

        serializer=CustomerSerialaizer(customer,data=request.data,partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message":"customer updated"},status=200)
        return Response(serializer.errors,status=400)
     except Customer.DoesNotExist:
          return Response({"error":"Customer not found"},status=404)
@api_view(["DELETE"])
def deleteCustomer(request,id):
     try:
          customer=Customer.objects.get(id=id)
          customer.delete()
          return Response({"message":"Customer deleted"})
     except Customer.DoesNotExist:
          return Response({"error":"Customer not found"},status=404)
@api_view(["POST"])
def addProduct(request):

     
     serializer=ProductSerializer(data=request.data)
     if serializer.is_valid():
          serializer.save()
          return Response({"message":"Product added succefully"})
     return Response({"error":"Failed to add product","details":serializer.errors},status=400)
@api_view(["Get"])
def getProducts(request):

     product=Product.objects.all()
     serializer=ProductSerializer(product,many=True)

     return Response(serializer.data)
@api_view(["PATCH"])
def updateProduct(request,id):
     try:
          product=Product.objects.get(id=id)
          serializer=ProductSerializer(product,data=request.data,partial=True)
          if serializer.is_valid():
               serializer.save()
               return Response({"message":"Product updated successfully"},status=200)
          return Response({"error":"Failed to update the product","details":serializer.errors},status=400)
     except Product.DoesNotExist:
          return Response({"error":"Product doeds not exists"},status=404)
     

@api_view(["DELETE"])
def deleteProduct(request,id):
     try:
          product=Product.objects.get(id=id)

          product.delete()

          return Response({"message":"Product deleted successfully"},status=200)
     except Product.DoesNotExist:
          return Response({"error":"Product not found"},status=404)
     except ProtectedError:
          return Response({"error":"This product is associted to a sale it can not be deleted"},status=400)
@api_view(["POST"])
def addSale(request):

     serializer=SaleSeriralizer(data=request.data)
     if serializer.is_valid():
          sale=serializer.save()
          return Response({"message":"Sale added successfully","sale":SaleSeriralizer(sale).data},status=201)
     
     return Response({"error":"Failed to add a sale","details":serializer.errors},status=400)

@api_view(["POST"])
def addSaleItem(request):

     serializer=SaleItemSerializer(data=request.data)

     if serializer.is_valid():
          item=serializer.save()
          item.sale.update_total()
          return Response({"message":"Sale items saved"},status=201)
     
     return Response({"error":"Failed to saved the items","details":serializer.errors},status=400)

@api_view(["POST"])
def addSaleItems(request,id):
     try:
          with transaction.atomic():

               sale=Sale.objects.select_for_update().get(id=id)
               if sale.status=="CANCELLED":
                    return Response({"error":"Cannot add an item to a canceled sale"},status=400)
               items=request.data.get("items",[])

               if not isinstance(items,list) or not items:
                    return Response({"error":"please select products"},status=400)
               quantities={}

               for item in items:

                    product_id=item.get("product")
                    quantity=item.get("quantity")

                    if (isinstance(quantity,bool) 
                        or not isinstance(quantity,int)
                        or quantity<1
                        or not product_id):
                         return Response({"error":"Invalid product or quantity"})
                    quantities[product_id]=(quantities.get(product_id,0)+quantity)

               products=Product.objects.select_for_update().filter(id__in=quantities.keys()).order_by("id")

               products=list(products)

               if len(products)!=len(quantities):
                    return Response({"error":"Product not found"},status=404)
               for product in products:
                    quantity=quantities[product.id]

                    if product.stock_quantity<quantity:
                         return Response({"error":f"Insuffient stock for {product.name}"},status=400)
                    sale_item,created=SaleItem.objects.get_or_create(sale=sale,product=product,defaults={"quantity":quantity,"unit_price":product.price})


                    if not created:
                         sale_item.quantity+=quantity
                         sale_item.save(update_fields=["quantity"])

                    product.stock_quantity-=quantity
                    product.save(update_fields=["stock_quantity"])
               sale.update_total()

          serializer=SaleSeriralizer(sale)

          return Response({"message":"Products added successfully","sale":serializer.data},status=200)
     except Sale.DoesNotExist:
          return Response({"error":"SAle not found"},status=404)

@api_view(["GET"])
def getSale(request,id=None):

     if id is not None:
          sale=get_object_or_404(Sale.objects.prefetch_related("items__product","payments"),id=id)

          serializer=SaleSeriralizer(sale)
          return Response ({"sale":serializer.data},status=200)


     sale=Sale.objects.prefetch_related("items__product","payments").all()
     serializer=SaleSeriralizer(sale,many=True)
     grand_total=sale.aggregate(grand_total=Sum("total_amount"))["grand_total"] or Decimal("0.00")

     return Response({"sales":serializer.data,"grand_total":grand_total},status=200)

@api_view(["POST"])
def addPayment(request,id):
     amount=request.data.get("amount_paid")
     payment_method=request.data.get("payment_method")

     

     try:
          amount=Decimal(str(amount))

          if not amount.is_finite() or amount<=0:
               return Response({"error":"Enter a valid payment amount"},status=status.HTTP_400_BAD_REQUEST)
          allowed_methods=["CASH","MPESA","CARD"]

          if payment_method not in allowed_methods:
               return Response({"error":"Method not allowed"},status=status.HTTP_400_BAD_REQUEST)

          with transaction.atomic():
               sale=get_object_or_404(Sale.objects.select_for_update(),id=id)

               if sale.status=="CANCELLED":
                    return Response({"error":"Can not pay a cancelled sale"},status=status.HTTP_400_BAD_REQUEST)
               if amount>sale.balance:
                    return Response({"error":"Payment exceeds the oustanding balance"},status=400)
               payment=Payment.objects.create(sale=sale,amount=amount,payment_method=payment_method)
               sale.refresh_from_db()

               sale.update_payment_status()
               return Response({
               "message":"Payment successfully",
               "payment":PaymentSerializer(payment).data,
               "amount_paid":str(sale.amount_paid),
               "balance":str(sale.balance),
               "payment_status":sale.payment_status
          },status=status.HTTP_201_CREATED)
     except (ValueError,TypeError):
          return Response({"error":"Invalid payment amount"},status=status.HTTP_400_BAD_REQUEST)
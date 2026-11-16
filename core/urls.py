from django.urls import path
from .views import addCategory,getCategory,updateCategory,deleteCategory,addCustomer,getCustomers,updateCustomer,addProduct,getProducts,updateProduct,deleteProduct,deleteCustomer,addSale,addSaleItem,getSale,addPayment,addSaleItems
from core import views

urlpatterns=[
    path("category/",addCategory),
    path("get/",getCategory),
    path("up/<int:id>/",updateCategory),
    path("delete/<int:id>/",deleteCategory),
    path("customer/",addCustomer),
    path("getcustomers/",getCustomers),
    path("updatecustomer/<int:id>/",updateCustomer),
    path("deleteCustomer/<int:id>/",deleteCustomer),
    path("addproduct/",addProduct),
    path("getproducts/",getProducts),
    path("updateproduct/<int:id>/",updateProduct),
    path("deleteproduct/<int:id>/",deleteProduct),
    path("addSale/",addSale),
    path("addItem/",addSaleItem),
    path("getSale/",getSale),
    path("getSale/<int:id>/",getSale),
    path("addpayment/<int:id>/",addPayment),
    path("addSaleItems/<int:id>/",addSaleItems)
]
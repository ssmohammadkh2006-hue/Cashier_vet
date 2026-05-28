from django.urls import path
from . import views

app_name = 'cashier'

urlpatterns = [
    
    path('boarding/', views.boarding, name='boarding'),
    path('boarding/<int:pk>/checkout/', views.boarding_checkout, name='boarding_checkout'),
    path('boarding/<int:pk>/delete/', views.delete_boarding, name='delete_boarding'),
    
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('pos/', views.pos, name='pos'),
    path('products/', views.products, name='products'),
    path('reports/', views.reports, name='reports'),
    path('products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('api/products/', views.products_api, name='products_api'),
    path('api/sales/complete/', views.complete_sale_api, name='complete_sale_api'),
]

from django.urls import path
from . import views

app_name = 'cashier'

urlpatterns = [
    
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_create, name='staff_create'),
    path('staff/<int:pk>/password/', views.staff_change_password, name='staff_change_password'),
    
    path('settings/', views.clinic_settings, name='clinic_settings'),
    
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

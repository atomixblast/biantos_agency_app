from django.urls import path

from . import views
from . import views_entities

app_name = 'order'

urlpatterns = [
    # Commandes
    path('list_orders/', views.list_orders, name='list_orders'),
    path('create_order/', views.create_order, name='create_order'),
    path('update_order/<int:order_id>/', views.update_order, name='update_order'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('change_status/<int:order_id>/', views.change_order_status, name='change_order_status'),
    path('add_payment/<int:order_id>/', views.add_payment, name='add_payment'),
    path('delete_payment/<int:payment_id>/', views.delete_payment, name='delete_payment'),
    path('report/', views.report_orders, name='report_orders'),
    path('report/export/', views.export_report_excel, name='export_report_excel'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('calendar/', views.calendar_orders, name='calendar_orders'),
    
    # Articles
    path('articles/', views_entities.list_articles, name='list_articles'),
    path('articles/create/', views_entities.create_article, name='create_article'),
    path('articles/<int:article_id>/', views_entities.detail_article, name='detail_article'),
    path('articles/<int:article_id>/update/', views_entities.update_article, name='update_article'),
    path('articles/<int:article_id>/delete/', views_entities.delete_article, name='delete_article'),
    
    # Clients
    path('customers/', views_entities.list_customers, name='list_customers'),
    path('customers/create/', views_entities.create_customer, name='create_customer'),
    path('customers/<int:customer_id>/', views_entities.detail_customer, name='detail_customer'),
    path('customers/<int:customer_id>/update/', views_entities.update_customer, name='update_customer'),
    path('customers/<int:customer_id>/delete/', views_entities.delete_customer, name='delete_customer'),
    
    # Apporteurs d'affaires
    path('sales-executives/', views_entities.list_sales_executives, name='list_sales_executives'),
    path('sales-executives/create/', views_entities.create_sales_executive, name='create_sales_executive'),
    path('sales-executives/<int:sales_executive_id>/', views_entities.detail_sales_executive, name='detail_sales_executive'),
    path('sales-executives/<int:sales_executive_id>/update/', views_entities.update_sales_executive, name='update_sales_executive'),
    path('sales-executives/<int:sales_executive_id>/delete/', views_entities.delete_sales_executive, name='delete_sales_executive'),
]
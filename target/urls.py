from django.urls import path

from target import views



app_name = 'target'


urlpatterns = [
    path('', views.list_targets, name='list_targets'),
    path('add/', views.create_target, name='create_target'),
    path('update/<int:target_id>/', views.update_target, name='update_target'),
]
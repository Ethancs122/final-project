from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('form/', views.form, name='form'),
    path('table/', views.table, name='table'),
    path('table/<str:identifier>', views.map, name='map')
]
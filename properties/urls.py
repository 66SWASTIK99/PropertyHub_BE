from django.urls import path
from .import views

urlpatterns = [
    path('addproperties/', views.add_property_api, name='addpropertiesapi'),
    path('addreview/', views.add_review_api, name='add_review'),
    path('searchproperties/', views.search_properties_api, name='search_properties'),
    path('getproperties', views.get_properties, name='get_properties'),
]
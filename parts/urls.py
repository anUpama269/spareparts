from django.urls import path
from . import views
app_name = 'parts'
urlpatterns = [
    # ---------- Parts ----------
    path('parts/', views.PartListView.as_view(), name='part_list'),
    path('parts/add/', views.PartCreateView.as_view(), name='part_add'),
    path('parts/edit/<int:pk>/', views.PartUpdateView.as_view(), name='part_edit'),
    path('parts/delete/<int:pk>/', views.PartDeleteView.as_view(), name='part_delete'),

    # ---------- Categories ----------
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('categories/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # ---------- Brands ----------
    path('brands/', views.BrandListView.as_view(), name='brand_list'),
    path('brands/add/', views.BrandCreateView.as_view(), name='brand_add'),
    path('brands/edit/<int:pk>/', views.BrandUpdateView.as_view(), name='brand_edit'),
    path('brands/delete/<int:pk>/', views.BrandDeleteView.as_view(), name='brand_delete'),
]

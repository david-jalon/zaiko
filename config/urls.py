"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from inventory import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("accounts.urls")), # Esto hace que todas las rutas de accounts/urls.py cuelguen de /accounts/
    path("", views.dashboard, name="dashboard"),
    # Rutas de spools
    path("spools/", views.SpoolListView.as_view(), name="spool_list"),
    path("spools/nueva/", views.SpoolCreateView.as_view(), name="spool_create"),
    path("spools/<int:pk>/editar/", views.SpoolUpdateView.as_view(), name="spool_update"),
    path("spools/<int:pk>/borrar/", views.SpoolDeleteView.as_view(), name="spool_delete"),
    # Rutas de materials
    path("materiales/", views.MaterialListView.as_view(), name="material_list"),
    path("materiales/nuevo/", views.MaterialCreateView.as_view(), name="material_create"),
    path("materiales/<int:pk>/editar/", views.MaterialUpdateView.as_view(), name="material_update"),
    path("materiales/<int:pk>/borrar/", views.MaterialDeleteView.as_view(), name="material_delete"),
    # Rutas de color
    path("color/", views.ColorListView.as_view(), name="color_list"),
    path("color/nuevo/", views.ColorCreateView.as_view(), name="color_create"),
    path("color/<int:pk>/editar/", views.ColorUpdateView.as_view(), name="color_update"),
    path("color/<int:pk>/borrar/", views.ColorDeleteView.as_view(), name="color_delete"),
    # Rutas de stockthreshold
    path("stock/", views.StockThresholdListView.as_view(), name="stock_list"),
    path("stock/nuevo/", views.StockThresholdCreateView.as_view(), name="stock_create"),
    path("stock/<int:pk>/editar/", views.StockThresholdUpdateView.as_view(), name="stock_update"),
    path("stock/<int:pk>/borrar/", views.StockThresholdDeleteView.as_view(), name="stock_delete"),
    # Rutas de ordenes de impresión
    path("ordenes/", views.PrintOrderListView.as_view(), name="printorder_list"),
    path("ordenes/nueva/", views.PrintOrderCreateView.as_view(), name="printorder_create"),
    # Rutas de exportación
    path("exportar/inventario/", views.export_inventory_csv, name="exportar_inventario"),
    path("exportar/ordenes/", views.export_printorders_csv, name="exportar_ordenes"),
]

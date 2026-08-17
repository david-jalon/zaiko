from django.contrib import admin
from .models import Material, Color, StockThreshold, Spool

# Register your models here.
@admin.register(Material) # Decorador que registra el modelo en el admin
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("tipo", "subtipo") # Columnas
    list_filter = ["tipo", "subtipo"] # Filtros
    search_fields = ("tipo", "subtipo") # Caja de búsqueda

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(StockThreshold)
class StockThresholdAdmin(admin.ModelAdmin):
    list_display = ("material", "color", "stock_minimo")
    search_fields = ("material__subtipo", "color__nombre")

@admin.register(Spool)
class SpoolAdmin(admin.ModelAdmin):
    list_display = ("material", "color", "marca", "diametro", "costo_por_kg", "peso_inicial", "peso_actual", "estado", "fecha_compra")
    list_filter = ["estado", "color"]
    search_fields = ("material__subtipo", "color__nombre", "marca")
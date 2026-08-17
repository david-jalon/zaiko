from django.contrib import admin
from .models import Material

# Register your models here.
@admin.register(Material) # Decorador que registra el modelo en el admin
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca", "tipo", "color", "diametro", "costo_por_kg", "stock_minimo") # Columnas
    list_filter = ["tipo"] # Filtros
    search_fields = ("nombre", "marca") # Caja de búsqueda
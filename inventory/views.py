from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import OperatorRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Spool, Material, Color, StockThreshold


# Create your views here.
@login_required
def home(request):
    return render(request, "inventory/home.html")

# Vista para listar las bobinas
class SpoolListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    model = Spool
    template_name = "inventory/spool_list.html"
    context_object_name = "spools"
    queryset = Spool.objects.select_related("material", "color")

class SpoolCreateView(LoginRequiredMixin, OperatorRequiredMixin, CreateView):
    model = Spool
    template_name = "inventory/spool_form.html"
    fields = ["material", "color", "marca", "diametro", "costo_por_kg", "peso_inicial", "peso_actual", "estado", "fecha_compra"]
    success_url = reverse_lazy("spool_list")

class SpoolUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = Spool
    template_name = "inventory/spool_form.html"
    fields = ["material", "color", "marca", "diametro", "costo_por_kg", "peso_inicial", "peso_actual", "estado", "fecha_compra"]
    success_url = reverse_lazy("spool_list")

class SpoolDeleteView(LoginRequiredMixin, OperatorRequiredMixin, DeleteView):
    model = Spool
    template_name = "inventory/spool_confirm_delete.html"
    success_url = reverse_lazy("spool_list")


# Vista para listar los materiales
class MaterialListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    model = Material
    template_name = "inventory/material_list.html"
    context_object_name = "materials"
    queryset = Material.objects.all()

class MaterialCreateView(LoginRequiredMixin, OperatorRequiredMixin, CreateView):
    model = Material
    template_name = "inventory/material_form.html"
    fields = ["tipo", "subtipo"]
    success_url = reverse_lazy("material_list")

class MaterialUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = Material
    template_name = "inventory/material_form.html"
    fields = ["tipo", "subtipo"]
    success_url = reverse_lazy("material_list")

class MaterialDeleteView(LoginRequiredMixin, OperatorRequiredMixin, DeleteView):
    model = Material
    template_name = "inventory/material_confirm_delete.html"
    success_url = reverse_lazy("material_list")


# Vista para listar los colores
class ColorListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    model = Color
    template_name = "inventory/color_list.html"
    context_object_name = "colors"
    queryset = Color.objects.all()

class ColorCreateView(LoginRequiredMixin, OperatorRequiredMixin, CreateView):
    model = Color
    template_name = "inventory/color_form.html"
    fields = ["nombre"]
    success_url = reverse_lazy("color_list")

class ColorUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = Color
    template_name = "inventory/color_form.html"
    fields = ["nombre"]
    success_url = reverse_lazy("color_list")

class ColorDeleteView(LoginRequiredMixin, OperatorRequiredMixin, DeleteView):
    model = Color
    template_name = "inventory/color_confirm_delete.html"
    success_url = reverse_lazy("color_list")


# Vista para listar el stock
class StockThresholdListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    model = StockThreshold
    template_name = "inventory/stock_list.html"
    context_object_name = "stocks"
    queryset = StockThreshold.objects.select_related("material", "color")

class StockThresholdCreateView(LoginRequiredMixin, OperatorRequiredMixin, CreateView):
    model = StockThreshold
    template_name = "inventory/stock_form.html"
    fields = ["material", "color", "stock_minimo"]
    success_url = reverse_lazy("stock_list")

class StockThresholdUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = StockThreshold
    template_name = "inventory/stock_form.html"
    fields = ["material", "color", "stock_minimo"]
    success_url = reverse_lazy("stock_list")

class StockThresholdDeleteView(LoginRequiredMixin, OperatorRequiredMixin, DeleteView):
    model = StockThreshold
    template_name = "inventory/stock_confirm_delete.html"
    success_url = reverse_lazy("stock_list")
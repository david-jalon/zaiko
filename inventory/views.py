from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import OperatorRequiredMixin
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from .models import PrintOrder, Printer, Spool, Material, Color, StockThreshold
from .forms import PrintOrderForm
import csv
from django.http import HttpResponse


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


# Vista para crear una orden de impresión
class PrintOrderListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    model = PrintOrder
    template_name = "inventory/printorder_list.html"
    context_object_name = "printorders"
    queryset = PrintOrder.objects.select_related("printer", "spool").order_by("-fecha_inicio")

class PrintOrderCreateView(LoginRequiredMixin, OperatorRequiredMixin, CreateView):
    model = PrintOrder
    form_class = PrintOrderForm
    template_name = "inventory/printorder_form.html"
    success_url = reverse_lazy("printorder_list")


# Vista del dashboard
@login_required
def dashboard(request):
    # KPIs
    total_bobinas = Spool.objects.count()
    bobinas_abiertas = Spool.objects.filter(estado="Abierta").count()
    gramos_totales = Spool.objects.aggregate(total_gramos=Sum("peso_actual"))["total_gramos"] or 0
    piezas_impresas = PrintOrder.objects.count()
    horas_totales = PrintOrder.objects.aggregate(total=Sum("duracion_minutos"))["total"] or 0

    # Stock por material+color con alerta
    stock_por_combinacion = (
        Spool.objects.values("material", "color").annotate(total=Sum("peso_actual"))
    )

    alertas = []
    for item in stock_por_combinacion:
        umbral = StockThreshold.objects.filter(material_id=item["material"], color_id=item["color"]).first()
        if umbral and item["total"] < umbral.stock_minimo:
            alertas.append({
                "material": Material.objects.get(id=item["material"]),
                "color": Color.objects.get(id=item["color"]),
                "stock_actual": item["total"],
                "stock_minimo": umbral.stock_minimo,
            })

    # Últimas órdenes
    ultimas_ordenes = PrintOrder.objects.select_related("printer", "spool")[:5]

    context = {
        "total_bobinas": total_bobinas,
        "bobinas_abiertas": bobinas_abiertas,
        "gramos_totales": gramos_totales,
        "piezas_impresas": piezas_impresas,
        "horas_totales": round(horas_totales / 60, 1),  # Convertir minutos a horas y redondear a 1 decimal
        "alertas": alertas,
        "ultimas_ordenes": ultimas_ordenes,
    }

    return render(request, "inventory/dashboard.html", context)


# Vista para exportar el inventario a CSV
@login_required
def export_inventory_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="inventario.csv"'

    writer = csv.writer(response)
    writer.writerow(["Material", "Color", "Marca", "Peso actual (g)", "Estado"])
    for spool in Spool.objects.select_related("material", "color"):
        writer.writerow([
            spool.material, spool.color, spool.marca, spool.peso_actual, spool.estado
        ])
    return response

@login_required
def export_printorders_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="ordenes_impresion.csv"'

    writer = csv.writer(response)
    writer.writerow(["Pieza", "Impresora", "Bobina", "Gramos usados", "Duración (min)", "Fecha inicio", "Fecha fin"])
    for order in PrintOrder.objects.select_related("printer", "spool"):
        writer.writerow([
            order.pieza, order.printer, order.spool, order.gramos_usados, order.duracion_minutos, order.fecha_inicio, order.fecha_fin
        ])
    return response


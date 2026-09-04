from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.mixins import OperatorRequiredMixin
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from .models import PrintOrder, Printer, Spool, Material, Color, StockThreshold
from .forms import PrintOrderForm, PrintOrderItemFormSet, SpoolForm, MaterialForm, ColorForm, StockThresholdForm, PrintOrderDeleteForm, CalculadoraForm, OtrosGastosFormSet
from django.http import HttpResponse
import csv
import re
from datetime import date


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
    form_class = SpoolForm
    success_url = reverse_lazy("spool_list")

class SpoolUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = Spool
    template_name = "inventory/spool_form.html"
    form_class = SpoolForm
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
    form_class = MaterialForm
    success_url = reverse_lazy("material_list")

class MaterialUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = Material
    template_name = "inventory/material_form.html"
    form_class = MaterialForm
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
    form_class = ColorForm
    success_url = reverse_lazy("color_list")

class ColorUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = Color
    template_name = "inventory/color_form.html"
    form_class = ColorForm
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
    form_class = StockThresholdForm
    success_url = reverse_lazy("stock_list")

class StockThresholdUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = StockThreshold
    template_name = "inventory/stock_form.html"
    form_class = StockThresholdForm
    success_url = reverse_lazy("stock_list")

class StockThresholdDeleteView(LoginRequiredMixin, OperatorRequiredMixin, DeleteView):
    model = StockThreshold
    template_name = "inventory/stock_confirm_delete.html"
    success_url = reverse_lazy("stock_list")


# Vista para listar las órdenes de impresión
class PrintOrderListView(LoginRequiredMixin, OperatorRequiredMixin, ListView):
    model = PrintOrder
    template_name = "inventory/printorder_list.html"
    context_object_name = "printorders"
    queryset = PrintOrder.objects.prefetch_related("items__spool").order_by("-fecha_inicio")

class PrintOrderCreateView(LoginRequiredMixin, OperatorRequiredMixin, CreateView):
    model = PrintOrder
    form_class = PrintOrderForm
    template_name = "inventory/printorder_form.html"
    success_url = reverse_lazy("printorder_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = PrintOrderItemFormSet(self.request.POST, prefix="items")
        else:
            context["items_formset"] = PrintOrderItemFormSet(prefix="items")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context["items_formset"]
        if items_formset.is_valid():
            self.object = form.save()
            items_formset.instance = self.object
            items_formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))

class PrintOrderUpdateView(LoginRequiredMixin, OperatorRequiredMixin, UpdateView):
    model = PrintOrder
    form_class = PrintOrderForm
    template_name = "inventory/printorder_form.html"
    success_url = reverse_lazy("printorder_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["items_formset"] = PrintOrderItemFormSet(self.request.POST, instance=self.object, prefix="items")
        else:
            context["items_formset"] = PrintOrderItemFormSet(instance=self.object, prefix="items")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        items_formset = context["items_formset"]
        if items_formset.is_valid():
            self.object = form.save()
            items_formset.instance = self.object
            items_formset.save()
            return super().form_valid(form)
        return self.render_to_response(self.get_context_data(form=form))


class PrintOrderDeleteView(LoginRequiredMixin, OperatorRequiredMixin, DeleteView):
    model = PrintOrder
    template_name = "inventory/printorder_confirm_delete.html"
    success_url = reverse_lazy("printorder_list")
    form_class = PrintOrderDeleteForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["delete_form"] = PrintOrderDeleteForm()
        return context

    def form_valid(self, form):                # ← reemplaza el override de delete()
        if form.cleaned_data["devolver_bobinas"] == "devolver":
            self.object.revertir_consumo()
        return super().form_valid(form)    

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
    ultimas_ordenes = PrintOrder.objects.prefetch_related("items__spool")[:5]

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
    response["Content-Disposition"] = 'attachment; filename="Inventario_bobinas.csv"'

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
    response["Content-Disposition"] = 'attachment; filename="Ordenes_impresion.csv"'

    writer = csv.writer(response)
    writer.writerow(["Pieza", "Impresora", "Bobina", "Gramos usados", "Duración (min)", "Coste (€)", "Fecha inicio", "Fecha fin"])
    for order in PrintOrder.objects.prefetch_related("items__spool"):
        for item in order.items.all():
            writer.writerow([
                order.pieza, order.printer, item.spool, item.gramos_usados, order.duracion_minutos, order.coste, order.fecha_inicio, order.fecha_fin
            ])
    return response

# Calculadora
def calcular_impresion(datos, otros_rows):
    gramos = datos["gramos"]
    merma_pct = datos["merma"]

    gramos_reales = gramos * (1 + merma_pct / 100)
    material = (gramos_reales / 1000) * float(datos["costo_kg"])
    coste_merma = ((gramos_reales - gramos) / 1000) * float(datos["costo_kg"])

    horas = datos["duracion_min"] / 60

    electricidad = None
    if datos.get("incluir_electricidad") and datos.get("potencia_w") and datos.get("precio_kwh") is not None:
        electricidad = (datos["potencia_w"] / 1000) * horas * float(datos["precio_kwh"])

    mantenimiento = None
    if datos.get("incluir_mantenimiento") and datos.get("mantenimiento_hora") is not None:
        mantenimiento = float(datos["mantenimiento_hora"]) * horas

    mano_obra = None
    if datos.get("incluir_mano_obra") and datos.get("mano_obra") is not None:
        mano_obra = float(datos["mano_obra"])

    otros = []
    if datos.get("incluir_otros"):
        otros = [fila for fila in otros_rows if fila["nombre"] and fila["valor"] is not None]

    otros_total = sum(float(fila["valor"]) for fila in otros)

    total = material + coste_merma
    if electricidad is not None:
        total += electricidad
    if mantenimiento is not None:
        total += mantenimiento
    if mano_obra is not None:
        total += mano_obra
    total += otros_total

    presupuesto = total * (1 + datos["margen"] / 100)

    return {
        "nombre_pieza": datos["nombre_pieza"],
        "gramos": gramos,
        "gramos_reales": gramos_reales,
        "merma_pct": merma_pct,
        "material": material,
        "coste_merma": coste_merma,
        "electricidad": electricidad,
        "mantenimiento": mantenimiento,
        "mano_obra": mano_obra,
        "otros": otros,
        "otros_total": otros_total,
        "total": total,
        "margen_pct": datos["margen"],
        "presupuesto": presupuesto,
    }

@login_required
def calculadora(request):
    resultado = None

    if request.method == "POST":
        form = CalculadoraForm(request.POST)
        otros_formset = OtrosGastosFormSet(request.POST, prefix="otros")
        if form.is_valid() and otros_formset.is_valid():
            otros_rows = [
                {
                    "nombre": fila.cleaned_data.get("nombre"),
                    "valor": fila.cleaned_data.get("valor"),
                }
                for fila in otros_formset
            ]
            resultado = calcular_impresion(form.cleaned_data, otros_rows)
    else:
        form = CalculadoraForm()
        otros_formset = OtrosGastosFormSet(prefix="otros")

    return render(request, "inventory/calculadora.html", {
        "form": form,
        "otros_formset": otros_formset,
        "resultado": resultado,
    })


@login_required
def calculadora_csv(request):
    form = CalculadoraForm(request.POST)
    otros_formset = OtrosGastosFormSet(request.POST, prefix="otros")

    if form.is_valid() and otros_formset.is_valid():
        otros_rows = [
            {
                "nombre": fila.cleaned_data.get("nombre"),
                "valor": fila.cleaned_data.get("valor"),
            }
            for fila in otros_formset
        ]
        r = calcular_impresion(form.cleaned_data, otros_rows)

        nombre_archivo = re.sub(r"[^\w\-]", "_", r["nombre_pieza"]) or "presupuesto"
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="Presupuesto_{nombre_archivo}.csv"'

        writer = csv.writer(response)
        writer.writerow(["Presupuesto", r["nombre_pieza"]])
        writer.writerow(["Fecha", date.today().isoformat()])
        writer.writerow([])
        writer.writerow(["Concepto", "Importe (€)"])
        writer.writerow([f"Material ({r['gramos']:.0f}g + {r['merma_pct']}% merma)", round(r["material"], 2)])
        writer.writerow([f"Merma ({r['merma_pct']}%)", round(r["coste_merma"], 2)])
        if r["electricidad"] is not None:
            writer.writerow(["Electricidad", round(r["electricidad"], 2)])
        if r["mantenimiento"] is not None:
            writer.writerow(["Mantenimiento", round(r["mantenimiento"], 2)])
        if r["mano_obra"] is not None:
            writer.writerow(["Mano de obra", round(r["mano_obra"], 2)])
        for fila in r["otros"]:
            writer.writerow([f"Otros: {fila['nombre']}", round(float(fila['valor']), 2)])
        writer.writerow([])
        writer.writerow(["Total", round(r["total"], 2)])
        writer.writerow([f"Margen ({r['margen_pct']}%)", round(r["presupuesto"] - r["total"], 2)])
        writer.writerow(["Presupuesto", round(r["presupuesto"], 2)])
        return response

    return redirect("calculadora")
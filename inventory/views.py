from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from .models import Spool

# Create your views here.
@login_required
def home(request):
    return render(request, "inventory/home.html")

class SpoolListView(ListView):
    model = Spool
    template_name = "inventory/spool_list.html"
    context_object_name = "spools"
    queryset = Spool.objects.select_related("material", "color")

class SpoolCreateView(CreateView):
    model = Spool
    template_name = "inventory/spool_form.html"
    fields = ["material", "color", "marca", "diametro", "costo_por_kg", "peso_inicial", "peso_actual", "estado", "fecha_compra"]
    success_url = reverse_lazy("spool_list")
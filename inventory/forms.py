from django import forms
from django.forms import inlineformset_factory, formset_factory
from .models import Material, PrintOrder, PrintOrderItem, Spool, Color, StockThreshold


class PrintOrderForm(forms.ModelForm):
    fecha_inicio = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"],
    )
    fecha_fin = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"},
            format="%Y-%m-%dT%H:%M",
        ),
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = PrintOrder
        fields = ["pieza", "printer", "duracion_minutos", "fecha_inicio", "fecha_fin", "notas", "coste"]

    def clean(self):
        printer = self.cleaned_data.get("printer")

        if printer and printer.estado == "Mantenimiento":
            self.add_error("printer", "La impresora está en mantenimiento y no puede usarse.")

        return self.cleaned_data

class PrintOrderItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["spool"].widget.attrs.update({"class": "form-control"})
        self.fields["gramos_usados"].widget.attrs.update({"class": "form-control"})
        
    class Meta:
        model = PrintOrderItem
        fields = ["spool", "gramos_usados"]

    def clean(self):
        spool = self.cleaned_data.get("spool")
        gramos = self.cleaned_data.get("gramos_usados")

        if spool and gramos:
            if spool.estado == "Vacía":
                self.add_error("spool", "Esa bobina está vacía.")
            elif spool.peso_actual < gramos:
                self.add_error("spool", f"Solo quedan {spool.peso_actual}g, no alcanzan para {gramos}g.")

        return self.cleaned_data


PrintOrderItemFormSet = inlineformset_factory(
    PrintOrder,
    PrintOrderItem,
    form=PrintOrderItemForm,
    fields=["spool", "gramos_usados"],
    extra=6,
    max_num=PrintOrderItem.MAX_FILAMENTOS,
    validate_max=True,
    can_delete=False,
)

class SpoolForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Spool
        fields = ["material", "color", "marca", "diametro", "costo_por_kg", "peso_inicial", "peso_actual", "estado", "fecha_compra"]

class MaterialForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Material
        fields = ["tipo", "subtipo"]

class ColorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Color
        fields = ["nombre"]

class StockThresholdForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = StockThreshold
        fields = ["material", "color", "stock_minimo"]

class PrintOrderDeleteForm(forms.Form):
    ACCIONES = [
        ("devolver", "Devolver el material a las bobinas"),
        ("dejar", "Dejar las bobinas como están"),
    ]
    devolver_bobinas = forms.ChoiceField(
        choices=ACCIONES,
        widget=forms.RadioSelect,
        initial="devolver",
    )

class OtroGastoForm(forms.Form):
    nombre = forms.CharField(label="Concepto", required=False)
    valor = forms.DecimalField(max_digits=6, decimal_places=2, label="Importe (€)", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


OtrosGastosFormSet = formset_factory(OtroGastoForm, extra=2)

class CalculadoraForm(forms.Form):
    nombre_pieza = forms.CharField(label="Nombre de la pieza")
    costo_kg = forms.DecimalField(max_digits=6, decimal_places=2, label="Coste material (€/kg)")
    gramos = forms.FloatField(label="Gramos a imprimir")
    merma = forms.IntegerField(initial=8, label="Merma (%)")
    duracion_min = forms.IntegerField(label="Duración (min)")
    margen = forms.IntegerField(initial=30, label="Margen (%)")

    incluir_electricidad = forms.BooleanField(required=False, label="Incluir electricidad")
    potencia_w = forms.IntegerField(initial=220, label="Potencia de la impresora (W)", required=False)
    precio_kwh = forms.DecimalField(max_digits=5, decimal_places=3, initial="0.20", label="Precio (€/kWh)", required=False)

    incluir_mantenimiento = forms.BooleanField(required=False, label="Incluir mantenimiento")
    mantenimiento_hora = forms.DecimalField(max_digits=6, decimal_places=2, initial="0.30", label="Mantenimiento (€/h)", required=False)

    incluir_mano_obra = forms.BooleanField(required=False, label="Incluir mano de obra")
    mano_obra = forms.DecimalField(max_digits=6, decimal_places=2, initial="10.00", label="Mano de obra (€)", required=False)

    incluir_otros = forms.BooleanField(required=False, label="Incluir otros gastos")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({"class": "form-check-input"})
            else:
                field.widget.attrs.update({"class": "form-control"})
from django import forms
from django.forms import inlineformset_factory
from .models import PrintOrder, PrintOrderItem, Spool


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
        fields = ["pieza", "printer", "duracion_minutos", "fecha_inicio", "fecha_fin", "notas"]

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
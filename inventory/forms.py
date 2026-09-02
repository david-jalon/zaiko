from django import forms
from django.forms import inlineformset_factory
from .models import PrintOrder, PrintOrderItem


class PrintOrderForm(forms.ModelForm):
    class Meta:
        model = PrintOrder
        fields = ["pieza", "printer", "duracion_minutos", "fecha_inicio", "fecha_fin", "notas"]

    def clean(self):
        printer = self.cleaned_data.get("printer")

        if printer and printer.estado == "Mantenimiento":
            self.add_error("printer", "La impresora está en mantenimiento y no puede usarse.")

        return self.cleaned_data

class PrintOrderItemForm(forms.ModelForm):
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
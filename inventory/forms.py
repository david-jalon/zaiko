from django import forms
from .models import PrintOrder


class PrintOrderForm(forms.ModelForm):
    class Meta:
        model = PrintOrder
        fields = ["pieza", "printer", "spool", "gramos_usados", "duracion_minutos", "fecha_inicio", "fecha_fin", "notas"]

        def clean(self):
            spool = self.cleaned_data.get("spool")
            gramos = self.cleaned_data.get("gramos_usados")
            printer = self.cleaned_data.get("printer")

            if spool and gramos:
                if spool.estado == "Vacía":
                    self.add_error("spool", "Esa bobina está vacía.")
                elif spool.peso_actual < gramos:
                    self.add_error("spool", f"Solo quedan {spool.peso_actual}g, no alcanzan para {gramos}g.")

            if printer and printer.estado == "Mantenimiento":
                self.add_error("printer", "La impresora está en mantenimiento y no puede usarse.")

            return self.cleaned_data
from django.db import models

TIPO_CHOICES = [("PLA", "PLA"), ("PETG", "PETG"), ("ABS", "ABS"), ("TPU", "TPU")]


# Create your models here.
class Material(models.Model):
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=30)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    color = models.CharField(max_length=30)
    diametro = models.FloatField()
    costo_por_kg = models.DecimalField(max_digits=4, decimal_places=2)
    stock_minimo = models.FloatField()

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]
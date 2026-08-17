from django.db import models

TIPO_CHOICES = [("PLA", "PLA"), ("PETG", "PETG"), ("ABS", "ABS"), ("TPU", "TPU")]
ESTADO_CHOICES =[("Sellada", "Sellada"), ("Abierta", "Abierta"), ("Vacía", "Vacía")]


# Create your models here.
class Material(models.Model):
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    subtipo = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.tipo} {self.subtipo}"

    class Meta:
        ordering = ["tipo", "subtipo"]
        unique_together = ("tipo", "subtipo")

class Color(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ["nombre"]

class StockThreshold(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    stock_minimo = models.FloatField()

    def __str__(self):
        return f"{self.material} {self.color} {self.stock_minimo}"

    class Meta:
        unique_together = ("material", "color")

class Spool(models.Model):
    material = models.ForeignKey(Material, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    marca = models.CharField(max_length=50)
    diametro = models.FloatField()
    costo_por_kg = models.DecimalField(max_digits=4, decimal_places=2)
    peso_inicial = models.FloatField()
    peso_actual = models.FloatField()
    estado = models.CharField(choices=ESTADO_CHOICES, max_length=30)
    fecha_compra = models.DateField()

    def __str__(self):
        return f"{self.material} {self.color} {self.peso_actual}"

    class Meta:
        ordering = ["estado"]
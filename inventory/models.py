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

class Printer(models.Model):
    ESTADO_CHOICES = [("Operativa", "Operativa"), ("Mantenimiento", "Mantenimiento"), ("Fuera de servicio", "Fuera de servicio")]

    nombre = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    estado = models.CharField(choices=ESTADO_CHOICES, max_length=30)
    horas_uso = models.FloatField(default=0)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        ordering = ["nombre"]

class PrintOrder(models.Model):
    pieza = models.CharField(max_length=100)
    printer = models.ForeignKey(Printer, on_delete=models.PROTECT)
    spool = models.ForeignKey(Spool, on_delete=models.PROTECT)
    gramos_usados = models.FloatField()
    duracion_minutos = models.IntegerField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.pieza} - {self.gramos_usados}g"

    class Meta:
        ordering = ["-fecha_inicio"]

    def save(self, *args, **kwargs):
        es_nueva = self.pk is None # True si la instancia es nueva (no tiene pk asignado)
        super().save(*args, **kwargs) # Guarda primero la instancia para obtener un pk si es nueva

        if es_nueva:
            # Actualiza el peso_actual del spool asociado
            self.spool.peso_actual -= self.gramos_usados
            if self.spool.peso_actual < 0:
                self.spool.peso_actual = 0
                self.spool.estado = "Vacía"
            self.spool.save() # Guarda la bobina actualizada

    
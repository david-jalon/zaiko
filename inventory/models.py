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
    spools = models.ManyToManyField(Spool, through="PrintOrderItem")
    duracion_minutos = models.IntegerField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    notas = models.TextField(blank=True)

    def __str__(self):
        return f"{self.pieza}"

    class Meta:
        ordering = ["-fecha_inicio"]

    def save(self, *args, **kwargs):
        es_nueva = self.pk is None # True si la instancia es nueva (no tiene pk asignado)
        duracion_anterior = 0 if es_nueva else PrintOrder.objects.get(pk=self.pk).duracion_minutos 
        super().save(*args, **kwargs) # Guarda primero la instancia para obtener un pk si es nueva

        delta_horas = (self.duracion_minutos - duracion_anterior) / 60
        if delta_horas != 0:
            self.printer.horas_uso += delta_horas
            self.printer.save()

    def revertir_consumo(self):
        for item in self.items.all():
            item.spool.peso_actual += item.gramos_usados
            if item.spool.peso_actual > 0:
                item.spool.estado = "Abierta"
            item.spool.save()

        self.printer.horas_uso -= self.duracion_minutos / 60
        self.printer.save()

class PrintOrderItem(models.Model):
    MAX_FILAMENTOS = 6

    print_order = models.ForeignKey(PrintOrder, on_delete=models.CASCADE, related_name="items")
    spool = models.ForeignKey(Spool, on_delete=models.PROTECT)
    gramos_usados = models.FloatField()

    def __str__(self):
        return f"{self.spool} - {self.gramos_usados}g"

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(gramos_usados__gt=0),
                name="printorderitem_gramos_positivos"
            ),
        ]

    def save(self, *args, **kwargs):
        es_nueva = self.pk is None

        if es_nueva:
            super().save(*args, **kwargs)
            self.spool.peso_actual -= self.gramos_usados
            if self.spool.peso_actual <= 0:
                self.spool.peso_actual = 0
                self.spool.estado = "Vacía"
            self.spool.save()
        else:
            previo = PrintOrderItem.objects.get(pk=self.pk)
            previo.spool.peso_actual += previo.gramos_usados
            if previo.spool.peso_actual > 0:
                previo.spool.estado = "Abierta"
            previo.spool.save()

            super().save(*args, **kwargs)

            self.spool.refresh_from_db()
            self.spool.peso_actual -= self.gramos_usados
            if self.spool.peso_actual <= 0:
                self.spool.peso_actual = 0
                self.spool.estado = "Vacía"
            self.spool.save()
import pytest
from django.contrib.auth.models import User, Group
from inventory.models import Material, Color, Spool, Printer


@pytest.fixture
def operador(db):
    grupo, _ = Group.objects.get_or_create(name="Operador")
    user = User.objects.create_user(username="operador", password="test1234")
    user.groups.add(grupo)
    return user


@pytest.fixture
def material(db):
    return Material.objects.create(tipo="PLA", subtipo="Matte")


@pytest.fixture
def color(db):
    return Color.objects.create(nombre="Rojo")


@pytest.fixture
def spool(db, material, color):
    return Spool.objects.create(
        material=material,
        color=color,
        marca="Test",
        diametro=1.75,
        costo_por_kg=25,
        peso_inicial=1000,
        peso_actual=1000,
        estado="Sellada",
        fecha_compra="2026-01-01",
    )


@pytest.fixture
def printer(db):
    return Printer.objects.create(nombre="Impresora A", modelo="X", estado="Operativa", horas_uso=0)
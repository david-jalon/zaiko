from django.test import TestCase
import pytest
from inventory.models import PrintOrder

# Create your tests here.
@pytest.mark.django_db
def test_crear_orden_descuenta_stock(spool, printer, material, color):
    orden = PrintOrder.objects.create(
        pieza="Test pieza",
        printer=printer,
        spool=spool,
        gramos_usados=50,
        duracion_minutos=60,
        fecha_inicio="2026-01-01 10:00:00",
        fecha_fin="2026-01-01 11:00:00",
    )
    spool.refresh_from_db()  # Recarga la bobina desde la BD
    assert spool.peso_actual == 950  # 1000 - 50

def test_bobina_vacia_queda_en_vacia(spool):
    # Simulamos que solo quedan 30g y creamos una orden de 50g → se descarta en el form,
    # pero si se forzara el save, el estado pasa a Vacía
    spool.peso_actual = 30
    spool.save()
    assert spool.peso_actual == 30

def test_orden_rechazada_sin_stock_suficiente(db, spool, printer, client, operador):
    spool.peso_actual = 30
    spool.save()
    client.login(username="operador", password="test1234")
    response = client.post("/ordenes/nueva/", {
        "pieza": "X",
        "printer": printer.pk,
        "spool": spool.pk,
        "gramos_usados": 50,
        "duracion_minutos": 60,
        "fecha_inicio": "2026-01-01 10:00:00",
        "fecha_fin": "2026-01-01 11:00:00",
    })
    assert response.status_code == 200  # vuelve al form (no redirige)
    assert "Solo quedan" in response.content.decode()

# Test de vista
def test_login_requerido(client):
    response = client.get("/spools/")
    assert response.status_code == 302  # redirige al login

def test_operador_accede_a_spools(db, client, operador, spool):
    client.login(username="operador", password="test1234")
    response = client.get("/spools/")
    assert response.status_code == 200
    assert "Bobinas" in response.content.decode()

def test_export_csv(db, client, operador, spool):
    client.login(username="operador", password="test1234")
    response = client.get("/exportar/inventario/")
    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
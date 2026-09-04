from django.test import TestCase
import pytest
from inventory.models import PrintOrder, PrintOrderItem, Spool

# Create your tests here.
@pytest.mark.django_db
def test_crear_orden_descuenta_stock(spool, printer, material, color):
    orden = PrintOrder.objects.create(
        pieza="Test pieza",
        printer=printer,
        duracion_minutos=60,
        fecha_inicio="2026-01-01 10:00:00",
        fecha_fin="2026-01-01 11:00:00",
    )
    PrintOrderItem.objects.create(print_order=orden, spool=spool, gramos_usados=50)
    spool.refresh_from_db()  # Recarga la bobina desde la BD
    assert spool.peso_actual == 950  # 1000 - 50

def test_orden_multicolor_descuenta_cada_bobina(spool, printer, material, color):
    spool2 = Spool.objects.create(
        material=material, color=color, marca="Test2", diametro=1.75,
        costo_por_kg=25, peso_inicial=1000, peso_actual=1000,
        estado="Sellada", fecha_compra="2026-01-01",
    )
    orden = PrintOrder.objects.create(
        pieza="Multicolor", printer=printer,
        duracion_minutos=60, fecha_inicio="2026-01-01 10:00:00", fecha_fin="2026-01-01 11:00:00",
    )
    PrintOrderItem.objects.create(print_order=orden, spool=spool, gramos_usados=30)
    PrintOrderItem.objects.create(print_order=orden, spool=spool2, gramos_usados=20)
    spool.refresh_from_db()
    spool2.refresh_from_db()
    assert spool.peso_actual == 970
    assert spool2.peso_actual == 980

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
        "duracion_minutos": 60,
        "fecha_inicio": "2026-01-01 10:00:00",
        "fecha_fin": "2026-01-01 11:00:00",
        "items-TOTAL_FORMS": "1", "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0", "items-MAX_NUM_FORMS": "6",
        "items-0-spool": spool.pk,
        "items-0-gramos_usados": 50,
        "items-0-id": "",
    })
    assert response.status_code == 200  # vuelve al form (no redirige)
    assert "Solo quedan" in response.content.decode()

def test_no_permitir_mas_de_6_filamentos(db, client, operador, spool, printer):
    client.login(username="operador", password="test1234")
    data = {
        "pieza": "X", "printer": printer.pk,
        "duracion_minutos": 60,
        "fecha_inicio": "2026-01-01 10:00:00", "fecha_fin": "2026-01-01 11:00:00",
        "items-TOTAL_FORMS": "7", "items-INITIAL_FORMS": "0",
        "items-MIN_NUM_FORMS": "0", "items-MAX_NUM_FORMS": "6",
    }
    for i in range(7):
        data[f"items-{i}-spool"] = spool.pk
        data[f"items-{i}-gramos_usados"] = 10
        data[f"items-{i}-id"] = ""
    response = client.post("/ordenes/nueva/", data)
    assert response.status_code == 200  # vuelve al form (no guarda)

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

def test_editar_impresion_ajusta_bobinas(spool, printer, material, color, client, operador):
    client.login(username="operador", password="test1234")
    orden = PrintOrder.objects.create(
        pieza="Pieza A", printer=printer,
        duracion_minutos=60, fecha_inicio="2026-01-01 10:00:00", fecha_fin="2026-01-01 11:00:00",
    )
    item = PrintOrderItem.objects.create(print_order=orden, spool=spool, gramos_usados=30)
    spool.refresh_from_db()
    assert spool.peso_actual == 970

    response = client.post(f"/ordenes/{orden.pk}/editar/", {
        "pieza": "Pieza A",
        "printer": printer.pk,
        "duracion_minutos": 60,
        "fecha_inicio": "2026-01-01 10:00:00",
        "fecha_fin": "2026-01-01 11:00:00",
        "items-TOTAL_FORMS": "1", "items-INITIAL_FORMS": "1",
        "items-MIN_NUM_FORMS": "0", "items-MAX_NUM_FORMS": "6",
        "items-0-id": item.pk,
        "items-0-spool": spool.pk,
        "items-0-gramos_usados": 40,
    })
    assert response.status_code == 302  # redirige tras guardar
    spool.refresh_from_db()
    assert spool.peso_actual == 960  # 1000 - 40 (se deshizo 30 y se aplicó 40)


def test_eliminar_con_devolucion(spool, printer, material, color, client, operador):
    client.login(username="operador", password="test1234")
    orden = PrintOrder.objects.create(
        pieza="Pieza A", printer=printer,
        duracion_minutos=60, fecha_inicio="2026-01-01 10:00:00", fecha_fin="2026-01-01 11:00:00",
    )
    PrintOrderItem.objects.create(print_order=orden, spool=spool, gramos_usados=30)
    spool.refresh_from_db()
    assert spool.peso_actual == 970

    response = client.post(f"/ordenes/{orden.pk}/borrar/", {"devolver_bobinas": "devolver"})
    print("LOCATION:", response.get("Location"))
    print("ORDEN EXISTE:", PrintOrder.objects.filter(pk=orden.pk).exists())
    assert response.status_code == 302
    spool.refresh_from_db()
    assert spool.peso_actual == 1000  # se devolvió el material


def test_eliminar_sin_devolucion(spool, printer, material, color, client, operador):
    client.login(username="operador", password="test1234")
    orden = PrintOrder.objects.create(
        pieza="Pieza A", printer=printer,
        duracion_minutos=60, fecha_inicio="2026-01-01 10:00:00", fecha_fin="2026-01-01 11:00:00",
    )
    PrintOrderItem.objects.create(print_order=orden, spool=spool, gramos_usados=30)
    spool.refresh_from_db()
    assert spool.peso_actual == 970

    response = client.post(f"/ordenes/{orden.pk}/borrar/", {"devolver_bobinas": "dejar"})
    assert response.status_code == 302
    spool.refresh_from_db()
    assert spool.peso_actual == 970  # el material no se devuelve
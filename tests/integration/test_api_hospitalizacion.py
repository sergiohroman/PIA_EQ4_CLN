"""US-11, US-12, US-15 vía API (N-006, BR-002)."""
from datetime import timedelta


def internar(client, mascota, vet, motivo="observación"):
    return client.post(
        "/hospitalizacion/ingresos",
        json={"mascota_id": mascota, "veterinario_id": vet, "motivo_ingreso": motivo},
    )


def llenar(client, vet, nueva_mascota, cantidad):
    ids = [nueva_mascota(f"Mascota{i}") for i in range(cantidad)]
    for mascota in ids:
        assert internar(client, mascota, vet).status_code == 201
    return ids


def test_us12_ingreso_once_devuelve_409_y_no_cambia_la_ocupacion(client, veterinario, nueva_mascota):
    llenar(client, veterinario["id"], nueva_mascota, 10)
    extra = nueva_mascota("Extra")
    r = internar(client, extra, veterinario["id"])
    assert r.status_code == 409
    assert r.json() == {
        "error": "CapacidadMaximaJaulasAlcanzada",
        "detalle": "Capacidad máxima de jaulas alcanzada",
    }
    ocupacion = client.get("/hospitalizacion/ocupacion").json()
    assert ocupacion["ocupadas"] == 10 and ocupacion["disponibles"] == 0  # rollback: sin cambios


def test_us15_ocupacion_en_tiempo_real(client, veterinario, nueva_mascota):
    llenar(client, veterinario["id"], nueva_mascota, 8)
    ocupacion = client.get("/hospitalizacion/ocupacion").json()
    assert (ocupacion["ocupadas"], ocupacion["capacidad"], ocupacion["porcentaje"]) == (8, 10, 80.0)
    assert len(ocupacion["jaulas"]) == 10


def test_llegar_a_diez_genera_alerta_en_dashboard(client, veterinario, nueva_mascota):
    llenar(client, veterinario["id"], nueva_mascota, 10)
    tipos = [n["tipo"] for n in client.get("/notificaciones").json()]
    assert tipos.count("alerta_capacidad") == 1


def test_alta_libera_jaula(client, veterinario, nueva_mascota):
    ids = llenar(client, veterinario["id"], nueva_mascota, 10)
    assert client.post(f"/hospitalizacion/altas/{ids[0]}").json()["ocupadas"] == 9
    assert internar(client, nueva_mascota("Nueva"), veterinario["id"]).status_code == 201
    assert client.post("/hospitalizacion/altas/no-internada").status_code == 409


def test_doble_ingreso_y_recursos_inexistentes(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    assert internar(client, mascota, veterinario["id"]).status_code == 201
    assert internar(client, mascota, veterinario["id"]).status_code == 409
    assert internar(client, "zzz", veterinario["id"]).status_code == 404
    assert internar(client, mascota, "zzz").status_code == 404


def test_us11_signos_pendientes_tras_4_horas(client, reloj, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    internar(client, mascota, veterinario["id"])
    assert client.get("/hospitalizacion/signos-pendientes").json() == []
    reloj.valor += timedelta(hours=4)
    pendientes = client.get("/hospitalizacion/signos-pendientes").json()
    assert pendientes[0]["mascota_id"] == mascota
    r = client.post(
        "/hospitalizacion/signos-vitales",
        json={"mascota_id": mascota, "temperatura": "38.5", "frecuencia_cardiaca": 100, "frecuencia_respiratoria": 30},
    )
    assert r.status_code == 201
    assert client.get("/hospitalizacion/signos-pendientes").json() == []


def test_signos_invalidos_o_paciente_no_internado(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    cuerpo = {"mascota_id": mascota, "temperatura": "38.5", "frecuencia_cardiaca": 100, "frecuencia_respiratoria": 30}
    assert client.post("/hospitalizacion/signos-vitales", json=cuerpo).status_code == 409  # no internado
    internar(client, mascota, veterinario["id"])
    assert client.post("/hospitalizacion/signos-vitales", json={**cuerpo, "temperatura": "50"}).status_code == 422

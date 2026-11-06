"""US-01, US-02, US-03, US-09, US-10 vía API (N-001, N-003, N-007)."""
from datetime import datetime


def agendar(client, mascota, vet, tipo="consulta", inicio="2026-11-10T09:00:00"):
    return client.post(
        "/citas", json={"mascota_id": mascota, "veterinario_id": vet, "tipo": tipo, "inicio": inicio}
    )


def test_us01_duracion_automatica_por_tipo(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    r = agendar(client, mascota, veterinario["id"], "vacuna", "2026-11-10T09:00:00")
    assert r.status_code == 201
    cita = r.json()["cita"]
    inicio, fin = datetime.fromisoformat(cita["inicio"]), datetime.fromisoformat(cita["fin"])
    assert (fin - inicio).total_seconds() == 15 * 60 and cita["estado"] == "PROGRAMADA"
    cirugia = agendar(client, mascota, veterinario["id"], "cirugia", "2026-11-10T12:00:00").json()["cita"]
    assert (datetime.fromisoformat(cirugia["fin"]) - datetime.fromisoformat(cirugia["inicio"])).total_seconds() == 7200


def test_traslape_devuelve_409(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    assert agendar(client, mascota, veterinario["id"]).status_code == 201
    r = agendar(client, mascota, veterinario["id"], "vacuna", "2026-11-10T09:15:00")
    assert r.status_code == 409 and r.json()["error"] == "TraslapeDeCitas"


def test_validaciones_422(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    assert agendar(client, mascota, veterinario["id"], "estetica").status_code == 422
    assert agendar(client, mascota, veterinario["id"], inicio="2026-11-09T09:00:00").status_code == 422  # pasado
    assert agendar(client, mascota, veterinario["id"], inicio="2026-11-10T22:00:00").status_code == 422  # fuera de horario
    assert agendar(client, mascota, veterinario["id"], inicio="2026-11-10T09:00:00Z").status_code == 422  # zona horaria


def test_recursos_inexistentes_404(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    assert agendar(client, "zzz", veterinario["id"]).status_code == 404
    assert agendar(client, mascota, "zzz").status_code == 404


def test_us02_espacios_libres_se_actualizan(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    params = {"fecha": "2026-11-10", "veterinario_id": veterinario["id"], "tipo": "consulta"}
    antes = client.get("/citas/espacios-libres", params=params).json()
    agendar(client, mascota, veterinario["id"], "consulta", "2026-11-10T08:00:00")
    despues = client.get("/citas/espacios-libres", params=params).json()
    assert len(despues) < len(antes)
    assert all(not e["inicio"].startswith("2026-11-10T08:00") for e in despues)


def test_us03_emergencia_va_primero_y_alerta(client, reloj, veterinario, nueva_mascota):
    regular, urgente = nueva_mascota("Firulais"), nueva_mascota("Rex")
    agendar(client, regular, veterinario["id"], "consulta", "2026-11-10T10:00:00")
    reloj.valor = datetime(2026, 11, 10, 10, 10)  # llega la emergencia a mitad de la consulta
    r = client.post("/emergencias", json={"mascota_id": urgente, "veterinario_id": veterinario["id"]})
    assert r.status_code == 201
    assert r.json()["posicion_en_cola"] == 1 and r.json()["cita"]["es_emergencia"]
    cola = client.get("/citas/cola", params={"fecha": "2026-11-10"}).json()
    assert cola[0]["es_emergencia"] is True
    tipos = [n["tipo"] for n in client.get("/notificaciones").json()]
    assert "alerta_emergencia" in tipos


def test_us09_us10_recordatorios_por_domain_events(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    agendar(client, mascota, veterinario["id"], "vacuna", "2026-11-20T10:00:00")
    outbox = client.get("/notificaciones").json()
    tipos = {n["tipo"]: n for n in outbox}
    assert tipos["recordatorio_3_dias"]["enviar_en"] == "2026-11-17T08:00:00"
    assert tipos["recordatorio_4_horas"]["enviar_en"] == "2026-11-20T06:00:00"
    assert tipos["recordatorio_4_horas"]["destino"] == "8112345678"


def test_consulta_no_genera_recordatorio_de_3_dias(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    agendar(client, mascota, veterinario["id"], "consulta", "2026-11-20T10:00:00")
    assert [n["tipo"] for n in client.get("/notificaciones").json()] == ["recordatorio_4_horas"]


def test_state_machine_via_api(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    cita = agendar(client, mascota, veterinario["id"]).json()["cita"]["id"]
    assert client.post(f"/citas/{cita}/transiciones", json={"accion": "completar"}).status_code == 409  # salto
    assert client.post(f"/citas/{cita}/transiciones", json={"accion": "aprobar"}).json()["estado"] == "EN_ATENCION"
    assert client.post(f"/citas/{cita}/transiciones", json={"accion": "aprobar"}).status_code == 409  # repetida
    assert client.post(f"/citas/{cita}/transiciones", json={"accion": "completar"}).json()["estado"] == "COMPLETADA"
    assert client.post(f"/citas/{cita}/transiciones", json={"accion": "cancelar"}).status_code == 409
    assert client.post("/citas/no-existe/transiciones", json={"accion": "aprobar"}).status_code == 404
    assert client.post(f"/citas/{cita}/transiciones", json={"accion": "saltar"}).status_code == 422


def test_cita_cancelada_libera_horario(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    cita = agendar(client, mascota, veterinario["id"]).json()["cita"]["id"]
    client.post(f"/citas/{cita}/transiciones", json={"accion": "cancelar"})
    assert agendar(client, mascota, veterinario["id"]).status_code == 201

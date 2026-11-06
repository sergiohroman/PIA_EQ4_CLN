"""US-14 y utilidades: reportes, reglas compuestas, salud y contrato OpenAPI."""


def test_health_y_openapi_expuestos(client):
    assert client.get("/health").json()["status"] == "ok"
    esquema = client.get("/openapi.json").json()
    for ruta in ("/citas", "/emergencias", "/hospitalizacion/ingresos", "/expedientes", "/notas/{nota_id}/firma"):
        assert ruta in esquema["paths"]
    assert client.get("/docs").status_code == 200
    assert client.get("/", follow_redirects=False).status_code in (302, 307)


def test_us14_productividad_por_veterinario(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    for hora, tipo in (("09:00", "consulta"), ("10:00", "vacuna"), ("11:00", "consulta")):
        cita = client.post(
            "/citas",
            json={"mascota_id": mascota, "veterinario_id": veterinario["id"], "tipo": tipo,
                  "inicio": f"2026-11-10T{hora}:00"},
        ).json()["cita"]["id"]
        client.post(f"/citas/{cita}/transiciones", json={"accion": "aprobar"})
        client.post(f"/citas/{cita}/transiciones", json={"accion": "completar"})
    sin_completar = client.post(
        "/citas",
        json={"mascota_id": mascota, "veterinario_id": veterinario["id"], "tipo": "cirugia",
              "inicio": "2026-11-10T14:00:00"},
    )
    assert sin_completar.status_code == 201
    r = client.get("/reportes/productividad", params={"desde": "2026-11-01", "hasta": "2026-11-30"})
    assert r.status_code == 200
    assert r.json() == [{
        "veterinario_id": veterinario["id"], "veterinario": "Dra. López",
        "consultas": 2, "vacunas": 1, "cirugias": 0, "total": 3,
    }]


def test_evaluar_reglas_compuestas(client):
    base = {"actor_activo": True, "actor_preferente": True, "autorizado": True,
            "lineas": [{"recurso_id": "P1", "precio": "800.00", "cantidad": 2}]}
    r = client.post("/reglas/operaciones/evaluar", json=base).json()
    assert r["total_mxn"] == "1600.00" and r["puede_procesarse"] and r["beneficio_referencia"]
    con_promo = client.post("/reglas/operaciones/evaluar", json={**base, "promocion_activa": True}).json()
    assert not con_promo["beneficio_referencia"] and con_promo["puede_procesarse"]
    sin_detalle = client.post("/reglas/operaciones/evaluar", json={**base, "lineas": []}).json()
    assert not sin_detalle["puede_procesarse"]
    assert client.post("/reglas/operaciones/evaluar",
                       json={**base, "lineas": [{"recurso_id": "P", "precio": "1", "cantidad": 0}]}).status_code == 422


def _cita(client, mascota, vet, tipo, inicio):
    r = client.post("/citas", json={"mascota_id": mascota, "veterinario_id": vet, "tipo": tipo, "inicio": inicio})
    assert r.status_code == 201
    return r.json()["cita"]["id"]


def test_us13_vacunas_pendientes_json_y_csv(client, reloj, veterinario, nueva_mascota):
    atrasada = nueva_mascota("Firulais", "8112345678", "Ana Martínez")
    aplicada = nueva_mascota("Rex", "8187654321", "Luis Pérez")
    futura = nueva_mascota("Luna", "8111112222", "Marta Ruiz")
    vet = veterinario["id"]
    _cita(client, atrasada, vet, "vacuna", "2026-11-10T09:00:00")   # no asistió -> atrasada
    hecha = _cita(client, aplicada, vet, "vacuna", "2026-11-10T10:00:00")
    client.post(f"/citas/{hecha}/transiciones", json={"accion": "aprobar"})
    client.post(f"/citas/{hecha}/transiciones", json={"accion": "completar"})
    _cita(client, futura, vet, "vacuna", "2026-11-15T09:00:00")      # aún no vence
    _cita(client, futura, vet, "consulta", "2026-11-10T11:00:00")   # consulta: no es vacuna
    reloj.valor = reloj.valor.replace(day=12)                         # pasan dos días

    r = client.get("/reportes/vacunas-pendientes", params={"desde": "2026-11-01", "hasta": "2026-11-30"})
    assert r.status_code == 200
    filas = r.json()
    assert len(filas) == 1
    assert filas[0]["mascota"] == "Firulais" and filas[0]["propietario"] == "Ana Martínez"
    assert filas[0]["celular"] == "8112345678" and filas[0]["dias_atraso"] == 2
    assert filas[0]["estado"] == "PROGRAMADA"

    exportado = client.get(
        "/reportes/vacunas-pendientes",
        params={"desde": "2026-11-01", "hasta": "2026-11-30", "formato": "csv"},
    )
    assert exportado.status_code == 200 and exportado.headers["content-type"].startswith("text/csv")
    lineas = exportado.text.strip().splitlines()
    assert lineas[0].startswith("mascota,especie,propietario,celular")
    assert "Firulais" in lineas[1] and "8112345678" in lineas[1]


def test_us13_cancelada_cuenta_y_rango_filtra(client, reloj, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    cita = _cita(client, mascota, veterinario["id"], "vacuna", "2026-11-10T09:00:00")
    client.post(f"/citas/{cita}/transiciones", json={"accion": "cancelar"})
    reloj.valor = reloj.valor.replace(day=12)
    en_rango = client.get("/reportes/vacunas-pendientes", params={"desde": "2026-11-10", "hasta": "2026-11-10"})
    assert [f["estado"] for f in en_rango.json()] == ["CANCELADA"]
    fuera = client.get("/reportes/vacunas-pendientes", params={"desde": "2026-12-01", "hasta": "2026-12-31"})
    assert fuera.json() == []


def test_us13_rango_invalido_422(client):
    r = client.get("/reportes/vacunas-pendientes", params={"desde": "2026-11-30", "hasta": "2026-11-01"})
    assert r.status_code == 422

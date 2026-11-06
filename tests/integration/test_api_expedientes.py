"""US-04..US-08 vía API (N-002, N-004, N-005)."""


def test_us04_celular_duplicado_devuelve_409(client):
    assert client.post("/expedientes", json={"nombre": "Ana", "celular": "8112345678"}).status_code == 201
    r = client.post("/expedientes", json={"nombre": "Otra", "celular": "81-1234-5678"})
    assert r.status_code == 409
    assert r.json()["error"] == "ClienteExistenteException"
    assert "Cliente existente" in r.json()["detalle"]


def test_celular_invalido_devuelve_422(client):
    assert client.post("/expedientes", json={"nombre": "Ana", "celular": "abc"}).status_code == 422


def test_expediente_inexistente_devuelve_404(client):
    assert client.get("/expedientes/8100000000").status_code == 404


def test_us06_varias_mascotas_mismo_propietario(client, nueva_mascota):
    nueva_mascota("Firulais")
    nueva_mascota("Michi")
    r = client.get("/expedientes/8112345678")
    assert r.status_code == 200
    assert [m["nombre"] for m in r.json()["mascotas"]] == ["Firulais", "Michi"] or len(r.json()["mascotas"]) == 2


def test_us05_fusion_consolida_historial(client, veterinario, nueva_mascota):
    original = nueva_mascota("Firulais")
    duplicada = nueva_mascota("Firu")
    nota = client.post(
        f"/mascotas/{duplicada}/notas",
        json={"veterinario_id": veterinario["id"], "diagnostico": "Revisión", "alergias": ["penicilina"]},
    )
    assert nota.status_code == 201
    r = client.post(
        "/expedientes/8112345678/mascotas/fusion", json={"origen_id": duplicada, "destino_id": original}
    )
    assert r.status_code == 200
    assert [m["id"] for m in r.json()["mascotas"]] == [original]
    historial = client.get(f"/mascotas/{original}/historial").json()
    assert len(historial["notas"]) == 1
    assert historial["mascota"]["alergias"] == ["penicilina"]
    assert client.get(f"/mascotas/{duplicada}/historial").status_code == 404


def test_us07_guardar_nota_con_receta_peso_y_alergias(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    r = client.post(
        f"/mascotas/{mascota}/notas",
        json={
            "veterinario_id": veterinario["id"],
            "diagnostico": "Otitis",
            "receta": [{"medicamento": "Amoxicilina", "dosis": "1 tableta c/12h"}],
            "peso": "12.5",
            "alergias": ["polen"],
        },
    )
    assert r.status_code == 201 and r.json()["estado"] == "BORRADOR"
    historial = client.get(f"/mascotas/{mascota}/historial").json()
    assert historial["mascota"]["peso"] == "12.50" or float(historial["mascota"]["peso"]) == 12.5
    assert historial["mascota"]["alergias"] == ["polen"]


def test_us08_firma_sella_y_bloquea_cambios(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    nota = client.post(
        f"/mascotas/{mascota}/notas", json={"veterinario_id": veterinario["id"], "diagnostico": "Otitis"}
    ).json()
    assert client.put(f"/notas/{nota['id']}", json={"notas": "gotas"}).status_code == 200
    firmada = client.post(f"/notas/{nota['id']}/firma", json={"veterinario_id": veterinario["id"]})
    assert firmada.status_code == 200
    assert firmada.json()["estado"] == "FIRMADA" and firmada.json()["firmada_por"] == veterinario["id"]
    assert len(firmada.json()["sello"]) == 64
    bloqueada = client.put(f"/notas/{nota['id']}", json={"diagnostico": "otro"})
    assert bloqueada.status_code == 409 and bloqueada.json()["error"] == "NotaFirmadaInmutable"
    assert client.post(f"/notas/{nota['id']}/firma", json={"veterinario_id": veterinario["id"]}).status_code == 409


def test_guardar_y_firmar_en_un_paso(client, veterinario, nueva_mascota):
    mascota = nueva_mascota()
    r = client.post(
        f"/mascotas/{mascota}/notas",
        json={"veterinario_id": veterinario["id"], "diagnostico": "Control", "firmar": True},
    )
    assert r.status_code == 201 and r.json()["estado"] == "FIRMADA"


def test_nota_con_veterinario_inexistente_404(client, nueva_mascota):
    mascota = nueva_mascota()
    r = client.post(f"/mascotas/{mascota}/notas", json={"veterinario_id": "zzz", "diagnostico": "x"})
    assert r.status_code == 404


def test_cu03_vincular_mascota_y_guardar_nota_en_una_transaccion(client, veterinario):
    client.post("/expedientes", json={"nombre": "Ana", "celular": "8112345678"})
    r = client.post(
        "/expedientes/8112345678/mascotas-con-nota",
        json={
            "mascota": {"nombre": "Luna", "especie": "gato"},
            "nota": {"veterinario_id": veterinario["id"], "diagnostico": "Primera revisión", "firmar": True},
        },
    )
    assert r.status_code == 201
    cuerpo = r.json()
    assert len(cuerpo["mascotas"]) == 1 and cuerpo["notas"][0]["estado"] == "FIRMADA"


def test_cu03_hace_rollback_si_la_nota_falla(client):
    client.post("/expedientes", json={"nombre": "Ana", "celular": "8112345678"})
    r = client.post(
        "/expedientes/8112345678/mascotas-con-nota",
        json={
            "mascota": {"nombre": "Luna", "especie": "gato"},
            "nota": {"veterinario_id": "no-existe", "diagnostico": "x"},
        },
    )
    assert r.status_code == 404
    assert client.get("/expedientes/8112345678").json()["mascotas"] == []  # nada quedó guardado


def test_veterinario_cedula_duplicada_409(client, veterinario):
    r = client.post("/veterinarios", json={"nombre": "Otro", "cedula": "CED-001"})
    assert r.status_code == 409
    assert len(client.get("/veterinarios").json()) == 1

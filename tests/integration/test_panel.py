"""Panel web: se sirve junto a la API sin reemplazar Swagger."""


def test_raiz_redirige_al_panel(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code in (302, 307)
    assert r.headers["location"] == "/app/"


def test_app_sin_diagonal_redirige(client):
    r = client.get("/app", follow_redirects=False)
    assert r.headers["location"] == "/app/"


def test_panel_se_sirve_con_sus_recursos(client):
    html = client.get("/app/")
    assert html.status_code == 200
    assert "VetCare 24" in html.text
    assert client.get("/app/app.js").status_code == 200
    assert client.get("/app/styles.css").status_code == 200


def test_swagger_sigue_disponible(client):
    assert client.get("/docs").status_code == 200

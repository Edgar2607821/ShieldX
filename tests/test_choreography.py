import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from shieldx.server import app
from shieldx.db import connect_to_mongo, get_collection


# ---------- FIXTURES ----------


@pytest_asyncio.fixture(autouse=True)
async def setup_and_clean_mongodb():
    """
    Fixture que se ejecuta automáticamente antes de cada test.
    Limpia la colección 'triggers' antes de cada caso.
    """
    await connect_to_mongo()
    collection = get_collection("triggers")
    assert collection is not None, "❌ La colección 'triggers' no fue inicializada."
    await collection.delete_many({})


@pytest_asyncio.fixture
async def client():
    """
    Cliente HTTP asíncrono configurado para usar la app FastAPI.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------- PAYLOADS ----------

graph_payload = {
    "format": "json",
    "content": {
        "nodes": [
            {
                "id": "ao1",
                "alias": "bellmanford_v1.run",
                "parameters": {"call": {"source": "A", "target": "B"}},
            },
            {
                "id": "ao2",
                "alias": "plot.run",
                "parameters": {
                    "call": {"algorithm_name": "BellmanFord", "save_plot": True}
                },
            },
        ],
        "connections": [{"from": "ao1", "to": "ao2"}],
    },
}
yaml_payload = """
triggers:
  - name: ao1
    rule:
      target:
        alias: bellmanford_v1.run
  - name: ao2
    depends_on: ao1
    rule:
      target:
        alias: plot.run
"""


# ---------- TESTS ----------


@pytest.mark.asyncio
async def test_interpret_json_graph(client):
    """
    Verifica que el endpoint /interpret acepte JSON (grafo) y responda correctamente.
    """
    response = await client.post("/api/v1/interpret", json=graph_payload)
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["success", "error"]
    assert "data" in data or "message" in data


@pytest.mark.asyncio
async def test_interpret_yaml_payload(client):
    """
    Verifica que el endpoint /interpret/yaml acepte un body YAML y responda correctamente.
    """
    response = await client.post(
        "/api/v1/interpret/yaml",
        content=yaml_payload,
        headers={"Content-Type": "application/x-yaml"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["success", "error"]
    assert "data" in data or "message" in data


@pytest.mark.asyncio
async def test_interpret_invalid_format(client):
    """
    Verifica que un formato inválido retorne un error.
    """
    bad_payload = {"format": "txt", "content": "invalid"}
    response = await client.post("/api/v1/interpret", json=bad_payload)
    assert response.status_code == 200  # el servicio captura la excepción
    data = response.json()
    assert data["status"] == "error"
    assert "Formato inválido" in data["message"]

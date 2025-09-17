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
    Establece conexión con la base de datos y limpia la colección 'event_types'.
    """
    await connect_to_mongo()
    collection = get_collection("event_types")
    assert collection is not None, "❌ La colección 'event_types' no fue inicializada. Revisa connect_to_mongo()."
    await collection.delete_many({})

@pytest_asyncio.fixture
async def client():
    """
    Fixture que proporciona un cliente HTTP asíncrono configurado para usar la app FastAPI.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Payload base para los tests
event_type_payload = {
    "event_type": "EncryptStart"
}

@pytest_asyncio.fixture
async def created_event_type(client):
    """
    Fixture que crea un tipo de evento válido antes de ejecutar los tests que lo requieren.
    Devuelve el ID del tipo de evento creado.
    """
    response = await client.post("/api/v1/event-types", json=event_type_payload)
    assert response.status_code == 201
    return response.json()["id"]  # ID devuelto como string con comillas

# ---------- TESTS ----------

@pytest.mark.asyncio
async def test_create_event_type(client):
    """
    Verifica que se pueda crear correctamente un tipo de evento.
    """
    response = await client.post("/api/v1/event-types", json=event_type_payload)
    assert response.status_code == 201
    assert response.json()["id"]

@pytest.mark.asyncio
async def test_list_event_types(client, created_event_type):
    """
    Verifica que se puedan listar todos los tipos de evento y que el tipo creado esté presente.
    """
    response = await client.get("/api/v1/event-types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(et["event_type"] == event_type_payload["event_type"] for et in data)

@pytest.mark.asyncio
async def test_get_event_type_by_id(client, created_event_type):
    """
    Verifica que se pueda recuperar un tipo de evento por su ID y que coincidan los datos.
    """
    response = await client.get(f"/api/v1/event-types/{created_event_type}")
    assert response.status_code == 200
    data = response.json()
    assert "_id" in data
    assert data["_id"] == created_event_type

@pytest.mark.asyncio
async def test_get_nonexistent_event_type(client):
    """
    Verifica que obtener un tipo de evento con un ID inexistente retorne 404.
    """
    response = await client.get("/api/v1/event-types/000000000000000000000000")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_event_type(client, created_event_type):
    """
    Verifica que se pueda eliminar correctamente un tipo de evento existente.
    """
    response = await client.delete(f"/api/v1/event-types/{created_event_type}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_nonexistent_event_type(client):
    """
    Verifica que eliminar un tipo de evento inexistente retorne 404.
    """
    response = await client.delete("/api/v1/event-types/000000000000000000000000")
    assert response.status_code == 404

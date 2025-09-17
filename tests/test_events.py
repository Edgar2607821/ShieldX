import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from shieldx.server import app
from shieldx.db import connect_to_mongo

# ---------- FIXTURES ----------

@pytest_asyncio.fixture(autouse=True)
async def setup_mongodb():
    """
    Fixture automática que asegura la conexión a MongoDB antes de cada prueba.
    No realiza limpieza de datos.
    """
    await connect_to_mongo()

@pytest_asyncio.fixture
async def client():
    """
    Crea un cliente HTTP asíncrono utilizando la aplicación FastAPI.
    """
    transport = ASGITransport(app=app)  # Usa app FastAPI directamente
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# ---------- TESTS ----------

# 🔸 CREATE EVENT
@pytest.mark.asyncio
async def test_create_event(client):
    await client.post("/api/v1/event-types", json={"event_type": "TestEventType"})
    """
    ✅ Verifica que se pueda crear un evento correctamente.
    """
    response = await client.post("/api/v1/events", json={
        "service_id": "service_test",
        "microservice_id": "micro_test",
        "function_id": "func_test",
        "event_type": "TestEventType",
        "payload": {"key": "value"}
    })
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Evento creado exitosamente"
    assert "id" in data


# 🔸 GET ALL EVENTS
@pytest.mark.asyncio
async def test_get_all_events(client):
    """
    ✅ Verifica que se puedan recuperar todos los eventos registrados.
    """
    response = await client.get("/api/v1/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# 🔸 GET BY SERVICE ID (Query param)
@pytest.mark.asyncio
async def test_filter_events_by_service(client):
    """
    ✅ Verifica el filtrado de eventos usando el parámetro de consulta `service_id`.
    """
    response = await client.get("/api/v1/events?service_id=service_test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(e["service_id"] == "service_test" for e in data)

# 🔸 GET BY SERVICE ID (Path param)
@pytest.mark.asyncio
async def test_get_events_by_service_path(client):
    """
    ✅ Verifica la obtención de eventos por `service_id` utilizando path param.
    """
    # Crear evento específico para esta prueba
    await client.post("/api/v1/events", json={
        "service_id": "service_test_path",
        "microservice_id": "micro_test",
        "function_id": "func_test",
        "event_type": "PathEvent",
        "payload": {}
    })

    response = await client.get("/api/v1/events/service/service_test_path")
    assert response.status_code == 200
    assert all(e["service_id"] == "service_test_path" for e in response.json())

# 🔸 GET BY MICROSERVICE ID
@pytest.mark.asyncio
async def test_get_events_by_microservice(client):
    """
    ✅ Verifica que se puedan recuperar eventos por ID de microservicio.
    """
    response = await client.get("/api/v1/events/microservice/micro_test")
    assert response.status_code == 200
    assert all(e["microservice_id"] == "micro_test" for e in response.json())

# 🔸 GET BY FUNCTION ID
@pytest.mark.asyncio
async def test_get_events_by_function(client):
    """
    ✅ Verifica que se puedan recuperar eventos por ID de función.
    """
    response = await client.get("/api/v1/events/function/func_test")
    assert response.status_code == 200
    assert all(e["function_id"] == "func_test" for e in response.json())

# 🔸 UPDATE EVENT
@pytest.mark.asyncio
async def test_update_event(client):
    await client.post("/api/v1/event-types", json={"event_type": "OriginalEvent"})

    """
    🔄 Verifica que se pueda actualizar un campo de un evento existente.
    """
    # Crear evento para actualizar
    create_response = await client.post("/api/v1/events", json={
        "service_id": "original_service",
        "microservice_id": "original_micro",
        "function_id": "original_func",
        "event_type": "OriginalEvent",
        "payload": {}
    })
    event_id = create_response.json()["id"]

    # Actualizar campo service_id
    update_response = await client.put(f"/api/v1/events/{event_id}", json={
        "service_id": "updated_service"
    })

    assert update_response.status_code == 200
    assert update_response.json()["service_id"] == "updated_service"

# 🔸 DELETE EVENT
@pytest.mark.asyncio
async def test_delete_event(client):
    await client.post("/api/v1/event-types", json={"event_type": "DeleteEvent"})

    """
    ❌ Verifica que se pueda eliminar correctamente un evento existente.
    """
    # Crear evento para eliminar
    create_response = await client.post("/api/v1/events", json={
        "service_id": "to_delete",
        "microservice_id": "micro_test",
        "function_id": "func_test",
        "event_type": "DeleteEvent",
        "payload": {}
    })
    event_id = create_response.json()["id"]

    # Eliminar evento
    delete_response = await client.delete(f"/api/v1/events/{event_id}")
    assert delete_response.status_code == 204
    

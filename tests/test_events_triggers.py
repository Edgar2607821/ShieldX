import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from shieldx.server import app
from shieldx.db import connect_to_mongo, get_collection

# ---------- FIXTURES ----------

@pytest_asyncio.fixture(autouse=True)
async def setup_collections():
    """
    Fixture automática que limpia las colecciones 'event_types', 'triggers' y 'events_triggers'
    antes de cada test para asegurar un entorno de prueba limpio.
    """
    await connect_to_mongo()
    for name in ["event_types", "triggers", "events_triggers"]:
        collection = get_collection(name)
        assert collection is not None, f"❌ La colección '{name}' no fue inicializada."
        await collection.delete_many({})

@pytest_asyncio.fixture
async def client():
    """
    Fixture que proporciona un cliente HTTP asíncrono para interactuar con la API durante los tests.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def setup_event_type_and_trigger(client):
    """
    Crea un tipo de evento y un trigger, y devuelve sus identificadores.

    Útil para pruebas que requieren ambos elementos vinculados.
    """
    # Crear un tipo de evento
    evt_resp = await client.post("/api/v1/event-types", json={"event_type": "LinkTestEvent"})
    assert evt_resp.status_code == 201
    event_type_id = evt_resp.text.strip('"')

    # Crear un trigger
    trg_resp = await client.post("/api/v1/triggers/", json={"name": "TriggerForLinking"})
    assert trg_resp.status_code == 201
    trigger_id = trg_resp.json()["id"]

    return event_type_id, trigger_id

# ---------- TESTS ----------

@pytest.mark.asyncio
async def test_link_trigger(client, setup_event_type_and_trigger):
    """
    ✅ Verifica que un trigger pueda ser vinculado correctamente a un tipo de evento.
    """
    event_type_id, trigger_id = setup_event_type_and_trigger
    response = await client.post(f"/api/v1/event-types/{event_type_id}/triggers/{trigger_id}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_list_triggers_for_event_type(client, setup_event_type_and_trigger):
    """
    ✅ Verifica que se puedan listar todos los triggers asociados a un tipo de evento.
    """
    event_type_id, trigger_id = setup_event_type_and_trigger

    # Vincula previamente para que exista la relación
    await client.post(f"/api/v1/event-types/{event_type_id}/triggers/{trigger_id}")

    response = await client.get(f"/api/v1/event-types/{event_type_id}/triggers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(link["trigger_id"] == trigger_id for link in data)

@pytest.mark.asyncio
async def test_replace_triggers_for_event_type(client, setup_event_type_and_trigger):
    """
    🔄 Verifica que al reemplazar los triggers asociados a un tipo de evento,
    solo queden los nuevos triggers indicados.
    """
    event_type_id, old_trigger_id = setup_event_type_and_trigger

    # Crear un segundo trigger
    response = await client.post("/api/v1/triggers/", json={"name": "SecondTrigger"})
    assert response.status_code == 201
    new_trigger_id = response.json()["id"]

    # Reemplazar lista de triggers con solo el nuevo
    response = await client.put(
        f"/api/v1/event-types/{event_type_id}/triggers",
        json=[new_trigger_id]
    )
    assert response.status_code == 204

    # Confirmar que solo el nuevo trigger esté asociado
    response = await client.get(f"/api/v1/event-types/{event_type_id}/triggers")
    trigger_links = response.json()
    assert all(link["trigger_id"] == new_trigger_id for link in trigger_links)

@pytest.mark.asyncio
async def test_unlink_trigger(client, setup_event_type_and_trigger):
    """
    ❌ Verifica que se pueda desvincular un trigger de un tipo de evento correctamente.
    """
    event_type_id, trigger_id = setup_event_type_and_trigger

    # Vincular el trigger antes de desvincularlo
    await client.post(f"/api/v1/event-types/{event_type_id}/triggers/{trigger_id}")

    # Desvincular trigger
    response = await client.delete(f"/api/v1/event-types/{event_type_id}/triggers/{trigger_id}")
    assert response.status_code == 204

    # Verificar que el trigger ya no esté vinculado
    response = await client.get(f"/api/v1/event-types/{event_type_id}/triggers")
    trigger_links = response.json()
    assert all(link["trigger_id"] != trigger_id for link in trigger_links)

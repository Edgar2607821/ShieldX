import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from shieldx.server import app
from shieldx.db import connect_to_mongo, get_collection

# ---------- FIXTURES ----------

@pytest_asyncio.fixture(autouse=True)
async def clear_triggers_collections():
    """
    Limpia las colecciones 'triggers' y 'triggers_triggers' antes de cada prueba.
    """
    await connect_to_mongo()
    for name in ["triggers", "triggers_triggers"]:
        collection = get_collection(name)
        assert collection is not None
        await collection.delete_many({})

@pytest_asyncio.fixture
async def client():
    """
    Proporciona un cliente HTTP asíncrono para ejecutar solicitudes contra la API FastAPI.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def create_parent_and_child_triggers(client):
    """
    Crea dos triggers: uno actuando como padre y otro como hijo.
    Devuelve ambos IDs.
    """
    # Crear trigger padre
    resp1 = await client.post("/api/v1/triggers/", json={"name": "PadreTrigger"})
    assert resp1.status_code == 201
    parent_id = resp1.json()["id"]

    # Crear trigger hijo
    resp2 = await client.post("/api/v1/triggers/", json={"name": "HijoTrigger"})
    assert resp2.status_code == 201
    child_id = resp2.json()["id"]

    return parent_id, child_id

# ---------- TESTS ----------

@pytest.mark.asyncio
async def test_link_trigger_child(client, create_parent_and_child_triggers):
    """
    ✅ Verifica que se pueda vincular un trigger hijo a un trigger padre.
    """
    parent_id, child_id = create_parent_and_child_triggers
    response = await client.post(f"/api/v1/triggers/{parent_id}/children/{child_id}")
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_list_trigger_children(client, create_parent_and_child_triggers):
    """
    📋 Verifica que se puedan listar todos los triggers hijos de un trigger padre.
    """
    parent_id, child_id = create_parent_and_child_triggers
    await client.post(f"/api/v1/triggers/{parent_id}/children/{child_id}")

    response = await client.get(f"/api/v1/triggers/{parent_id}/children")
    assert response.status_code == 200
    children = response.json()
    assert isinstance(children, list)
    assert any(c["trigger_child_id"] == child_id for c in children)

@pytest.mark.asyncio
async def test_list_trigger_parents(client, create_parent_and_child_triggers):
    """
    📋 Verifica que se puedan listar todos los triggers padres de un trigger hijo.
    """
    parent_id, child_id = create_parent_and_child_triggers
    await client.post(f"/api/v1/triggers/{parent_id}/children/{child_id}")

    response = await client.get(f"/api/v1/triggers/{child_id}/parents")
    assert response.status_code == 200
    parents = response.json()
    assert isinstance(parents, list)
    assert any(p["trigger_parent_id"] == parent_id for p in parents)

@pytest.mark.asyncio
async def test_unlink_trigger_child(client, create_parent_and_child_triggers):
    """
    ❌ Verifica que se pueda desvincular correctamente un trigger hijo de su padre.
    """
    parent_id, child_id = create_parent_and_child_triggers
    await client.post(f"/api/v1/triggers/{parent_id}/children/{child_id}")

    response = await client.delete(f"/api/v1/triggers/{parent_id}/children/{child_id}")
    assert response.status_code == 204

    # Confirmar que el trigger hijo ya no aparece como vinculado
    response = await client.get(f"/api/v1/triggers/{parent_id}/children")
    assert all(c["trigger_child_id"] != child_id for c in response.json())

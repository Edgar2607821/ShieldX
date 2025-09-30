from shieldx_client import ShieldXClient
from shieldx.models.choreography_models import ChoreographyRequest, GraphSpec
from shieldx import config
from shieldx.log.logger_config import get_logger
import yaml, time as T

L = get_logger(__name__)
SHIELDX_CLIENT_BASE_URL = config.SHIELDX_CLIENT_BASE_URL


def graph_to_triggers_yaml(graph: GraphSpec) -> str:
    triggers = []
    incoming = {}

    for c in graph.connections:
        incoming.setdefault(c.to, []).append(c.from_)

    for n in graph.nodes:
        alias = n.alias or (f"{(n.type or 'object').lower()}_v1.run")
        trig: dict = {
            "name": n.id,
            "rule": {
                "target": {"alias": alias},
                "parameters": {}
            }
        }

        if n.parameters and "init" in n.parameters:
            trig["rule"]["parameters"]["init"] = n.parameters["init"]
        if n.parameters and "call" in n.parameters:
            trig["rule"]["parameters"]["call"] = n.parameters["call"]

        deps = incoming.get(n.id, [])
        if len(deps) == 1:
            trig["depends_on"] = deps[0]
        elif len(deps) > 1:
            trig["depends_on"] = deps

        triggers.append(trig)

    return yaml.dump({"triggers": triggers}, sort_keys=False, allow_unicode=True)


class ChoreographyService:
    """
    Servicio encargado de procesar e interpretar coreografías
    utilizando ShieldXClient.
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or SHIELDX_CLIENT_BASE_URL
        self.client = ShieldXClient(base_url=self.base_url)

    async def interpret(self, request: ChoreographyRequest) -> dict:
        """
        Procesa una coreografía en YAML o JSON (grafo) y la interpreta.
        Devuelve un dict con 'status' y 'data' o 'message'.
        """
        t1 = T.time()
        try:
            L.debug({"event": "CHOREOGRAPHY.INTERPRET.RECEIVED", "request": request.model_dump()})

            # ---------- Caso JSON ----------
            if request.format == "json":
                if isinstance(request.content, dict):
                    graph = GraphSpec(**request.content)
                elif isinstance(request.content, GraphSpec):
                    graph = request.content
                else:
                    raise ValueError("El contenido JSON no es válido")

                yaml_text = graph_to_triggers_yaml(graph)
                payload = yaml_text
                L.debug({"event": "CHOREOGRAPHY.BUILD.YAML", "yaml": yaml_text})

            # ---------- Caso YAML ----------
            elif request.format == "yaml":
                if isinstance(request.content, dict):
                    payload = yaml.dump(request.content, sort_keys=False, allow_unicode=True)
                    L.debug({"event": "CHOREOGRAPHY.CONTENT.DICT", "yaml": payload})
                else:
                    payload = request.content
                    L.debug({"event": "CHOREOGRAPHY.CONTENT.STRING", "yaml": payload})

            else:
                raise ValueError("Formato inválido. Use 'json' o 'yaml'.")

            # ---------- Interpretar con ShieldXClient ----------
            L.info({"event": "CHOREOGRAPHY.CLIENT.CALL", "elapsed": T.time() - t1})
            result = await self.client.interpret_async(payload, as_text=True)

            if result.is_ok:
                data = result.unwrap()
                L.info({"event": "CHOREOGRAPHY.SUCCESS", "elapsed": T.time() - t1})
                return {"status": "success", "data": data}
            else:
                error = str(result.unwrap_err())
                L.error({"event": "CHOREOGRAPHY.CLIENT.ERROR", "error": error})
                return {"status": "error", "message": error}

        except Exception as e:
            L.error({"event": "CHOREOGRAPHY.EXCEPTION", "error": str(e)})
            return {"status": "error", "message": str(e)}

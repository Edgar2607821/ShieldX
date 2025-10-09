import networkx as nx
import time as T
from option import Result
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager
from axo.storage.services import MictlanXStorageService
from axo.errors import AxoError
from axo import Axo

from shieldx_core.dtos import GraphSpecDTO, NodeDTO
from shieldx.log.logger_config import get_logger

L = get_logger(__name__)


class ChoreographyRunServiece:
    def __init__(self):
        self.endpoint_manager = DistributedEndpointManager()
        self.storage_service = MictlanXStorageService()

    async def run(self, graph: GraphSpecDTO):
        dem = DistributedEndpointManager()
        print("GRAPH", graph.model_dump_json(indent=2))
        endpoint_ids = {
            node.rule.target.axo_endpoint_id
            for node in graph.vertices
            if node.type == "ActiveObject" and node.rule
        }

        # for eid in endpoint_ids:
            # print(eid)
        dem.add_endpoint(
            endpoint_id  = "axo-endpoint-0",
            hostname     = "localhost",
            protocol     = "tcp",
            req_res_port = 16667,
            pubsub_port  = 16666
        )
        ss = MictlanXStorageService()

        G = nx.DiGraph()
        for v in graph.vertices:
            G.add_node(v.id, data=v)
            print(v)
            print("_"*20)
        for e in graph.edges:
            G.add_edge(e.from_, e.to)

        # 2. Orden topológico de ejecución
        order = list(nx.topological_sort(G))
        results = {}
        # print(G.nodes(data=True))
        # print(order)
        # raise Exception("BOOOM!")


        with AxoContextManager.distributed(endpoint_manager=dem, storage_service=ss):
            for node_id in order:
                gnode = G.nodes[node_id]
                node: NodeDTO = gnode.get("data",None)
                if node is None:
                    continue
                L.debug({
                    "event": "CHOREOGRAPHY.NODE",
                    "node_id": node.id,
                    "node_name": node.name,
                    "node_type": node.type
                })
                # print("NO")
                if node.type == "ActiveObject":

                    res = await Axo.get_by_key(
                                                bucket_id=node.rule.target.axo_bucket_id,
                                                key=node.name
                    )
                    # print("RES", res)
                    # T.sleep(100)
                    if res.is_err:
                        raise Exception(f"No se pudo recuperar AO {node.name}")
                    
                    ao: Axo = res.unwrap()

                    # Configurar en tiempo de ejecución
                    # ao.set_endpoint_id(node.rule.target.axo_endpoint_id)
                    ao.set_endpoint_id("axo-endpoint-0")
                    if node.params.init:
                        ao.set_source_bucket_id(node.params.init.get("source_bucket_id"))
                        ao.set_sink_bucket_id(node.params.init.get("sink_bucket_id"))
                    print("AO", ao)
                    # Ejecutar método
                    method_name = node.rule.target.alias.split(".")[-1].replace("()", "")
                    call_params = node.params.call or {}
                    res: Result = getattr(ao, method_name)(**call_params)
                    print("RES2", res)
                    # T.sleep(100)

                    if res.is_ok:
                        ball_ref = res.unwrap()
                        result = await ball_ref.to_pointer(
                            self.storage_service,
                            consume=True,
                            delete_remote=False
                        ).into_bytes()
                        print("RESULT", result)
                        results[node.id] = result.unwrap()
                    else:
                        err: AxoError = res.unwrap_err()
                        results[node.id] = f"Error: {err}"

        return results
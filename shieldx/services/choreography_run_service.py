import networkx as nx
from option import Result
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager
from axo.storage.services import MictlanXStorageService
from axo.errors import AxoError
from axo import Axo

from shieldx_core.dtos import EnrichedGraphSpecDTO, NodeDTO, DeploymentInfoDTO

class ChoreographyRunServiece:
    def __init__(self):
        self.endpoint_manager = DistributedEndpointManager()
        self.storage_service = MictlanXStorageService()

    async def run(self, graph: EnrichedGraphSpecDTO):

        dem = DistributedEndpointManager()
        ss = MictlanXStorageService()
        for node in graph.vertices:
            if node.type == "ActiveObject" and node.deployment_info:
                info: DeploymentInfoDTO = node.deployment_info
                dem.add_endpoint(
                    endpoint_id=node.rule.target.axo_endpoint_id,
                    hostname=info.host,
                    protocol="tcp",
                    req_res_port=info.req_res_port,
                    pubsub_port=info.pubsub_port
                )

        

        G = nx.DiGraph()
        for v in graph.vertices:
            G.add_node(v.id, data=v)
        for e in graph.edges:
            G.add_edge(e.from_, e.to)

        # 2. Orden topológico de ejecución
        order = list(nx.topological_sort(G))
        results = {}


        with AxoContextManager.distributed(endpoint_manager=dem, storage_service=ss):
            for node_id in order:
                node: NodeDTO = G.nodes[node_id]["data"]

                if node.type == "ActiveObject":

                    res = await Axo.get_by_key(
                                                bucket_id=node.rule.target.axo_bucket_id,
                                                key=node.name
                    )
                    if not res.is_ok:
                        raise Exception(f"No se pudo recuperar AO {node.name}")
                    
                    ao: Axo = res.unwrap()

                    # Configurar en tiempo de ejecución
                    ao.set_endpoint_id(node.rule.target.axo_endpoint_id)
                    if node.params.init:
                        ao.set_source_bucket_id(node.params.init.get("source_bucket_id"))
                        ao.set_sink_bucket_id(node.params.init.get("sink_bucket_id"))

                    # Ejecutar método
                    method_name = node.rule.target.alias.split(".")[-1]
                    call_params = node.params.call or {}
                    res: Result = getattr(ao, method_name)(**call_params)

                    if res.is_ok:
                        ball_ref = res.unwrap()
                        result = await ball_ref.to_pointer(
                            self.storage_service,
                            consume=True,
                            delete_remote=False
                        ).into_bytes()
                        results[node.id] = result.unwrap()
                    else:
                        err: AxoError = res.unwrap_err()
                        results[node.id] = f"Error: {err}"

        return results
import networkx as nx
import time as T
from option import Result
from axo.contextmanager import AxoContextManager
from axo.endpoint.manager import DistributedEndpointManager
from axo.storage.services import MictlanXStorageService
from axo.errors import AxoError
from axo.core.models import BallRef
from axo import Axo
from uuid import uuid4
from typing import Dict
# from shieldx_core.dtos import  NodeDTO,EnrichedGraphSpecDTO
from shieldx.log.logger_config import get_logger
L = get_logger(__name__)
from shieldx import config
from shieldx_core.dtos import EnrichedGraphSpecDTO, NodeDTO, DeploymentInfoDTO
from shieldx.dtos import ChoreographyResultDTO

class ChoreographyRunServiece:
    def __init__(self):
        self.endpoint_manager = DistributedEndpointManager()
        self.storage_service = MictlanXStorageService()

    async def run(self, graph: EnrichedGraphSpecDTO):
        dem = DistributedEndpointManager()
        print("GRAPH", graph.model_dump_json(indent=2))

        # for eid in endpoint_ids:
            # print(eid)
        if config.SHIELDX_ENV == "dev" and config.SHIELDX_TEST:
            dem.add_endpoint(
                endpoint_id  = "axo-endpoint-0",
                hostname     = "localhost",
                protocol     = "tcp",
                req_res_port = 16667,
                pubsub_port  = 16666
            )
        ss = MictlanXStorageService()
        for node in graph.vertices:
            if node.type == "ActiveObject" and node.deployment_info:
                info: DeploymentInfoDTO = node.deployment_info
                hostname = "localhost" if  config.SHIELDX_ENV == "dev" else info.host 
                L.debug({
                    "event": "CHOREOGRAPHY.ADDING.ENDPOINT",
                    "env": config.SHIELDX_ENV,
                    "node_id": node.id,
                    "node_name": node.name,
                    "endpoint_id": node.rule.target.axo_endpoint_id,
                    "hostname": hostname,
                    "req_res_port": info.req_res_port,
                    "pubsub_port": info.pubsub_port
                })
                if not config.SHIELDX_TEST:
                    dem.add_endpoint(
                        endpoint_id  = node.rule.target.axo_endpoint_id ,
                        hostname     = hostname,
                        protocol     = "tcp" ,
                        req_res_port = info.req_res_port ,
                        pubsub_port  = info.pubsub_port
                    )

        

        G = nx.DiGraph()
        for v in graph.vertices:
            G.add_node(v.id, data=v)
        for e in graph.edges:
            G.add_edge(e.from_, e.to)

        # 2. Orden topológico de ejecución
        order = list(nx.topological_sort(G))
        results:Dict[str,ChoreographyResultDTO] = {}
        # print(G.nodes(data=True))
        # print(order)
        # raise Exception("BOOOM!")


        with AxoContextManager.distributed(endpoint_manager=dem, storage_service=ss):
            for node_id in order:
                try: 
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
                        if res.is_err:
                            raise Exception(f"No se pudo recuperar AO {node.name}")
                        
                        ao: Axo = res.unwrap()

                        # Configurar en tiempo de ejecución
                        # ao.set_endpoint_id(node.rule.target.axo_endpoint_id)
                        ao.set_endpoint_id("axo-endpoint-0")
                        if node.params.init:
                            default_source_bucket_id = uuid4().hex.replace("-","").lower()
                            default_sink_bucket_id = uuid4().hex.replace("-","").lower()

                            ao.set_source_bucket_id(node.params.init.get("source_bucket_id", default_source_bucket_id))
                            ao.set_sink_bucket_id(node.params.init.get("sink_bucket_id", default_sink_bucket_id))
                        # Ejecutar método
                        method_name = node.rule.target.alias.split(".")[-1].replace("()", "")
                        call_params = node.params.call or {}
                        res: Result = getattr(ao, method_name)(**call_params)

                        if res.is_ok:
                            ball_ref:BallRef = res.unwrap()
                            result = await ball_ref.to_pointer(
                                storage       = self.storage_service,
                                consume       = True,
                                delete_remote = False
                            ).into_bytes()
                            # print("RESULT", result)
                            results[node.id] =  ChoreographyResultDTO(
                                node_id       = node.id,
                                status        = "success",
                                output_url    = f"mictlanx://{ball_ref.bucket_id}/{ball_ref.key}",
                                error_message = ""
                            )
                            # result.unwrap()
                        else:
                            err: AxoError = res.unwrap_err()
                            results[node.id] = ChoreographyResultDTO(
                                node_id       = node.id,
                                status        = "error",
                                output_url    = "",
                                error_message = str(err)
                            )
                except Exception as e:
                    L.error({
                        "event": "CHOREOGRAPHY.NODE.ERROR",
                        "node_id": node.id,
                        "node_name": node.name,
                        "error": str(e)
                    })
                    results[node.id] = ChoreographyResultDTO(
                        node_id       = node.id,
                        status        = "error",
                        output_url    = "",
                        error_message = str(e)
                    )

        return results
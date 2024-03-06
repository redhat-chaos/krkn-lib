import base64
import json
from dataclasses import dataclass

import yaml


@dataclass(order=False)
class ScenarioTelemetry:
    """
    Scenario Telemetry collection
    """

    startTimeStamp: float
    """
    Timestamp when the Krkn run started
    """
    endTimeStamp: float
    """
    Timestamp when the Krkn run ended
    """
    scenario: str
    """
    Scenario filename
    """
    exitStatus: int
    """
    Exit Status of the Scenario Run
    """
    parametersBase64: str
    """
        Scenario configuration file base64 encoded
    """
    parameters: any

    def __init__(self, json_object: any = None):
        if json_object is not None:
            self.startTimeStamp = int(json_object.get("startTimeStamp"))
            self.endTimeStamp = int(json_object.get("endTimeStamp"))
            self.scenario = json_object.get("scenario")
            self.exitStatus = json_object.get("exitStatus")
            self.parametersBase64 = json_object.get("parametersBase64")
            self.parameters = json_object.get("parameters")

            if (
                self.parametersBase64 is not None
                and self.parametersBase64 != ""
            ):
                try:
                    yaml_params = base64.b64decode(self.parametersBase64)
                    yaml_object = yaml.safe_load(yaml_params)
                    json_string = json.dumps(yaml_object, indent=2)
                    self.parameters = json.loads(json_string)
                    if not isinstance(
                        self.parameters, dict
                    ) and not isinstance(self.parameters, list):
                        raise Exception()
                    self.parametersBase64 = ""
                except Exception as e:
                    raise Exception(
                        "invalid parameters format: {0}".format(str(e))
                    )
        else:
            # if constructor is called without params
            # property are initialized so are available
            self.startTimeStamp = 0
            self.endTimeStamp = 0
            self.scenario = ""
            self.exitStatus = 0
            self.parametersBase64 = ""
            self.parameters = {}


@dataclass(order=False)
class Taint:
    """
    Cluster Node Taint details
    """

    node_name: str = ""
    """
    node name
    """
    effect: str = ""
    """
    effect of the taint in the node
    """
    key: str = ""
    """
    Taint key
    """
    value: str = ""
    """
    Taint Value
    """


@dataclass(order=False)
class NodeInfo:
    """
    Cluster node telemetry informations
    """

    count: int = 1
    """
    number of nodes of this kind
    """

    architecture: str = ""
    """
    CPU Architecture
    """
    instance_type: str = ""
    """
    Cloud instance type (if available)
    """
    node_type: str = ""
    """
    Node Type (worker/infra/master etc.)
    """
    kernel_version: str = ""
    "Node kernel version"
    kubelet_version: str = ""
    "Kubelet Version"
    os_version: str = ""
    "Operating system version"

    def __eq__(self, other):
        if isinstance(other, NodeInfo):
            return (
                other.architecture == self.architecture
                and other.instance_type == self.instance_type
                and other.node_type == self.node_type
                and other.kernel_version == self.kernel_version
                and other.kubelet_version == self.kubelet_version
                and other.os_version == self.os_version
            )
        else:
            return False

    def __repr__(self):
        return (
            f"{self.architecture} {self.instance_type} "
            f"{self.node_type} {self.kernel_version} "
            f"{self.kubelet_version} {self.os_version}"
        )

    def __hash__(self):
        return hash(self.__repr__())


@dataclass(order=False)
class ChaosRunTelemetry:
    """
    Root object for the Telemetry Collection
    """

    scenarios: list[ScenarioTelemetry]
    """
    List of the scenarios performed during the chaos run
    """
    node_summary_infos: list[NodeInfo]
    """
    Summary of node Infos collected from the target cluster.
    It will report all the master and infra nodes and only one
    of the workers that usually are configured to have the same
    resources.
    """
    node_taints: list[Taint]
    """
    The list of node taints detected
    """

    kubernetes_objects_count: dict[str, int]
    """
    Dictionary containing the number of objects deployed
    in the cluster during the chaos run
    """
    network_plugins: list[str]
    """
    Network plugins deployed in the target cluster
    """
    total_node_count: int = 0
    """
    Number of all kind of nodes in the target cluster
    """
    cloud_infrastructure: str = "Unknown"
    """
    Cloud infrastructure (if available) of the target cluster
    """
    run_uuid: str = ""
    """
    Run uuid generated by Krkn for the Run
    """

    def __init__(self, json_object: any = None):
        self.scenarios = list[ScenarioTelemetry]()
        self.node_summary_infos = list[NodeInfo]()
        self.node_taints = list[Taint]()
        self.kubernetes_objects_count = dict[str, int]()
        self.network_plugins = ["Unknown"]
        if json_object is not None:
            scenarios = json_object.get("scenarios")
            if scenarios is None or isinstance(scenarios, list) is False:
                raise Exception("scenarios param must be a list of object")
            for scenario in scenarios:
                scenario_telemetry = ScenarioTelemetry(scenario)
                self.scenarios.append(scenario_telemetry)

            self.node_summary_infos = json_object.get("node_summary_infos")
            self.node_taints = json_object.get("node_taints")
            self.total_node_count = json_object.get("total_node_count")
            self.cloud_infrastructure = json_object.get("cloud_infrastructure")
            self.kubernetes_objects_count = json_object.get(
                "kubernetes_objects_count"
            )
            self.network_plugins = json_object.get("network_plugins")
            self.run_uuid = json_object.get("run_uuid")

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)


@dataclass(order=False)
class S3BucketObject:
    """
    Class that represents an S3 bucket object provided
    by the telemetry webservice
    """

    type: str
    """
    can be "folder" or "file"
    """

    path: str
    """
    the path or the filename wit
    """

    size: int
    """
    if it's a file represents the file size
    """

    modified: str
    """
    if it's a file represents the date when the file
    has been created/modified
    """

import os

from ruamel.yaml import YAML
from openpectus.aggregator.aggregator_server import AggregatorServer

if __name__ == "__main__":
    openapi_yml_path = os.path.join(
        os.path.dirname(__file__),
        "src",
        "openapi.yml",
    )
    with open(openapi_yml_path, "w") as f:
        yaml = YAML()
        yaml.indent(mapping=2, sequence=4, offset=2)
        yaml.dump(AggregatorServer().fastapi.openapi(), f)

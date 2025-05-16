import json
import os
import subprocess
import shutil

from openpectus.aggregator.aggregator_server import AggregatorServer

frontend_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "..",
    "frontend",
)
openapi_json_path = os.path.join(
    frontend_path,
    "openapi.json",
)

if __name__ == "__main__":
    print(f"Generate/update openapi spec file {openapi_json_path}")
    with open(openapi_json_path, "wt") as f:
        json.dump(AggregatorServer().fastapi.openapi(), f, indent=2)

    cmd = "npm run generate"
    if shutil.which("npm") is None:
        print('Generation failed. npm is not available. Please consult https://docs.openpectus.org/latest/src/Development.html#frontend-setup')
    else:
        print(f"Generating typescript interfaces using command: {cmd}")
        retval = subprocess.check_call(cmd, cwd=frontend_path, shell=True)
        if retval == 0:
            print("Generation complete")
        else:
            print(f"Generation failed with error code: {retval}")
            print('Did you remember to run "npm ci" before running this script?')

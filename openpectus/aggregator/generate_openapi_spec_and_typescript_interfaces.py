
import json
import os
import subprocess

from openpectus.aggregator.aggregator_server import AggregatorServer
from fastapi.testclient import TestClient

# check we're running from the right place
cwd = os.getcwd().lower()
if not (cwd.endswith("openpectus/aggregator") or cwd.endswith("openpectus\\aggregator")):
    raise ValueError("This script must be run from the openpectus/aggregator directory")

# update spec file
frontend_path = "../frontend"
openapi_file = os.path.join(frontend_path, "openapi.json")
print("Generate/update openapi spec file " + openapi_file)
client = TestClient(AggregatorServer().fastapi)
response = client.get("/openapi.json")
assert response.status_code == 200
with open(openapi_file, "wt") as f:
    json.dump(response.json(), f, indent=2)

# Generate typescript interfaces
print("Change working directory to " + frontend_path)
os.chdir(frontend_path)

print("Generating typescript interfaces")
cmd = "npm run generate"
print("Using command: " + cmd)
retval = subprocess.check_call(cmd, shell=True)
if retval == 0:
    print("Generation complete")
else:
    print(f"Generation failed with error code: {retval}")

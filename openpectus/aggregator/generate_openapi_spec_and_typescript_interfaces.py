
import json
import subprocess
import shutil
import os
from fastapi.testclient import TestClient
from main import app

# check we're running from the right place
cwd = os.getcwd().lower()
if not (cwd.endswith("openpectus/aggregator") or cwd.endswith("openpectus\\aggregator")):
    raise ValueError("This script must be run from the openpectus/aggregator directory")

# update spec file
openapi_file = "aggregator-openapi-spec.json"
print("Generate update openapi spec file " + openapi_file)
client = TestClient(app)
response = client.get("/openapi.json")
assert response.status_code == 200
with open(openapi_file, "wt") as f:
    json.dump(response.json(), f, indent=2)


# Generate typescript interfaces
frontend_path = "../frontend"
gen_path = "src/app/api"  # relative to frontend
spec_file = "../aggregator/aggregator-openapi-spec.json"  # relative to frontend


print("Change working directory to " + frontend_path)
os.chdir(frontend_path)

if os.path.exists(gen_path):
    print(f"Deleting existing typescript interfaces from {gen_path}")
    shutil.rmtree(gen_path)

print(f"Generating new typescript interfaces at {gen_path}")

cmd = "npx openapi --input " + spec_file + " --output " + gen_path
print("Using command: " + cmd)
retval = subprocess.check_call(cmd, shell=True)
if retval == 0:
    print("Generation complete")
else:
    print(f"Generation failed with error code: {retval}")

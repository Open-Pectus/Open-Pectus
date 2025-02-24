import hashlib
import json
import os
import unittest

from openpectus.aggregator.aggregator_server import AggregatorServer
from fastapi.testclient import TestClient

project_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
fastapi = AggregatorServer().fastapi
client = TestClient(fastapi)


class AggregatorOpenAPIApiTest(unittest.TestCase):
    def test_read_openapi_docs(self):
        response = client.get("/docs")
        self.assertEqual(200, response.status_code)

    def test_read_openapi_spec(self):
        response = client.get("/openapi.json")
        self.assertEqual(200, response.status_code)
        spec = response.json()
        self.assertEqual(fastapi.title, spec["info"]["title"])

    def test_write_openapi_spec_to_file_and_compare_with_existing(self):
        response = client.get("/openapi.json")
        self.assertEqual(200, response.status_code)
        openapi_file = os.path.join(project_path, "..", "frontend", "openapi.json")
        current_md5, updated_md5 = "", ""
        with open(openapi_file, "rb") as f:
            current_md5 = hashlib.md5(f.read()).hexdigest()

        # parsed and pretty printed
        with open(openapi_file, "wt") as f:
            json.dump(response.json(), f, indent=2)

        with open(openapi_file, "rb") as f:
            updated_md5 = hashlib.md5(f.read()).hexdigest()

        self.assertEqual(current_md5, updated_md5, f"""
The generated Aggregator API specification does not match the one stored in:
{openapi_file}

You probably forgot to update it using the update script:
(pectus) aggregator> python generate_openapi_spec_and_typescript_interfaces.py
""")


if __name__ == "__main__":
    unittest.main()

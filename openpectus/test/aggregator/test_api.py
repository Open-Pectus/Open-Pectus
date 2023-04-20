import json
import unittest

from fastapi.testclient import TestClient
from aggregator.main import app


client = TestClient(app)


class AggregatorApiTest(unittest.TestCase):
    pass


class AggregatorOpenAPIApiTest(unittest.TestCase):
    def test_read_openapi_docs(self):
        response = client.get("/docs")
        self.assertEqual(200, response.status_code)

    def test_read_openapi_spec(self):
        response = client.get("/openapi.json")
        self.assertEqual(200, response.status_code)
        spec = response.json()
        self.assertEqual(app.title, spec["info"]["title"])

    def test_write_openapi_spec_to_file(self):
        response = client.get("/openapi.json")
        self.assertEqual(200, response.status_code)
        openapi_file = "openpectus/aggregator/aggregator-openapi-spec.json"

        # raw dump
        # with open(openapi_file, "wb") as f:
        #     f.write(response.read())

        # parsed and pretty printed
        with open(openapi_file, "wt") as f:
            json.dump(response.json(), f, indent=2)


if __name__ == "__main__":
    unittest.main()

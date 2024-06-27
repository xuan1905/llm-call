import unittest
from fastapi.testclient import TestClient
from src.main import app


class BaseIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        pass

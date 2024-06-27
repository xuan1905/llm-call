from unittest.mock import patch, Mock

from src.services.invocation import get_inference
from src.services.sagemaker_models.connector import Connector
from src.services.sagemaker_models.model import Model
from tests.base_integration_test import BaseIntegrationTest


class ChatbotTest(BaseIntegrationTest):
    @patch("src.routes.monitor.check_app_health")
    def test_health(self, mock_get_data):
        mock_data = {"status": "OK"}
        mock_get_data.return_value = mock_data

        response = self.client.get("/healthcheck")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), None)

    @patch("src.services.model_use.get_inference")
    def test_gen_testcases(self, infer):
        mock_tc = [{"generated_text": "dummy testcases"}]
        body = {"inputs": "dummy inputs",
                "parameters": {"temperature": 0.1}}
        infer.return_value = mock_tc
        response = self.client.post("/inference/testcases", json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_tc)

    @patch.object(Connector, 'connect')
    def test_get_inference(self, mock_connect):
        mock_tc = [{"generated_text": "dummy testcases"}]
        mock_model = Mock(spec=Model)
        mock_connect.return_value = mock_model
        mock_model.predict.return_value = mock_tc
        body = {"inputs": "dummy inputs",
                "parameters": {"temperature": 0.1}}
        response = self.client.post("/inference/testcases", json=body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mock_tc)
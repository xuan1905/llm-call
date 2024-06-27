import boto3
import json
import yaml

from .model_config import ModelConfig


class Model:
    """Model class

    This class is used to simulate offline model prediction
    """
    def __init__(self, smr_client: boto3.client, model_config: ModelConfig, config_file: str = None):
        """Constructor

        Args:
            smr_client (boto3.client): sage maker runtime client
            model_config (ModelConfig): model config
            config_file (str, optional): path to config file. Defaults to None.
        """
        self.smr_client = smr_client
        self.model_config = model_config

        if config_file is None:
            self.default_parameters = dict()

        else:
            self.default_parameters = self._get_default_parameters(config_file)

    def _invoke(self, payload: dict) -> dict:
        """Invoke model

        Args:
            payload (dict): payload

        Returns:
            dict: result
        """
        response = self.smr_client.invoke_endpoint(
            EndpointName=self.model_config.endpoints[0]["EndpointName"],
            Body=payload,
            ContentType="application/json",
        )
        return response
    def _invoke_jumpstart(self, payload: dict) -> dict:
        """Invoke model

        Args:
            payload (dict): payload

        Returns:
            dict: result
        """
        response = self.smr_client.invoke_endpoint(
            EndpointName=self.model_config.endpoints[0]["EndpointName"],
            Body=payload,
            ContentType="application/json",
            CustomAttributes="accept_eula=true",
        )
        return response


    
    def _get_default_parameters(self, config_file: str) -> dict:
        """Get default parameters from config file (yaml)

        Args:
            config_file (str): path to config file

        Returns:
            dict: default parameters
        """
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)
        return config["default_parameters"]
    
    def predict(self, payload) -> dict:
        """Predict

        Args:
            payload (str): input string and parameters for model to generate prediction

        Raises:
            RuntimeError: if failed to predict (status code != 200)

        Returns:
            dict: prediction result
        """

        result = self._invoke(payload)

        if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise RuntimeError(f"Failed to predict: {result}")
        
        return json.loads(result["Body"].read().decode("utf-8"))

    @staticmethod
    def build_inputs_jumpstart(query_prompt: str, system_prompt: str = None) -> list:
        inputs = []
        if system_prompt:
            inputs.append({"role": "system", "content": system_prompt})
        inputs.append({"role": "user", "content": query_prompt})
        return [inputs]

    @staticmethod
    def parse_jumpstart_response(response):
        return response[0]['generation']['content']

    def predict_jumpstart(self, payload) -> dict:
        # payload = dict()
        # payload["inputs"] = inputs
        # payload["parameters"] = self.default_parameters
        # payload["parameters"].update(parameters)

        result = self._invoke_jumpstart(payload)

        if result["ResponseMetadata"]["HTTPStatusCode"] != 200:
            raise RuntimeError(f"Failed to predict: {result}")

        return json.loads(result["Body"].read().decode("utf-8"))



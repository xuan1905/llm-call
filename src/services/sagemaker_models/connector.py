
import boto3
import logging
import traceback
from datetime import datetime

from ...logging_config import LogConfig

logger = LogConfig("Connector").get_logger()

from .model_config import ModelConfig
from .model import Model


class Connector:
    """Sagemaker connector class

    This connector using for manage sagemaker models and endpoints
    """

    def __init__(self, region: str = "us-east-1", logger=logger, aws_profile: str = "default"):
        """Constructor

        Args:
            region (str, optional): region of sagemaker. Defaults to "us-east-1".
            logger (_type_, optional): logger. Defaults to logger.
        """
        session = boto3.Session(profile_name=aws_profile)
        self.sm_client = session.client("sagemaker", region_name=region)
        self.smr_client = session.client("sagemaker-runtime", region_name=region)
        self.logger = logger

    def get_models(self) -> dict[str, ModelConfig]:
        """Get all available models

        Returns:
            dict[str, ModelConfig]: dict[model_name, ModelConfig] of all available models
        """
        endpoint_configs = self.sm_client.list_endpoint_configs(
           NameContains="-",
        )

        endpoints = self.get_endpoints()

        endpoint_config_names = [
            endpoint_config["EndpointConfigName"]
            for endpoint_config in endpoint_configs["EndpointConfigs"]
        ]

        self.logger.info(f"Endpoint config names: {endpoint_config_names}")

        result = dict()
        for name in endpoint_config_names:
            detail = self.sm_client.describe_endpoint_config(EndpointConfigName=name)
            model_config = ModelConfig(detail, endpoints, self.logger)
            result[name] = model_config

        return result

    def get_endpoints(self) -> dict:
        """Get all available endpoints
        
        Returns:
            dict: dict of all available endpoints"""
        try:
            return self.sm_client.list_endpoints(SortBy="Name")["Endpoints"]
        except Exception as ex:
            raise RuntimeError(
                f"Failed to get endpoints: {ex}\nTracback: {traceback.format_exc()}"
            )

    def create_model(self, model_name: str):
        """Deploy model to endpoint

        Args:
            model_name (str): model name, must be in available models

        Raises:
            RuntimeError: model not found
            RuntimeError: model is already active
        """
        model_configs = self.get_models()
        if model_name not in model_configs:
            raise RuntimeError(f"Model {model_name} not found")

        model_config = model_configs[model_name]
        if model_config.is_active:
            raise RuntimeError(f"Model {model_name} is already active")

        model_postfix = "" # datetime.now().strftime("%Y%m%d%H%M%S")
        self._deploy_model(model_name + model_postfix, model_config.model_name)

    def _deploy_model(
        self, endpoint_name: str, model_name: str, max_wait_time: int = 600, delete_on_fail: bool = True
    ):
        """Deploy model to endpoint

        Args:
            endpoint_name (str): name of endpoint
            model_name (str): name of model
            max_wait_time (int, optional): max waiting time for model ready. Defaults to 600.
            delete_on_fail (bool, optional): delete endpoint if failed to deploy. Defaults to True.

        Raises:
            RuntimeError: endpoint failed to deploy in max_wait_time seconds
        """
        self.logger.info(f"Deploying model {model_name} to endpoint {endpoint_name}")
        self.sm_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=model_name,
            Tags=[
                {"Key": "Name", "Value": endpoint_name},
                {"Key": "ModelName", "Value": model_name},
                {"Key": "CreatedBy", "Value": "ModelConnector"},
                {"Key": "CreatedOn", "Value": datetime.now().strftime("%Y%m%d%H%M%S")},
            ],
        )

        # Wait for endpoint to be created
        self.logger.info(f"Waiting for endpoint {endpoint_name} to be created")
        start = datetime.now()
        epoch = 0
        while True:
            endpoint = self.sm_client.describe_endpoint(EndpointName=endpoint_name)
            if endpoint["EndpointStatus"] == "InService":
                logger.info(f"Endpoint {endpoint_name} is in service")
                break

            if (datetime.now() - start).seconds > max_wait_time//10 * epoch:
                self.logger.info(
                    f"Endpoint {endpoint_name} is still creating, waiting for {max_wait_time - (datetime.now() - start).seconds} seconds"
                )
                epoch += 1

            if (datetime.now() - start).seconds > max_wait_time:
                if delete_on_fail:
                    self.delete_endpoint(endpoint_name)
                raise RuntimeError(
                    f"Endpoint {endpoint_name} failed to deploy in {max_wait_time} seconds"
                )

    def delete_endpoint(self, endpoint_name: str):
        """Delete endpoint

        Args:
            endpoint_name (str): name of endpoint
        """
        self.logger.info(f"Deleting endpoint {endpoint_name}")
        self.sm_client.delete_endpoint(EndpointName=endpoint_name)

    def connect(self, model_name: str, config_file: str = None, force_deploy: bool = False) -> Model:
        """Connect to model

        Args:
            model_name (str): name of model, must be in available models
            config_file (str): path to config file
            force_deploy (bool, optional): deploy model to endpoint if not active. Defaults to False.

        Raises:
            RuntimeError: model not found
            RuntimeError: model is not active (when fore_deploy is False)

        Returns:
            _type_: _description_
        """
        models = self.get_models()
        self.logger.debug(f"Models: {models}")

        if model_name not in models:
            raise RuntimeError(f"Model {model_name} not found")
        
        model_config = models[model_name]
        if not model_config.is_active:
            if force_deploy:
                print(f"Model {model_name} is not active, deploying...")
                self._deploy_model(model_name, model_name)
            else:
                raise RuntimeError(f"Model {model_name} is not active")
            
        return Model(self.smr_client, model_config, config_file)

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class ModelConfig:
    """Model config class

    This class is used to manage model config
    """
    def __init__(self, detail: dict, endpoints: list[dict], logger=logger):
        """Constructor

        Args:
            detail (dict): detail of model config
            endpoints (list[dict]): list of current endpoints
            logger (_type_, optional): logger. Defaults to logger.
        """
        self.logger = logger
        self.model_name = detail["EndpointConfigName"]
        self.model_arn = detail["EndpointConfigArn"]
        self.product_variants = detail["ProductionVariants"]
        self.creation_time = detail["CreationTime"]

        model_endpoints = [
            endpoint
            for endpoint in endpoints
            if endpoint["EndpointName"].startswith(self.model_name)
        ]
        self.logger.debug(f"Model endpoints: {model_endpoints}")

        self.is_active = False
        self.num_endpoints = 0
        self.endpoints = []

        for endpoint in model_endpoints:
            if endpoint["EndpointStatus"] == "InService":
                self.logger.debug(f"Endpoint {endpoint['EndpointName']} is active")
                self.is_active = True
                self.num_endpoints += 1
                self.endpoints.append(endpoint)

    def __str__(self) -> str:
        return f"ModelConfig: {self.model_name} ({self.model_arn}): {str(self.num_endpoints) + ' ' if self.is_active else ''}{'Active' if self.is_active else 'Inactive'}"

    def _get_endpoint_status(self) -> dict:
        """Get endpoint status

        Returns:
            dict: endpoint status
        """
        return {
            "model_name": self.model_name,
            "model_arn": self.model_arn,
            "is_active": self.is_active,
            "num_endpoints": self.num_endpoints,
        }

    def get_name(self) -> str:
        return self.model_name

    def get_creation_time(self) -> str:
        return str(self.creation_time)
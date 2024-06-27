from enum import Enum
class ModelEndpoint:
    MODEL_NAME = "Models-LlaMa-2-70b"
    REGION_NAME = "us-east-1"
    LOCALSTACK_ENDPOINT = "http://localhost.localstack.cloud:4566"


class EndpointStatus:
    CREATING = "Creating"
    IN_SERVICE = "InService"
    NONEXISTENT = "Nonexistent"


class ModelName(str, Enum):
    llama2_7b = "Models-LlaMa-2-7b"
    llama2_13b = "Models-LlaMa-2-13b"
    llama2_13n_4096 = "Models-LlaMa-2-13b-4096"
    llama2_70b = "Models-LlaMa-2-70b"
    llama2_7b_jumpstart = "JumpStart-Model-LLaMa-2-7B"
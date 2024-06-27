from typing import Any

from src.constants import EndpointStatus
from src.logging_config import LogConfig
from src.services.invocation import create_endpoint, get_all_endpoints, del_endpoint
from src.services.sagemaker_models.connector import Connector

logger = LogConfig("endpoint_use").get_logger()


def create_model_endpoint(model_name: str, conn: Connector) -> str:
    result = create_endpoint(model_name, conn)
    logger.info(f"Successfully deployed model {model_name}. Result: {result}")
    return result


def retrieve_available_models(conn: Connector) -> list[dict[str, Any]]:
    response = get_all_endpoints(conn)
    result = [{"name": item["EndpointName"], "status": item["EndpointStatus"]}
              for item in response]
    return result


def delete_endpoint(endpoint_name: str, conn: Connector) -> str:
    return del_endpoint(endpoint_name, conn)


def retrieve_endpoint_status(incoming_endpoints: list[str], connector: Connector) -> list[dict]:
    response = get_all_endpoints(connector)
    # Response looks like this
    # [
    #     {
    #         "EndpointName": "jumpstart-sklearn-model-test",
    #         "EndpointArn": "arn:aws:sagemaker:us-east-1:382700730806:endpoint/jumpstart-sklearn-model-test",
    #         "CreationTime": "2023-08-17T13:20:00.189000+07:00",
    #         "LastModifiedTime": "2023-08-17T13:22:14.984000+07:00",
    #         "EndpointStatus": "InService"
    #     }
    # ]
    available_names = [item["EndpointName"] for item in response]
    common_endpoints = set(incoming_endpoints).intersection(available_names)
    result = [{"name": item["EndpointName"], "status": item["EndpointStatus"]}
              for item in response if item["EndpointName"] in common_endpoints]

    only_incoming_endpoints = set(incoming_endpoints).difference(available_names)
    na_result = [{"name": n, "status": EndpointStatus.NONEXISTENT} for n in only_incoming_endpoints]

    final_result = result + na_result
    return final_result

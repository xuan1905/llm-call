import asyncio
import json
import os
import time
import traceback
from functools import lru_cache
from fastapi import HTTPException, WebSocket
from pydantic.main import BaseModel

from src.constants import ModelEndpoint, EndpointStatus
from src.logging_config import LogConfig
from src.services.endpoint_use import retrieve_endpoint_status
from src.services.invocation import create_endpoint
from src.services.sagemaker_models.connector import Connector


logger = LogConfig("utils").get_logger()


@lru_cache()
def init_connector():
    deploy_environment = os.environ.get("DEPLOY_ENV", "local")
    aws_profile = "default"

    connector = None
    if deploy_environment in ["local"]:
        aws_profile = "create"
    elif deploy_environment == "prod":
        aws_profile = None
    logger.info(f"Creating AWS connection with profile {aws_profile}")
    try:
        connector = Connector(region=ModelEndpoint.REGION_NAME,
                              aws_profile=aws_profile)
    except Exception as ex:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=ex.args[0])
    return connector


def read_file(filepath):
    with open(filepath) as f:
        return f.read()


def make_prompt(prompt, input_api, input_testcase=None):
    if input_testcase:
        return prompt.replace('{input_api}', input_api).replace('{input_test}', input_testcase)
    return prompt.format(input_api=input_api)


def remove_field(model: BaseModel, field_name: str) -> None:
    if field_name in model.__fields__:
        delattr(model, field_name)


def create_endpoint_sync(name: str, connector: Connector, ws: WebSocket):
    create_endpoint(name, connector)


async def async_retrieve_status(name, connector, ws: WebSocket):
    poll_interval = 60  # seconds
    max_probes = 2
    result = retrieve_endpoint_status(incoming_endpoints=[name], connector=connector)
    status = result[0]["status"]
    logger.debug(f"Result async: {result}")

    i = 0
    while status in [EndpointStatus.CREATING, EndpointStatus.NONEXISTENT]:
        logger.info(f'Model creation status in loop of {name}: {status}')
        status_result_inner = retrieve_endpoint_status(incoming_endpoints=[name], connector=connector)
        status = status_result_inner[0]["status"]
        if (i == max_probes) & (status == EndpointStatus.NONEXISTENT):
            await ws.close()
        await ws.send_json(status_result_inner)
        time.sleep(poll_interval)  # blocking operation
        i += 1

    logger.info(f'Final model creation status of {name}: {status}')
    await ws.send_json({"name": name, "status": EndpointStatus.IN_SERVICE})
    return result

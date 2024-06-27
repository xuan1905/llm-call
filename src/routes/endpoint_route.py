import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Body

from ..models.request import ModelInfo
from ..models.response import ModelStatus
from ..services.endpoint_use import create_model_endpoint, retrieve_available_models, delete_endpoint, \
    retrieve_endpoint_status
from ..services.sagemaker_models.connector import Connector
from ..utilities.preparation import init_connector


router = APIRouter(prefix="/model")


@router.post("/create-endpoint", tags=["Deploy model endpoint"])
async def build_model_endpoint(model_info: ModelInfo, conn: Annotated[Connector, Depends(init_connector)]) -> str:
    response = create_model_endpoint(model_info.endpoint_name, conn)
    return response


@router.get("/deployed-endpoints", tags=["Get all deployed models"], response_model=list[ModelStatus])
async def get_deployed_models(conn: Annotated[Connector, Depends(init_connector)]):
    response = retrieve_available_models(conn)
    return response


@router.post("/status", tags=["Get model status"], response_model=list[ModelStatus])
async def get_model_status(endpoints: Annotated[list[str], Body(title="List of model endpoint names")],
                           conn: Annotated[Connector, Depends(init_connector)]) -> Any:
    response = retrieve_endpoint_status(endpoints, conn)
    return response


@router.delete("/remove-endpoint", tags=["Remove a deployed model"])
async def remove_deployed_endpoint(endpoint: ModelInfo, conn: Annotated[Connector, Depends(init_connector)]) -> str:
    response = delete_endpoint(endpoint.endpoint_name, conn)
    return response

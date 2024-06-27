import os
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from ..constants import ModelEndpoint, ModelName
from ..models.request import StepInferencePayload, SpecInferencePayload
from ..services.model_use import generate_testcases, generate_step_definition, generate_chatgpt_testcases, \
    generate_testcases_jumpstart, generate_step_definition_jumpstart
from ..services.sagemaker_models.connector import Connector
from ..utilities.preparation import init_connector


router = APIRouter(prefix="/inference")


@router.post("/testcases", tags=["Test cases"])
async def gen_tests(spec: SpecInferencePayload, conn: Annotated[Connector, Depends(init_connector)]):
    response = generate_testcases_jumpstart(spec, conn) #generate_testcases(spec, conn)
    return response


@router.post("/step-definition", tags=["Gherkin step definition"])
async def gen_steps(test: StepInferencePayload, conn: Annotated[Connector, Depends(init_connector)]):
    response = generate_step_definition_jumpstart(test, conn) #generate_step_definition(test, conn)
    return response

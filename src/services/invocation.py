import os
import traceback

from fastapi import HTTPException
from langchain.chat_models import ChatOpenAI

from .sagemaker_models.connector import Connector

os.environ["OPENAI_API_KEY"] = ""

def get_inference(payload: str, model_name: str, connector: Connector):
    result = None
    try:
        model = connector.connect(model_name=model_name,
                                  config_file=None,
                                  force_deploy=False)
        result = model.predict(payload)
    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=e.args[0])
    return result


def get_inference_jumpstart(payload: str, model_name: str, connector: Connector):
    result = None
    try:
        model = connector.connect(model_name=model_name,
                                  config_file=None,
                                  force_deploy=False)
        result = model.predict_jumpstart(payload)
    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=e.args[0])
    return result


def openai_predict(temp, inputs):
    llm = ChatOpenAI(temperature=temp)
    return llm.predict(inputs)


def create_endpoint(model_name: str, connector: Connector) -> str:
    result = None
    try:
        connector.create_model(model_name=model_name)
        result = f"Model {model_name} has been successfully deployed."
    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=e.args[0])
    return result


def get_all_endpoints(connector: Connector) -> dict:
    endpoints = None
    try:
        endpoints = connector.get_endpoints()
    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=e.args[0])
    return endpoints


def del_endpoint(endpoint_name: str, connector: Connector) -> str:
    try:
        connector.delete_endpoint(endpoint_name)
    except RuntimeError as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=e.args[0])
    return f"Endpoint {endpoint_name} has been removed"


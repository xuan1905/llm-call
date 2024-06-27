from pydantic import BaseModel
from typing import List, Dict
from src.constants import ModelEndpoint, ModelName


class ModelInfo(BaseModel):
    endpoint_name: str


class SpecParameters(BaseModel):
    do_sample: bool = True
    max_new_tokens: int = 2048
    repetition_penalty: float = 1.03
    return_full_text: bool = False
    seed: int = 42
    temperature: float = 0.5
    top_k: int = 50
    top_p: float = 0.95
    typical_p: float = 0.95


class SpecInferencePayload(BaseModel):
    inputs: str | List[List[Dict[str, str]]]
    parameters: SpecParameters | None
    model: str | None = ModelName.llama2_7b_jumpstart


class StepParameters(BaseModel):
    do_sample: bool = True
    max_new_tokens: int = 2048
    repetition_penalty: float = 1.03
    return_full_text: bool = False
    seed: int = 42
    temperature: float = 0.1
    top_k: int = 50
    top_p: float = 0.95
    typical_p: float = 0.95


class StepInferenceInput(BaseModel):
    spec: str
    tc: str


class StepInferencePayload(BaseModel):
    inputs: StepInferenceInput | List[List[Dict[str, str]]]
    parameters: StepParameters | None
    model: str | None = ModelName.llama2_7b_jumpstart


class StepInferenceMlRequest(BaseModel):
    inputs: str
    parameters: StepParameters

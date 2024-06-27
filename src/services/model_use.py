import json

from .sagemaker_models.connector import Connector
from ..logging_config import LogConfig
from ..models.request import SpecInferencePayload, StepInferencePayload, StepInferenceMlRequest
from ..services.invocation import get_inference, openai_predict, get_inference_jumpstart
from fastapi.encoders import jsonable_encoder

from ..utilities.preparation import read_file, make_prompt, remove_field

logger = LogConfig("model_use").get_logger()


def prompt_llma_step_definition(api_spec: str, testcase: str):
    prompt = read_file("src/prompts/llama_prompts/prompt_bdd.txt")
    prompt = make_prompt(prompt=prompt, input_api=api_spec, input_testcase=testcase)
    return prompt


def prompt_llama_testcases(api_spec: str):
    prompt = read_file("src/prompts/llama_prompts/prompt_test_plan.txt")
    prompt = make_prompt(prompt=prompt, input_api=api_spec, input_testcase=None)
    return prompt


def prompt_chatgpt_testcases(api_spec: str):
    prompt = read_file("src/prompts/chatgpt_prompts/prompt_test_openai.txt")
    prompt = make_prompt(prompt=prompt, input_api=api_spec, input_testcase=None)
    return prompt


# TODO: put the methods in a callable class that receives Connector as an arg and is used in chatbot_route.py
def generate_testcases(specification: SpecInferencePayload, connector: Connector):
    specification.inputs = prompt_llama_testcases(specification.inputs)
    payload = jsonable_encoder(specification)
    payload = json.dumps(payload)
    model = specification.model
    print(f"case payload: {payload}")
    logger.debug(f"new payload: {payload}")
    result = get_inference(payload, model, connector)

    return result


def generate_chatgpt_testcases(specification: SpecInferencePayload, connector: Connector):
    inputs = prompt_chatgpt_testcases(specification.inputs)
    temperature = specification.parameters.temperature
    logger.info(f"OpenAI request: {inputs} and temperature {temperature}")
    result = openai_predict(temp=temperature, inputs=inputs)

    return result


def generate_step_definition(test_plan: StepInferencePayload, connector: Connector):
    model = test_plan.model
    spec_input = test_plan.inputs.spec
    testcase_input = test_plan.inputs.tc
    final_inputs = prompt_llma_step_definition(api_spec=spec_input, testcase=testcase_input)
    inputs_with_prompts = StepInferenceMlRequest(inputs=final_inputs, parameters=test_plan.parameters)

    payload = jsonable_encoder(inputs_with_prompts)
    payload = json.dumps(payload)
    print(f"step payload: {payload}")
    logger.info(f"payload: {payload}")
    result = get_inference(payload, model, connector)

    return result

#######################################
#######        JUMPSTART         ######
#######################################


def build_inputs_jumpstart(query_prompt: str, system_prompt: str = None) -> list:
    inputs = []
    if system_prompt:
        inputs.append({"role": "system", "content": system_prompt})
    inputs.append({"role": "user", "content": query_prompt})
    return [inputs]


def parse_jumpstart_response(response):
    return response[0]['generation']['content']


def generate_testcases_jumpstart(specification: SpecInferencePayload, connector: Connector):
    model = specification.model
    remove_field(specification, "model")
    api_spec = specification.inputs
    sys_prompt = read_file("src/prompts/llama_prompts/prompt_testcase_sys.txt")
    query_prompt = read_file("src/prompts/llama_prompts/prompt_testcase_query.txt")
    query_prompt = make_prompt(prompt=query_prompt, input_api=api_spec, input_testcase=None)
    specification.inputs = build_inputs_jumpstart(query_prompt=query_prompt, system_prompt=sys_prompt)
    payload = jsonable_encoder(specification)
    payload = json.dumps(payload)
    logger.info(f"Jumpstart testcase payload: {payload}")
    result = get_inference_jumpstart(payload, model, connector)
    result = parse_jumpstart_response(result)
    return result


def generate_step_definition_jumpstart(test_plan: StepInferencePayload, connector: Connector):
    model = test_plan.model
    remove_field(test_plan, "model")
    spec_input = test_plan.inputs.spec
    testcase_input = test_plan.inputs.tc
    sys_prompt = read_file("src/prompts/llama_prompts/prompt_bdd_sys.txt")
    query_prompt = read_file("src/prompts/llama_prompts/prompt_bdd_query.txt")
    query_prompt = make_prompt(prompt=query_prompt, input_api=spec_input, input_testcase=testcase_input)
    test_plan.inputs = build_inputs_jumpstart(query_prompt=query_prompt, system_prompt=sys_prompt)

    payload = jsonable_encoder(test_plan)
    payload = json.dumps(payload)
    logger.info(f"BDD Jumpstart payload: {payload}")
    result = get_inference_jumpstart(payload, model, connector)
    result = parse_jumpstart_response(result)
    return result

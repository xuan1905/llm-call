import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Annotated

from fastapi import WebSocket, APIRouter, Depends

from src.logging_config import LogConfig
from src.services.sagemaker_models.connector import Connector
from src.utilities.preparation import init_connector, create_endpoint_sync, async_retrieve_status

router = APIRouter(prefix="/ws/model")

executor = ThreadPoolExecutor()

logger = LogConfig("utils").get_logger()


@router.websocket("/create-endpoint")
async def make_db(*, websocket: WebSocket, conn: Annotated[Connector, Depends(init_connector)]):
    await websocket.accept()
    received_data = await websocket.receive_json()
    model_name = received_data["endpoint_name"]

    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, create_endpoint_sync, model_name, conn, websocket)
    await async_retrieve_status(model_name, conn, websocket)
    await websocket.close()



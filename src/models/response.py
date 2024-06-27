from pydantic import BaseModel
from typing import List, Dict


class ModelStatus(BaseModel):
    name: str
    status: str



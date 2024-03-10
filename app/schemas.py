from pydantic import BaseModel
from typing import Literal

class Transacao(BaseModel):
    valor: int
    tipo: Literal["c", "d"]
    descricao : str

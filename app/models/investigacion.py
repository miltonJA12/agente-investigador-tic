from typing import Literal
from pydantic import BaseModel, Field


class SolicitudInvestigacion(BaseModel):
    pregunta: str = Field(min_length=1)
    modo: Literal["rapido", "comparativo", "profundo"] = "rapido"
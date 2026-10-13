import os
import hmac
from pathlib import Path

from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.investigacion import SolicitudInvestigacion
from app.services.investigador_service import InvestigadorService


app = FastAPI(
    title="Radar TIC",
    description="Agente investigador con inteligencia artificial y Web Search",
    version="1.0.0"
)

RAIZ = Path(__file__).resolve().parents[1]


@app.get("/")
def inicio():
    return FileResponse(
        RAIZ / "templates" / "index.html"
    )


@app.get("/api/estado")
def estado():
    return {
        "estado": "activo",
        "agente": "Radar TIC",
        "backend": "FastAPI",
        "investigacion_habilitada": (
            os.getenv("ENABLE_PAID_RESEARCH", "false").lower() == "true"
        )
    }


@app.post("/api/investigar")
def investigar(
    solicitud: SolicitudInvestigacion,
    x_research_token: str | None = Header(default=None)
):

    # Protección 1: desactivar investigaciones de pago
    habilitado = (
        os.getenv("ENABLE_PAID_RESEARCH", "false").lower() == "true"
    )

    if not habilitado:
        raise HTTPException(
            status_code=403,
            detail="Las investigaciones están desactivadas en esta demostración."
        )

    # Protección 2: exigir autorización privada
    token_servidor = os.getenv("RESEARCH_ACCESS_TOKEN")

    if not token_servidor:
        raise HTTPException(
            status_code=503,
            detail="El acceso a investigaciones no está configurado."
        )

    if not x_research_token or not hmac.compare_digest(
        x_research_token,
        token_servidor
    ):
        raise HTTPException(
            status_code=401,
            detail="No autorizado para realizar investigaciones."
        )

    # Prueba temporal de autenticación
    if solicitud.pregunta == "__TEST_AUTH__":
         return {
        "autorizado": True,
        "mensaje": "Token privado aceptado correctamente"
    }

    # Ejecutar la investigación
    try:
        servicio = InvestigadorService()

        resultado = servicio.investigar(
            pregunta=solicitud.pregunta,
            modo=solicitud.modo,
            usar_web=True
        )

        return resultado

    except Exception as error:
        print(
            "Error de investigación:",
            type(error).__name__
        )

        raise HTTPException(
            status_code=500,
            detail="No se pudo completar la investigación."
        )


app.mount(
    "/assets",
    StaticFiles(directory=RAIZ / "assets"),
    name="assets"
)
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.investigacion import SolicitudInvestigacion
from app.services.investigador_service import InvestigadorService

app = FastAPI(title="Radar TIC")

RAIZ = Path(__file__).resolve().parents[1]


@app.get("/")
def inicio():
    return FileResponse(RAIZ / "templates" / "index.html")


@app.get("/api/estado")
def estado():
    return {
        "estado": "activo",
        "agente": "Radar TIC",
        "backend": "FastAPI"
    }


@app.post("/api/investigar")
def investigar(solicitud: SolicitudInvestigacion):

    try:
        servicio = InvestigadorService()

        resultado = servicio.investigar(
            pregunta=solicitud.pregunta,
            modo=solicitud.modo,
            usar_web=True
        )

        return resultado

    except Exception as error:
        print("Error de investigación:", type(error).__name__)

        raise HTTPException(
            status_code=500,
            detail="No se pudo completar la investigación. Revisa la terminal."
        )


app.mount(
    "/assets",
    StaticFiles(directory=RAIZ / "assets"),
    name="assets"
)
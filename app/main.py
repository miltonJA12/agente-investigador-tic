
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models.investigacion import SolicitudInvestigacion
from app.services.investigador_service import InvestigadorService


# ======================================================
# CONFIGURACIÓN GENERAL DE RADAR TIC
# ======================================================

app = FastAPI(
    title="Radar TIC",
    description=(
        "Agente investigador con inteligencia artificial "
        "y Web Search"
    ),
    version="1.0.0"
)

RAIZ = Path(__file__).resolve().parents[1]


# ======================================================
# PÁGINA PRINCIPAL
# ======================================================

@app.get("/")
def inicio():
    return FileResponse(
        RAIZ / "templates" / "index.html"
    )


# ======================================================
# ESTADO DEL AGENTE
# ======================================================

@app.get("/api/estado")
def estado():

    habilitado = (
        os.getenv(
            "ENABLE_PAID_RESEARCH",
            "false"
        ).lower() == "true"
    )

    return {
        "estado": "activo",
        "agente": "Radar TIC",
        "backend": "FastAPI",
        "investigacion_habilitada": habilitado
    }


# ======================================================
# INVESTIGACIÓN PÚBLICA
# ======================================================

@app.post("/api/investigar")
def investigar(solicitud: SolicitudInvestigacion):

    # Permite detener las investigaciones desde Vercel
    habilitado = (
        os.getenv(
            "ENABLE_PAID_RESEARCH",
            "false"
        ).lower() == "true"
    )

    if not habilitado:
        raise HTTPException(
            status_code=503,
            detail=(
                "Las investigaciones están "
                "temporalmente desactivadas."
            )
        )

    # Validar la pregunta recibida
    pregunta = solicitud.pregunta.strip()

    if len(pregunta) < 5:
        raise HTTPException(
            status_code=400,
            detail=(
                "La pregunta debe contener "
                "al menos 5 caracteres."
            )
        )

    if len(pregunta) > 300:
        raise HTTPException(
            status_code=400,
            detail=(
                "La pregunta no puede superar "
                "los 300 caracteres."
            )
        )

    # Ejecutar únicamente el modo rápido
    # para reducir el costo por investigación
    try:
        servicio = InvestigadorService()

        resultado = servicio.investigar(
            pregunta=pregunta,
            modo="rapido",
            usar_web=True
        )

        return resultado

    except Exception as error:

        # Registrar detalles en Vercel sin mostrar
        # información interna al visitante
        print(
            "RADAR TIC - Tipo de error:",
            type(error).__name__,
            flush=True
        )

        print(
            "RADAR TIC - HTTP externo:",
            getattr(error, "status_code", None),
            flush=True
        )

        print(
            "RADAR TIC - Código externo:",
            getattr(error, "code", None),
            flush=True
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo completar la investigación. "
                "Inténtalo más tarde."
            )
        )


# ======================================================
# ARCHIVOS ESTÁTICOS
# ======================================================

app.mount(
    "/assets",
    StaticFiles(
        directory=RAIZ / "assets"
    ),
    name="assets"
)

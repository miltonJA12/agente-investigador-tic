
from openai import OpenAI

from app.core.config import OPENAI_API_KEY, OPENAI_MODEL


class InvestigadorService:

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError(
                "Falta configurar OPENAI_API_KEY en el servidor."
            )

        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            timeout=180.0,
            max_retries=0
        )

    def investigar(
        self,
        pregunta: str,
        modo: str = "rapido",
        usar_web: bool = True
    ):

        instrucciones = """
Eres Radar TIC, un agente investigador especializado en
Tecnologías de la Información y Comunicación.

Responde siempre en español, con información verificable.

Adapta la profundidad del análisis al modo de investigación
solicitado.

REGLAS:
- No inventes información ni fuentes.
- Prioriza documentación oficial, universidades y organismos
  especializados.
- Utiliza fuentes actuales cuando exista acceso a Web Search.
- Distingue hechos comprobados, opiniones y tendencias.
- No inventes URLs.
- Conserva exactamente los encabezados solicitados.
- Devuelve el reporte en Markdown.

FORMATO OBLIGATORIO:

# Título de la investigación

## 1. Pregunta de investigación
Explica claramente la pregunta investigada.

## 2. Plan de investigación
- Identificar el problema.
- Consultar fuentes relevantes.
- Evaluar la evidencia.
- Comparar los hallazgos.
- Elaborar conclusiones.

## 3. Hallazgos principales

### Hallazgo 1
**Nombre:** Nombre del hallazgo
**Descripción:** Explicación detallada.
**Fuente:** Nombre de la fuente consultada
**URL:** URL real verificable

### Hallazgo 2
**Nombre:** Nombre del hallazgo
**Descripción:** Explicación detallada.
**Fuente:** Nombre de la fuente consultada
**URL:** URL real verificable

### Hallazgo 3
**Nombre:** Nombre del hallazgo
**Descripción:** Explicación detallada.
**Fuente:** Nombre de la fuente consultada
**URL:** URL real verificable

Incluye únicamente hallazgos respaldados por evidencia.
Si no tienes una URL verificable, indica que no está disponible.

## 4. Comparación de información

| Elemento | Descripción | Ventajas | Limitaciones | Escenarios recomendados |
|---|---|---|---|---|
| Elemento 1 | Descripción | Ventajas | Limitaciones | Escenario |
| Elemento 2 | Descripción | Ventajas | Limitaciones | Escenario |
| Elemento 3 | Descripción | Ventajas | Limitaciones | Escenario |

Sustituye los ejemplos por información real.

## 5. Coincidencias y diferencias entre fuentes

### Coincidencias
- Coincidencia identificada.
- Otra coincidencia identificada.

### Diferencias
- Diferencia identificada.
- Otra diferencia identificada.

## 6. Tendencias identificadas
- Tendencia identificada.
- Segunda tendencia identificada.
- Tercera tendencia identificada.

## 7. Conclusiones
Presenta las conclusiones principales fundamentadas
en la evidencia encontrada.

IMPORTANTE:
No cambies los nombres ni la numeración de las secciones.
"""

        modos = {
            "rapido": (
                "Realiza una investigación breve y clara."
            ),
            "comparativo": (
                "Compara perspectivas, ventajas, "
                "desventajas y diferencias."
            ),
            "profundo": (
                "Realiza una investigación detallada "
                "con análisis y evidencias."
            )
        }

        instrucciones += "\n" + modos.get(
            modo,
            modos["rapido"]
        )

        parametros = {
            "model": OPENAI_MODEL,
            "instructions": instrucciones,
            "input": pregunta,
            "max_output_tokens": 2500
        }

        if usar_web:
            parametros["tools"] = [
                {
                    "type": "web_search",
                    "search_context_size": "low"
                }
            ]

        # 1. Mostrar el modelo configurado
        print(
            "RADAR TIC - Modelo utilizado:",
            OPENAI_MODEL,
            flush=True
        )

        # 2. Consultar OpenAI
        respuesta = self.client.responses.create(
            **parametros
        )

        # 3. Diagnosticar la respuesta
        print(
            "RADAR TIC - Estado:",
            respuesta.status,
            flush=True
        )

        print(
            "RADAR TIC - Motivo incompleto:",
            respuesta.incomplete_details,
            flush=True
        )

        if respuesta.usage:
            print(
                "RADAR TIC - Uso de tokens:",
                respuesta.usage.model_dump(),
                flush=True
            )

        # 4. Comprobar que existe texto
        reporte = (respuesta.output_text or "").strip()

        if not reporte:
            raise RuntimeError(
                "OpenAI no generó texto. "
                f"Estado: {respuesta.status}. "
                f"Motivo: {respuesta.incomplete_details}"
            )

        # 5. Extraer fuentes consultadas
        fuentes = []
        urls_vistas = set()

        for item in respuesta.output:

            if getattr(item, "type", None) != "message":
                continue

            for contenido in getattr(
                item,
                "content",
                []
            ):

                for anotacion in getattr(
                    contenido,
                    "annotations",
                    []
                ):

                    if getattr(
                        anotacion,
                        "type",
                        None
                    ) == "url_citation":

                        url = getattr(
                            anotacion,
                            "url",
                            None
                        )

                        if url and url not in urls_vistas:

                            urls_vistas.add(url)

                            fuentes.append({
                                "titulo": getattr(
                                    anotacion,
                                    "title",
                                    url
                                ),
                                "url": url
                            })

        # 6. Devolver el reporte completo
        return {
            "pregunta": pregunta,
            "modo": modo,
            "reporte": reporte,
            "fuentes": fuentes,
            "total_fuentes": len(fuentes)
        }

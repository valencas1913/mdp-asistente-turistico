"""
ai_service.py
Integración con Groq (API compatible con OpenAI, con capa gratuita sin tarjeta)
para generar itinerarios turísticos personalizados usando como contexto:
  - el clima actual (OpenWeatherMap)
  - las actividades reales de la base de datos
  - lo que escribe el usuario en lenguaje natural

Se prueba primero GROQ_MODEL y, si falla (límite de uso, modelo retirado, error
del servidor), se prueba GROQ_MODEL_FALLBACK. Si los dos fallan, o si no hay
GROQ_API_KEY, se devuelve un itinerario de demostración armado localmente.
"""

import os
import time
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = os.environ.get(
    "GROQ_URL", "https://api.groq.com/openai/v1/chat/completions"
)
# Groq retiró los modelos Llama 3.x de la capa gratuita (16/08/2026).
# Los nombres son configurables por variable de entorno por si cambian de nuevo.
GROQ_MODEL = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")
GROQ_MODEL_FALLBACK = os.environ.get("GROQ_MODEL_FALLBACK", "openai/gpt-oss-120b")

SYSTEM_PROMPT = (
    "Sos el Asistente Turístico y Cultural Autónomo de Mar del Plata, Argentina. "
    "Tu trabajo es armar itinerarios breves, cálidos y realistas, usando SOLO las "
    "actividades de la lista de contexto que te paso (no inventes lugares que no "
    "estén ahí). Tené en cuenta el clima actual para priorizar actividades bajo "
    "techo si llueve o hace mucho viento, y actividades al aire libre/playa si "
    "está soleado. Respondé en español rioplatense, en formato de lista breve "
    "con 3 a 5 paradas, indicando horario sugerido y una frase de por qué la "
    "elegiste. Cerrá con un tip práctico."
)


def _construir_contexto(clima: dict, actividades: list) -> str:
    lista_actividades = "\n".join(
        f"- {a['nombre']} ({a['categoria_nombre']}, zona {a['zona']}): "
        f"{a['descripcion']} | horario: {a['horario']} | clima ideal: {a['recomendado_clima']}"
        for a in actividades
    )
    return (
        f"Clima actual en Mar del Plata: {clima.get('temperatura')}°C, "
        f"condición general: {clima.get('condicion')}, "
        f"descripción: {clima.get('descripcion')}.\n\n"
        f"Actividades disponibles en la base de datos:\n{lista_actividades}"
    )


def _llamar_groq(modelo: str, mensaje_usuario: str, contexto: str) -> str:
    cuerpo = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"CONTEXTO:\n{contexto}\n\nPEDIDO DEL USUARIO: {mensaje_usuario}",
            },
        ],
        # los modelos "gpt-oss" razonan antes de responder y ese razonamiento
        # cuenta dentro del límite: hay que dejar margen para no cortar la respuesta
        "max_completion_tokens": 2048,
        "temperature": 0.7,
    }
    if modelo.startswith("openai/gpt-oss"):
        cuerpo["reasoning_effort"] = "low"

    resp = requests.post(
        GROQ_URL,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json=cuerpo,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return (data["choices"][0]["message"].get("content") or "").strip()


def generar_itinerario(mensaje_usuario: str, clima: dict, actividades: list) -> dict:
    """Devuelve {'respuesta': texto, 'fuente': 'groq' | 'demo'} (+ 'error' si falló)."""
    if not GROQ_API_KEY:
        return {
            "respuesta": _itinerario_demo(mensaje_usuario, clima, actividades),
            "fuente": "demo",
            "error": "Falta GROQ_API_KEY en el servidor",
        }

    contexto = _construir_contexto(clima, actividades)
    modelos = [GROQ_MODEL]
    if GROQ_MODEL_FALLBACK and GROQ_MODEL_FALLBACK != GROQ_MODEL:
        modelos.append(GROQ_MODEL_FALLBACK)

    errores = []
    for i, modelo in enumerate(modelos):
        try:
            texto = _llamar_groq(modelo, mensaje_usuario, contexto)
            if texto:
                return {"respuesta": texto, "fuente": "groq", "modelo": modelo}
            motivo = "respuesta vacía"
        except requests.HTTPError as e:
            cuerpo = e.response.text[:300] if e.response is not None else ""
            codigo = e.response.status_code if e.response is not None else "?"
            motivo = f"HTTP {codigo}: {cuerpo}"
        except requests.RequestException as e:
            motivo = str(e)
        except (KeyError, IndexError, ValueError) as e:
            motivo = f"respuesta inesperada: {e}"

        errores.append(f"{modelo} -> {motivo}")
        print(f"[ai_service] falló {modelo}: {motivo}", flush=True)
        if i < len(modelos) - 1:
            time.sleep(1)

    return {
        "respuesta": _itinerario_demo(mensaje_usuario, clima, actividades),
        "fuente": "demo",
        "error": " | ".join(errores),
    }


def _itinerario_demo(mensaje_usuario: str, clima: dict, actividades: list) -> str:
    """Fallback sin IA: ordena actividades según compatibilidad con el clima."""
    condicion = clima.get("condicion", "cualquiera")
    compatibles = [a for a in actividades if a["recomendado_clima"] in (condicion, "cualquiera")]
    elegidas = (compatibles or actividades)[:4]

    lineas = [
        f"🗺️ Itinerario sugerido para hoy en Mar del Plata "
        f"({clima.get('temperatura')}°C, {condicion}):",
        "",
    ]
    for i, a in enumerate(elegidas, start=1):
        lineas.append(f"{i}. **{a['nombre']}** ({a['zona']}) — {a['horario']}")
        lineas.append(f"   {a['descripcion']}")
    lineas.append("")
    lineas.append("💡 El asistente de IA no está disponible en este momento, probá de nuevo en un rato.")
    return "\n".join(lineas)

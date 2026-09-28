"""
ai_service.py
Integración con DeepSeek (API compatible con OpenAI) para generar
itinerarios turísticos personalizados usando como contexto:
  - el clima actual (OpenWeatherMap)
  - las actividades reales de la base de datos
  - lo que escribe el usuario en lenguaje natural

Si no hay DEEPSEEK_API_KEY configurada, o si DeepSeek falla, se devuelve
un itinerario de demostración armado localmente para que la app siga andando.
"""

import os
import time
import requests

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")
DEEPSEEK_URL = os.environ.get(
    "DEEPSEEK_URL", "https://api.deepseek.com/chat/completions"
)

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


def _llamar_deepseek(mensaje_usuario: str, contexto: str) -> str:
    resp = requests.post(
        DEEPSEEK_URL,
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEEPSEEK_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"CONTEXTO:\n{contexto}\n\nPEDIDO DEL USUARIO: {mensaje_usuario}",
                },
            ],
            "max_tokens": 1024,
            "stream": False,
            # sin "pensar" de más: más rápido y no gasta tokens en razonamiento
            "thinking": {"type": "disabled"},
        },
        timeout=45,
    )
    resp.raise_for_status()
    data = resp.json()
    return (data["choices"][0]["message"].get("content") or "").strip()


def generar_itinerario(mensaje_usuario: str, clima: dict, actividades: list) -> dict:
    """Devuelve {'respuesta': texto, 'fuente': 'deepseek' | 'demo'} (+ 'error' si falló)."""
    if not DEEPSEEK_API_KEY:
        return {
            "respuesta": _itinerario_demo(mensaje_usuario, clima, actividades),
            "fuente": "demo",
            "error": "Falta DEEPSEEK_API_KEY en el servidor",
        }

    contexto = _construir_contexto(clima, actividades)
    ultimo_error = ""

    # hasta 2 intentos: los errores pasajeros (429/500/503, timeouts) suelen resolverse solos
    for intento in range(2):
        try:
            texto = _llamar_deepseek(mensaje_usuario, contexto)
            if texto:
                return {"respuesta": texto, "fuente": "deepseek"}
            ultimo_error = "DeepSeek devolvió una respuesta vacía"
        except requests.HTTPError as e:
            cuerpo = e.response.text[:300] if e.response is not None else ""
            ultimo_error = f"HTTP {e.response.status_code if e.response is not None else '?'}: {cuerpo}"
        except requests.RequestException as e:
            ultimo_error = str(e)
        except (KeyError, IndexError, ValueError) as e:
            ultimo_error = f"Respuesta inesperada de DeepSeek: {e}"

        print(f"[ai_service] intento {intento + 1} falló: {ultimo_error}", flush=True)
        if intento == 0:
            time.sleep(1.5)

    return {
        "respuesta": _itinerario_demo(mensaje_usuario, clima, actividades),
        "fuente": "demo",
        "error": ultimo_error,
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

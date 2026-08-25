"""
ai_service.py
Integración con un LLM (Claude, vía API de Anthropic) para generar
itinerarios turísticos 100% personalizados, usando como contexto:
  - el clima actual (obtenido de OpenWeatherMap)
  - las actividades reales guardadas en la base de datos (ACTIVIDAD)
  - la preferencia en lenguaje natural que escribe el usuario

Si no hay ANTHROPIC_API_KEY configurada, se genera una respuesta local
de demostración (sin llamar a ningún servicio externo) para que la app
siga siendo usable.
"""

import os
import requests

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"


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


def generar_itinerario(mensaje_usuario: str, clima: dict, actividades: list) -> dict:
    """
    Genera un itinerario personalizado. Devuelve dict con 'respuesta' (texto)
    y 'fuente' ('anthropic' o 'demo').
    """
    contexto = _construir_contexto(clima, actividades)

    system_prompt = (
        "Sos el Asistente Turístico y Cultural Autónomo de Mar del Plata, Argentina. "
        "Tu trabajo es armar itinerarios breves, cálidos y realistas, usando SOLO las "
        "actividades de la lista de contexto que te paso (no inventes lugares que no "
        "estén ahí). Tené en cuenta el clima actual para priorizar actividades bajo "
        "techo si llueve o hace mucho viento, y actividades al aire libre/playa si "
        "está soleado. Respondé en español rioplatense, en formato de lista breve "
        "con 3 a 5 paradas, indicando horario sugerido y una frase de por qué la "
        "elegiste. Cerrá con un tip práctico."
    )

    if not ANTHROPIC_API_KEY:
        return {"respuesta": _itinerario_demo(mensaje_usuario, clima, actividades), "fuente": "demo"}

    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": ANTHROPIC_MODEL,
                "max_tokens": 700,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            f"CONTEXTO:\n{contexto}\n\n"
                            f"PEDIDO DEL USUARIO: {mensaje_usuario}"
                        ),
                    }
                ],
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        texto = "".join(
            block.get("text", "") for block in data.get("content", []) if block.get("type") == "text"
        )
        return {"respuesta": texto.strip() or _itinerario_demo(mensaje_usuario, clima, actividades),
                "fuente": "anthropic"}
    except requests.RequestException as e:
        return {
            "respuesta": _itinerario_demo(mensaje_usuario, clima, actividades),
            "fuente": "demo",
            "error": str(e),
        }


def _itinerario_demo(mensaje_usuario: str, clima: dict, actividades: list) -> str:
    """Fallback simple sin LLM: ordena actividades por compatibilidad con el clima."""
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
    lineas.append(
        "💡 Tip: configurá tu ANTHROPIC_API_KEY en el backend para recibir "
        "itinerarios generados por IA totalmente personalizados según lo que escribas."
    )
    return "\n".join(lineas)

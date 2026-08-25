"""
weather_service.py
Integración con la API pública de OpenWeatherMap.
No requiere librerías adicionales: usa `requests`.
"""

import os
import requests

OWM_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Coordenadas de Mar del Plata (por defecto)
MDP_LAT = -38.0055
MDP_LON = -57.5426


def _clasificar_condicion(owm_main: str, wind_speed: float) -> str:
    """
    Traduce la condición cruda de OpenWeatherMap a una de nuestras
    4 categorías: soleado | nublado | lluvia | viento
    """
    owm_main = (owm_main or "").lower()

    if wind_speed and wind_speed >= 10:  # m/s ~ 36 km/h
        return "viento"
    if owm_main in ("rain", "drizzle", "thunderstorm", "snow"):
        return "lluvia"
    if owm_main in ("clouds", "mist", "fog", "haze"):
        return "nublado"
    if owm_main in ("clear",):
        return "soleado"
    return "nublado"


def obtener_clima_actual(ciudad: str = "Mar del Plata,AR"):
    """
    Devuelve el clima actual. Si no hay API key configurada, devuelve
    datos de demostración para que el frontend siga siendo funcional.
    """
    if not OWM_API_KEY:
        return _clima_demo()

    try:
        resp = requests.get(
            f"{OWM_BASE_URL}/weather",
            params={
                "q": ciudad,
                "appid": OWM_API_KEY,
                "units": "metric",
                "lang": "es",
            },
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()

        main = data.get("weather", [{}])[0].get("main", "Clear")
        descripcion = data.get("weather", [{}])[0].get("description", "")
        temperatura = data.get("main", {}).get("temp", 18.0)
        viento = data.get("wind", {}).get("speed", 0.0)
        condicion = _clasificar_condicion(main, viento)
        alerta = temperatura >= 32 or temperatura <= 2 or viento >= 15

        return {
            "temperatura": round(temperatura, 1),
            "condicion": condicion,
            "descripcion": descripcion.capitalize(),
            "alerta_vigente": alerta,
            "fuente": "openweathermap",
        }
    except requests.RequestException as e:
        demo = _clima_demo()
        demo["error"] = f"No se pudo contactar OpenWeatherMap: {e}"
        return demo


def obtener_pronostico(ciudad: str = "Mar del Plata,AR"):
    """
    Devuelve un pronóstico simplificado en 3 franjas horarias
    (Mañana / Tarde / Noche) a partir del endpoint /forecast (cada 3hs).
    """
    if not OWM_API_KEY:
        return _pronostico_demo()

    try:
        resp = requests.get(
            f"{OWM_BASE_URL}/forecast",
            params={
                "q": ciudad,
                "appid": OWM_API_KEY,
                "units": "metric",
                "lang": "es",
                "cnt": 8,  # próximas 24hs (cada 3hs)
            },
            timeout=8,
        )
        resp.raise_for_status()
        data = resp.json()

        franjas = {"Mañana": [], "Tarde": [], "Noche": []}
        for item in data.get("list", []):
            hora = int(item["dt_txt"].split(" ")[1].split(":")[0])
            if 6 <= hora < 13:
                franja = "Mañana"
            elif 13 <= hora < 20:
                franja = "Tarde"
            else:
                franja = "Noche"
            franjas[franja].append(item)

        resultado = []
        for nombre, items in franjas.items():
            if not items:
                continue
            temp_prom = sum(i["main"]["temp"] for i in items) / len(items)
            main = items[0]["weather"][0]["main"]
            viento = items[0].get("wind", {}).get("speed", 0.0)
            resultado.append(
                {
                    "franja_horaria": nombre,
                    "temperatura": round(temp_prom, 1),
                    "condicion": _clasificar_condicion(main, viento),
                }
            )
        return resultado or _pronostico_demo()
    except requests.RequestException:
        return _pronostico_demo()


def _clima_demo():
    return {
        "temperatura": 21.5,
        "condicion": "soleado",
        "descripcion": "Cielo despejado (datos de demostración, configurá OPENWEATHER_API_KEY)",
        "alerta_vigente": False,
        "fuente": "demo",
    }


def _pronostico_demo():
    return [
        {"franja_horaria": "Mañana", "temperatura": 18.0, "condicion": "nublado"},
        {"franja_horaria": "Tarde", "temperatura": 23.0, "condicion": "soleado"},
        {"franja_horaria": "Noche", "temperatura": 16.5, "condicion": "nublado"},
    ]

"""
seed_data.py
Carga datos iniciales en la base de datos: categorías, actividades reales
de Mar del Plata, ubicaciones, tips locales, contenido cultural y las
reglas de recomendación según clima.
"""

from models import (
    db,
    Categoria,
    Actividad,
    Ubicacion,
    TipLocal,
    ContenidoCiudad,
    RecomendacionClima,
)

CATEGORIAS = [
    {"nombre": "Playas", "icono": "🏖️"},
    {"nombre": "Cultura y Museos", "icono": "🏛️"},
    {"nombre": "Gastronomía", "icono": "🍽️"},
    {"nombre": "Aire libre", "icono": "🌳"},
    {"nombre": "Vida nocturna", "icono": "🌙"},
    {"nombre": "Compras y paseos", "icono": "🛍️"},
]

# recomendado_clima: soleado | nublado | lluvia | viento | cualquiera
ACTIVIDADES = [
    dict(
        nombre="Playa Grande",
        categoria="Playas",
        zona="Playa Grande",
        descripcion="La playa más icónica de Mar del Plata, junto al Club Náutico y la Rambla.",
        calificacion=4.6,
        recomendado_clima="soleado",
        horario="Todo el día",
    ),
    dict(
        nombre="Playa Bristol",
        categoria="Playas",
        zona="Centro",
        descripcion="Frente al Casino Central, la playa más concurrida y tradicional de la ciudad.",
        calificacion=4.3,
        recomendado_clima="soleado",
        horario="Todo el día",
    ),
    dict(
        nombre="Torreón del Monje",
        categoria="Aire libre",
        zona="Playa Grande",
        descripcion="Mirador histórico sobre el mar, ideal para fotos y atardeceres.",
        calificacion=4.7,
        recomendado_clima="cualquiera",
        horario="9:00 a 20:00",
    ),
    dict(
        nombre="Museo MAR (Museo de Arte Contemporáneo)",
        categoria="Cultura y Museos",
        zona="Playa Grande",
        descripcion="Arte contemporáneo argentino y latinoamericano en un edificio icónico frente al mar.",
        calificacion=4.5,
        recomendado_clima="lluvia",
        horario="14:00 a 20:00 (cerrado martes)",
    ),
    dict(
        nombre="Museo del Mar",
        categoria="Cultura y Museos",
        zona="Centro",
        descripcion="Una de las mayores colecciones de caracoles y moluscos del mundo.",
        calificacion=4.2,
        recomendado_clima="lluvia",
        horario="10:00 a 20:00",
    ),
    dict(
        nombre="Catedral de los Santos Pedro y Cecilia",
        categoria="Cultura y Museos",
        zona="Centro",
        descripcion="Catedral neogótica en el centro de la ciudad, ideal para visitar en días de lluvia.",
        calificacion=4.5,
        recomendado_clima="lluvia",
        horario="8:00 a 20:00",
    ),
    dict(
        nombre="Villa Victoria (Villa Victoria Ocampo)",
        categoria="Cultura y Museos",
        zona="Barrio Los Troncos",
        descripcion="Casa museo de la escritora Victoria Ocampo, con jardines y muestras culturales.",
        calificacion=4.4,
        recomendado_clima="nublado",
        horario="14:00 a 20:00",
    ),
    dict(
        nombre="Puerto de Mar del Plata",
        categoria="Gastronomía",
        zona="Puerto",
        descripcion="Zona de lobos marinos, barcos pesqueros y los tradicionales restaurantes de mariscos.",
        calificacion=4.6,
        recomendado_clima="cualquiera",
        horario="Todo el día",
    ),
    dict(
        nombre="Paseo Gastronómico Alem",
        categoria="Gastronomía",
        zona="Puerto",
        descripcion="Calle icónica del puerto con restaurantes de pescados y mariscos frescos.",
        calificacion=4.4,
        recomendado_clima="cualquiera",
        horario="12:00 a 00:00",
    ),
    dict(
        nombre="Bosque Peralta Ramos",
        categoria="Aire libre",
        zona="Peralta Ramos",
        descripcion="Área forestada ideal para caminatas y picnics en días templados.",
        calificacion=4.3,
        recomendado_clima="nublado",
        horario="Todo el día",
    ),
    dict(
        nombre="Reserva del Puerto",
        categoria="Aire libre",
        zona="Puerto",
        descripcion="Reserva natural urbana para avistaje de aves junto al mar.",
        calificacion=4.1,
        recomendado_clima="nublado",
        horario="8:00 a 19:00",
    ),
    dict(
        nombre="Peatonal San Martín",
        categoria="Compras y paseos",
        zona="Centro",
        descripcion="La calle comercial más transitada, con locales, heladerías y espectáculos callejeros.",
        calificacion=4.2,
        recomendado_clima="cualquiera",
        horario="10:00 a 22:00",
    ),
    dict(
        nombre="Paseo Jesús de Galíndez (La Feliz)",
        categoria="Compras y paseos",
        zona="Playa Grande",
        descripcion="Paseo costero techado, ideal para caminar incluso con mal tiempo.",
        calificacion=4.0,
        recomendado_clima="lluvia",
        horario="10:00 a 21:00",
    ),
    dict(
        nombre="Casino Central",
        categoria="Vida nocturna",
        zona="Centro",
        descripcion="Casino histórico frente a la Playa Bristol, opción de entretenimiento nocturno.",
        calificacion=4.0,
        recomendado_clima="lluvia",
        horario="14:00 a 04:00",
    ),
    dict(
        nombre="Zona de bares y after-beach en Playa Grande",
        categoria="Vida nocturna",
        zona="Playa Grande",
        descripcion="Bares y restaurantes con vista al mar, ideales para el atardecer en días despejados.",
        calificacion=4.3,
        recomendado_clima="soleado",
        horario="18:00 a 02:00",
    ),
    dict(
        nombre="Estadio José María Minella",
        categoria="Aire libre",
        zona="Playa Serena",
        descripcion="Estadio de Aldosivi y sede de partidos y eventos deportivos de la ciudad.",
        calificacion=4.1,
        recomendado_clima="cualquiera",
        horario="Según cartelera de eventos",
    ),
    dict(
        nombre="Cabo Corrientes",
        categoria="Aire libre",
        zona="Playa Grande",
        descripcion="Punto panorámico con el histórico faro y vistas espectaculares en días de viento.",
        calificacion=4.5,
        recomendado_clima="viento",
        horario="Todo el día",
    ),
    dict(
        nombre="Circuito de Golf y Complejo Bristol",
        categoria="Aire libre",
        zona="Bristol",
        descripcion="Complejo deportivo al aire libre ideal para días soleados y templados.",
        calificacion=4.0,
        recomendado_clima="soleado",
        horario="8:00 a 19:00",
    ),
]

UBICACIONES = [
    dict(nombre_lugar="Playa Grande", latitud=-38.0298, longitud=-57.5384,
         descripcion="Playa principal junto al Club Náutico."),
    dict(nombre_lugar="Playa Bristol", latitud=-38.0055, longitud=-57.5426,
         descripcion="Frente al Casino Central."),
    dict(nombre_lugar="Torreón del Monje", latitud=-38.0301, longitud=-57.5372,
         descripcion="Mirador histórico sobre el mar."),
    dict(nombre_lugar="Museo MAR", latitud=-38.0292, longitud=-57.5401,
         descripcion="Museo de Arte Contemporáneo."),
    dict(nombre_lugar="Puerto de Mar del Plata", latitud=-38.0472, longitud=-57.5323,
         descripcion="Zona portuaria y pesquera."),
    dict(nombre_lugar="Peatonal San Martín", latitud=-38.0023, longitud=-57.5475,
         descripcion="Calle comercial peatonal del centro."),
    dict(nombre_lugar="Cabo Corrientes", latitud=-38.0349, longitud=-57.5350,
         descripcion="Punto panorámico con el faro histórico."),
]

TIPS = [
    dict(texto="En verano, la Rambla y Playa Grande se llenan temprano: llegá antes de las 10 para conseguir buen lugar.", icono="☀️"),
    dict(texto="Los días de lluvia son ideales para visitar el Museo MAR o la Catedral, ambos en el centro.", icono="🌧️"),
    dict(texto="El Puerto es el mejor lugar para comer mariscos frescos; probá las rabas en algún local de Alem.", icono="🦐"),
    dict(texto="Con viento fuerte, Cabo Corrientes ofrece una vista espectacular pero abrigate bien.", icono="🌬️"),
    dict(texto="La temporada alta va de diciembre a marzo; fuera de temporada la ciudad es mucho más tranquila.", icono="📅"),
    dict(texto="Aldosivi juega en el Estadio José María Minella: revisá el fixture si querés vivir un partido en 'la Feliz'.", icono="⚽"),
]

CONTENIDO_CIUDAD = [
    dict(tipo="historia", titulo="Origen de 'La Feliz'",
         descripcion="Mar del Plata nació como balneario aristocrático a fines del siglo XIX y hoy es el destino de veraneo más popular de Argentina.",
         icono="⛵"),
    dict(tipo="cultura", titulo="Cuna del rock nacional",
         descripcion="La ciudad fue escenario clave del rock argentino, con bandas emblemáticas que marcaron los veranos marplatenses.",
         icono="🎸"),
    dict(tipo="gastronomia", titulo="Capital de las rabas",
         descripcion="Los mariscos, especialmente las rabas (calamar frito), son un ícono gastronómico de la ciudad portuaria.",
         icono="🦑"),
    dict(tipo="deporte", titulo="Pasión por Aldosivi",
         descripcion="Club Atlético Aldosivi, fundado en 1913, es uno de los símbolos deportivos de Mar del Plata.",
         icono="⚽"),
]

# Reglas de recomendación: condición climática -> categorías sugeridas
RECOMENDACIONES = {
    "soleado": ["Playas", "Aire libre", "Vida nocturna", "Compras y paseos"],
    "nublado": ["Aire libre", "Compras y paseos", "Cultura y Museos"],
    "lluvia": ["Cultura y Museos", "Gastronomía", "Vida nocturna", "Compras y paseos"],
    "viento": ["Aire libre", "Cultura y Museos", "Gastronomía"],
}


def seed_database():
    """Carga los datos iniciales solo si la base está vacía."""
    if Categoria.query.first():
        return  # ya hay datos

    cat_map = {}
    for c in CATEGORIAS:
        cat = Categoria(nombre=c["nombre"], icono=c["icono"])
        db.session.add(cat)
        db.session.flush()
        cat_map[c["nombre"]] = cat.id_categoria

    for a in ACTIVIDADES:
        db.session.add(
            Actividad(
                id_categoria=cat_map[a["categoria"]],
                nombre=a["nombre"],
                zona=a["zona"],
                descripcion=a["descripcion"],
                calificacion=a["calificacion"],
                recomendado_clima=a["recomendado_clima"],
                horario=a["horario"],
            )
        )

    for u in UBICACIONES:
        db.session.add(Ubicacion(**u))

    for t in TIPS:
        db.session.add(TipLocal(**t))

    for c in CONTENIDO_CIUDAD:
        db.session.add(ContenidoCiudad(**c))

    for condicion, categorias in RECOMENDACIONES.items():
        for nombre_cat in categorias:
            db.session.add(
                RecomendacionClima(
                    condicion_general=condicion,
                    id_categoria=cat_map[nombre_cat],
                )
            )

    db.session.commit()
    print("✅ Base de datos poblada con datos de Mar del Plata.")

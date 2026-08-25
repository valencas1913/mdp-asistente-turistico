"""
models.py
Modelos SQLAlchemy que reflejan 1:1 el Diagrama Entidad-Relación
"Asistente Turístico y Cultural Autónomo - MdP Guide".

Entidades: CATEGORIA, ACTIVIDAD, USUARIO, FAVORITO, CLIMA_ACTUAL,
PRONOSTICO, RECOMENDACION_CLIMA, CONTENIDO_CIUDAD, TIP_LOCAL, UBICACION.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Categoria(db.Model):
    __tablename__ = "categoria"

    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False, unique=True)
    icono = db.Column(db.String(10), nullable=False, default="📍")

    actividades = db.relationship(
        "Actividad", backref="categoria", lazy=True, cascade="all, delete-orphan"
    )
    recomendaciones = db.relationship(
        "RecomendacionClima", backref="categoria", lazy=True
    )

    def to_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "nombre": self.nombre,
            "icono": self.icono,
        }


class Actividad(db.Model):
    __tablename__ = "actividad"

    id_actividad = db.Column(db.Integer, primary_key=True)
    id_categoria = db.Column(
        db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=False
    )
    nombre = db.Column(db.String(150), nullable=False)
    zona = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.String(300))
    calificacion = db.Column(db.Float, default=0.0)
    # valores esperados: soleado | nublado | lluvia | viento | cualquiera
    recomendado_clima = db.Column(db.String(30), default="cualquiera")
    horario = db.Column(db.String(100))

    favoritos = db.relationship(
        "Favorito", backref="actividad", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id_actividad": self.id_actividad,
            "id_categoria": self.id_categoria,
            "categoria_nombre": self.categoria.nombre if self.categoria else None,
            "categoria_icono": self.categoria.icono if self.categoria else None,
            "nombre": self.nombre,
            "zona": self.zona,
            "descripcion": self.descripcion,
            "imagen_url": self.imagen_url,
            "calificacion": self.calificacion,
            "recomendado_clima": self.recomendado_clima,
            "horario": self.horario,
        }


class Usuario(db.Model):
    __tablename__ = "usuario"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    contrasena = db.Column("contraseña", db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    favoritos = db.relationship(
        "Favorito", backref="usuario", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "email": self.email,
            "fecha_registro": self.fecha_registro.isoformat()
            if self.fecha_registro
            else None,
        }


class Favorito(db.Model):
    __tablename__ = "favorito"

    id_favorito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(
        db.Integer, db.ForeignKey("usuario.id_usuario"), nullable=False
    )
    id_actividad = db.Column(
        db.Integer, db.ForeignKey("actividad.id_actividad"), nullable=False
    )
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id_favorito": self.id_favorito,
            "id_usuario": self.id_usuario,
            "id_actividad": self.id_actividad,
            "fecha_agregado": self.fecha_agregado.isoformat()
            if self.fecha_agregado
            else None,
            "actividad": self.actividad.to_dict() if self.actividad else None,
        }


class ClimaActual(db.Model):
    __tablename__ = "clima_actual"

    id_clima = db.Column(db.Integer, primary_key=True)
    temperatura = db.Column(db.Float, nullable=False)
    condicion = db.Column(db.String(30), nullable=False)  # soleado/nublado/lluvia/viento
    descripcion = db.Column(db.String(150))
    alerta_vigente = db.Column(db.Boolean, default=False)
    fecha_consulta = db.Column(db.DateTime, default=datetime.utcnow)

    pronosticos = db.relationship(
        "Pronostico", backref="clima", lazy=True, cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id_clima": self.id_clima,
            "temperatura": self.temperatura,
            "condicion": self.condicion,
            "descripcion": self.descripcion,
            "alerta_vigente": self.alerta_vigente,
            "fecha_consulta": self.fecha_consulta.isoformat()
            if self.fecha_consulta
            else None,
            "pronostico": [p.to_dict() for p in self.pronosticos],
        }


class Pronostico(db.Model):
    __tablename__ = "pronostico"

    id_pronostico = db.Column(db.Integer, primary_key=True)
    id_clima = db.Column(
        db.Integer, db.ForeignKey("clima_actual.id_clima"), nullable=False
    )
    franja_horaria = db.Column(db.String(30))  # ej: "Mañana", "Tarde", "Noche"
    temperatura = db.Column(db.Float)
    condicion = db.Column(db.String(30))

    def to_dict(self):
        return {
            "id_pronostico": self.id_pronostico,
            "franja_horaria": self.franja_horaria,
            "temperatura": self.temperatura,
            "condicion": self.condicion,
        }


class RecomendacionClima(db.Model):
    __tablename__ = "recomendacion_clima"

    id_recomendacion = db.Column(db.Integer, primary_key=True)
    id_clima = db.Column(db.Integer, db.ForeignKey("clima_actual.id_clima"))
    # condicion_general permite reutilizar la recomendación para cualquier
    # registro futuro de clima con la misma condición (soleado/nublado/lluvia/viento)
    condicion_general = db.Column(db.String(30), nullable=False)
    id_categoria = db.Column(
        db.Integer, db.ForeignKey("categoria.id_categoria"), nullable=False
    )

    def to_dict(self):
        return {
            "id_recomendacion": self.id_recomendacion,
            "condicion_general": self.condicion_general,
            "id_categoria": self.id_categoria,
            "categoria_nombre": self.categoria.nombre if self.categoria else None,
        }


class ContenidoCiudad(db.Model):
    __tablename__ = "contenido_ciudad"

    id_contenido = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50))  # ej: "historia", "cultura", "gastronomia"
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    icono = db.Column(db.String(10), default="🏛️")

    def to_dict(self):
        return {
            "id_contenido": self.id_contenido,
            "tipo": self.tipo,
            "titulo": self.titulo,
            "descripcion": self.descripcion,
            "icono": self.icono,
        }


class TipLocal(db.Model):
    __tablename__ = "tip_local"

    id_tip = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    icono = db.Column(db.String(10), default="💡")

    def to_dict(self):
        return {"id_tip": self.id_tip, "texto": self.texto, "icono": self.icono}


class Ubicacion(db.Model):
    __tablename__ = "ubicacion"

    id_ubicacion = db.Column(db.Integer, primary_key=True)
    nombre_lugar = db.Column(db.String(150), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    descripcion = db.Column(db.Text)

    def to_dict(self):
        return {
            "id_ubicacion": self.id_ubicacion,
            "nombre_lugar": self.nombre_lugar,
            "latitud": self.latitud,
            "longitud": self.longitud,
            "descripcion": self.descripcion,
        }

"""
app.py
Backend Flask del Asistente Turístico y Cultural Autónomo de Mar del Plata.

Endpoints principales:
  GET  /api/clima                 -> clima actual + pronóstico (OpenWeatherMap)
  GET  /api/categorias            -> categorías
  GET  /api/actividades           -> actividades (filtrables por ?clima= y ?categoria=)
  GET  /api/actividades/<id>      -> detalle de una actividad
  GET  /api/contenido-ciudad      -> contenido cultural/histórico
  GET  /api/tips                  -> tips locales
  GET  /api/ubicaciones           -> puntos geográficos
  POST /api/usuarios/registro     -> alta de usuario
  POST /api/usuarios/login        -> login simple
  GET  /api/favoritos/<id_usuario>-> favoritos de un usuario
  POST /api/favoritos             -> agregar favorito
  DELETE /api/favoritos/<id>      -> quitar favorito
  POST /api/asistente/chat        -> chat con IA (itinerario personalizado)
"""

import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

from models import (
    db,
    Categoria,
    Actividad,
    Usuario,
    Favorito,
    ClimaActual,
    Pronostico,
    RecomendacionClima,
    ContenidoCiudad,
    TipLocal,
    Ubicacion,
)
from seed_data import seed_database
import weather_service
import ai_service

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'mdp_guide.db')}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        seed_database()

    register_routes(app)
    return app


def register_routes(app):
    # ---------- CLIMA ----------
    @app.route("/api/clima", methods=["GET"])
    def get_clima():
        ciudad = request.args.get("ciudad", "Mar del Plata,AR")
        actual = weather_service.obtener_clima_actual(ciudad)
        pronostico = weather_service.obtener_pronostico(ciudad)

        # Persistimos la consulta en CLIMA_ACTUAL y PRONOSTICO (según el ER)
        registro = ClimaActual(
            temperatura=actual["temperatura"],
            condicion=actual["condicion"],
            descripcion=actual.get("descripcion", ""),
            alerta_vigente=actual.get("alerta_vigente", False),
            fecha_consulta=datetime.utcnow(),
        )
        db.session.add(registro)
        db.session.flush()

        for p in pronostico:
            db.session.add(
                Pronostico(
                    id_clima=registro.id_clima,
                    franja_horaria=p["franja_horaria"],
                    temperatura=p["temperatura"],
                    condicion=p["condicion"],
                )
            )
        db.session.commit()

        resultado = registro.to_dict()
        resultado["fuente"] = actual.get("fuente")
        if actual.get("error"):
            resultado["error"] = actual["error"]
        return jsonify(resultado)

    # ---------- CATEGORIAS ----------
    @app.route("/api/categorias", methods=["GET"])
    def get_categorias():
        categorias = Categoria.query.all()
        return jsonify([c.to_dict() for c in categorias])

    # ---------- ACTIVIDADES ----------
    @app.route("/api/actividades", methods=["GET"])
    def get_actividades():
        query = Actividad.query
        condicion = request.args.get("clima")
        id_categoria = request.args.get("categoria", type=int)

        if id_categoria:
            query = query.filter_by(id_categoria=id_categoria)

        actividades = query.all()

        if condicion:
            recomendadas_ids = {
                r.id_categoria
                for r in RecomendacionClima.query.filter_by(
                    condicion_general=condicion
                ).all()
            }
            actividades = [
                a
                for a in actividades
                if a.recomendado_clima in (condicion, "cualquiera")
                or a.id_categoria in recomendadas_ids
            ]
            actividades.sort(
                key=lambda a: 0 if a.recomendado_clima == condicion else 1
            )

        return jsonify([a.to_dict() for a in actividades])

    @app.route("/api/actividades/<int:id_actividad>", methods=["GET"])
    def get_actividad(id_actividad):
        actividad = Actividad.query.get_or_404(id_actividad)
        return jsonify(actividad.to_dict())

    # ---------- CONTENIDO CIUDAD ----------
    @app.route("/api/contenido-ciudad", methods=["GET"])
    def get_contenido_ciudad():
        contenidos = ContenidoCiudad.query.all()
        return jsonify([c.to_dict() for c in contenidos])

    # ---------- TIPS ----------
    @app.route("/api/tips", methods=["GET"])
    def get_tips():
        tips = TipLocal.query.all()
        return jsonify([t.to_dict() for t in tips])

    # ---------- UBICACIONES ----------
    @app.route("/api/ubicaciones", methods=["GET"])
    def get_ubicaciones():
        ubicaciones = Ubicacion.query.all()
        return jsonify([u.to_dict() for u in ubicaciones])

    # ---------- USUARIOS ----------
    @app.route("/api/usuarios/registro", methods=["POST"])
    def registrar_usuario():
        data = request.get_json(force=True)
        nombre = (data.get("nombre") or "").strip()
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        if not nombre or not email or not password:
            return jsonify({"error": "nombre, email y password son obligatorios"}), 400

        if Usuario.query.filter_by(email=email).first():
            return jsonify({"error": "Ese email ya está registrado"}), 409

        usuario = Usuario(
            nombre=nombre,
            email=email,
            contrasena=generate_password_hash(password),
        )
        db.session.add(usuario)
        db.session.commit()
        return jsonify(usuario.to_dict()), 201

    @app.route("/api/usuarios/login", methods=["POST"])
    def login_usuario():
        data = request.get_json(force=True)
        email = (data.get("email") or "").strip().lower()
        password = data.get("password") or ""

        usuario = Usuario.query.filter_by(email=email).first()
        if not usuario or not check_password_hash(usuario.contrasena, password):
            return jsonify({"error": "Credenciales inválidas"}), 401

        return jsonify(usuario.to_dict())

    # ---------- FAVORITOS ----------
    @app.route("/api/favoritos/<int:id_usuario>", methods=["GET"])
    def get_favoritos(id_usuario):
        favoritos = Favorito.query.filter_by(id_usuario=id_usuario).all()
        return jsonify([f.to_dict() for f in favoritos])

    @app.route("/api/favoritos", methods=["POST"])
    def agregar_favorito():
        data = request.get_json(force=True)
        id_usuario = data.get("id_usuario")
        id_actividad = data.get("id_actividad")

        if not id_usuario or not id_actividad:
            return jsonify({"error": "id_usuario e id_actividad son obligatorios"}), 400

        existente = Favorito.query.filter_by(
            id_usuario=id_usuario, id_actividad=id_actividad
        ).first()
        if existente:
            return jsonify(existente.to_dict()), 200

        favorito = Favorito(id_usuario=id_usuario, id_actividad=id_actividad)
        db.session.add(favorito)
        db.session.commit()
        return jsonify(favorito.to_dict()), 201

    @app.route("/api/favoritos/<int:id_favorito>", methods=["DELETE"])
    def quitar_favorito(id_favorito):
        favorito = Favorito.query.get_or_404(id_favorito)
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({"ok": True})

    # ---------- ASISTENTE IA ----------
    @app.route("/api/asistente/chat", methods=["POST"])
    def asistente_chat():
        data = request.get_json(force=True)
        mensaje = (data.get("mensaje") or "").strip()
        if not mensaje:
            return jsonify({"error": "El campo 'mensaje' es obligatorio"}), 400

        clima = weather_service.obtener_clima_actual()
        actividades = [a.to_dict() for a in Actividad.query.all()]

        resultado = ai_service.generar_itinerario(mensaje, clima, actividades)
        resultado["clima_usado"] = clima
        return jsonify(resultado)

    # ---------- HEALTHCHECK ----------
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

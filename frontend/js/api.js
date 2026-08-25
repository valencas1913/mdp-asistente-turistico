// api.js
// Capa fina sobre fetch para hablar con el backend Flask.

const Api = {
  async _get(path) {
    const res = await fetch(`${API_BASE_URL}${path}`);
    if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
    return res.json();
  },

  async _post(path, body) {
    const res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `POST ${path} -> ${res.status}`);
    return data;
  },

  async _delete(path) {
    const res = await fetch(`${API_BASE_URL}${path}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`DELETE ${path} -> ${res.status}`);
    return res.json();
  },

  getClima: () => Api._get("/clima"),
  getCategorias: () => Api._get("/categorias"),
  getActividades: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return Api._get(`/actividades${qs ? "?" + qs : ""}`);
  },
  getTips: () => Api._get("/tips"),
  getContenidoCiudad: () => Api._get("/contenido-ciudad"),

  registrarUsuario: (nombre, email, password) =>
    Api._post("/usuarios/registro", { nombre, email, password }),
  loginUsuario: (email, password) =>
    Api._post("/usuarios/login", { email, password }),

  getFavoritos: (idUsuario) => Api._get(`/favoritos/${idUsuario}`),
  agregarFavorito: (idUsuario, idActividad) =>
    Api._post("/favoritos", { id_usuario: idUsuario, id_actividad: idActividad }),
  quitarFavorito: (idFavorito) => Api._delete(`/favoritos/${idFavorito}`),

  chatAsistente: (mensaje) => Api._post("/asistente/chat", { mensaje }),
};

// actividades.js
// Maneja categorías, filtrado por clima/categoría, y el renderizado
// de tarjetas de actividad tanto en "Inicio" como en "Actividades".

const Actividades = {
  categorias: [],
  categoriaActiva: "",

  async init() {
    try {
      this.categorias = await Api.getCategorias();
      this._renderChips();
    } catch (err) {
      console.error("Error cargando categorías:", err);
    }
  },

  _renderChips() {
    const row = document.getElementById("chip-categorias");
    this.categorias.forEach((c) => {
      const btn = document.createElement("button");
      btn.className = "chip";
      btn.dataset.categoria = c.id_categoria;
      btn.textContent = `${c.icono} ${c.nombre}`;
      btn.addEventListener("click", () => this._onChipClick(btn));
      row.appendChild(btn);
    });
  },

  _onChipClick(btn) {
    document.querySelectorAll("#chip-categorias .chip").forEach((c) => c.classList.remove("active"));
    btn.classList.add("active");
    this.categoriaActiva = btn.dataset.categoria || "";
    this.cargarListaCompleta();
  },

  async cargarInicio() {
    const condicion = Clima.actual ? Clima.actual.condicion : "";
    try {
      const actividades = await Api.getActividades({ clima: condicion });
      this._render(actividades.slice(0, 4), "inicio-actividades");
    } catch (err) {
      console.error("Error cargando actividades de inicio:", err);
    }
  },

  async cargarListaCompleta() {
    const params = {};
    if (this.categoriaActiva) params.categoria = this.categoriaActiva;
    try {
      const actividades = await Api.getActividades(params);
      this._render(actividades, "actividades-list");
    } catch (err) {
      console.error("Error cargando actividades:", err);
    }
  },

  _render(actividades, contenedorId) {
    const cont = document.getElementById(contenedorId);
    cont.innerHTML = "";

    if (!actividades.length) {
      cont.innerHTML = `
        <div class="empty-state">
          <div class="glyph">🧭</div>
          <p>No encontramos actividades para este filtro.</p>
        </div>`;
      return;
    }

    actividades.forEach((a) => cont.appendChild(this._card(a)));
  },

  _card(a) {
    const card = document.createElement("div");
    card.className = "activity-card";
    const esFavorito = Favoritos.esFavorito(a.id_actividad);

    card.innerHTML = `
      <div class="activity-icon">${a.categoria_icono || "📍"}</div>
      <div class="activity-body">
        <div class="activity-top">
          <h3 class="activity-name">${a.nombre}</h3>
          <span class="activity-rating">★ ${a.calificacion?.toFixed(1) ?? "-"}</span>
        </div>
        <p class="activity-meta">${a.zona || ""} · ${a.horario || ""}</p>
        <p class="activity-desc">${a.descripcion || ""}</p>
        <div class="activity-footer">
          <span class="activity-tag">${a.categoria_nombre || ""}</span>
          <button class="fav-btn ${esFavorito ? "active" : ""}" data-id="${a.id_actividad}">
            ${esFavorito ? "❤️" : "🤍"}
          </button>
        </div>
      </div>
    `;

    card.querySelector(".fav-btn").addEventListener("click", (e) => {
      e.stopPropagation();
      Favoritos.toggle(a.id_actividad, card.querySelector(".fav-btn"));
    });

    return card;
  },
};

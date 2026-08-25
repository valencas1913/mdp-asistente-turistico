// clima.js
// Consulta el clima actual y actualiza el hero + el acento de color global.

const ETIQUETAS_CLIMA = {
  soleado: "☀️ Soleado",
  nublado: "☁️ Nublado",
  lluvia: "🌧️ Lluvia",
  viento: "🌬️ Viento",
};

const Clima = {
  actual: null,

  async cargar() {
    try {
      const data = await Api.getClima();
      this.actual = data;
      this._pintar(data);
      return data;
    } catch (err) {
      console.error("Error cargando clima:", err);
      document.getElementById("weather-desc").textContent =
        "No se pudo conectar con el backend. ¿Está corriendo en " + API_BASE_URL + "?";
      return null;
    }
  },

  _pintar(data) {
    document.body.setAttribute("data-clima", data.condicion || "soleado");

    document.getElementById("weather-temp").innerHTML =
      `${Math.round(data.temperatura)}<sup>°C</sup>`;

    document.getElementById("weather-condicion").textContent =
      ETIQUETAS_CLIMA[data.condicion] || data.condicion;

    document.getElementById("weather-desc").textContent = data.descripcion || "";

    const alerta = document.getElementById("weather-alerta");
    alerta.style.display = data.alerta_vigente ? "block" : "none";

    const fecha = document.getElementById("fecha-actual");
    fecha.textContent = "Mar del Plata, AR";

    const row = document.getElementById("forecast-row");
    row.innerHTML = "";
    (data.pronostico || []).forEach((p) => {
      const chip = document.createElement("div");
      chip.className = "forecast-chip";
      chip.innerHTML = `
        <div class="franja">${p.franja_horaria}</div>
        <div class="temp">${Math.round(p.temperatura)}°</div>
      `;
      row.appendChild(chip);
    });
  },
};

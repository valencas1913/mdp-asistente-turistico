// asistente.js
// Chat con el asistente de IA: arma itinerarios personalizados
// usando el clima actual + las actividades reales del backend.

const Asistente = {
  enviando: false,

  init() {
    const form = document.getElementById("chat-form");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const input = document.getElementById("chat-input");
      const texto = input.value.trim();
      if (!texto) return;
      input.value = "";
      this.enviarMensaje(texto);
    });

    document.querySelectorAll(".suggestion-chip").forEach((chip) => {
      chip.addEventListener("click", () => this.enviarMensaje(chip.dataset.prompt));
    });
  },

  async enviarMensaje(texto) {
    if (this.enviando) return;
    this.enviando = true;

    this._agregarMensaje(texto, "user");
    const loadingEl = this._agregarMensaje("Armando tu itinerario…", "ai loading");

    try {
      const data = await Api.chatAsistente(texto);
      loadingEl.remove();
      this._agregarMensaje(data.respuesta, "ai");
    } catch (err) {
      loadingEl.remove();
      this._agregarMensaje(
        "No pude conectarme con el asistente. Revisá que el backend esté corriendo.",
        "ai"
      );
      console.error(err);
    } finally {
      this.enviando = false;
    }
  },

  _agregarMensaje(texto, clase) {
    const log = document.getElementById("chat-log");
    const div = document.createElement("div");
    div.className = `msg ${clase}`;
    div.textContent = texto;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
    return div;
  },
};

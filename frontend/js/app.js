// app.js
// Orquesta la navegación entre vistas y el arranque general de la app.

const App = {
  vistaActual: "inicio",
  deferredPrompt: null,

  async init() {
    this._initNav();
    this._initInstallPrompt();
    this._registerServiceWorker();

    Favoritos.init();
    Asistente.init();

    await Clima.cargar();
    await Actividades.init();
    await this._cargarInicioExtra();
    await Actividades.cargarInicio();
    await Actividades.cargarListaCompleta();
  },

  _initNav() {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => this.irAVista(btn.dataset.view));
    });
  },

  irAVista(nombre) {
    this.vistaActual = nombre;
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    document.getElementById(`view-${nombre}`).classList.add("active");

    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.view === nombre);
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  },

  async _cargarInicioExtra() {
    try {
      const [tips, contenido] = await Promise.all([
        Api.getTips(),
        Api.getContenidoCiudad(),
      ]);

      const tipsCont = document.getElementById("inicio-tips");
      const tip = tips[Math.floor(Math.random() * tips.length)];
      if (tip) {
        tipsCont.innerHTML = `
          <div class="tip-card">
            <span>${tip.icono}</span>
            <span>${tip.texto}</span>
          </div>`;
      }

      const contCont = document.getElementById("inicio-contenido");
      contCont.innerHTML = "";
      contenido.slice(0, 2).forEach((c) => {
        const div = document.createElement("div");
        div.className = "culture-card";
        div.innerHTML = `
          <div>${c.icono}</div>
          <h4>${c.titulo}</h4>
          <p>${c.descripcion}</p>
        `;
        contCont.appendChild(div);
      });
    } catch (err) {
      console.error("Error cargando contenido de inicio:", err);
    }
  },

  _initInstallPrompt() {
    const banner = document.getElementById("install-banner");
    const btn = document.getElementById("install-btn");
    const dismiss = document.getElementById("install-dismiss");

    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      this.deferredPrompt = e;
      if (!localStorage.getItem("mdp_install_dismissed")) {
        banner.classList.add("show");
      }
    });

    btn.addEventListener("click", async () => {
      if (!this.deferredPrompt) return;
      this.deferredPrompt.prompt();
      await this.deferredPrompt.userChoice;
      this.deferredPrompt = null;
      banner.classList.remove("show");
    });

    dismiss.addEventListener("click", () => {
      banner.classList.remove("show");
      localStorage.setItem("mdp_install_dismissed", "1");
    });
  },

  _registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      window.addEventListener("load", () => {
        navigator.serviceWorker.register("service-worker.js").catch((err) => {
          console.warn("No se pudo registrar el service worker:", err);
        });
      });
    }
  },
};

document.addEventListener("DOMContentLoaded", () => App.init());

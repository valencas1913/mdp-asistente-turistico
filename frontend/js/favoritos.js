// favoritos.js
// Auth mínima (registro/login) + guardado de favoritos por usuario.
// El usuario logueado se persiste en memoria + localStorage del navegador.

const Favoritos = {
  usuario: null,
  lista: [],
  modo: "registro", // "registro" | "login"

  init() {
    const guardado = localStorage.getItem("mdp_usuario");
    if (guardado) {
      try {
        this.usuario = JSON.parse(guardado);
      } catch (e) {
        this.usuario = null;
      }
    }
    this._renderAuth();
    if (this.usuario) this.cargarFavoritos();

    document.getElementById("auth-registro-btn").addEventListener("click", () => this._submit());
    document.getElementById("auth-tab-registro").addEventListener("click", () => this._cambiarModo("registro"));
    document.getElementById("auth-tab-login").addEventListener("click", () => this._cambiarModo("login"));
    document.getElementById("auth-logout-btn").addEventListener("click", () => this._logout());

    ["auth-nombre", "auth-email", "auth-password"].forEach((id) => {
      document.getElementById(id).addEventListener("keydown", (e) => {
        if (e.key === "Enter") this._submit();
      });
    });
  },

  _cambiarModo(modo) {
    this.modo = modo;
    const esRegistro = modo === "registro";

    document.getElementById("auth-tab-registro").classList.toggle("active", esRegistro);
    document.getElementById("auth-tab-login").classList.toggle("active", !esRegistro);
    document.getElementById("auth-field-nombre").style.display = esRegistro ? "flex" : "none";
    document.getElementById("auth-registro-btn").textContent = esRegistro ? "Crear cuenta" : "Iniciar sesión";
  },

  async _submit() {
    const nombre = document.getElementById("auth-nombre").value.trim();
    const email = document.getElementById("auth-email").value.trim();
    const password = document.getElementById("auth-password").value;
    const esRegistro = this.modo === "registro";

    if (!email || !password || (esRegistro && !nombre)) {
      alert("Completá todos los campos.");
      return;
    }

    try {
      const usuario = esRegistro
        ? await Api.registrarUsuario(nombre, email, password)
        : await Api.loginUsuario(email, password);

      this.usuario = usuario;
      localStorage.setItem("mdp_usuario", JSON.stringify(usuario));
      this._renderAuth();
      this.cargarFavoritos();
    } catch (err) {
      alert(err.message || "Ocurrió un error.");
    }
  },

  _logout() {
    this.usuario = null;
    this.lista = [];
    localStorage.removeItem("mdp_usuario");
    this._renderAuth();
    document.getElementById("favoritos-list").innerHTML = "";
  },

  _renderAuth() {
    const loggedOut = document.getElementById("auth-logged-out");
    const loggedIn = document.getElementById("auth-logged-in");

    if (this.usuario) {
      loggedOut.style.display = "none";
      loggedIn.style.display = "block";
      document.getElementById("auth-user-nombre").textContent = this.usuario.nombre;
      document.getElementById("auth-user-email").textContent = this.usuario.email;
      document.getElementById("profile-avatar").textContent = (this.usuario.nombre || "?").charAt(0);
    } else {
      loggedOut.style.display = "block";
      loggedIn.style.display = "none";
      this._cambiarModo(this.modo);
    }
  },

  async cargarFavoritos() {
    if (!this.usuario) return;
    try {
      this.lista = await Api.getFavoritos(this.usuario.id_usuario);
      this._renderLista();
    } catch (err) {
      console.error("Error cargando favoritos:", err);
    }
  },

  esFavorito(idActividad) {
    return this.lista.some((f) => f.id_actividad === idActividad);
  },

  async toggle(idActividad, btnEl) {
    if (!this.usuario) {
      alert("Creá una cuenta o iniciá sesión para guardar favoritos.");
      App.irAVista("favoritos");
      return;
    }

    const existente = this.lista.find((f) => f.id_actividad === idActividad);
    try {
      if (existente) {
        await Api.quitarFavorito(existente.id_favorito);
        this.lista = this.lista.filter((f) => f.id_favorito !== existente.id_favorito);
        btnEl.classList.remove("active");
        btnEl.textContent = "🤍";
      } else {
        const nuevo = await Api.agregarFavorito(this.usuario.id_usuario, idActividad);
        this.lista.push(nuevo);
        btnEl.classList.add("active");
        btnEl.textContent = "❤️";
      }
      this._renderLista();
    } catch (err) {
      console.error("Error actualizando favorito:", err);
    }
  },

  _renderLista() {
    const cont = document.getElementById("favoritos-list");
    cont.innerHTML = "";

    const contador = document.getElementById("profile-fav-count");
    if (contador) contador.textContent = this.lista.length;

    if (!this.usuario) return;

    if (!this.lista.length) {
      cont.innerHTML = `
        <div class="empty-state">
          <div class="glyph">🤍</div>
          <p>Todavía no guardaste actividades favoritas.</p>
        </div>`;
      return;
    }

    this.lista.forEach((f) => {
      if (!f.actividad) return;
      const card = Actividades._card(f.actividad);
      cont.appendChild(card);
    });
  },
};

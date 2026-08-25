// favoritos.js
// Auth mínima (registro/login) + guardado de favoritos por usuario.
// El usuario logueado se persiste en memoria + localStorage del navegador
// (no confundir con el storage de Artifacts: esto es una PWA real).

const Favoritos = {
  usuario: null,
  lista: [], // [{id_favorito, id_actividad, ...}]
  modoLogin: false,

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
    document.getElementById("auth-login-toggle").addEventListener("click", () => this._toggleModo());
    document.getElementById("auth-logout-btn").addEventListener("click", () => this._logout());
  },

  _toggleModo() {
    this.modoLogin = !this.modoLogin;
    const btn = document.getElementById("auth-registro-btn");
    const toggle = document.getElementById("auth-login-toggle");
    const nombreInput = document.getElementById("auth-nombre");
    if (this.modoLogin) {
      btn.textContent = "Iniciar sesión";
      toggle.textContent = "No tengo cuenta, crear una";
      nombreInput.style.display = "none";
    } else {
      btn.textContent = "Crear cuenta";
      toggle.textContent = "Ya tengo cuenta, iniciar sesión";
      nombreInput.style.display = "block";
    }
  },

  async _submit() {
    const nombre = document.getElementById("auth-nombre").value.trim();
    const email = document.getElementById("auth-email").value.trim();
    const password = document.getElementById("auth-password").value;

    if (!email || !password || (!this.modoLogin && !nombre)) {
      alert("Completá todos los campos.");
      return;
    }

    try {
      const usuario = this.modoLogin
        ? await Api.loginUsuario(email, password)
        : await Api.registrarUsuario(nombre, email, password);

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
    } else {
      loggedOut.style.display = "block";
      loggedIn.style.display = "none";
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

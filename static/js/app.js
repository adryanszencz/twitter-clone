// Cliente da API REST do Piu: guarda o token no navegador e monta os componentes das páginas.

const Piu = (() => {
  const TOKEN_KEY = "piu-token";
  const USER_KEY = "piu-user";

  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch { /* navegador sem storage */ } },
    remove(key) { try { localStorage.removeItem(key); } catch { /* navegador sem storage */ } },
  };

  const token = () => storage.get(TOKEN_KEY);
  const currentUser = () => JSON.parse(storage.get(USER_KEY) || "null");

  function saveSession({ token: t, user }) {
    storage.set(TOKEN_KEY, t);
    storage.set(USER_KEY, JSON.stringify(user));
  }

  function clearSession() {
    storage.remove(TOKEN_KEY);
    storage.remove(USER_KEY);
  }

  // páginas que exigem login chamam isto logo no início
  function requireLogin() {
    if (!token()) {
      window.location.href = "/login/";
      return false;
    }
    return true;
  }

  async function api(path, { method = "GET", body, form } = {}) {
    const headers = {};
    if (token()) headers.Authorization = `Token ${token()}`;
    let payload;
    if (form) payload = form;
    else if (body !== undefined) {
      headers["Content-Type"] = "application/json";
      payload = JSON.stringify(body);
    }
    const response = await fetch(path.startsWith("http") ? path : `/api${path}`, { method, headers, body: payload });
    if (response.status === 401) {
      clearSession();
      window.location.href = "/login/";
      throw new Error("Sessão expirada");
    }
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) {
      const error = new Error(firstError(data));
      error.data = data;
      throw error;
    }
    return data;
  }

  function firstError(data) {
    if (!data) return "Algo deu errado. Tente de novo.";
    if (typeof data.detail === "string") return data.detail;
    const values = Object.values(data).flat();
    return values.length ? String(values[0]) : "Algo deu errado. Tente de novo.";
  }

  function el(tag, attrs = {}, ...children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(attrs)) {
      if (key === "class") node.className = value;
      else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
      else if (value !== undefined && value !== null && value !== false) node.setAttribute(key, value);
    }
    for (const child of children.flat()) {
      if (child === null || child === undefined || child === false) continue;
      node.append(child instanceof Node ? child : document.createTextNode(String(child)));
    }
    return node;
  }

  function avatar(user, big = false) {
    const cls = `avatar${big ? " big" : ""}`;
    if (user.avatar) return el("img", { class: cls, src: user.avatar, alt: user.display_name });
    return el("div", { class: `${cls} avatar-fallback`, "aria-hidden": "true" }, (user.display_name || "?")[0].toUpperCase());
  }

  function timeAgo(iso) {
    const seconds = Math.floor((Date.now() - new Date(iso)) / 1000);
    if (seconds < 60) return "agora";
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} h`;
    return new Date(iso).toLocaleDateString("pt-BR", { day: "2-digit", month: "short" });
  }

  function postCard(post, { onDelete } = {}) {
    const likeButton = el("button", { class: `action${post.liked_by_me ? " liked" : ""}`, title: "Curtir" });
    const renderLike = () => { likeButton.textContent = `${post.liked_by_me ? "♥" : "♡"} ${post.likes_count}`; };
    renderLike();
    likeButton.addEventListener("click", async () => {
      likeButton.disabled = true;
      try {
        const result = await api(`/posts/${post.id}/like/`, { method: post.liked_by_me ? "DELETE" : "POST" });
        post.liked_by_me = result.liked;
        post.likes_count = result.likes_count;
        likeButton.classList.toggle("liked", post.liked_by_me);
        renderLike();
      } finally {
        likeButton.disabled = false;
      }
    });

    const actions = el("div", { class: "post-actions" },
      likeButton,
      el("a", { class: "action", href: `/post/${post.id}/`, title: "Comentários" }, `💬 ${post.comments_count}`),
    );
    if (post.is_mine) {
      actions.append(el("button", {
        class: "action",
        onclick: async () => {
          if (!confirm("Apagar este post?")) return;
          await api(`/posts/${post.id}/`, { method: "DELETE" });
          card.remove();
          if (onDelete) onDelete(post);
        },
      }, "🗑 Apagar"));
    }

    const author = post.author;
    const card = el("article", { class: "card post" },
      el("a", { href: `/u/${author.username}/` }, avatar(author)),
      el("div", { class: "post-body" },
        el("div", { class: "post-head" },
          el("a", { href: `/u/${author.username}/` }, el("strong", {}, author.display_name)),
          el("span", { class: "muted" }, `@${author.username} · ${timeAgo(post.created_at)}`),
        ),
        el("p", { class: "post-content" }, post.content),
        actions,
      ),
    );
    return card;
  }

  function personRow(user) {
    const button = el("button", { class: user.is_following ? "btn outline" : "btn" }, user.is_following ? "Seguindo" : "Seguir");
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await api(`/users/${user.username}/follow/`, { method: user.is_following ? "DELETE" : "POST" });
        user.is_following = !user.is_following;
        button.className = user.is_following ? "btn outline" : "btn";
        button.textContent = user.is_following ? "Seguindo" : "Seguir";
      } finally {
        button.disabled = false;
      }
    });
    const me = currentUser();
    return el("div", { class: "card person" },
      el("a", { href: `/u/${user.username}/` }, avatar(user)),
      el("div", { class: "info" },
        el("a", { href: `/u/${user.username}/` }, el("strong", {}, user.display_name)),
        el("div", { class: "muted" }, `@${user.username}`),
        user.bio ? el("div", {}, user.bio) : null,
      ),
      me && me.username === user.username ? null : button,
    );
  }

  // lista paginada da API: busca a página, desenha cada item e mostra "Carregar mais" se houver next
  async function paginatedList(container, firstUrl, render, emptyText) {
    let next = firstUrl;
    const more = el("button", { class: "btn outline", style: "display:block;margin:0 auto 16px" }, "Carregar mais");
    async function load() {
      more.disabled = true;
      const page = await api(next);
      if (!page.results.length && !container.childElementCount) {
        container.append(el("p", { class: "card empty" }, emptyText));
      }
      page.results.forEach((item) => container.append(render(item)));
      next = page.next;
      more.disabled = false;
      if (next) container.after(more); else more.remove();
    }
    more.addEventListener("click", load);
    await load();
  }

  function fillSidebar() {
    const user = currentUser();
    const slot = document.getElementById("me");
    if (!user || !slot) return;
    slot.replaceChildren(avatar(user), el("div", {}, el("strong", {}, user.display_name), el("div", { class: "muted" }, `@${user.username}`)));
    const profileLink = document.getElementById("nav-profile");
    if (profileLink) profileLink.href = `/u/${user.username}/`;
    const logout = document.getElementById("logout");
    if (logout) {
      logout.addEventListener("click", async (event) => {
        event.preventDefault();
        try { await api("/auth/logout/", { method: "POST" }); } catch { /* token já inválido */ }
        clearSession();
        window.location.href = "/login/";
      });
    }
  }

  return { api, token, currentUser, saveSession, clearSession, requireLogin, el, avatar, postCard, personRow, paginatedList, fillSidebar };
})();

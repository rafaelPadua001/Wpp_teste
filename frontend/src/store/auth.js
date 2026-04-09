const TOKEN_KEY = "wpp_vue_access_token";
const REFRESH_KEY = "wpp_vue_refresh_token";
const USER_KEY = "wpp_vue_user";

export const authStore = {
  state: {
    accessToken: "",
    refreshToken: "",
    user: null,
  },
  hydrate() {
    this.state.accessToken = localStorage.getItem(TOKEN_KEY) || "";
    this.state.refreshToken = localStorage.getItem(REFRESH_KEY) || "";
    const rawUser = localStorage.getItem(USER_KEY);
    this.state.user = rawUser ? JSON.parse(rawUser) : decodeToken(this.state.accessToken);
  },
  setSession(tokens, fallbackEmail = "") {
    this.state.accessToken = tokens.access_token;
    this.state.refreshToken = tokens.refresh_token || "";
    const payload = decodeToken(tokens.access_token);
    this.state.user = {
      id: payload?.user_id || null,
      tenantId: payload?.tenant_id || null,
      role: payload?.role || "user",
      email: fallbackEmail,
      name: fallbackEmail || "Usuario",
      whatsapp: "",
    };
    localStorage.setItem(TOKEN_KEY, this.state.accessToken);
    localStorage.setItem(REFRESH_KEY, this.state.refreshToken);
    localStorage.setItem(USER_KEY, JSON.stringify(this.state.user));
  },
  updateUser(user) {
    this.state.user = {
      ...this.state.user,
      ...user,
      tenantId: user.tenant_id ?? user.tenantId ?? this.state.user?.tenantId ?? null,
    };
    localStorage.setItem(USER_KEY, JSON.stringify(this.state.user));
  },
  clear() {
    this.state.accessToken = "";
    this.state.refreshToken = "";
    this.state.user = null;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
  },
  isAuthenticated() {
    return Boolean(this.state.accessToken);
  },
  isAdmin() {
    return this.state.user?.role === "admin";
  },
};

function decodeToken(token) {
  if (!token) return null;
  try {
    const [, payload] = token.split(".");
    const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
    return JSON.parse(window.atob(normalized));
  } catch {
    return null;
  }
}

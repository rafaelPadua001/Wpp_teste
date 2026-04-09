import { createRouter, createWebHistory } from "vue-router";
import { authStore } from "@/store/auth";
import LoginView from "@/views/LoginView.vue";
import DashboardView from "@/views/DashboardView.vue";
import ContactsView from "@/views/ContactsView.vue";
import MessagesView from "@/views/MessagesView.vue";
import ProfileView from "@/views/ProfileView.vue";
import AdminUsersView from "@/views/AdminUsersView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/dashboard" },
    { path: "/login", name: "login", component: LoginView, meta: { guestOnly: true } },
    { path: "/dashboard", name: "dashboard", component: DashboardView, meta: { requiresAuth: true } },
    { path: "/contacts", name: "contacts", component: ContactsView, meta: { requiresAuth: true } },
    { path: "/messages", name: "messages", component: MessagesView, meta: { requiresAuth: true } },
    { path: "/profile", name: "profile", component: ProfileView, meta: { requiresAuth: true } },
    {
      path: "/admin",
      name: "admin",
      component: AdminUsersView,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
});

router.beforeEach((to) => {
  const authenticated = authStore.isAuthenticated();
  if (to.meta.requiresAuth && !authenticated) {
    return { name: "login" };
  }
  if (to.meta.guestOnly && authenticated) {
    return { name: "dashboard" };
  }
  if (to.meta.requiresAdmin && !authStore.isAdmin()) {
    return { name: "dashboard" };
  }
  return true;
});

export default router;

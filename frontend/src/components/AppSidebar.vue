<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { authStore } from "@/store/auth";

const props = defineProps({
  rail: Boolean,
});

const route = useRoute();
const router = useRouter();

const items = computed(() => {
  const base = [
    { title: "Dashboard", icon: "mdi-view-dashboard-outline", to: "/dashboard" },
    { title: "Contatos", icon: "mdi-account-multiple-outline", to: "/contacts" },
    { title: "Profile", icon: "mdi-account-circle-outline", to: "/profile" },
  ];

  if (authStore.isAdmin()) {
    base.push({ title: "Admin", icon: "mdi-shield-account-outline", to: "/admin" });
  }

  return base;
});

function logout() {
  authStore.clear();
  router.push("/login");
}
</script>

<template>
  <v-navigation-drawer
    :rail="props.rail"
    permanent
    color="#020617"
    width="276"
    class="soft-border"
  >
    <div class="pa-4 d-flex align-center ga-3">
      <v-avatar size="44" color="primary" rounded="xl">W</v-avatar>
      <div v-if="!props.rail">
        <div class="text-subtitle-1 font-weight-bold">WhatsApp SaaS</div>
        <div class="text-caption text-medium-emphasis">
          Tenant {{ authStore.state.user?.tenantId || "-" }}
        </div>
      </div>
    </div>

    <v-list nav density="comfortable" class="px-2">
      <v-list-item
        v-for="item in items"
        :key="item.to"
        :title="item.title"
        :prepend-icon="item.icon"
        :active="route.path === item.to"
        rounded="xl"
        color="primary"
        @click="router.push(item.to)"
      />

      <v-list-group value="messages" color="primary">
        <template #activator="{ props: groupProps }">
          <v-list-item
            v-bind="groupProps"
            prepend-icon="mdi-message-text-outline"
            title="Mensagens"
            rounded="xl"
            color="primary"
            :active="route.path === '/messages'"
          />
        </template>

        <v-list-item
          title="Enviar mensagens"
          rounded="xl"
          color="primary"
          :active="route.path === '/messages' && route.query.tab !== 'history'"
          @click="router.push({ path: '/messages', query: { tab: 'send' } })"
        />
        <v-list-item
          title="Historico"
          rounded="xl"
          color="primary"
          :active="route.path === '/messages' && route.query.tab === 'history'"
          @click="router.push({ path: '/messages', query: { tab: 'history' } })"
        />
      </v-list-group>
    </v-list>

    <template #append>
      <div class="pa-4">
        <v-card class="glass-card pa-4">
          <div class="text-body-2 font-weight-bold">Sessao ativa</div>
          <div class="text-caption text-medium-emphasis mt-1">
            {{ authStore.isAdmin() ? "Administrador conectado" : "Operador conectado" }}
          </div>
          <v-btn
            class="mt-4"
            block
            variant="tonal"
            color="primary"
            prepend-icon="mdi-logout"
            @click="logout"
          >
            Logout
          </v-btn>
        </v-card>
      </div>
    </template>
  </v-navigation-drawer>
</template>

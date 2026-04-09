<script setup>
import { onMounted, reactive, ref } from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api from "@/services/api";

const loading = ref(true);
const dashboard = reactive({
  total_users: 0,
  total_contacts: 0,
  total_messages: 0,
  messages_used: 0,
  message_limit: 0,
});
const messages = ref([]);
const snackbar = reactive({ show: false, text: "", color: "success" });

function notify(text, color = "success") {
  snackbar.show = true;
  snackbar.text = text;
  snackbar.color = color;
}

async function loadData() {
  loading.value = true;
  try {
    const [dashboardResponse, messagesResponse] = await Promise.all([
      api.get("/dashboard"),
      api.get("/messages"),
    ]);
    Object.assign(dashboard, dashboardResponse.data);
    messages.value = messagesResponse.data;
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel carregar o dashboard.", "error");
  } finally {
    loading.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <AppLayout
    title="Dashboard"
    subtitle="Visão geral do tenant com métricas e atividade recente."
  >
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="glass-card pa-6">
          <div class="text-body-2 text-medium-emphasis">Total de contatos</div>
          <div class="metric-value mt-3">{{ dashboard.total_contacts }}</div>
          <div class="text-caption text-info mt-3">Base ativa do tenant</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="glass-card pa-6">
          <div class="text-body-2 text-medium-emphasis">Mensagens registradas</div>
          <div class="metric-value mt-3">{{ dashboard.total_messages }}</div>
          <div class="text-caption text-info mt-3">Histórico operacional</div>
        </v-card>
      </v-col>
      <v-col cols="12" md="4">
        <v-card class="glass-card pa-6">
          <div class="text-body-2 text-medium-emphasis">Consumo do plano</div>
          <div class="metric-value mt-3">{{ dashboard.messages_used }}/{{ dashboard.message_limit }}</div>
          <div class="text-caption text-info mt-3">Capacidade usada até agora</div>
        </v-card>
      </v-col>
    </v-row>

    <v-row class="mt-2">
      <v-col cols="12" md="7">
        <v-card class="glass-card pa-6">
          <div class="section-heading">
            <div>
              <div class="text-h6 font-weight-bold">Status recentes</div>
              <div class="section-subtitle">Últimos envios e comportamento da operação.</div>
            </div>
            <v-btn variant="tonal" color="primary" @click="loadData">Atualizar</v-btn>
          </div>

          <v-skeleton-loader
            v-if="loading"
            type="list-item-two-line, list-item-two-line, list-item-two-line"
            color="surface"
          />

          <v-list v-else bg-color="transparent" lines="two">
            <template v-if="messages.length">
              <v-list-item
                v-for="message in messages.slice(0, 6)"
                :key="message.id"
                class="soft-border rounded-xl mb-3"
              >
                <template #title>
                  <div class="d-flex justify-space-between align-center">
                    <span>{{ message.phone }}</span>
                    <v-chip :color="message.status === 'sent' ? 'success' : 'warning'" size="small" rounded="pill">
                      {{ message.status }}
                    </v-chip>
                  </div>
                </template>
                <template #subtitle>
                  <div>{{ message.content }}</div>
                  <div class="text-caption text-medium-emphasis mt-1">{{ message.created_at }}</div>
                </template>
              </v-list-item>
            </template>
            <v-list-item v-else title="Sem atividade ainda" subtitle="Os próximos envios aparecerão aqui." />
          </v-list>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card class="glass-card pa-6 h-100">
          <div class="text-h6 font-weight-bold mb-2">Resumo operacional</div>
          <div class="section-subtitle mb-6">Uma leitura rápida do ambiente atual.</div>

          <v-list bg-color="transparent">
            <v-list-item class="soft-border rounded-xl mb-3">
              <template #title>Usuários</template>
              <template #subtitle>{{ dashboard.total_users }} usuários com acesso ao tenant.</template>
            </v-list-item>
            <v-list-item class="soft-border rounded-xl mb-3">
              <template #title>Contatos</template>
              <template #subtitle>{{ dashboard.total_contacts }} contatos prontos para ação.</template>
            </v-list-item>
            <v-list-item class="soft-border rounded-xl">
              <template #title>Capacidade restante</template>
              <template #subtitle>{{ Math.max(dashboard.message_limit - dashboard.messages_used, 0) }} envios disponíveis.</template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </AppLayout>
</template>

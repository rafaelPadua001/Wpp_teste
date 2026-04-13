<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api, { messageApi } from "@/services/api";

const route = useRoute();
const router = useRouter();

const loading = ref(true);
const sending = ref(false);
const clearing = ref(false);
const contacts = ref([]);
const messages = ref([]);
const selectedContacts = ref([]);
const selectAll = ref(false);
const historyPage = ref(1);
const historyPerPage = 10;
const form = reactive({
  content: "",
  delay_seconds: 0,
});
const snackbar = reactive({ show: false, text: "", color: "success" });

const activeTab = computed({
  get: () => (route.query.tab === "history" ? "history" : "send"),
  set: (value) => {
    router.replace({ path: "/messages", query: { tab: value } });
  },
});

const recentMessages = computed(() => messages.value.slice(0, 10));
const totalHistoryPages = computed(() => Math.max(Math.ceil(messages.value.length / historyPerPage), 1));
const paginatedHistory = computed(() => {
  const start = (historyPage.value - 1) * historyPerPage;
  return messages.value.slice(start, start + historyPerPage);
});

watch(activeTab, () => {
  historyPage.value = 1;
});

watch(selectedContacts, (newValue) => {
  const total = contacts.value.length;
  if (!total) {
    selectAll.value = false;
    return;
  }
  selectAll.value = newValue.length === total;
});

watch(contacts, (newValue) => {
  if (!newValue.length) {
    selectAll.value = false;
    selectedContacts.value = [];
  } else if (selectAll.value) {
    selectedContacts.value = newValue.map((contact) => contact.id);
  }
});

function notify(text, color = "success") {
  snackbar.show = true;
  snackbar.text = text;
  snackbar.color = color;
}

function toggleSelectAll() {
  if (selectAll.value) {
    selectedContacts.value = contacts.value.map((contact) => contact.id);
  } else {
    selectedContacts.value = [];
  }
}

async function loadData() {
  loading.value = true;
  try {
    const [contactsResponse, messagesResponse] = await Promise.all([
      api.get("/contacts"),
      messageApi.list(),
    ]);
    contacts.value = contactsResponse.data;
    messages.value = messagesResponse.data;
    if (historyPage.value > totalHistoryPages.value) {
      historyPage.value = totalHistoryPages.value;
    }
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel carregar mensagens e contatos.", "error");
  } finally {
    loading.value = false;
  }
}

async function sendMessages() {
  if (!selectedContacts.value.length) {
    notify("Selecione pelo menos um contato.", "warning");
    return;
  }

  sending.value = true;
  try {
    await api.post("/messages/bulk", {
      content: form.content,
      delay_seconds: Number(form.delay_seconds || 0),
      contact_ids: selectedContacts.value,
    });
    notify("Disparo enviado com sucesso.");
    form.content = "";
    form.delay_seconds = 0;
    selectedContacts.value = [];
    await loadData();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel enviar as mensagens.", "error");
  } finally {
    sending.value = false;
  }
}

async function clearHistory() {
  clearing.value = true;
  try {
    await messageApi.clear();
    messages.value = [];
    historyPage.value = 1;
    notify("Histórico limpo com sucesso");
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel limpar o histórico.", "error");
  } finally {
    clearing.value = false;
  }
}

onMounted(loadData);
</script>

<template>
  <AppLayout
    title="Mensagens"
    subtitle="Envie campanhas, acompanhe resultados e navegue pelo histórico com clareza."
  >
    <v-card class="glass-card pa-3 mb-6">
      <v-tabs v-model="activeTab" color="primary" grow>
        <v-tab value="send">Enviar mensagens</v-tab>
        <v-tab value="history">Histórico</v-tab>
      </v-tabs>
    </v-card>

    <v-window v-model="activeTab">
      <v-window-item value="send">
        <v-row>
          <v-col cols="12" md="5">
            <v-card class="glass-card pa-6">
              <div class="text-h6 font-weight-bold mb-2">Novo disparo</div>
              <div class="section-subtitle mb-6">
                Selecione contatos, escreva a campanha e envie com segurança.
              </div>

              <v-form @submit.prevent="sendMessages">
                <v-textarea v-model="form.content" label="Mensagem" rows="6" required />
                <v-text-field
                  v-model="form.delay_seconds"
                  label="Delay entre envios (segundos)"
                  type="number"
                  min="0"
                  max="5"
                />

                <v-card class="glass-card pa-4 mb-4">
                  <div class="text-subtitle-2 font-weight-bold mb-3">Contatos disponíveis</div>
                  <v-progress-linear v-if="loading" indeterminate color="primary" />
                  <v-checkbox
                    v-model="selectAll"
                    label="Selecionar todos"
                    :disabled="loading || !contacts.length"
                    @change="toggleSelectAll"
                    hide-details
                    color="primary"
                    class="mb-2"
                  />
                  <v-checkbox
                    v-for="contact in contacts"
                    :key="contact.id"
                    v-model="selectedContacts"
                    :label="`${contact.name} · ${contact.phone}`"
                    :value="contact.id"
                    hide-details
                    color="primary"
                  />
                  <div v-if="!loading && !contacts.length" class="text-body-2 text-medium-emphasis">
                    Cadastre contatos antes de disparar.
                  </div>
                </v-card>

                <v-btn type="submit" color="primary" block size="large" :loading="sending">
                  Enviar mensagens
                </v-btn>
              </v-form>
            </v-card>
          </v-col>

          <v-col cols="12" md="7">
            <v-card class="glass-card pa-6">
              <div class="section-heading">
                <div>
                  <div class="text-h6 font-weight-bold">Mensagens recentes</div>
                  <div class="section-subtitle">Últimas 10 tentativas de envio do usuário logado.</div>
                </div>
                <v-btn variant="tonal" color="primary" @click="loadData">Atualizar</v-btn>
              </div>

              <v-skeleton-loader
                v-if="loading"
                type="list-item-two-line, list-item-two-line, list-item-two-line"
                color="surface"
              />

              <v-list v-else bg-color="transparent">
                <v-list-item
                  v-for="message in recentMessages"
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
                    <div class="mt-1">{{ message.content }}</div>
                    <div class="text-caption text-medium-emphasis mt-1">
                      {{ message.created_at }}
                      <span v-if="message.error_message"> · {{ message.error_message }}</span>
                    </div>
                  </template>
                </v-list-item>

                <v-list-item
                  v-if="!recentMessages.length"
                  title="Sem mensagens ainda"
                  subtitle="As novas campanhas aparecerão aqui."
                />
              </v-list>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

      <v-window-item value="history">
        <v-card class="glass-card pa-6">
          <div class="section-heading">
            <div>
              <div class="text-h6 font-weight-bold">Histórico completo</div>
              <div class="section-subtitle">Todas as mensagens visíveis do usuário, com paginação.</div>
            </div>
            <div class="d-flex ga-3">
              <v-btn variant="tonal" color="primary" @click="loadData">Atualizar</v-btn>
              <v-btn variant="flat" color="error" :loading="clearing" @click="clearHistory">
                Limpar histórico
              </v-btn>
            </div>
          </div>

          <v-skeleton-loader
            v-if="loading"
            type="list-item-two-line, list-item-two-line, list-item-two-line"
            color="surface"
          />

          <template v-else>
            <v-list bg-color="transparent">
              <v-list-item
                v-for="message in paginatedHistory"
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
                  <div class="mt-1">{{ message.content }}</div>
                  <div class="text-caption text-medium-emphasis mt-1">
                    {{ message.created_at }}
                    <span v-if="message.error_message"> · {{ message.error_message }}</span>
                  </div>
                </template>
              </v-list-item>

              <v-list-item
                v-if="!paginatedHistory.length"
                title="Histórico vazio"
                subtitle="Não há mensagens ativas para mostrar."
              />
            </v-list>

            <div class="d-flex justify-end mt-4">
              <v-pagination
                v-model="historyPage"
                :length="totalHistoryPages"
                rounded="circle"
                color="primary"
              />
            </div>
          </template>
        </v-card>
      </v-window-item>
    </v-window>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </AppLayout>
</template>

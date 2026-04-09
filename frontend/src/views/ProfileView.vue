<script setup>
import { onMounted, reactive } from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api from "@/services/api";
import { authStore } from "@/store/auth";

const user = authStore.state.user || {};
const form = reactive({
  name: user.name || "",
  email: user.email || "",
  whatsapp: user.whatsapp || "",
  password: "",
});
const snackbar = reactive({ show: false, text: "", color: "success" });
const loading = reactive({ save: false });
const summary = reactive({
  company_name: "",
});

function notify(text, color = "success") {
  snackbar.show = true;
  snackbar.text = text;
  snackbar.color = color;
}

async function saveProfile() {
  loading.save = true;
  try {
    const payload = {
      name: form.name,
      email: form.email,
      whatsapp: form.whatsapp || null,
    };
    if (form.password) {
      payload.password = form.password;
    }

    const { data } = await api.put(`/users/${user.id}`, payload);
    authStore.updateUser(data);
    form.password = "";
    notify("Perfil atualizado com sucesso.");
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel atualizar o perfil.", "error");
  } finally {
    loading.save = false;
  }
}

async function loadSummary() {
  try {
    const { data } = await api.get("/dashboard");
    summary.company_name = data.tenant_name || "";
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel carregar o resumo da conta.", "error");
  }
}

onMounted(loadSummary);
</script>

<template>
  <AppLayout
    title="Profile"
    subtitle="Atualize seus dados pessoais e mantenha a conta sincronizada."
  >
    <v-row>
      <v-col cols="12" md="7">
        <v-card class="glass-card pa-6">
          <div class="text-h6 font-weight-bold mb-2">Editar perfil</div>
          <div class="section-subtitle mb-6">Seu usuário opera dentro do tenant autenticado.</div>

          <v-form @submit.prevent="saveProfile">
            <v-text-field v-model="form.name" label="Nome" required />
            <v-text-field v-model="form.email" label="E-mail" type="email" required />
            <v-text-field v-model="form.whatsapp" label="WhatsApp" />
            <v-text-field v-model="form.password" label="Nova senha" type="password" />
            <v-btn type="submit" color="primary" size="large" :loading="loading.save">
              Salvar alterações
            </v-btn>
          </v-form>
        </v-card>
      </v-col>

      <v-col cols="12" md="5">
        <v-card class="glass-card pa-6 h-100">
          <div class="text-h6 font-weight-bold mb-4">Resumo da conta</div>
          <v-list bg-color="transparent">
            <v-list-item class="soft-border rounded-xl mb-3" title="Nome" :subtitle="form.name || '-'" />
            <v-list-item class="soft-border rounded-xl mb-3" title="Email" :subtitle="form.email || '-'" />
            <v-list-item class="soft-border rounded-xl mb-3" title="Empresa" :subtitle="summary.company_name || '-'" />
            <v-list-item class="soft-border rounded-xl" title="WhatsApp" :subtitle="form.whatsapp || '-'" />
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </AppLayout>
</template>

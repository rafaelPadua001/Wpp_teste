<script setup>
import { onMounted, reactive, ref } from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api from "@/services/api";
import { authStore } from "@/store/auth";

const loading = ref(true);
const saving = ref(false);
const users = ref([]);
const editingId = ref(null);
const snackbar = reactive({ show: false, text: "", color: "success" });
const form = reactive({
  name: "",
  email: "",
  whatsapp: "",
  role: "user",
  password: "",
});

function notify(text, color = "success") {
  snackbar.show = true;
  snackbar.text = text;
  snackbar.color = color;
}

function resetForm() {
  editingId.value = null;
  form.name = "";
  form.email = "";
  form.whatsapp = "";
  form.role = "user";
  form.password = "";
}

function editUser(user) {
  editingId.value = user.id;
  form.name = user.name;
  form.email = user.email;
  form.whatsapp = user.whatsapp || "";
  form.role = user.role;
  form.password = "";
}

async function loadUsers() {
  loading.value = true;
  try {
    const { data } = await api.get("/users");
    users.value = data;
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel carregar os usuarios.", "error");
  } finally {
    loading.value = false;
  }
}

async function saveUser() {
  saving.value = true;
  try {
    const payload = {
      name: form.name,
      email: form.email,
      whatsapp: form.whatsapp || null,
      role: form.role,
    };

    if (editingId.value) {
      if (form.password) payload.password = form.password;
      await api.put(`/users/${editingId.value}`, payload);
      notify("Usuario atualizado com sucesso.");
    } else {
      payload.password = form.password;
      await api.post("/users", payload);
      notify("Usuario criado com sucesso.");
    }

    resetForm();
    await loadUsers();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel salvar o usuario.", "error");
  } finally {
    saving.value = false;
  }
}

async function removeUser(id) {
  try {
    await api.delete(`/users/${id}`);
    notify("Usuario removido com sucesso.");
    await loadUsers();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel remover o usuario.", "error");
  }
}

onMounted(loadUsers);
</script>

<template>
  <AppLayout
    title="Admin"
    subtitle="Gerencie usuários internos, papéis e acessos do tenant."
  >
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="glass-card pa-6">
          <div class="text-h6 font-weight-bold mb-2">
            {{ editingId ? "Editar usuario" : "Novo usuario" }}
          </div>
          <div class="section-subtitle mb-6">Administradores podem criar e ajustar acessos internos.</div>

          <v-form @submit.prevent="saveUser">
            <v-text-field v-model="form.name" label="Nome" required />
            <v-text-field v-model="form.email" label="E-mail" type="email" required />
            <v-text-field v-model="form.whatsapp" label="WhatsApp" />
            <v-select
              v-model="form.role"
              label="Papel"
              :items="['user', 'admin']"
            />
            <v-text-field
              v-model="form.password"
              :label="editingId ? 'Nova senha (opcional)' : 'Senha'"
              type="password"
              :required="!editingId"
            />
            <div class="d-flex ga-3">
              <v-btn type="submit" color="primary" :loading="saving">
                {{ editingId ? "Atualizar" : "Salvar" }}
              </v-btn>
              <v-btn v-if="editingId" variant="tonal" color="secondary" @click="resetForm">
                Cancelar
              </v-btn>
            </div>
          </v-form>
        </v-card>
      </v-col>

      <v-col cols="12" md="8">
        <v-card class="glass-card pa-6">
          <div class="section-heading">
            <div>
              <div class="text-h6 font-weight-bold">Usuarios do tenant</div>
              <div class="section-subtitle">Operadores e administradores em uma visão unificada.</div>
            </div>
            <v-btn variant="tonal" color="primary" @click="loadUsers">Atualizar</v-btn>
          </div>

          <v-skeleton-loader
            v-if="loading"
            type="table-heading, table-row-divider@4"
            color="surface"
          />

          <v-table v-else class="soft-border rounded-xl overflow-hidden">
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Papel</th>
                <th>Status</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!users.length">
                <td colspan="5" class="text-center py-8 text-medium-emphasis">
                  Nenhum usuário cadastrado.
                </td>
              </tr>
              <tr v-for="user in users" :key="user.id">
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.role }}</td>
                <td>{{ user.is_active ? "ativo" : "inativo" }}</td>
                <td>
                  <div class="d-flex ga-2">
                    <v-btn size="small" variant="tonal" color="primary" @click="editUser(user)">
                      Editar
                    </v-btn>
                    <v-btn
                      v-if="user.id !== authStore.state.user?.id"
                      size="small"
                      variant="tonal"
                      color="error"
                      @click="removeUser(user.id)"
                    >
                      Remover
                    </v-btn>
                  </div>
                </td>
              </tr>
            </tbody>
          </v-table>
        </v-card>
      </v-col>
    </v-row>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </AppLayout>
</template>

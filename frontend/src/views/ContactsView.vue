<script setup>
import { onMounted, reactive, ref } from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api from "@/services/api";

const loading = ref(true);
const importLoading = ref(false);
const editingId = ref(null);
const contacts = ref([]);
const snackbar = reactive({ show: false, text: "", color: "success" });
const form = reactive({
  name: "",
  phone: "",
  email: "",
  notes: "",
});

function notify(text, color = "success") {
  snackbar.show = true;
  snackbar.text = text;
  snackbar.color = color;
}

function resetForm() {
  editingId.value = null;
  form.name = "";
  form.phone = "";
  form.email = "";
  form.notes = "";
}

function editContact(contact) {
  editingId.value = contact.id;
  form.name = contact.name;
  form.phone = contact.phone;
  form.email = contact.email || "";
  form.notes = contact.notes || "";
}

async function loadContacts() {
  loading.value = true;
  try {
    const { data } = await api.get("/contacts");
    contacts.value = data;
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel carregar os contatos.", "error");
  } finally {
    loading.value = false;
  }
}

async function saveContact() {
  try {
    const payload = {
      name: form.name,
      phone: form.phone,
      email: form.email || null,
      notes: form.notes || null,
    };
    if (editingId.value) {
      await api.put(`/contacts/${editingId.value}`, payload);
      notify("Contato atualizado com sucesso.");
    } else {
      await api.post("/contacts", payload);
      notify("Contato criado com sucesso.");
    }
    resetForm();
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel salvar o contato.", "error");
  }
}

async function removeContact(id) {
  try {
    await api.delete(`/contacts/${id}`);
    notify("Contato removido com sucesso.");
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel remover o contato.", "error");
  }
}

async function importCsv(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  importLoading.value = true;
  try {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await api.post("/contacts/import-csv", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    notify(`${data.length} contatos importados com sucesso.`);
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel importar o CSV.", "error");
  } finally {
    importLoading.value = false;
    event.target.value = "";
  }
}

onMounted(loadContacts);
</script>

<template>
  <AppLayout
    title="Contatos"
    subtitle="Gerencie a base do tenant com criação, edição, exclusão e importação CSV."
  >
    <v-row>
      <v-col cols="12" md="4">
        <v-card class="glass-card pa-6">
          <div class="text-h6 font-weight-bold mb-2">
            {{ editingId ? "Editar contato" : "Novo contato" }}
          </div>
          <div class="section-subtitle mb-6">Crie ou atualize registros rapidamente.</div>

          <v-form @submit.prevent="saveContact">
            <v-text-field v-model="form.name" label="Nome" required />
            <v-text-field v-model="form.phone" label="Telefone" required />
            <v-text-field v-model="form.email" label="E-mail" type="email" />
            <v-textarea v-model="form.notes" label="Notas" rows="4" />

            <div class="d-flex ga-3">
              <v-btn type="submit" color="primary" block>
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
              <div class="text-h6 font-weight-bold">Base de contatos</div>
              <div class="section-subtitle">Importe, edite e organize sua operação.</div>
            </div>
            <div class="d-flex ga-3">
              <v-btn :loading="loading" variant="tonal" color="primary" @click="loadContacts">Atualizar</v-btn>
              <v-file-input
                label="Importar CSV"
                prepend-icon="mdi-upload"
                density="comfortable"
                variant="outlined"
                hide-details
                :loading="importLoading"
                @update:model-value="importCsv"
              />
            </div>
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
                <th>Telefone</th>
                <th>E-mail</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!contacts.length">
                <td colspan="4" class="text-center py-8 text-medium-emphasis">
                  Nenhum contato cadastrado ainda.
                </td>
              </tr>
              <tr v-for="contact in contacts" :key="contact.id">
                <td>{{ contact.name }}</td>
                <td>{{ contact.phone }}</td>
                <td>{{ contact.email || "-" }}</td>
                <td>
                  <div class="d-flex ga-2">
                    <v-btn size="small" variant="tonal" color="primary" @click="editContact(contact)">
                      Editar
                    </v-btn>
                    <v-btn size="small" variant="tonal" color="error" @click="removeContact(contact.id)">
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

<script setup>
import { onMounted, reactive, ref } from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api from "@/services/api";

const loading = ref(true);
const loadingImport = ref(false);
const file = ref(null);
const confirmClear = ref(false);
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

async function clearContacts() {
  try {
    await api.post("/contacts/clear");
    notify("Contatos limpos com sucesso. Voce pode recuperar em ate 48 horas.");
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel limpar os contatos.", "error");
  } finally {
    confirmClear.value = false;
  }
}

async function recoverContacts() {
  try {
    const { data } = await api.post("/contacts/recover");
    notify(`Recuperados ${data.recovered || 0} contatos nas ultimas 48 horas.`);
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel recuperar os contatos.", "error");
  }
}

async function uploadFile() {
  if (!file.value) return;
  loadingImport.value = true;
  try {
    const formData = new FormData();
    const selectedFile = Array.isArray(file.value) ? file.value[0] : file.value;
    formData.append("file", selectedFile);
    const { data } = await api.post("/contacts/import", formData);
    notify(`Importacao concluida: ${data.imported} importados, ${data.skipped} ignorados.`);
    file.value = null;
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel importar a planilha.", "error");
  } finally {
    loadingImport.value = false;
  }
}

onMounted(loadContacts);
</script>

<template>
  <AppLayout
    title="Contatos"
    subtitle="Gerencie a base do tenant com criacao, edicao, exclusao e importacao."
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
              <div class="section-subtitle">Importe, edite e organize sua operacao.</div>
            </div>
            <div class="d-flex ga-3">
              <v-btn :loading="loading" variant="tonal" color="primary" @click="loadContacts">
                Atualizar
              </v-btn>
            </div>
          </div>

          <div class="d-flex flex-wrap align-center ga-3 mb-6">
            <v-file-input
              v-model="file"
              label="Selecionar planilha (.xls, .xlsx)"
              accept=".xls,.xlsx"
              prepend-icon="mdi-file-excel"
              density="comfortable"
              variant="outlined"
              :multiple="false"
              hide-details
              :loading="loadingImport"
            />
            <v-btn
              color="primary"
              class="mt-4"
              :disabled="!file || loadingImport"
              :loading="loadingImport"
              @click="uploadFile"
            >
              Importar contatos
            </v-btn>
            <v-btn
              color="error"
              variant="tonal"
              class="mt-4"
              @click="confirmClear = true"
            >
              Limpar contatos
            </v-btn>
            <v-btn
              color="primary"
              variant="outlined"
              class="mt-4"
              @click="recoverContacts"
            >
              Recuperar contatos (48h)
            </v-btn>
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
                <th>Notas</th>
                <th>Acoes</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!contacts.length">
                <td colspan="5" class="text-center py-8 text-medium-emphasis">
                  Nenhum contato cadastrado ainda.
                </td>
              </tr>
              <tr v-for="contact in contacts" :key="contact.id">
                <td>{{ contact.name }}</td>
                <td>{{ contact.phone }}</td>
                <td>{{ contact.email || "-" }}</td>
                <td>{{ contact.notes || "-" }}</td>
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

    <v-dialog v-model="confirmClear" max-width="420">
      <v-card class="glass-card">
        <v-card-title class="text-h6 font-weight-bold">Limpar contatos?</v-card-title>
        <v-card-text>
          Voce podera recuperar os contatos em ate 48 horas.
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn variant="text" color="secondary" @click="confirmClear = false">Cancelar</v-btn>
          <v-btn color="error" variant="tonal" @click="clearContacts">Confirmar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </AppLayout>
</template>

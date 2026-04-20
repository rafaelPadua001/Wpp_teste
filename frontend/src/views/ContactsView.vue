<script setup>
import { computed, onMounted, reactive, ref, watch } from "vue";
import AppLayout from "@/layouts/AppLayout.vue";
import AppSnackbar from "@/components/AppSnackbar.vue";
import api from "@/services/api";

const loading = ref(true);
const loadingImport = ref(false);
const file = ref(null);
const confirmClear = ref(false);
const editingId = ref(null);
const contacts = ref([]);
const selectedIds = ref([]);
const snackbar = reactive({ show: false, text: "", color: "success" });
const contactHeaders = [
  { title: "Nome", key: "name" },
  { title: "Telefone", key: "phone" },
  { title: "E-mail", key: "email" },
  { title: "Notas", key: "notes" },
  { title: "Acoes", key: "actions", sortable: false },
];
const form = reactive({
  name: "",
  phone: "",
  email: "",
  notes: "",
});

function getContactId(contact, index) {
  return String(contact.id ?? contact._id ?? contact.uuid ?? `tmp-${index}`);
}

const normalizedContacts = computed(() =>
  contacts.value.map((contact, index) => ({
    id: getContactId(contact, index),
    name: contact.name ?? "",
    phone: contact.phone ?? "",
    email: contact.email ?? "",
    notes: contact.notes ?? "",
  })),
);

watch(contacts, () => {
  const validIds = new Set(normalizedContacts.value.map((contact) => contact.id));
  selectedIds.value = selectedIds.value.filter((id) => validIds.has(String(id))).map((id) => String(id));
});

watch(selectedIds, (value) => {
  const normalized = [...new Set((value || []).map((id) => String(id)).filter(Boolean))];
  if (normalized.length !== value.length || normalized.some((id, index) => id !== value[index])) {
    selectedIds.value = normalized;
  }
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

async function handleDeleteSelected() {
  if (!selectedIds.value.length) return;

  const ids = selectedIds.value
    .map((id) => Number(id))
    .filter((id) => Number.isInteger(id) && id > 0);

  if (!ids.length) return;

  try {
    const { data } = await api.post("/contacts/clear", {
      contact_ids: ids,
    });
    notify(`Contatos removidos: ${data.cleared || 0}. Voce pode recuperar em ate 48 horas.`);
    selectedIds.value = [];
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
    formData.append("file", selectedFile, selectedFile.name);
    const { data } = await api.post("/contacts/import", formData);
    notify(`Importacao concluida: ${data.imported} importados, ${data.skipped} ignorados.`);
    file.value = null;
    await loadContacts();
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel importar o arquivo.", "error");
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
              label="Selecionar arquivo (.xml, .xls, .xlsx, .vcf)"
              accept=".xml,.xls,.xlsx,.vcf"
              prepend-icon="mdi-file-upload"
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
              :disabled="!selectedIds.length"
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

          <v-data-table
            v-else
            v-model="selectedIds"
            :headers="contactHeaders"
            :items="normalizedContacts"
            item-value="id"
            show-select
            class="soft-border rounded-xl overflow-hidden"
            density="comfortable"
            hide-default-footer
            no-data-text="Nenhum contato cadastrado ainda."
          >
            <template #item.name="{ item }">
              {{ item.name || "-" }}
            </template>
            <template #item.phone="{ item }">
              {{ item.phone || "-" }}
            </template>
            <template #item.email="{ item }">
              {{ item.email || "-" }}
            </template>
            <template #item.notes="{ item }">
              {{ item.notes || "-" }}
            </template>
            <template #item.actions="{ item }">
              <div class="d-flex ga-2">
                <v-btn size="small" variant="tonal" color="primary" @click="editContact(item)">
                  Editar
                </v-btn>
                <v-btn size="small" variant="tonal" color="error" @click="removeContact(item.id)">
                  Remover
                </v-btn>
              </div>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="confirmClear" max-width="420">
      <v-card class="glass-card">
        <v-card-title class="text-h6 font-weight-bold">Limpar contatos?</v-card-title>
        <v-card-text>
          Voce removera {{ selectedIds.length }} contato(s). Voce podera recuperar em ate 48 horas.
        </v-card-text>
        <v-card-actions class="pa-4 pt-0">
          <v-spacer />
          <v-btn variant="text" color="secondary" @click="confirmClear = false">Cancelar</v-btn>
          <v-btn color="error" variant="tonal" :disabled="!selectedIds.length" @click="handleDeleteSelected">
            Confirmar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </AppLayout>
</template>

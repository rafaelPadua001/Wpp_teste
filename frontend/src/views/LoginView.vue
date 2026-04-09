<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import api from "@/services/api";
import { authStore } from "@/store/auth";
import AppSnackbar from "@/components/AppSnackbar.vue";

const router = useRouter();
const activeTab = ref("login");
const loading = ref(false);
const snackbar = reactive({ show: false, text: "", color: "success" });

const loginForm = reactive({
  email: "",
  password: "",
});

const registerForm = reactive({
  company_name: "",
  admin_name: "",
  admin_email: "",
  whatsapp: "",
  password: "",
});

function notify(text, color = "success") {
  snackbar.show = true;
  snackbar.text = text;
  snackbar.color = color;
}

async function submitLogin() {
  loading.value = true;
  try {
    const { data } = await api.post("/auth/login", loginForm);
    authStore.setSession(data, loginForm.email);
    notify("Login realizado com sucesso.");
    router.push("/dashboard");
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel fazer login.", "error");
  } finally {
    loading.value = false;
  }
}

async function submitRegister() {
  loading.value = true;
  try {
    const { data } = await api.post("/auth/register", registerForm);
    notify(`Tenant criado com ID ${data.tenant_id}. Agora faca login.`);
    activeTab.value = "login";
    registerForm.company_name = "";
    registerForm.admin_name = "";
    registerForm.admin_email = "";
    registerForm.whatsapp = "";
    registerForm.password = "";
  } catch (error) {
    notify(error.response?.data?.detail || "Nao foi possivel criar o tenant.", "error");
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <v-app class="page-shell">
    <v-container fluid class="fill-height pa-4 pa-md-8">
      <v-row align="center" class="fill-height" no-gutters>
        <v-col cols="12" md="7" class="pr-md-4 mb-6 mb-md-0">
          <v-card class="glass-card pa-8">
            <v-chip color="primary" variant="flat" rounded="pill" class="mb-6">
              WhatsApp Cloud API SaaS
            </v-chip>
            <div class="text-h2 font-weight-black mb-4">
              Plataforma SaaS de automação de mensagens com arquitetura multi-tenant.
            </div>
            <div class="text-body-1 text-medium-emphasis mb-8">
              Plataforma SaaS de automação de mensagens com arquitetura multi-tenant, projetada para equipes que precisam escalar comunicação com eficiência e controle.
              <br /><br />
              Gerencie contatos, acompanhe métricas em tempo real e execute campanhas com uma interface moderna, rápida e intuitiva.
              <br /><br />
              Segurança e isolamento por tenant garantidos via autenticação JWT, com controle total dos dados de cada cliente.
              <br /><br />
              Integração pronta com WhatsApp Cloud API, incluindo suporte a ambiente de testes (sandbox) e operação em produção.
              <br /><br />
              Interface responsiva, com navegação fluida, dark mode e componentes otimizados para o uso diário.
            </div>

            <v-row>
              <v-col cols="12" md="4">
                <v-card class="glass-card pa-4 h-100">
                  <div class="text-subtitle-1 font-weight-bold mb-2">JWT isolado por tenant</div>
                  <div class="text-body-2 text-medium-emphasis">
                    Tenant vem do token e o backend aplica isolamento automatico.
                  </div>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card class="glass-card pa-4 h-100">
                  <div class="text-subtitle-1 font-weight-bold mb-2">Cloud API pronta</div>
                  <div class="text-body-2 text-medium-emphasis">
                    Sandbox e modo real preparados para o fluxo de mensagens.
                  </div>
                </v-card>
              </v-col>
              <v-col cols="12" md="4">
                <v-card class="glass-card pa-4 h-100">
                  <div class="text-subtitle-1 font-weight-bold mb-2">UI responsiva</div>
                  <div class="text-body-2 text-medium-emphasis">
                    SPA com navegação fluida, dark mode e cards pensados para operacao diária.
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </v-card>
        </v-col>

        <v-col cols="12" md="5">
          <v-card class="glass-card pa-6 pa-md-8">
            <v-tabs v-model="activeTab" color="primary" grow>
              <v-tab value="login">Entrar</v-tab>
              <v-tab value="register">Criar tenant</v-tab>
            </v-tabs>

            <v-window v-model="activeTab" class="mt-6">
              <v-window-item value="login">
                <div class="text-h5 font-weight-bold mb-1">Acessar painel</div>
                <div class="text-body-2 text-medium-emphasis mb-6">
                  Use o e-mail e a senha do seu usuário.
                </div>

                <v-form @submit.prevent="submitLogin">
                  <v-text-field v-model="loginForm.email" label="E-mail" type="email" required />
                  <v-text-field v-model="loginForm.password" label="Senha" type="password" required />
                  <v-btn
                    type="submit"
                    block
                    color="primary"
                    size="large"
                    :loading="loading"
                  >
                    Entrar no sistema
                  </v-btn>
                </v-form>
              </v-window-item>

              <v-window-item value="register">
                <div class="text-h5 font-weight-bold mb-1">Criar tenant inicial</div>
                <div class="text-body-2 text-medium-emphasis mb-6">
                  Registre a empresa e o admin principal.
                </div>

                <v-form @submit.prevent="submitRegister">
                  <v-text-field v-model="registerForm.company_name" label="Empresa" required />
                  <v-text-field v-model="registerForm.admin_name" label="Administrador" required />
                  <v-text-field v-model="registerForm.admin_email" label="E-mail" type="email" required />
                  <v-text-field v-model="registerForm.whatsapp" label="WhatsApp" />
                  <v-text-field v-model="registerForm.password" label="Senha" type="password" required />
                  <v-btn
                    type="submit"
                    block
                    color="primary"
                    size="large"
                    :loading="loading"
                  >
                    Criar tenant
                  </v-btn>
                </v-form>
              </v-window-item>
            </v-window>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <AppSnackbar v-model="snackbar.show" :text="snackbar.text" :color="snackbar.color" />
  </v-app>
</template>

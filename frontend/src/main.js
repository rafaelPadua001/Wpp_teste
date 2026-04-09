import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import vuetify from "./plugins/vuetify";
import { authStore } from "./store/auth";
import "./styles/main.scss";

authStore.hydrate();

createApp(App).use(router).use(vuetify).mount("#app");

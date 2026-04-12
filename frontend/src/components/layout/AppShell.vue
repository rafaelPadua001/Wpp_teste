<script setup>
import { ref, watch } from "vue";
import { useDisplay } from "vuetify";
import AppDrawer from "@/components/layout/AppDrawer.vue";
import AppHeader from "@/components/layout/AppHeader.vue";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});

const { smAndDown, mdAndUp } = useDisplay();
const drawer = ref(mdAndUp.value);

watch(mdAndUp, (isDesktop) => {
  drawer.value = isDesktop;
});
</script>

<template>
  <v-app class="page-shell">
    <v-layout class="app-layout">
      <AppDrawer
        v-model="drawer"
        :temporary="smAndDown"
        :permanent="mdAndUp"
      />

      <v-main class="app-main">
        <AppHeader :title="title" :subtitle="subtitle" @toggle-sidebar="drawer = !drawer" />
        <v-container fluid class="pa-4 pa-md-6">
          <div class="content-wrap">
            <slot />
          </div>
        </v-container>
      </v-main>
    </v-layout>
  </v-app>
</template>

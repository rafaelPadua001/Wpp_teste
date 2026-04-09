<script setup>
import { ref } from "vue";
import AppSidebar from "@/components/AppSidebar.vue";
import AppHeader from "@/components/AppHeader.vue";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});

const drawer = ref(false);
</script>

<template>
  <v-app class="page-shell">
    <div class="d-none d-md-block">
      <AppSidebar />
    </div>

    <v-navigation-drawer
      v-model="drawer"
      temporary
      location="left"
      color="#020617"
      class="d-md-none"
      width="276"
    >
      <AppSidebar />
    </v-navigation-drawer>

    <v-main>
      <AppHeader :title="title" :subtitle="subtitle" @toggle-sidebar="drawer = !drawer" />
      <v-container fluid class="px-md-6 px-3 pb-8">
        <slot />
      </v-container>
    </v-main>
  </v-app>
</template>

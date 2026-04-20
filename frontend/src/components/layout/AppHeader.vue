<script setup>
import { useDisplay } from "vuetify";
import { authStore } from "@/store/auth";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});

const emit = defineEmits(["toggle-sidebar"]);
const { smAndDown } = useDisplay();
</script>

<template>
  <v-app-bar app fixed elevation="1" color="surface" class="px-3 px-md-6 py-2 app-header">
    <v-app-bar-nav-icon
      v-if="smAndDown"
      variant="text"
      @click="emit('toggle-sidebar')"
    />

    <div>
      <div class="text-h5 font-weight-bold">{{ title }}</div>
      <div class="text-body-2 text-medium-emphasis">{{ subtitle }}</div>
    </div>

    <v-spacer />

    <v-chip rounded="xl" color="surface-bright" variant="flat" class="px-4">
      {{ authStore.state.user?.name || authStore.state.user?.email || "Usuario" }}
    </v-chip>
  </v-app-bar>
</template>

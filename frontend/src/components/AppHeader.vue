<script setup>
import { authStore } from "@/store/auth";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});

const emit = defineEmits(["toggle-sidebar"]);
</script>

<template>
  <v-app-bar flat color="transparent" class="px-md-4 px-2 py-2">
    <v-btn
      icon="mdi-menu"
      variant="text"
      class="mr-2 d-md-none"
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

<script setup>
import AppShell from "@/components/layout/AppShell.vue";

defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: "" },
});
</script>

<template>
  <AppShell :title="title" :subtitle="subtitle">
    <slot />
  </AppShell>
</template>

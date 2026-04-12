<script setup>
import AppSidebar from "@/components/AppSidebar.vue";

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  temporary: { type: Boolean, default: false },
  permanent: { type: Boolean, default: false },
});

const emit = defineEmits(["update:modelValue"]);
</script>

<template>
  <v-navigation-drawer
    :model-value="props.modelValue"
    @update:model-value="emit('update:modelValue', $event)"
    :temporary="props.temporary"
    :permanent="props.permanent"
    color="#020617"
    width="260"
    class="soft-border"
  >
    <AppSidebar />
  </v-navigation-drawer>
</template>

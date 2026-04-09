<script setup>
defineProps({
  modelValue: Boolean,
  text: String,
  color: { type: String, default: "success" },
});

const emit = defineEmits(["update:modelValue"]);
</script>

<template>
  <v-snackbar
    :model-value="modelValue"
    :color="color"
    location="bottom right"
    rounded="pill"
    @update:model-value="emit('update:modelValue', $event)"
  >
    {{ text }}
  </v-snackbar>
</template>

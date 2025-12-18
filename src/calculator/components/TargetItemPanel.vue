<template>
  <ul>
    <li v-for="t in targets" :key="t.id">
      {{ t.name }} ({{ t.id }})
      <button @click="$emit('remove', t.id)">remove</button>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  targets: {
    type: Array,
    default: () => [],
  },
});

defineEmits(["remove"]);
</script>

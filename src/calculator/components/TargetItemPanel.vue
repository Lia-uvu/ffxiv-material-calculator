<template>
  <ul>
    <li v-for="t in targets" :key="t.id">
      {{ t.name }} ({{ t.id }})
      <button @click="onRemove(t.id)">remove</button>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  targets: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(["remove"])
function onRemove(id) {
  emit("remove", id)
}
</script>

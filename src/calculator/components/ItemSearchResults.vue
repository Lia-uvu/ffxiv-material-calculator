<template>
  <ul>
    <li v-for="it in results" :key="it.id">
      <button @click="onSelect(it.id)">
        {{ it.name }} ({{ it.id }})
      </button>
    </li>
  </ul>
</template>

<script setup>
defineProps({
  results: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(["select"])

function onSelect(id) {
  emit("select", id)
}
</script>

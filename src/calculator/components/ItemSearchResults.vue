<template>
  <ul>
    <li v-for="it in results" :key="it.id">//这个key是什么又忘了
      <button @click="$emit('select', it.id)"> //这里没看懂
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
});

defineEmits(["select"]);//这里没看懂
</script>

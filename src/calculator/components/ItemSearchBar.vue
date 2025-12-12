<template>
  <input
    :value="props.query"
    placeholder="Search item..."
    @input="emit('update:query', $event.target.value)"
  />
</template>

<script setup>
const props = defineProps({
  query: { type: String, default: "" },
});

const emit = defineEmits(["update:query"]);
</script>



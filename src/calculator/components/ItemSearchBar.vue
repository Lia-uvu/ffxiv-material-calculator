<template>
  <input
    :value="props.query"
    placeholder="Search item..."
    @input="onInput"
  />
</template>

<script setup>
const props = defineProps({
  query: { type: String, default: "" },
});

const emit = defineEmits(["update:query"])

function onInput(e) {
  emit("update:query", e.target.value)
}

</script>



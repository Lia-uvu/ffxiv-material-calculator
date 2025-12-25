<!-- <template>
  <div class="mb-4 rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
  <input
    class="h-10 w-full rounded-xl border border-zinc-200 bg-white px-3 text-sm outline-none focus:ring-4 focus:ring-zinc-200"
    placeholder="Search item..."
    :value="props.query"
    @input="onInput"
  />
  </div>
</template>

<script setup>
const props = defineProps({
  query: { type: String, default: "" },
});

const emit = defineEmits(["update:query"])

function onInput(e) {
  emit("update:query", e.target.value)
}

</script> -->


<!-- ItemSearchInput.vue -->
<template>
  <input
    class="h-10 w-full rounded-xl border border-zinc-200 bg-white px-3 text-sm outline-none focus:ring-4 focus:ring-zinc-200"
    placeholder="Search item..."
    :value="props.query"
    @input="onInput"
  />
</template>

<script setup>
const props = defineProps({
  query: { type: String, default: "" },
});

const emit = defineEmits(["update:query"]);

function onInput(e) {
  emit("update:query", e.target.value);
}
</script>

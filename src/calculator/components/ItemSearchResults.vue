<template>
  <!-- 让它贴在搜索框下面：父级需要 relative，这里用 absolute -->
  <div
    v-if="results.length"
    class="absolute left-0 right-0 top-full z-50 mt-2 overflow-hidden rounded-2xl border border-zinc-200 bg-white shadow-lg"
  >
    <ul class="max-h-72 overflow-auto py-1">
      <li v-for="it in results" :key="it.id">
        <button
          type="button"
          class="flex w-full items-center justify-between gap-3 px-3 py-2 text-left text-sm text-zinc-900 hover:bg-zinc-50 focus:bg-zinc-50 focus:outline-none"
          @click="onSelect(it.id)"
        >
          <span class="min-w-0 flex-1 truncate">{{ it.name }}</span>
          <span
            class="shrink-0 rounded-full border border-zinc-200 bg-zinc-50 px-2 py-0.5 text-xs text-zinc-600"
          >
            #{{ it.id }}
          </span>
        </button>
      </li>
    </ul>

    <!-- 可选：底部提示（你想要就留，不想要删） -->
    <div class="border-t border-zinc-200 px-3 py-2 text-xs text-zinc-500">
      Click an item to add it.
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
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

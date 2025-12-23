<template>
  <ul>
    <li v-for="t in targets" :key="t.id" class="row">
      <span class="name">
        {{ t.name }} ({{ t.id }})
      </span>

      <input
        class="qty"
        type="number"
        min="1"
        step="1"
        :value="t.amount ?? 1"
        @input="onAmountInput(t.id, $event)"
        @blur="onAmountBlur(t.id, $event)"
      />

      <button @click="onRemove(t.id)">remove</button>
    </li>
  </ul>
</template>

<script setup>
const props = defineProps({
  targets: {
    type: Array,
    default: () => [],
  },
});

// 两个事件：删除、更新数量
const emit = defineEmits(["remove", "update-amount"]);

function clampAmount(raw) {
  const n = Number(raw);
  if (!Number.isFinite(n)) return 1;
  return Math.max(1, Math.floor(n));
}

function onRemove(id) {
  emit("remove", id);
}

// 输入时就更新（即时反馈）
function onAmountInput(id, e) {
  const next = clampAmount(e.target.value);
  emit("update-amount", { id, amount: next });
}

// blur 时再强制把输入框里的值“纠正”为合法整数（体验更稳）
function onAmountBlur(id, e) {
  const next = clampAmount(e.target.value);
  e.target.value = String(next);
  emit("update-amount", { id, amount: next });
}
</script>

<style scoped>
.row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.name {
  flex: 1;
}
.qty {
  width: 80px;
}
</style>

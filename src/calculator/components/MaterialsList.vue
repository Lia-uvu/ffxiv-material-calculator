<template>
  <section class="materials">
    <h2>Materials List</h2>

    <p v-if="!props.entries.length" class="empty">
      No materials yet. Add a target item to see the list.
    </p>

    <template v-else>
      <!-- 可选：先把水晶单独拎出来（你不想分组就把这段删掉） -->
      <div v-if="crystals.length" class="group">
        <h3>Crystals</h3>
        <ul class="list">
          <li v-for="m in crystals" :key="m.id" class="row">
            <span class="name">{{ m.name }}</span>
            <!-- <span class="meta">#{{ m.id }}</span> -->
            <span class="amount">× {{ m.amount }}</span>
          </li>
        </ul>
      </div>

      <div v-if="others.length" class="group">
        <h3>Materials</h3>
        <ul class="list">
          <li v-for="m in others" :key="m.id" class="row">
            <span class="name">{{ m.name }}</span>
            <!-- <span class="meta">#{{ m.id }}</span> -->
            <span class="amount">× {{ m.amount }}</span>
          </li>
        </ul>
      </div>

      <!-- 调试：总计多少种材料 -->
      <p class="footer">Total: {{ props.entries.length }} items</p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, PropType } from "vue";

type MaterialEntry = {
  id: number;
  name: string;
  amount: number;
  isCrystal?: boolean;
};

const props = defineProps({
  entries: {
    type: Array as PropType<MaterialEntry[]>,
    required: true,
  },
});

const crystals = computed(() => props.entries.filter((e) => e.isCrystal));
const others = computed(() => props.entries.filter((e) => !e.isCrystal));
</script>

<style scoped>
.materials {
  padding: 12px;
  border: 1px solid #333;
  border-radius: 8px;
}

.empty {
  opacity: 0.8;
}

.group {
  margin-top: 12px;
  /* 强制左对齐 */
  text-align: left;
}

.list {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
}

.row {
  display: flex;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px dashed #444;
}

.name {
  flex: 1;
}

.meta {
  opacity: 0.7;
}

.amount {
  font-weight: 600;
}

.footer {
  margin-top: 12px;
  opacity: 0.8;
}
</style>

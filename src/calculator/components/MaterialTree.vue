<template>
  <table class="material-result-table">
    <thead>
      <tr>
        <th>材料名</th>
        <th>数量</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="material in visibleMaterials" :key="material.id">
        <td>{{ material.name }}</td>
        <td>{{ material.quantity }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 所有材料列表
  // 期望结构类似：[{ id: 1, name: '铁矿', quantity: 3 }, ...]
  materials: {
    type: Array,
    default: () => [],
  },
  // 要隐藏的材料 id 列表
  // 例如：[1, 3]
  hiddenMaterialIds: {
    type: Array,
    default: () => [],
  },
})

// 用 computed 做 “所有材料 - 要隐藏的材料”
const visibleMaterials = computed(() => {
  const hiddenSet = new Set(props.hiddenMaterialIds)
  return props.materials.filter((m) => !hiddenSet.has(m.id))
})
</script>

<style scoped>
.material-result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.material-result-table th,
.material-result-table td {
  border: 1px solid #444;
  padding: 4px 8px;
  text-align: left;
}

.material-result-table thead {
  background: #222;
  font-weight: 600;
}
</style>

<template>
  <section class="target-item-panel">
    <h2 class="title">目标成品</h2>

    <table class="target-item-table">
      <thead>
        <tr>
          <th>名称</th>
          <th>数量</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="item in items"
          :key="item.id"
        >
          <td>{{ item.name }}</td>
          <td>{{ item.quantity ?? '-' }}</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>

<script setup>
const props = defineProps({
  // 成品列表
  items: {
    type: Array,
    default: () => [],
  },
})
</script>

<style scoped>
.target-item-panel {
  padding: 12px;
  border: 1px solid #444;
  border-radius: 8px;
  font-size: 14px;
}

.title {
  margin: 0 0 8px;
  font-size: 16px;
}

.target-item-table {
  width: 100%;
  border-collapse: collapse;
}

.target-item-table th,
.target-item-table td {
  border: 1px solid #444;
  padding: 4px 8px;
  text-align: left;
}
</style>

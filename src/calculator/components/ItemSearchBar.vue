<template>
  <input
    v-model="keyword"
    type="text"
    placeholder="输入物品名..."
  />
  <button @click="search" >搜索</button>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({
// 传入对象
}
)
const keyword = ref('')
</script>

<style scoped>

</style>
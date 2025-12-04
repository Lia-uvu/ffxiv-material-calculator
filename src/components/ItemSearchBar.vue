<script setup>
function addAndNotify(a, b, whenDone) {
  const sum = a + b
  whenDone(sum)
}

function handleDone(result) {
  console.log('加法完成，结果是：', result)
}

</script>

<template>
    <p class="read-the-docs">这是另外的组件里的</p>
    <button @click="addAndNotify(1,2,handleDone)" >a button {{ result }}</button>
</template>

<style scoped>
p {color: coral;}
</style>
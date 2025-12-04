<script setup>
import ItemSearchBar from './components/ItemSearchBar.vue';
import TargetItemPanel from './components/TargetItemPanel.vue';
</script>

<template>
  <TargetItemPanel msg="archieved items" />
  <ItemSearchBar></ItemSearchBar>
</template>

<style scoped>
.logo {
  height: 5em;
  padding: 1em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #ffffffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #ffffffaa);
}
</style>

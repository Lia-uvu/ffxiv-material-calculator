<script setup>
import CalculatorPage from './calculator/pages/CalculatorPage.vue';
import TopNav from './calculator/components/TopNav.vue';
</script>

<template>
  <div class="min-h-screen bg-[#2D2C34] text-[#EDE9F7]">
    <TopNav />
    <main class="mx-auto max-w-3xl px-4 pt-6 pb-10">
      <CalculatorPage />
    </main>
  </div>
</template>

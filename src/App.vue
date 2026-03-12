<script setup>
import { onMounted } from 'vue';
import CalculatorPage from './calculator/pages/CalculatorPage.vue';
import TopNav from './calculator/components/TopNav.vue';
import OnboardingModal from './calculator/pages/OnboardingModal.vue';
import { useOnboarding } from './calculator/composables/useOnboarding.js';

const { init } = useOnboarding();
onMounted(() => init());
</script>

<template>
  <div class="min-h-screen bg-[#2D2C34] text-[#EDE9F7]">
    <TopNav />
    <main class="mx-auto max-w-3xl px-4 pt-6 pb-10">
      <CalculatorPage />
    </main>
    <OnboardingModal />
  </div>
</template>

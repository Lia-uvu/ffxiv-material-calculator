import { ref } from "vue";

const STORAGE_KEY = "msjcalc.onboarding.v1";
const isOpen = ref(false);

function init() {
  const seen = localStorage.getItem(STORAGE_KEY);
  if (!seen) isOpen.value = true;
}

function open() {
  isOpen.value = true;
}

function close() {
  isOpen.value = false;
  localStorage.setItem(STORAGE_KEY, "1");
}

export function useOnboarding() {
  return { isOpen, open, close, init };
}

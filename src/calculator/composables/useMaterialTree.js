const filteredTodos = computed(() => {
  return hideCompleted.value
  ? todos.value.filter((t) => !t.done)
  : todos.value
})
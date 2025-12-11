// 共享数据中心（单向数据流根文件）
import { reactive, ref, watch } from 'vue'

const defaultSettings = {
  searchText: '',
  showCrystal:true,
  showOnlyCraftable: false,
  showHQ: true,
  showNQ: true,
  sortBy: 'name',
  sortDirection: 'asc',
}

// “主设置对象”：所有和业务有关的设置都塞这里
const settings = reactive({ ...defaultSettings })

// 这种“UI 级别”的状态你可以决定要不要也放进来
// 比如：“高级选项是否展开”
const isAdvancedOpen = ref(false)

// === 监控 settings 的变化（比如做持久化）===
watch(
  settings,
  (newVal) => {
    // 这里写副作用逻辑，比如存 localStorage
    localStorage.setItem('calculatorSettings', JSON.stringify(newVal))
  },
  { deep: true }
)

function loadFromStorage() {
  const raw = localStorage.getItem('calculatorSettings')
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    Object.assign(settings, parsed)
  } catch (e) {
    console.warn('invalid settings from storage', e)
  }
}

function resetSettings() {
  Object.assign(settings, defaultSettings)
}

export function useCalculatorSettings() {
  // 注意：这里返回的是同一份 settings / ref
  return {
    settings,
    isAdvancedOpen,
    loadFromStorage,
    resetSettings,
  }
}

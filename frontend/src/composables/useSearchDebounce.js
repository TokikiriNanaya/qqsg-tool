/**
 * 搜索防抖 composable
 */
import { ref } from 'vue'

export function useSearchDebounce(searchFn, delay = 300) {
  let timer = null
  const currentPage = ref(1)

  const handleSearchInput = () => {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      currentPage.value = 1
      searchFn()
    }, delay)
  }

  return { currentPage, handleSearchInput }
}

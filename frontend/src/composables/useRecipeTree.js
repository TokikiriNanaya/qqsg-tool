/**
 * 配方树导航逻辑 - Items 和 Recipes 页面共用
 */
import { ref } from 'vue'
import { getItemRecipeTree } from '@/api/recipe'

export function useRecipeTree() {
  const itemTreeVisible = ref(false)
  const itemTreeLoading = ref(false)
  const itemTreeTitle = ref('')
  const itemTreeData = ref({ recipesByMaterial: [], recipesAsResult: [] })

  // 显示物品配方树弹窗
  const showItemTree = async (itemId, itemName) => {
    itemTreeTitle.value = itemName
    itemTreeVisible.value = true
    itemTreeLoading.value = true
    itemTreeData.value = { recipesByMaterial: [], recipesAsResult: [] }

    try {
      const res = await getItemRecipeTree(itemId)
      itemTreeData.value = {
        recipesByMaterial: res.recipes_by_material || [],
        recipesAsResult: res.recipes_as_result || []
      }
    } catch (error) {
      console.error('加载配方失败:', error)
    } finally {
      itemTreeLoading.value = false
    }
  }

  // 在弹窗内导航到另一个物品的配方树
  const navigateItemTree = async (itemId, itemName) => {
    await showItemTree(itemId, itemName || `物品${itemId}`)
  }

  return {
    itemTreeVisible,
    itemTreeLoading,
    itemTreeTitle,
    itemTreeData,
    showItemTree,
    navigateItemTree
  }
}

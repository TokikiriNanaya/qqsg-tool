/**
 * 配方树导航逻辑 - Items 和 Recipes 页面共用
 * 现在改为使用 Vue Flow 思维导图式展示
 */
import { ref } from 'vue'
import { getItemRecipeTree } from '@/api/recipe'
import { getItemById } from '@/api/item'
import { buildSingleRecipeFlow, buildItemRecipeFlow } from '@/composables/useFlowTransform'

export function useRecipeTree() {
  // 配方图弹窗
  const flowVisible = ref(false)
  const flowLoading = ref(false)
  const flowTitle = ref('')
  const flowData = ref({ nodes: [], edges: [] })

  // 物品详情弹窗（从配方图中点击物品时触发）
  const flowItemDetailVisible = ref(false)
  const flowItemDetailLoading = ref(false)
  const flowItemDetail = ref(null)

  // 配方详情弹窗（从配方图中点击配方时触发）
  const flowRecipeDetailVisible = ref(false)
  const flowRecipeDetailLoading = ref(false)
  const flowRecipeDetail = ref(null)

  /**
   * 显示配方图弹窗（配方详情页使用 — 展示单个配方的产物→材料关系）
   * @param {Object} recipe - 配方完整数据
   */
  const showRecipeFlow = (recipe) => {
    flowTitle.value = `${recipe.name} - 配方关系图`
    flowVisible.value = true
    const data = buildSingleRecipeFlow(recipe)
    flowData.value = data
  }

  /**
   * 显示物品配方图弹窗（物品详情页使用 — 展示物品的完整配方树）
   * @param {Object} item - 物品信息
   * @param {Object} treeData - 配方树数据 { recipesAsResult, recipesByMaterial }
   */
  const showItemFlow = (item, treeData) => {
    flowTitle.value = `${item.name} - 配方关系图`
    flowVisible.value = true
    const data = buildItemRecipeFlow(treeData, item)
    flowData.value = data
  }

  /**
   * 从配方图中点击物品 → 打开物品详情弹窗
   */
  const showFlowItemDetail = async (itemId, itemName) => {
    flowItemDetailVisible.value = true
    flowItemDetailLoading.value = true
    flowItemDetail.value = null
    try {
      const item = await getItemById(itemId)
      flowItemDetail.value = item
    } catch (e) {
      console.error('加载物品详情失败:', e)
    } finally {
      flowItemDetailLoading.value = false
    }
  }

  /**
   * 从配方图中点击配方 → 打开配方详情弹窗
   */
  const showFlowRecipeDetail = async (recipeId) => {
    // 直接通过事件抛出，由父页面处理
  }

  return {
    flowVisible,
    flowLoading,
    flowTitle,
    flowData,
    flowItemDetailVisible,
    flowItemDetailLoading,
    flowItemDetail,
    flowRecipeDetailVisible,
    flowRecipeDetailLoading,
    flowRecipeDetail,
    showRecipeFlow,
    showItemFlow,
    showFlowItemDetail,
    showFlowRecipeDetail
  }
}

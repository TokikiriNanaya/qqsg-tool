<template>
  <el-dialog
    v-model="visible"
    :title="title + ' - 配方关系'"
    width="700px"
    :close-on-click-modal="true"
  >
    <div v-loading="loading">
      <!-- 制作配方（该物品作为产物的配方） -->
      <div class="item-tree-section">
        <h4><el-icon><Tickets /></el-icon> 制作配方</h4>
        <div v-if="treeData.recipesAsResult.length > 0" class="recipe-cards">
          <RecipeCard
            v-for="recipe in treeData.recipesAsResult"
            :key="recipe.id"
            :recipe="recipe"
            card-type="as-result"
            @click-card="navigateItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
            @click-material="navigateItemTree"
          />
        </div>
        <div v-else class="empty-hint">暂无</div>
      </div>

      <!-- 可制作配方（该物品作为材料的配方） -->
      <div class="item-tree-section">
        <h4><el-icon><Grid /></el-icon> 可制作配方</h4>
        <div v-if="treeData.recipesByMaterial.length > 0" class="recipe-cards">
          <RecipeCard
            v-for="recipe in treeData.recipesByMaterial"
            :key="recipe.id"
            :recipe="recipe"
            card-type="by-material"
            @click-card="navigateItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
            @click-material="navigateItemTree"
          />
        </div>
        <div v-else class="empty-hint">暂无</div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import RecipeCard from './RecipeCard.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  treeData: {
    type: Object,
    default: () => ({ recipesByMaterial: [], recipesAsResult: [] })
  }
})

const emit = defineEmits(['update:modelValue', 'navigate'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const navigateItemTree = (itemId, itemName) => {
  emit('navigate', itemId, itemName)
}
</script>

<style scoped>
.item-tree-section {
  margin-bottom: 20px;
}

.item-tree-section h4 {
  margin-bottom: 10px;
  color: #606266;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.recipe-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.empty-hint {
  padding: 6px 12px;
  color: #909399;
  font-size: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}
</style>

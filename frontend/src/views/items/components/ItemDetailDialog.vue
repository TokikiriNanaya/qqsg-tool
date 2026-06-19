<template>
  <el-dialog
    v-model="visible"
    title="物品详情"
    width="700px"
    :close-on-click-modal="true"
  >
    <div v-loading="loading">
      <div v-if="item" class="item-detail">
        <!-- 基本信息 -->
        <div class="detail-info-grid">
          <div class="info-item">
            <span class="info-label">物品名称</span>
            <span class="info-value">
              {{ item.name }}
              <span class="item-id-badge">ID: {{ item.id }}</span>
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">物品分类</span>
            <span class="info-value">{{ item.category || '-' }}</span>
          </div>
          <div class="info-item" v-if="item.description">
            <span class="info-label">物品描述</span>
            <span class="info-value info-desc">{{ item.description }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">默认价格</span>
            <span class="info-value">{{ item.default_price ?? '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">背包上限</span>
            <span class="info-value">{{ item.bag_limit }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">仓库上限</span>
            <span class="info-value">{{ item.warehouse_limit }}</span>
          </div>
        </div>

        <!-- 关联配方 -->
        <div v-if="recipes" class="recipes-section">
          <div class="item-tree-section">
            <h3>
              <el-icon><Tickets /></el-icon>
              产出此物品的配方
            </h3>
            <div v-if="recipes.as_result.length > 0" class="recipe-cards">
              <RecipeCard
                v-for="recipe in recipes.as_result"
                :key="recipe.id"
                :recipe="recipe"
                card-type="as-result"
                @click-card="$emit('show-tree', recipe.result_item_id, recipe.result_item_name || recipe.name)"
                @click-material="(id, name) => $emit('show-tree', id, name)"
              />
            </div>
            <div v-else class="empty-hint">暂无</div>
          </div>

          <div class="item-tree-section">
            <h3>
              <el-icon><Grid /></el-icon>
              用作材料的配方
            </h3>
            <div v-if="recipes.as_material.length > 0" class="recipe-cards">
              <RecipeCard
                v-for="recipe in recipes.as_material"
                :key="recipe.id"
                :recipe="recipe"
                card-type="by-material"
                @click-card="$emit('show-tree', recipe.result_item_id, recipe.result_item_name || recipe.name)"
                @click-material="(id, name) => $emit('show-tree', id, name)"
              />
            </div>
            <div v-else class="empty-hint">暂无</div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import RecipeCard from '@/components/RecipeCard.vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  item: { type: Object, default: null },
  recipes: {
    type: Object,
    default: () => ({ as_result: [], as_material: [] })
  }
})

const emit = defineEmits(['update:modelValue', 'show-tree'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})
</script>

<style scoped>
.item-detail {
  background: #fff;
}

.detail-info-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1px;
  background: #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #ebeef5;
}

.info-item {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 14px 18px;
  transition: background 0.2s;
}

.info-item:hover {
  background: #fafbfc;
}

.info-label {
  font-size: 13px;
  color: #909399;
  flex-shrink: 0;
  width: 80px;
}

.info-value {
  font-size: 14px;
  color: #303133;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.item-id-badge {
  display: inline-block;
  margin-left: 10px;
  background: #f0f2f5;
  color: #909399;
  padding: 1px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 400;
}

.info-desc {
  line-height: 1.8;
  color: #606266;
  font-weight: 400;
}

.recipes-section {
  margin-top: 24px;
}

.item-tree-section {
  margin-bottom: 20px;
}

.item-tree-section h3 {
  margin-bottom: 12px;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  padding-left: 8px;
  border-left: 3px solid #409eff;
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

<template>
  <el-dialog
    v-model="visible"
    title="物品详情"
    width="900px"
    :close-on-click-modal="true"
    top="3vh"
  >
    <div v-loading="loading">
      <div v-if="item" class="item-detail">
        <!-- 基本信息 -->
        <div class="detail-info-grid">
          <div class="info-item">
            <span class="info-label">物品名称</span>
            <span class="info-value">
              {{ item.name }}
              <el-tag v-if="item.category" size="small" class="info-tag">{{ item.category }}</el-tag>
              <el-tag v-if="item.default_price != null" size="small" type="warning" class="info-tag">{{ item.default_price }}三国币</el-tag>
            </span>
          </div>
          <div class="info-item" v-if="item.description">
            <span class="info-label">物品描述</span>
            <span class="info-value info-desc">{{ item.description }}</span>
          </div>
        </div>

        <!-- 配方关系图 -->
        <div v-if="recipes && (recipes.as_result.length > 0 || recipes.as_material.length > 0)" class="flow-section">
          <h3>
            <el-icon><Connection /></el-icon>
            配方关系图
          </h3>
          <RecipeFlow
            :flow-data="flowData"
            :loading="false"
            :current-item-id="item?.id"
            @click-recipe="(id) => $emit('show-recipe', id)"
            @click-item="(id, name) => $emit('show-item-detail', id, name)"
          />
          <div class="flow-legend">
            <span class="legend-item"><span class="legend-dot upstream"></span> 制作材料（实线）</span>
            <span class="legend-item"><span class="legend-dot downstream"></span> 可制作物品（虚线）</span>
          </div>
        </div>
        <div v-else-if="recipes" class="no-recipes">
          该物品暂无关联配方
        </div>
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, watch } from 'vue'
import RecipeFlow from '@/components/RecipeFlow.vue'
import { buildItemRecipeFlow } from '@/composables/useFlowTransform'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  item: { type: Object, default: null },
  recipes: {
    type: Object,
    default: () => ({ as_result: [], as_material: [] })
  },
  flowData: {
    type: Object,
    default: () => ({ nodes: [], edges: [] })
  }
})

const emit = defineEmits(['update:modelValue', 'show-recipe', 'show-item-detail'])

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
  margin-bottom: 24px;
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

.info-tag {
  margin-left: 8px;
}

.info-desc {
  line-height: 1.8;
  color: #606266;
  font-weight: 400;
}

.flow-section {
  margin-top: 8px;
}

.flow-section h3 {
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

.no-recipes {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}

.flow-legend {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  padding: 0 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #909399;
}

.legend-dot {
  width: 24px;
  height: 3px;
  border-radius: 2px;
}

.legend-dot.upstream {
  background: #e6a23c;
}

.legend-dot.downstream {
  background: #67c23a;
  background-image: repeating-linear-gradient(90deg, #67c23a 0, #67c23a 6px, transparent 6px, transparent 9px);
}
</style>

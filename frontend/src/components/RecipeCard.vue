<template>
  <div
    class="recipe-card-item"
    :class="cardClasses"
    @click="$emit('click-card')"
  >
    <div class="recipe-card-header">
      <el-icon><Box /></el-icon>
      <span>{{ recipe.name }}</span>
      <template v-if="cardType === 'by-material'">
        <el-tag size="small" type="info">产出</el-tag>
      </template>
    </div>
    <div class="recipe-card-info">
      <el-tag size="small" :type="professionTagType">
        {{ recipe.profession_type_label }}
      </el-tag>
      <span class="level">Lv.{{ recipe.level_required }}</span>
      <span v-if="cardType === 'by-material' && recipe.result_quantity > 1" class="quantity">
        ×{{ recipe.result_quantity }}
      </span>
    </div>
    <div class="recipe-card-materials">
      <span>材料:</span>
      <template v-for="(mat, idx) in materials" :key="idx">
        <span v-if="idx > 0">, </span>
        <span
          class="material-link"
          @click.stop="$emit('click-material', mat.id, mat.name)"
        >{{ mat.name }}</span>×{{ mat.quantity }}
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  recipe: { type: Object, required: true },
  cardType: {
    type: String,
    default: 'as-result',
    validator: (v) => ['as-result', 'by-material'].includes(v)
  }
})

defineEmits(['click-card', 'click-material'])

const cardClasses = computed(() => ({
  'recipe-card': true,
  'result-card': props.cardType === 'by-material'
}))

const professionTagType = computed(() => {
  const typeMap = { 1: 'success', 2: 'primary', 3: 'warning', 4: 'danger', 5: 'info' }
  return typeMap[props.recipe.profession_type] || 'default'
})

const materials = computed(() => {
  const list = []
  const r = props.recipe
  if (r.material1_id) list.push({ id: r.material1_id, name: r.material1_name || `物品${r.material1_id}`, quantity: r.material1_quantity || 0 })
  if (r.material2_id) list.push({ id: r.material2_id, name: r.material2_name || `物品${r.material2_id}`, quantity: r.material2_quantity || 0 })
  if (r.material3_id) list.push({ id: r.material3_id, name: r.material3_name || `物品${r.material3_id}`, quantity: r.material3_quantity || 0 })
  return list
})
</script>

<style scoped>
.recipe-card-item {
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid #409eff;
}

.recipe-card-item:hover {
  background: #ecf5ff;
  transform: translateX(2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.recipe-card-item.result-card {
  border-left-color: #67c23a;
}

.recipe-card-item.result-card:hover {
  background: #f0f9eb;
  box-shadow: 0 2px 8px rgba(103, 194, 58, 0.15);
}

.recipe-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
}

.recipe-card-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 13px;
}

.recipe-card-info .level {
  color: #909399;
}

.recipe-card-info .quantity {
  color: #e6a23c;
}

.recipe-card-materials {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
}

.material-link {
  color: #409eff;
  cursor: pointer;
  text-decoration: none;
}

.material-link:hover {
  text-decoration: underline;
}
</style>

<template>
  <div class="materials-section">
    <h3>所需材料</h3>
    <div class="recipe-tree">
      <!-- 根节点：产物 -->
      <div class="tree-root">
        <div class="tree-node result-node" @click="$emit('show-tree', recipe.result_item_id, recipe.result_item_name)">
          <el-icon><Box /></el-icon>
          <span>{{ recipe.result_item_name || recipe.name }}</span>
          <span v-if="recipe.result_quantity > 1" class="quantity">× {{ recipe.result_quantity }}</span>
        </div>
      </div>

      <!-- 连接线 -->
      <div v-if="materials.length > 0" class="tree-connector">
        <div class="connector-line"></div>
        <div class="connector-arrow">
          <el-icon><DArrowRight /></el-icon>
        </div>
        <div class="connector-line"></div>
      </div>

      <!-- 子节点：材料 -->
      <div class="tree-children">
        <div
          v-for="(mat, index) in materials"
          :key="index"
          class="tree-node material-node"
          @click="$emit('show-tree', mat.id, mat.name)"
        >
          <el-icon><Grid /></el-icon>
          <span>{{ mat.name }}</span>
          <span class="quantity">× {{ mat.quantity }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  recipe: { type: Object, required: true }
})

defineEmits(['show-tree'])

const materials = computed(() => {
  const list = []
  const r = props.recipe
  if (r.material1_id && r.material1_quantity > 0) {
    list.push({ id: r.material1_id, name: r.material1_name || `物品${r.material1_id}`, quantity: r.material1_quantity })
  }
  if (r.material2_id && r.material2_quantity > 0) {
    list.push({ id: r.material2_id, name: r.material2_name || `物品${r.material2_id}`, quantity: r.material2_quantity })
  }
  if (r.material3_id && r.material3_quantity > 0) {
    list.push({ id: r.material3_id, name: r.material3_name || `物品${r.material3_id}`, quantity: r.material3_quantity })
  }
  return list
})
</script>

<style scoped>
.materials-section {
  margin-top: 24px;
}

.materials-section h3 {
  margin-bottom: 10px;
  color: #303133;
  font-size: 15px;
  font-weight: 600;
  padding-left: 8px;
  border-left: 3px solid #409eff;
}

.recipe-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  position: relative;
}

.tree-root {
  position: relative;
  z-index: 2;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.result-node {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  min-width: 180px;
  justify-content: center;
}

.result-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.result-node .el-icon { font-size: 18px; }

.result-node .quantity {
  background: rgba(255,255,255,0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.tree-connector {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10px;
}

.connector-line {
  width: 40px;
  height: 2px;
  background: #dcdfe6;
}

.connector-arrow {
  color: #909399;
  font-size: 16px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.tree-children {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.material-node {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #606266;
  border: 1px solid #dcdfe6;
  min-width: 160px;
  justify-content: center;
}

.material-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
  border-color: #409eff;
}

.material-node .el-icon { color: #409eff; }

.material-node .quantity {
  background: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}
</style>

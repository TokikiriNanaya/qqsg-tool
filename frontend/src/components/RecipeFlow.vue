<template>
  <div ref="flowWrapper" class="recipe-flow-wrapper" :class="{ 'is-fullscreen': isFullscreen }">
    <!-- 全屏按钮 -->
    <el-button
      v-if="!isFullscreen"
      class="fullscreen-btn"
      :icon="FullScreen"
      circle
      @click="enterFullscreen"
    />
    <!-- 退出全屏按钮 -->
    <el-button
      v-else
      class="fullscreen-exit-btn"
      :icon="Close"
      circle
      type="danger"
      @click="exitFullscreen"
    />
    <VueFlow
      ref="vueFlowRef"
      :nodes="nodes"
      :edges="edges"
      :default-viewport="{ zoom: 1, x: 0, y: 0 }"
      :min-zoom="0.2"
      :max-zoom="3"
      :fit-view-on-init="true"
      :nodes-draggable="false"
      :connection-line-style="{ stroke: '#909399', strokeWidth: 2 }"
      class="recipe-flow-canvas"
      @node-mouse-enter="onNodeMouseEnter"
      @node-mouse-leave="onNodeMouseLeave"
      @node-click="onNodeClick"
    >
      <Background :gap="20" :size="1" />
      <Controls position="bottom-right" />

      <!-- 物品节点 -->
      <template #node-item="itemProps">
        <div
          class="flow-node item-node"
          :class="{
            'item-highlight': hoveredNode === itemProps.id,
            'item-current': props.currentItemId != null && itemProps.data.item_id === props.currentItemId,
            'node-root': itemProps.data.nodeType === 'root'
          }"
        >
          <div class="node-header">
            <el-icon><Grid /></el-icon>
            <span class="node-name">{{ itemProps.data.label }}</span>
            <span class="node-badge" :class="'badge-' + (itemProps.data.nodeType || 'default')">
              {{ nodeTypeLabel(itemProps.data.nodeType) }}
            </span>
            <span class="node-quantity" v-if="itemProps.data.quantity > 1">
              ×{{ itemProps.data.quantity }}
            </span>
          </div>
          <div class="node-body">
            <div class="node-row" v-if="itemProps.data.category">
              <span class="node-label">分类</span>
              <span class="node-value">{{ itemProps.data.category }}</span>
            </div>
            <div class="node-row" v-if="itemProps.data.default_price != null">
              <span class="node-label">价格</span>
              <span class="node-value price">{{ itemProps.data.default_price }}</span>
            </div>
            <div class="node-row node-desc" v-if="itemProps.data.description">
              <span class="node-value-desc">{{ itemProps.data.description }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- 配方节点 -->
      <template #node-recipe="recipeProps">
        <div
          class="flow-node recipe-node"
          :class="{
            'item-highlight': hoveredNode === recipeProps.id,
            'node-root': recipeProps.data.recipe?.nodeType === 'root'
          }"
          @mouseenter="onRecipeMouseEnter(recipeProps.data.recipe, $event)"
          @mouseleave="onRecipeMouseLeave"
        >
          <div class="node-header recipe-header">
            <el-icon><Coin /></el-icon>
            <span class="node-name">{{ recipeProps.data.recipe?.name }}</span>
            <span
              class="node-badge"
              :class="recipeProps.data.recipe?.nodeType === 'root' ? 'badge-root' : 'badge-recipe'"
            >
              {{ recipeProps.data.recipe?.nodeType === 'root' ? nodeTypeLabel('root', 'recipe') : '配方' }}
            </span>
          </div>
          <div class="node-body">
            <div class="node-row" v-if="recipeProps.data.recipe?.profession_type_label">
              <span class="node-value recipe-tag">{{ recipeProps.data.recipe.profession_type_label }} Lv.{{ recipeProps.data.recipe.level_required }}</span>
            </div>
            <div class="node-row recipe-mats" v-if="recipeProps.data.recipe?.materials?.length">
              <span
                v-for="(m, j) in recipeProps.data.recipe.materials"
                :key="j"
                class="recipe-mat-item"
              >{{ m.name }}×{{ m.quantity }}</span>
            </div>
            <div class="node-row recipe-result" v-if="recipeProps.data.recipe?.result">
              → {{ recipeProps.data.recipe.result.name }}×{{ recipeProps.data.recipe.result.quantity }}
            </div>
          </div>
        </div>
      </template>

      <!-- 自定义 smoothstep 边 -->
      <template #edge-smoothstep="edgeProps">
        <SmoothStepEdge v-bind="edgeProps" :style="getEdgeStyle(edgeProps)" />
      </template>
    </VueFlow>

    <!-- hover 提示（浅色主题，显示配方卡片） -->
    <Teleport to="body">
      <div
        v-if="tooltipVisible"
        class="flow-tooltip"
        :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
      >
        <div class="tooltip-header">{{ tooltipData.label }}</div>
        <div class="tooltip-body">
          <div v-if="tooltipData.category">分类: {{ tooltipData.category }}</div>
          <div v-if="tooltipData.description" class="tooltip-desc">{{ tooltipData.description }}</div>

          <!-- 作为产物的配方 -->
          <template v-if="tooltipData.asResultRecipes && tooltipData.asResultRecipes.length > 0">
            <div class="tooltip-section-title">制作配方</div>
            <div
              v-for="(r, i) in tooltipData.asResultRecipes"
              :key="'ar_' + i"
              class="tooltip-recipe-card"
            >
              <div class="tooltip-recipe-name">
                {{ r.name }}
                <span v-if="r.profession_type_label" class="tooltip-recipe-tag">{{ r.profession_type_label }} Lv.{{ r.level_required }}</span>
              </div>
              <div class="tooltip-recipe-mats">
                <span v-for="(m, j) in r.materials" :key="j" class="tooltip-recipe-mat">
                  {{ m.name }} ×{{ m.quantity }}
                </span>
              </div>
              <div class="tooltip-recipe-result">
                → {{ r.result.name }} ×{{ r.result.quantity }}
                <span v-if="r.vitality_cost > 0" class="tooltip-vitality">活力{{ r.vitality_cost }}</span>
              </div>
            </div>
          </template>
        </div>
        <div class="tooltip-footer">点击查看详情</div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { FullScreen, Close } from '@element-plus/icons-vue'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { SmoothStepEdge } from '@vue-flow/core'
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'

const router = useRouter()

const props = defineProps({
  flowData: {
    type: Object,
    default: () => ({ nodes: [], edges: [] })
  },
  currentItemId: { type: Number, default: null },
  currentRecipeId: { type: Number, default: null }
})

// 全屏状态
const isFullscreen = ref(false)
// VueFlow 实例 ref
const vueFlowRef = ref(null)

const enterFullscreen = () => {
  isFullscreen.value = true
  // 全屏后自动居中树状图
  nextTick(() => {
    setTimeout(() => {
      vueFlowRef.value?.fitView({ padding: 0.15, duration: 300 })
    }, 100)
  })
}

const exitFullscreen = () => {
  isFullscreen.value = false
  // 退出全屏后也居中
  nextTick(() => {
    setTimeout(() => {
      vueFlowRef.value?.fitView({ padding: 0.1, duration: 300 })
    }, 100)
  })
}

// 组件根 DOM ref
const flowWrapper = ref(null)

// 节点和边
const nodes = ref([])
const edges = ref([])

// 节点间固定间距
const NODE_GAP = 60

// 同一行节点等高，且动态计算 y 坐标保证节点间距固定
let resizeObserver = null
let isEqualizing = false // 防止死循环标志

function equalizeRowHeights() {
  if (isEqualizing) return
  const wrapper = flowWrapper.value?.querySelector('.recipe-flow-canvas')
  if (!wrapper) return
  const nodeEls = wrapper.querySelectorAll('.flow-node')
  if (nodeEls.length === 0) return
  const rowMap = new Map() // key: y坐标, value: { y, nodeIds: [], maxHeight: 0 }

  // 先重置所有节点高度为 auto，让浏览器计算自然高度
  nodeEls.forEach(el => { el.style.height = '' })

  nodeEls.forEach(el => {
    const nodeContainer = el.closest('.vue-flow__node')
    if (!nodeContainer) return
    const nodeId = nodeContainer.getAttribute('data-id')
    if (!nodeId) return
    const transform = nodeContainer.style.transform
    const yMatch = transform.match(/translate\([^,]+,\s*([^)]+)px\)/)
    if (!yMatch) return
    const y = Math.round(parseFloat(yMatch[1]))
    const height = el.offsetHeight
    if (!rowMap.has(y)) {
      rowMap.set(y, { y, nodeIds: [], maxHeight: 0 })
    }
    const row = rowMap.get(y)
    row.nodeIds.push(nodeId)
    if (height > row.maxHeight) {
      row.maxHeight = height
    }
  })

  // 设置同一行所有节点高度为最大值
  rowMap.forEach(row => {
    row.nodeIds.forEach(id => {
      const el = wrapper.querySelector(`[data-id="${id}"] .flow-node`)
      if (el) el.style.height = row.maxHeight + 'px'
    })
  })

  // 按 y 坐标排序行，重新计算每行的 y 位置
  const sortedRows = [...rowMap.values()].sort((a, b) => a.y - b.y)
  let currentY = sortedRows.length > 0 ? sortedRows[0].y : 0
  const newPositions = new Map() // nodeId → newY

  sortedRows.forEach(row => {
    row.nodeIds.forEach(id => {
      newPositions.set(id, currentY)
    })
    currentY += row.maxHeight + NODE_GAP
  })

  // 更新 nodes ref，让 Vue Flow 重新渲染边（锚点正确）
  isEqualizing = true
  const updated = nodes.value.map(node => {
    const newY = newPositions.get(node.id)
    if (newY !== undefined && node.position.y !== newY) {
      return { ...node, position: { ...node.position, y: newY } }
    }
    return node
  })
  nodes.value = updated
  nextTick(() => {
    isEqualizing = false
  })
}

// 使用 ResizeObserver 监听节点内容变化，DOM 稳定后自动触发等高计算
function setupResizeObserver() {
  if (resizeObserver) resizeObserver.disconnect()
  resizeObserver = new ResizeObserver(() => {
    // 双重 rAF 确保 Vue Flow 完成所有内部布局计算后再执行
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        equalizeRowHeights()
      })
    })
  })
  const wrapper = flowWrapper.value?.querySelector('.recipe-flow-canvas')
  if (wrapper) {
    resizeObserver.observe(wrapper)
  }
}

// 监听节点数据变化，在 Vue 渲染完成后通过 ResizeObserver 感知 DOM 变化
watch(nodes, () => {
  if (isEqualizing) return
  nextTick(() => {
    setupResizeObserver()
  })
}, { deep: true })

// 组件挂载时初始化 ResizeObserver
onMounted(() => {
  nextTick(() => {
    setupResizeObserver()
  })
})

// 悬浮 tooltip
const hoveredNode = ref(null)
const tooltipVisible = ref(false)
const tooltipData = ref({})
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipTimer = ref(null)

// 节点类型标签（root 标签根据节点类型动态显示）
const nodeTypeLabel = (type, nodeType) => {
  if (type === 'root' && nodeType === 'recipe') return '当前配方'
  if (type === 'root') return '当前物品'
  const map = { material: '材料', product: '产物' }
  return map[type] || ''
}

// 边样式：upstream=实线（材料→配方），downstream=虚线（可制作相关）
const getEdgeStyle = (edgeProps) => {
  const edge = edgeProps || {}
  const dir = edge.data?.direction
  if (dir === 'upstream') {
    return { stroke: '#e6a23c', strokeWidth: 2 }
  }
  return { stroke: '#67c23a', strokeWidth: 2, strokeDasharray: '6 3' }
}

// 点击节点 → 新窗口打开物品/配方详情页
const onNodeClick = ({ node }) => {
  // 物品节点：新窗口打开物品详情页
  if (node.data && node.data.item_id) {
    if (props.currentItemId != null && node.data.item_id === props.currentItemId) return
    const url = router.resolve(`/items/${node.data.item_id}`).href
    window.open(url, '_blank')
    return
  }
  // 配方节点：新窗口打开配方详情页
  if (node.type === 'recipe' && node.data?.recipe?.id) {
    if (props.currentRecipeId != null && node.data.recipe.id === props.currentRecipeId) return
    const url = router.resolve(`/recipes/${node.data.recipe.id}`).href
    window.open(url, '_blank')
  }
}

// 配方节点悬浮（配方节点自身已展示完整信息，tooltip 仅做补充）
const onRecipeMouseEnter = (recipe, event) => {
  clearTimeout(tooltipTimer.value)
  if (!recipe) return
  tooltipData.value = {
    label: recipe.name || '配方',
    category: recipe.profession_type_label ? `${recipe.profession_type_label} Lv.${recipe.level_required}` : ''
  }
  tooltipX.value = event.clientX + 12
  tooltipY.value = event.clientY + 12
  tooltipVisible.value = true
}

const onRecipeMouseLeave = () => {
  tooltipTimer.value = setTimeout(() => {
    tooltipVisible.value = false
  }, 150)
}

// 鼠标悬浮节点 → 弹出 tooltip
const onNodeMouseEnter = ({ node, event }) => {
  clearTimeout(tooltipTimer.value)
  hoveredNode.value = node.id
  tooltipData.value = { label: node.data.label, ...node.data }
  tooltipX.value = event.clientX + 12
  tooltipY.value = event.clientY + 12
  tooltipVisible.value = true
}

// 鼠标离开节点 → 延迟关闭 tooltip
const onNodeMouseLeave = () => {
  tooltipTimer.value = setTimeout(() => {
    tooltipVisible.value = false
    hoveredNode.value = null
  }, 150)
}

// tooltip 跟随鼠标
const onMouseMove = (e) => {
  if (tooltipVisible.value) {
    tooltipX.value = e.clientX + 12
    tooltipY.value = e.clientY + 12
  }
}

// 监听 props 变化
watch(() => props.flowData, (data) => {
  if (data && data.nodes && data.edges) {
    nodes.value = data.nodes
    edges.value = data.edges
  }
}, { deep: true, immediate: true })

// 全局鼠标移动
if (typeof window !== 'undefined') {
  window.addEventListener('mousemove', onMouseMove)
}

onBeforeUnmount(() => {
  if (typeof window !== 'undefined') {
    window.removeEventListener('mousemove', onMouseMove)
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})
</script>

<style scoped>
.recipe-flow-wrapper {
  width: 100%;
  height: 550px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fafbfc;
  position: relative;
}

.recipe-flow-wrapper.is-fullscreen {
  position: fixed;
  inset: 0;
  z-index: 10000;
  width: 100%;
  height: 100%;
  border-radius: 0;
  border: none;
}

.recipe-flow-canvas {
  width: 100%;
  height: 100%;
}

/* ===== 节点通用样式 ===== */
.flow-node {
  background: #fff;
  border: 2px solid #dcdfe6;
  border-radius: 10px;
  padding: 0;
  width: 200px;
  min-height: 100px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: box-shadow 0.25s ease, transform 0.25s ease;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.flow-node:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

.node-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  font-weight: 600;
  font-size: 14px;
  color: #fff;
}

.node-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-badge {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 500;
  padding: 1px 6px;
  border-radius: 3px;
  line-height: 1.4;
  opacity: 0.9;
}

.badge-root {
  color: #fff;
  font-weight: 600;
}

.item-node .badge-root {
  background: #409eff;
}

.recipe-node .badge-root {
  background: rgba(255, 255, 255, 0.35);
  color: #fff;
}

.badge-material {
  background: rgba(255, 255, 255, 0.3);
  color: #303133;
}

.badge-product {
  background: rgba(103, 194, 58, 0.3);
  color: #fff;
}

.badge-recipe {
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.badge-default {
  background: rgba(255, 255, 255, 0.2);
  color: #303133;
}

.node-quantity {
  background: rgba(255,255,255,0.25);
  padding: 1px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.node-body {
  padding: 6px 14px 8px;
}

.node-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2px 0;
  font-size: 12px;
}

.node-desc {
  margin-top: 2px;
  padding-top: 2px;
  border-top: 1px solid #f0f0f0;
}

.node-label {
  color: #909399;
}

.node-value {
  color: #303133;
  font-weight: 500;
}

.node-value.price {
  color: #e6a23c;
  font-weight: 600;
}

.node-value-desc {
  color: #909399;
  font-size: 11px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* ===== 物品节点 ===== */
.item-node .node-header {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  color: #303133;
}

.item-node {
  border-color: #43e97b;
}

.item-node .node-header .el-icon {
  color: #303133;
}

.item-node .node-quantity {
  background: rgba(0,0,0,0.1);
  color: #303133;
}

.item-node.item-highlight {
  border-color: #67c23a;
  box-shadow: 0 4px 20px rgba(103, 194, 58, 0.3);
}

.item-node.item-current {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.35);
}

.item-node.item-current .node-header {
  background: linear-gradient(135deg, #409eff 0%, #337ecc 100%);
  color: #fff;
}

.item-node.item-current .node-header .el-icon {
  color: #fff;
}

/* ===== 根节点（当前物品/当前配方）视觉强化 ===== */
.item-node.node-root {
  border-width: 3px;
  border-color: #409eff;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.3), 0 0 20px 4px rgba(64, 158, 255, 0.5), 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 2;
}

.item-node.node-root:hover {
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.45), 0 0 30px 6px rgba(64, 158, 255, 0.65), 0 6px 24px rgba(0, 0, 0, 0.2);
}

.recipe-node.node-root {
  border-width: 3px;
  border-color: #f0ad4e;
  box-shadow: 0 0 0 4px rgba(240, 173, 78, 0.3), 0 0 20px 4px rgba(240, 173, 78, 0.5), 0 4px 20px rgba(0, 0, 0, 0.15);
  z-index: 2;
}

.recipe-node.node-root:hover {
  box-shadow: 0 0 0 4px rgba(240, 173, 78, 0.45), 0 0 30px 6px rgba(240, 173, 78, 0.65), 0 6px 24px rgba(0, 0, 0, 0.2);
}

/* ===== 配方节点 ===== */
.recipe-node {
  border-color: #e6a23c;
  background: #fef9e7;
}

.recipe-node .node-header {
  background: linear-gradient(135deg, #f0ad4e 0%, #ec971f 100%);
  color: #fff;
}

.recipe-node .node-header .el-icon {
  color: #fff;
}

.recipe-node .node-body {
  background: #fef9e7;
}

.recipe-node .node-body .node-value {
  color: #e6a23c;
  font-size: 11px;
}

.recipe-node .recipe-tag {
  font-size: 11px;
  font-weight: 600;
}

.recipe-node .recipe-mats {
  flex-wrap: wrap;
  gap: 4px;
}

.recipe-node .recipe-mat-item {
  background: #fdf6ec;
  color: #e6a23c;
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 11px;
  white-space: nowrap;
}

.recipe-node .recipe-result {
  color: #67c23a;
  font-weight: 600;
  font-size: 12px;
  margin-top: 2px;
}

.recipe-node.item-highlight {
  border-color: #f56c6c;
  box-shadow: 0 4px 16px rgba(245, 108, 108, 0.3);
}
</style>

<style>
/* ===== 全局 tooltip 悬浮窗样式（浅色主题，含配方卡片） ===== */
.flow-tooltip {
  position: fixed;
  z-index: 9999;
  background: #fff;
  color: #303133;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  pointer-events: none;
  max-width: 300px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  border: 1px solid #e4e7ed;
}

.tooltip-header {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 6px;
  padding-bottom: 6px;
  border-bottom: 1px solid #ebeef5;
  color: #303133;
}

.tooltip-body {
  line-height: 1.5;
  color: #606266;
}

.tooltip-desc {
  color: #909399;
  font-size: 12px;
  margin-bottom: 4px;
}

.tooltip-section-title {
  margin-top: 8px;
  margin-bottom: 4px;
  font-size: 11px;
  font-weight: 600;
  color: #409eff;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tooltip-recipe-card {
  background: #f5f7fa;
  border-radius: 6px;
  padding: 6px 8px;
  margin-bottom: 4px;
}

.tooltip-recipe-name {
  font-size: 12px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 3px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tooltip-recipe-tag {
  font-size: 10px;
  font-weight: 400;
  color: #909399;
  background: #ececec;
  padding: 0 4px;
  border-radius: 3px;
}

.tooltip-recipe-mats {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 3px;
}

.tooltip-recipe-mat {
  font-size: 11px;
  background: #fff;
  color: #606266;
  padding: 1px 6px;
  border-radius: 3px;
  border: 1px solid #e4e7ed;
}

.tooltip-recipe-result {
  font-size: 11px;
  color: #67c23a;
  font-weight: 500;
}

.tooltip-vitality {
  margin-left: 6px;
  font-size: 10px;
  color: #e6a23c;
}

.tooltip-footer {
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid #ebeef5;
  font-size: 11px;
  color: #909399;
  text-align: center;
}

/* ===== 全屏按钮 ===== */
.fullscreen-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.fullscreen-exit-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10001;
  box-shadow: 0 2px 12px rgba(245, 108, 108, 0.4);
}
</style>

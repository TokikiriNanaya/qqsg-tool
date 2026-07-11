<template>
  <div class="page-container">
    <Header />

    <el-main>
      <div class="content-wrapper">
        <div v-loading="loading">
          <div v-if="item" class="item-detail">
            <h1 class="detail-title">{{ item.name }}</h1>

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

          <div v-else-if="!loading" class="not-found">
            <el-empty description="物品不存在或已被删除" />
          </div>
        </div>
      </div>
    </el-main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import RecipeFlow from '@/components/RecipeFlow.vue'
import { getItemById } from '@/api/item'
import { getItemRecipeTree } from '@/api/recipe'
import { buildItemRecipeFlow } from '@/composables/useFlowTransform'
const route = useRoute()

const loading = ref(false)
const item = ref(null)
const recipes = ref({ as_result: [], as_material: [] })

const flowData = computed(() => {
  if (!item.value) return { nodes: [], edges: [] }
  return buildItemRecipeFlow(recipes.value, item.value)
})

const loadItem = async (id) => {
  loading.value = true
  item.value = null
  recipes.value = { as_result: [], as_material: [] }

  try {
    const res = await getItemById(id)
    item.value = res
    try {
      const recipeRes = await getItemRecipeTree(id)
      recipes.value = {
        as_result: recipeRes.recipes_as_result || recipeRes.recipesAsResult || [],
        as_material: recipeRes.recipes_by_material || recipeRes.recipesByMaterial || []
      }
    } catch (e) {
      console.error('加载关联配方失败:', e)
    }
  } catch (error) {
    console.error('加载物品详情失败:', error)
    item.value = null
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) loadItem(parseInt(newId))
}, { immediate: true })
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-main { flex: 1; }

.content-wrapper {
  max-width: 1100px;
  margin: 0 auto;
  padding: 20px;
}

.back-nav {
  margin-bottom: 16px;
}

.detail-title {
  margin-bottom: 20px;
  color: #303133;
  font-size: 22px;
}

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

.not-found {
  display: flex;
  justify-content: center;
  padding: 80px 0;
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

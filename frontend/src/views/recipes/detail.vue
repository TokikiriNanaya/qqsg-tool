<template>
  <div class="page-container">
    <Header />

    <el-main>
      <div class="content-wrapper">
        <div v-loading="loading">
          <div v-if="recipe" class="recipe-detail">
            <h1 class="detail-title">{{ recipe.name }}</h1>

            <!-- 基本信息 -->
            <div class="detail-info-grid">
              <div class="info-item">
                <span class="info-label">配方名称</span>
                <span class="info-value">
                  {{ recipe.name }}
                  <el-tag :type="getProfessionType(recipe.profession_type)" size="small" class="inline-tag">
                    {{ recipe.profession_type_label || '未知' }} Lv.{{ recipe.level_required }}
                  </el-tag>
                  <el-tag v-if="recipe.is_ban === 1" type="danger" size="small" class="inline-tag" effect="dark">
                    已禁用
                  </el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">配方描述</span>
                <span class="info-value info-desc">
                  {{ recipe.description || '暂无描述' }}
                  <span class="vitality-badge" v-if="recipe.vitality_cost > 0">
                    消耗活力 {{ recipe.vitality_cost }}
                  </span>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">幸运概率</span>
                <span class="info-value">
                  <template v-if="recipe.lucky_probability > 0">
                    <span class="formula">
                      <span class="formula-col">
                        <span class="formula-note">幸运概率</span>
                        <span class="formula-val">{{ (recipe.lucky_probability / 100).toFixed(1) }}%</span>
                      </span>
                      <template v-if="recipe.profession_level_bonus > 0">
                        <span class="formula-op">+</span>
                        <span class="formula-col">
                          <span class="formula-note">副职增益</span>
                          <span class="formula-val">{{ (recipe.profession_level_bonus / 100).toFixed(1) }}%</span>
                        </span>
                        <span class="formula-op">×</span>
                        <span class="formula-col">
                          <span class="formula-note">副职等级</span>
                          <span class="formula-val">{{ PROFESSION_LEVEL }}</span>
                        </span>
                      </template>
                      <span class="formula-op">=</span>
                      <span class="formula-col">
                        <span class="formula-note">&nbsp;</span>
                        <span class="formula-val highlight">{{ calcLuckyRate(recipe).toFixed(1) }}%</span>
                      </span>
                    </span>
                  </template>
                  <span v-else>-</span>
                </span>
              </div>
              <div class="info-item">
                <span class="info-label">产出</span>
                <span class="info-value">
                  {{ recipe.result_item_name || recipe.name }}
                  <span class="quantity-badge">× {{ recipe.result_quantity }}</span>
                </span>
              </div>
              <div class="info-item" v-if="recipe.lucky_result_item_id > 0">
                <span class="info-label">幸运产出</span>
                <span class="info-value">
                  {{ recipe.lucky_result_item_name || '未知物品' }}
                  <span class="lucky-quantity">× {{ recipe.lucky_result_quantity || 1 }}</span>
                </span>
              </div>
            </div>

            <!-- 配方关系图 -->
            <div class="flow-section">
              <h3>
                <el-icon><Connection /></el-icon>
                配方关系图
              </h3>
              <RecipeFlow
                :flow-data="flowData"
                :loading="false"
                :current-item-id="null"
                :current-recipe-id="recipe?.id ?? null"
              />
              <div class="flow-legend">
                <span class="legend-item"><span class="legend-dot upstream"></span> 制作材料（实线）</span>
                <span class="legend-item"><span class="legend-dot downstream"></span> 可制作物品（虚线）</span>
              </div>
            </div>
          </div>

          <div v-else-if="!loading" class="not-found">
            <el-empty description="配方不存在或已被删除" />
          </div>
        </div>
      </div>
    </el-main>

    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import RecipeFlow from '@/components/RecipeFlow.vue'
import { getRecipeById, getItemRecipeTree } from '@/api/recipe'
import { getProfessionType, calcLuckyRate, PROFESSION_LEVEL } from '@/composables/useProfession'
import { buildSingleRecipeFlow } from '@/composables/useFlowTransform'
const route = useRoute()

const loading = ref(false)
const recipe = ref(null)

// 产物作为材料的配方（可制作物品）
const asMaterialRecipes = ref([])

// 当配方变化时，获取该产物作为材料的配方
watch(recipe, async (newRecipe) => {
  asMaterialRecipes.value = []
  if (newRecipe && newRecipe.result_item_id) {
    try {
      const treeData = await getItemRecipeTree(newRecipe.result_item_id)
      asMaterialRecipes.value = treeData.recipes_by_material || treeData.recipesByMaterial || []
    } catch (e) {
      console.error('获取可制作配方失败:', e)
    }
  }
})

// 实时计算 flowData
const flowData = computed(() => {
  if (!recipe.value) return { nodes: [], edges: [] }
  return buildSingleRecipeFlow(recipe.value, asMaterialRecipes.value)
})

const loadRecipe = async (id) => {
  loading.value = true
  recipe.value = null
  try {
    const res = await getRecipeById(id)
    recipe.value = res
  } catch (error) {
    console.error('加载配方详情失败:', error)
    recipe.value = null
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化
watch(() => route.params.id, (newId) => {
  if (newId) loadRecipe(parseInt(newId))
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

.recipe-detail { background: #fff; }

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

.info-item:hover { background: #fafbfc; }

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

.info-desc { line-height: 1.8; color: #606266; font-weight: 400; }

.inline-tag { margin-left: 10px; }

.quantity-badge, .lucky-quantity {
  display: inline-block;
  margin-left: 6px;
  background: #e6f7ff;
  color: #409eff;
  padding: 0 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.lucky-quantity { background: #fef0f0; color: #f56c6c; }

.vitality-badge {
  display: inline-block;
  margin-left: 12px;
  background: #fef0f0;
  color: #e6a23c;
  padding: 2px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.flow-section { margin-top: 8px; }

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

/* 幸运公式 */
.formula { display: inline-flex; align-items: flex-end; }
.formula-col { display: flex; flex-direction: column; align-items: center; }
.formula-note { font-size: 10px; color: #909399; font-weight: 400; line-height: 1; }
.formula-val { font-size: 14px; color: #303133; font-weight: 500; }
.formula-val.highlight { color: #409eff; font-weight: 600; }
.formula-op { margin: 0 6px 1px; color: #909399; font-size: 14px; }

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

.not-found {
  display: flex;
  justify-content: center;
  padding: 80px 0;
}
</style>

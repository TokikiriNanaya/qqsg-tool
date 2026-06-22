<template>
  <div class="page-container">
    <Header />

    <el-main>
      <div class="content-wrapper">
        <h1>物品列表</h1>

        <!-- 搜索和筛选 -->
        <el-card class="search-card">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input
                v-model="searchQuery"
                placeholder="搜索物品名称（支持拼音首字母，如 gh=钙化大骨）"
                clearable
                @input="handleSearchInput"
                @clear="loadItems"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-button type="primary" @click="loadItems">搜索</el-button>
            </el-col>
            <el-col v-if="userStore.isAdmin" :span="6" class="admin-actions">
              <el-button type="success" @click="showCreate">
                <el-icon><Plus /></el-icon>
                新增物品
              </el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 物品列表 -->
        <el-card class="list-card">
          <el-table :data="items" v-loading="loading" stripe>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="物品名称" min-width="200">
              <template #default="{ row }">
                <span class="item-link" @click="showDetail(row)">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="default_price" label="默认价格" width="100">
              <template #default="{ row }">
                <span v-if="row.default_price !== null && row.default_price !== undefined">{{ row.default_price }}</span>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="bag_limit" label="背包上限" width="100" />
            <el-table-column prop="warehouse_limit" label="仓库上限" width="100" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="showDetail(row)">查看详情</el-button>
                <template v-if="userStore.isAdmin">
                  <el-button size="small" type="primary" @click="showEdit(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
                </template>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="loadItems"
              @size-change="loadItems"
            />
          </div>
        </el-card>
      </div>
    </el-main>

    <Footer />

    <!-- 物品详情弹窗 -->
    <ItemDetailDialog
      v-model="detailVisible"
      :loading="detailLoading"
      :item="currentItem"
      :recipes="itemRecipes"
      :flow-data="itemFlowData"
      @show-item-detail="(id, name) => showItemDetailFromFlow(id, name)"
      @show-recipe="(id) => showRecipeFromFlow(id)"
    />

    <!-- 从配方图点击物品后打开的二级物品详情弹窗 -->
    <el-dialog
      v-model="subDetailVisible"
      :title="'物品详情 - ' + (subDetailItem?.name || '')"
      width="900px"
      :close-on-click-modal="true"
      top="5vh"
    >
      <div v-loading="subDetailLoading">
        <div v-if="subDetailItem" class="sub-item-detail">
          <div class="detail-info-grid">
            <div class="info-item">
              <span class="info-label">物品名称</span>
              <span class="info-value">
                {{ subDetailItem.name }}
                <span class="item-id-badge">ID: {{ subDetailItem.id }}</span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">物品分类</span>
              <span class="info-value">{{ subDetailItem.category || '-' }}</span>
            </div>
            <div class="info-item" v-if="subDetailItem.description">
              <span class="info-label">物品描述</span>
              <span class="info-value info-desc">{{ subDetailItem.description }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">默认价格</span>
              <span class="info-value">{{ subDetailItem.default_price ?? '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">背包上限</span>
              <span class="info-value">{{ subDetailItem.bag_limit }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">仓库上限</span>
              <span class="info-value">{{ subDetailItem.warehouse_limit }}</span>
            </div>
          </div>

          <!-- 配方关系图 -->
          <div v-if="subItemRecipes && (subItemRecipes.as_result.length > 0 || subItemRecipes.as_material.length > 0)" class="flow-section">
            <h3><el-icon><Connection /></el-icon> 配方关系图</h3>
            <RecipeFlow
              :flow-data="subItemFlowData"
              :loading="false"
              :current-item-id="subDetailItem?.id"
              @click-item="(id, name) => showItemDetailFromFlow(id, name)"
              @click-recipe="(id) => showRecipeFromFlow(id)"
            />
          </div>
          <div v-else-if="subItemRecipes" class="no-recipes">该物品暂无关联配方</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="subDetailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 配方详情弹窗（从流程图中点击配方卡片打开） -->
    <RecipeDetailDialog
      v-model="recipeDetailVisible"
      :loading="recipeDetailLoading"
      :recipe="currentRecipeDetail"
      @show-item-detail="(id, name) => showItemDetailFromFlow(id, name)"
      @show-recipe="(id) => showRecipeFromFlow(id)"
    />

    <!-- 编辑/新增弹窗 -->
    <ItemEditDialog
      v-model="editVisible"
      :is-creating="isCreating"
      :init-form="editForm"
      @saved="loadItems"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import RecipeFlow from '@/components/RecipeFlow.vue'
import ItemDetailDialog from './components/ItemDetailDialog.vue'
import ItemEditDialog from './components/ItemEditDialog.vue'
import RecipeDetailDialog from '../recipes/components/RecipeDetailDialog.vue'
import { getItems, getItemById, deleteItem } from '@/api/item'
import { getItemRecipeTree, getRecipeById } from '@/api/recipe'
import { useUserStore } from '@/stores/user'
import { useSearchDebounce } from '@/composables/useSearchDebounce'
import { buildItemRecipeFlow } from '@/composables/useFlowTransform'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

// 列表数据
const items = ref([])
const loading = ref(false)
const searchQuery = ref('')
const pageSize = ref(10)
const total = ref(0)

// 详情弹窗
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentItem = ref(null)
const itemRecipes = ref({ as_result: [], as_material: [] })
const itemFlowData = computed(() => {
  if (!currentItem.value) return { nodes: [], edges: [] }
  return buildItemRecipeFlow(itemRecipes.value, currentItem.value)
})

// 二级物品详情弹窗（从配方图中点击物品打开）
const subDetailVisible = ref(false)
const subDetailLoading = ref(false)
const subDetailItem = ref(null)
const subItemRecipes = ref({ as_result: [], as_material: [] })
const subItemFlowData = computed(() => {
  if (!subDetailItem.value) return { nodes: [], edges: [] }
  return buildItemRecipeFlow(subItemRecipes.value, subDetailItem.value)
})

// 配方详情弹窗（从配方图中点击配方卡片打开）
const recipeDetailVisible = ref(false)
const recipeDetailLoading = ref(false)
const currentRecipeDetail = ref(null)

// 编辑弹窗
const editVisible = ref(false)
const isCreating = ref(false)
const editForm = ref({})

// 搜索防抖
const { currentPage, handleSearchInput } = useSearchDebounce(() => loadItems())

async function loadItems() {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) params.name = searchQuery.value
    const res = await getItems(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载物品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showDetail = async (row) => {
  detailVisible.value = true
  detailLoading.value = true
  currentItem.value = null
  itemRecipes.value = { as_result: [], as_material: [] }

  try {
    const res = await getItemById(row.id)
    currentItem.value = res
    try {
      const recipeRes = await getItemRecipeTree(row.id)
      itemRecipes.value = {
        as_result: recipeRes.recipes_as_result || recipeRes.recipesAsResult || [],
        as_material: recipeRes.recipes_by_material || recipeRes.recipesByMaterial || []
      }
    } catch (e) {
      console.error('加载关联配方失败:', e)
    }
  } catch (error) {
    console.error('加载物品详情失败:', error)
  } finally {
    detailLoading.value = false
  }
}

// 从配方图中点击配方卡片 → 打开配方详情弹窗
// 先关闭已有的二级弹窗和配方弹窗，再弹出新的配方弹窗（保持与物品节点一致的关闭→重新弹出逻辑）
const showRecipeFromFlow = async (recipeId) => {
  subDetailVisible.value = false
  // 如果配方弹窗已打开，先关闭再重新打开（确保是"新的二级弹窗"而非原地更新）
  if (recipeDetailVisible.value) {
    recipeDetailVisible.value = false
    await nextTick()
  }
  recipeDetailVisible.value = true
  recipeDetailLoading.value = true
  currentRecipeDetail.value = null
  try {
    const res = await getRecipeById(recipeId)
    currentRecipeDetail.value = res
  } catch (error) {
    console.error('加载配方详情失败:', error)
  } finally {
    recipeDetailLoading.value = false
  }
}

// 从配方图中点击物品 → 打开该物品的详情弹窗
const showItemDetailFromFlow = async (itemId, itemName) => {
  subDetailVisible.value = true
  subDetailLoading.value = true
  subDetailItem.value = null
  subItemRecipes.value = { as_result: [], as_material: [] }

  try {
    const res = await getItemById(itemId)
    subDetailItem.value = res
    try {
      const recipeRes = await getItemRecipeTree(itemId)
      subItemRecipes.value = {
        as_result: recipeRes.recipes_as_result || recipeRes.recipesAsResult || [],
        as_material: recipeRes.recipes_by_material || recipeRes.recipesByMaterial || []
      }
    } catch (e) {
      console.error('加载关联配方失败:', e)
    }
  } catch (error) {
    console.error('加载物品详情失败:', error)
  } finally {
    subDetailLoading.value = false
  }
}

const showCreate = () => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  isCreating.value = true
  editForm.value = {
    id: null, name: '', category: '', description: '',
    default_price: null, bag_limit: 999, warehouse_limit: 9999
  }
  editVisible.value = true
}

const showEdit = (row) => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  isCreating.value = false
  editForm.value = {
    id: row.id, name: row.name, category: row.category || '',
    description: row.description || '', default_price: row.default_price ?? null,
    bag_limit: row.bag_limit || 99, warehouse_limit: row.warehouse_limit || 999
  }
  editVisible.value = true
}

const handleDelete = async (row) => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  try {
    await ElMessageBox.confirm('确定要删除这个物品吗？', '警告', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await deleteItem(row.id)
    ElMessage.success('删除成功')
    loadItems()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

onMounted(() => {
  loadItems()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-main { flex: 1; }

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.content-wrapper h1 {
  margin-bottom: 20px;
  color: #303133;
}

.search-card { margin-bottom: 20px; }

.list-card { min-height: 400px; }

.admin-actions { display: flex; justify-content: flex-end; }

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.item-link {
  color: #409eff;
  text-decoration: none;
  cursor: pointer;
}

.item-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 二级物品详情弹窗样式 */
.sub-item-detail { background: #fff; }

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

.info-desc { line-height: 1.8; color: #606266; font-weight: 400; }

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

.no-recipes {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}
</style>

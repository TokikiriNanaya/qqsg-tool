<template>
  <div class="items-page">
    <Header/>

    <el-main>
      <div class="container">
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
                  <el-icon>
                    <Search/>
                  </el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-button type="primary" @click="loadItems">搜索</el-button>
            </el-col>
            <el-col v-if="userStore.isAdmin" :span="6" class="admin-actions">
              <el-button type="success" @click="showCreate">
                <el-icon>
                  <Plus/>
                </el-icon>
                新增物品
              </el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 物品列表 -->
        <el-card class="list-card">
          <el-table :data="items" v-loading="loading" stripe>
            <el-table-column prop="id" label="ID" width="80"/>
            <el-table-column prop="name" label="物品名称" min-width="200">
              <template #default="{ row }">
                <span class="item-link" @click="showDetail(row)">
                  {{ row.name }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100"/>
            <el-table-column prop="default_price" label="默认价格" width="100">
              <template #default="{ row }">
                <span v-if="row.default_price !== null && row.default_price !== undefined">{{ row.default_price }}</span>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="bag_limit" label="背包上限" width="100"/>
            <el-table-column prop="warehouse_limit" label="仓库上限" width="100"/>
        <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="showDetail(row)">
                  查看详情
                </el-button>
                <template v-if="userStore.isAdmin">
                  <el-button size="small" type="primary" @click="showEdit(row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDelete(row)">
                    删除
                  </el-button>
                </template>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                @current-change="loadItems"
            />
          </div>
        </el-card>
      </div>
    </el-main>

    <Footer/>

    <!-- 物品详情弹窗 -->
    <el-dialog
        v-model="detailVisible"
        title="物品详情"
        width="700px"
        :close-on-click-modal="true"
    >
      <div v-loading="detailLoading">
        <el-descriptions v-if="currentItem" :column="2" border>
          <el-descriptions-item label="物品ID">{{ currentItem.id }}</el-descriptions-item>
          <el-descriptions-item label="物品名称">{{ currentItem.name }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ currentItem.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="默认价格">{{ currentItem.default_price ?? '-' }}</el-descriptions-item>
          <el-descriptions-item label="背包上限">{{ currentItem.bag_limit }}</el-descriptions-item>
          <el-descriptions-item label="仓库上限">{{ currentItem.warehouse_limit }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentItem?.description" class="description-section">
      <h3>物品描述</h3>
      <p>{{ currentItem.description }}</p>
    </div>

    <!-- 关联配方：该物品作为产出或材料的配方 -->
        <div v-if="itemRecipes" class="recipes-section">
          <div class="item-tree-section">
            <h3>
              <el-icon>
                <Tickets/>
              </el-icon>
              产出此物品的配方
            </h3>
            <div v-if="itemRecipes.as_result.length > 0" class="recipe-cards">
              <div
                  v-for="recipe in itemRecipes.as_result"
                  :key="recipe.id"
                  class="recipe-card"
                  @click="showItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
              >
                <div class="recipe-card-header">
                  <el-icon>
                    <Box/>
                  </el-icon>
                  <span>{{ recipe.name }}</span>×{{ recipe.material1_quantity }}
                </div>
                <div class="recipe-card-info">
                  <el-tag size="small" :type="getProfessionType(recipe.profession_type)">
                    {{ recipe.profession_type_label }}
                  </el-tag>
                  <span class="level">Lv.{{ recipe.level_required }}</span>
                </div>
                <div class="recipe-card-materials">
                  <span>材料:</span>
                  <span
                      v-if="recipe.material1_id"
                      class="material-link"
                      @click.stop="showItemTree(recipe.material1_id, recipe.material1_name)"
                  >{{ recipe.material1_name || '物品' + recipe.material1_id }}</span>
                  <span v-if="recipe.material2_id">,
                    <span class="material-link" @click.stop="showItemTree(recipe.material2_id, recipe.material2_name)">{{
                        recipe.material2_name || '物品' + recipe.material2_id
                      }}</span>×{{ recipe.material2_quantity }}
                  </span>
                  <span v-if="recipe.material3_id">,
                    <span class="material-link" @click.stop="showItemTree(recipe.material3_id, recipe.material3_name)">{{
                        recipe.material3_name || '物品' + recipe.material3_id
                      }}</span>×{{ recipe.material3_quantity }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-hint">暂无</div>
          </div>

          <div class="item-tree-section">
            <h3>
              <el-icon>
                <Grid/>
              </el-icon>
              用作材料的配方
            </h3>
            <div v-if="itemRecipes.as_material.length > 0" class="recipe-cards">
              <div
                  v-for="recipe in itemRecipes.as_material"
                  :key="recipe.id"
                  class="recipe-card result-card"
                  @click="showItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
              >
                <div class="recipe-card-header">
                  <el-icon>
                    <Box/>
                  </el-icon>
                  <span>{{ recipe.name }}</span>×{{ recipe.material1_quantity }}
                  <el-tag size="small" type="info">产出</el-tag>
                </div>
                <div class="recipe-card-info">
                  <el-tag size="small" :type="getProfessionType(recipe.profession_type)">
                    {{ recipe.profession_type_label }}
                  </el-tag>
                  <span class="level">Lv.{{ recipe.level_required }}</span>
                  <span v-if="recipe.result_quantity > 1" class="quantity">×{{ recipe.result_quantity }}</span>
                </div>
                <div class="recipe-card-materials">
                  <span>材料:</span>
                  <span
                      v-if="recipe.material1_id"
                      class="material-link"
                      @click.stop="showItemTree(recipe.material1_id, recipe.material1_name)"
                  >{{ recipe.material1_name || '物品' + recipe.material1_id }}</span>
                  <span v-if="recipe.material2_id">,
                    <span class="material-link" @click.stop="showItemTree(recipe.material2_id, recipe.material2_name)">{{
                        recipe.material2_name || '物品' + recipe.material2_id
                      }}</span>×{{ recipe.material2_quantity }}
                  </span>
                  <span v-if="recipe.material3_id">,
                    <span class="material-link" @click.stop="showItemTree(recipe.material3_id, recipe.material3_name)">{{
                        recipe.material3_name || '物品' + recipe.material3_id
                      }}</span>×{{ recipe.material3_quantity }}
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-hint">暂无</div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 配方树弹窗：从物品点击进入的配方关系 -->
    <el-dialog
        v-model="itemTreeVisible"
        :title="itemTreeTitle + ' - 配方关系'"
        width="700px"
        :close-on-click-modal="true"
    >
      <div v-loading="itemTreeLoading">
        <div class="item-tree-section">
          <h4>
            <el-icon>
              <Tickets/>
            </el-icon>
            制作配方
          </h4>
          <div v-if="itemTreeData.recipesAsResult.length > 0" class="recipe-cards">
            <div
                v-for="recipe in itemTreeData.recipesAsResult"
                :key="recipe.id"
                class="recipe-card"
                @click="navigateItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
            >
              <div class="recipe-card-header">
                <el-icon>
                  <Box/>
                </el-icon>
                <span>{{ recipe.name }}</span>×{{ recipe.material1_quantity }}
              </div>
              <div class="recipe-card-info">
                <el-tag size="small" :type="getProfessionType(recipe.profession_type)">
                  {{ recipe.profession_type_label }}
                </el-tag>
                <span class="level">Lv.{{ recipe.level_required }}</span>
              </div>
              <div class="recipe-card-materials">
                <span>材料:</span>
                <span
                    v-if="recipe.material1_id"
                    class="material-link"
                    @click.stop="navigateItemTree(recipe.material1_id, recipe.material1_name)"
                >{{ recipe.material1_name || '物品' + recipe.material1_id }}</span>
                <span v-if="recipe.material2_id">,
                  <span class="material-link"
                        @click.stop="navigateItemTree(recipe.material2_id, recipe.material2_name)">{{
                      recipe.material2_name || '物品' + recipe.material2_id
                    }}</span>×{{ recipe.material2_quantity }}
                </span>
                <span v-if="recipe.material3_id">,
                  <span class="material-link"
                        @click.stop="navigateItemTree(recipe.material3_id, recipe.material3_name)">{{
                      recipe.material3_name || '物品' + recipe.material3_id
                    }}</span>×{{ recipe.material3_quantity }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">暂无</div>
        </div>

        <div class="item-tree-section">
          <h4>
            <el-icon>
              <Grid/>
            </el-icon>
            可制作配方
          </h4>
          <div v-if="itemTreeData.recipesByMaterial.length > 0" class="recipe-cards">
            <div
                v-for="recipe in itemTreeData.recipesByMaterial"
                :key="recipe.id"
                class="recipe-card result-card"
                @click="navigateItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
            >
              <div class="recipe-card-header">
                <el-icon>
                  <Box/>
                </el-icon>
                <span>{{ recipe.name }}</span>×{{ recipe.result_quantity }}
                <el-tag size="small" type="info">产出</el-tag>
              </div>
              <div class="recipe-card-info">
                <el-tag size="small" :type="getProfessionType(recipe.profession_type)">
                  {{ recipe.profession_type_label }}
                </el-tag>
                <span class="level">Lv.{{ recipe.level_required }}</span>
                <span v-if="recipe.result_quantity > 1" class="quantity"></span>
              </div>
              <div class="recipe-card-materials">
                <span>材料:</span>
                <span
                    v-if="recipe.material1_id"
                    class="material-link"
                    @click.stop="navigateItemTree(recipe.material1_id, recipe.material1_name)"
                >{{ recipe.material1_name || '物品' + recipe.material1_id }}</span>×{{ recipe.material1_quantity }}
                <span v-if="recipe.material2_id">,
                  <span class="material-link"
                        @click.stop="navigateItemTree(recipe.material2_id, recipe.material2_name)">{{
                      recipe.material2_name || '物品' + recipe.material2_id
                    }}</span>×{{ recipe.material2_quantity }}
                </span>
                <span v-if="recipe.material3_id">,
                  <span class="material-link"
                        @click.stop="navigateItemTree(recipe.material3_id, recipe.material3_name)">{{
                      recipe.material3_name || '物品' + recipe.material3_id
                    }}</span>×{{ recipe.material3_quantity }}
                </span>
              </div>
            </div>
          </div>
          <div v-else class="empty-hint">暂无</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="itemTreeVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 编辑/新增物品弹窗（仅管理员） -->
    <el-dialog
        v-if="userStore.isAdmin"
        v-model="editVisible"
        :title="isCreating ? '新增物品' : '编辑物品'"
        width="700px"
        :close-on-click-modal="true"
    >
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="物品名称" prop="name">
              <el-input v-model="editForm.name"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物品分类">
              <el-input v-model="editForm.category" placeholder="如：庖丁、工匠"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="默认价格">
              <el-input-number v-model="editForm.default_price" :min="0" class="full-width"/>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="背包上限">
              <el-input-number v-model="editForm.bag_limit" :min="1" class="full-width"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="仓库上限">
              <el-input-number v-model="editForm.warehouse_limit" :min="1" class="full-width"/>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="24">
            <el-form-item label="物品描述">
              <el-input v-model="editForm.description" type="textarea" :rows="3"/>
            </el-form-item>
          </el-col>
        </el-row>


      </el-form>

      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitEdit" :loading="editLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, onMounted} from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import {getItems, getItemById, createItem, updateItem, deleteItem} from '@/api/item'
import {getItemRecipeTree} from '@/api/recipe'
import {useUserStore} from '@/stores/user'
import {ElMessage, ElMessageBox} from 'element-plus'

const userStore = useUserStore()

const items = ref([])
const loading = ref(false)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 详情弹窗相关
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentItem = ref(null)
const itemRecipes = ref({as_result: [], as_material: []})

// 配方树弹窗相关
const itemTreeVisible = ref(false)
const itemTreeLoading = ref(false)
const itemTreeTitle = ref('')
const itemTreeData = ref({recipesByMaterial: [], recipesAsResult: []})

// 副职类型对应的tag类型
const getProfessionType = (type) => {
  const typeMap = {
    1: 'success',
    2: 'primary',
    3: 'warning',
    4: 'danger',
    5: 'info'
  }
  return typeMap[type] || 'default'
}

// 编辑弹窗相关
const editVisible = ref(false)
const editLoading = ref(false)
const formRef = ref(null)
const isCreating = ref(false)
const editForm = ref({
  id: null,
  name: '',
  category: '',
  description: '',
  default_price: null,
  bag_limit: 999,
  warehouse_limit: 9999
})

const rules = {
  name: [{required: true, message: '请输入物品名称', trigger: 'blur'}]
}

// 搜索防抖
let searchTimer = null
const handleSearchInput = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadItems()
  }, 300)
}

const loadItems = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (searchQuery.value) {
      params.name = searchQuery.value
    }

    const res = await getItems(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载物品列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示详情弹窗
const showDetail = async (row) => {
  detailVisible.value = true
  detailLoading.value = true
  currentItem.value = null
  itemRecipes.value = {as_result: [], as_material: []}

  try {
    const res = await getItemById(row.id)
    currentItem.value = res

    // 同时查询关联配方
    try {
      const recipeRes = await getItemRecipeTree(row.id)
      itemRecipes.value = {
        as_result: recipeRes.recipes_as_result || [],
        as_material: recipeRes.recipes_by_material || []
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

// 显示配方树弹窗（从物品点击进入）
const showItemTree = async (itemId, itemName) => {
  itemTreeTitle.value = itemName
  itemTreeVisible.value = true
  itemTreeLoading.value = true
  itemTreeData.value = {recipesByMaterial: [], recipesAsResult: []}

  try {
    const res = await getItemRecipeTree(itemId)
    itemTreeData.value = {
      recipesByMaterial: res.recipes_by_material || [],
      recipesAsResult: res.recipes_as_result || []
    }
  } catch (error) {
    console.error('加载配方失败:', error)
  } finally {
    itemTreeLoading.value = false
  }
}

// 导航到另一个物品的配方树（在弹窗内切换）
const navigateItemTree = async (itemId, itemName) => {
  await showItemTree(itemId, itemName || `物品${itemId}`)
}

// 显示新增弹窗
const showCreate = async () => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }

  isCreating.value = true
  editForm.value = {
    id: null,
    name: '',
    category: '',
    description: '',
    default_price: null,
    bag_limit: 999,
    warehouse_limit: 9999
  }
  editVisible.value = true
}

// 显示编辑弹窗
const showEdit = async (row) => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }

  isCreating.value = false

  editForm.value = {
    id: row.id,
    name: row.name,
    category: row.category || '',
    description: row.description || '',
    default_price: row.default_price ?? null,
    bag_limit: row.bag_limit || 99,
    warehouse_limit: row.warehouse_limit || 999
  }
  editVisible.value = true
}

// 提交编辑/创建
const handleSubmitEdit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      editLoading.value = true
      try {
        if (isCreating.value) {
          const {id, ...createData} = editForm.value
          await createItem(createData)
          ElMessage.success('创建成功')
        } else {
          const {id, ...updateData} = editForm.value
          await updateItem(Number(id), updateData)
          ElMessage.success('更新成功')
        }
        editVisible.value = false
        loadItems()
      } catch (error) {
        console.error('操作失败:', error)
      } finally {
        editLoading.value = false
      }
    }
  })
}

// 删除物品
const handleDelete = async (row) => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }

  try {
    await ElMessageBox.confirm('确定要删除这个物品吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteItem(row.id)
    ElMessage.success('删除成功')
    loadItems()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  loadItems()
})
</script>

<style scoped>
.items-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-main {
  flex: 1;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

.search-card {
  margin-bottom: 20px;
}

.admin-actions {
  display: flex;
  justify-content: flex-end;
}

.list-card {
  min-height: 400px;
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.description-section,
.recipes-section {
  margin-top: 20px;
}

.description-section h3,
.recipes-section h3 {
  margin-bottom: 10px;
  color: #606266;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.description-section p {
  line-height: 1.8;
  color: #606266;
}

/* 配方树卡片样式 */
.item-tree-section {
  margin-bottom: 20px;
}

.item-tree-section h3,
.item-tree-section h4 {
  margin-bottom: 10px;
  color: #606266;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-tree-section h4 {
  font-size: 15px;
}

.recipe-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recipe-card {
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border-left: 3px solid #409eff;
}

.recipe-card:hover {
  background: #ecf5ff;
  transform: translateX(2px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.recipe-card.result-card {
  border-left-color: #67c23a;
}

.recipe-card.result-card:hover {
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

/* 空状态紧凑提示 */
.empty-hint {
  padding: 6px 12px;
  color: #909399;
  font-size: 12px;
  background: #f5f7fa;
  border-radius: 4px;
  text-align: center;
}

.full-width {
  width: 100%;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}



</style>
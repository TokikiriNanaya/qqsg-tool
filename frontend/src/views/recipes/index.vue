<template>
  <div class="page-container">
    <Header />

    <el-main>
      <div class="content-wrapper">
        <h1>配方列表</h1>

        <!-- 搜索和筛选 -->
        <el-card class="search-card">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-input
                v-model="searchQuery"
                placeholder="搜索配方名称（支持拼音首字母）"
                clearable
                @input="handleSearchInput"
                @clear="loadRecipes"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-select v-model="professionType" placeholder="选择副职类型" clearable @change="loadRecipes">
                <el-option label="全部" value="" />
                <el-option
                  v-for="tag in professionTags"
                  :key="tag.value"
                  :label="tag.name"
                  :value="tag.value"
                />
              </el-select>
            </el-col>
            <el-col :span="4">
              <el-button type="primary" @click="loadRecipes">搜索</el-button>
            </el-col>
            <el-col v-if="userStore.isAdmin" :span="6" class="admin-actions">
              <el-button type="success" @click="showCreate">
                <el-icon><Plus /></el-icon> 新增配方
              </el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 配方列表 -->
        <el-card class="list-card">
          <el-table :data="recipes" v-loading="loading" stripe :row-class-name="getRowClassName">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="配方名称" min-width="200">
              <template #default="{ row }">
                <span class="recipe-link" @click="showDetail(row)">
                  {{ row.name }}
                  <el-tag v-if="row.is_ban === 1" size="small" type="danger" effect="plain">已禁用</el-tag>
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="profession_type_label" label="副职类型" width="120">
              <template #default="{ row }">
                <el-tag :type="getProfessionType(row.profession_type)">
                  {{ row.profession_type_label || '未知' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="level_required" label="所需等级" width="80" />
            <el-table-column label="幸运概率" width="100">
              <template #default="{ row }">
                <span v-if="row.lucky_probability > 0">{{ (row.lucky_probability / 100).toFixed(1) }}%</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="副职增益" width="100">
              <template #default="{ row }">
                <span v-if="row.profession_level_bonus > 0">{{ (row.profession_level_bonus / 100).toFixed(1) }}%</span>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="250" fixed="right">
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
              @current-change="loadRecipes"
              @size-change="loadRecipes"
            />
          </div>
        </el-card>
      </div>
    </el-main>

    <Footer />

    <!-- 配方详情弹窗 -->
    <RecipeDetailDialog
      v-model="detailVisible"
      :loading="detailLoading"
      :recipe="currentRecipe"
      @show-tree="(id, name) => showItemTree(id, name)"
    />

    <!-- 物品配方树弹窗 -->
    <ItemTreeDialog
      v-model="itemTreeVisible"
      :title="itemTreeTitle"
      :loading="itemTreeLoading"
      :tree-data="itemTreeData"
      @navigate="navigateItemTree"
    />

    <!-- 编辑弹窗 -->
    <RecipeEditDialog
      v-model="editVisible"
      :is-creating="isCreating"
      :init-form="editForm"
      :profession-tags="professionTags"
      @saved="loadRecipes"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import ItemTreeDialog from '@/components/ItemTreeDialog.vue'
import RecipeDetailDialog from './components/RecipeDetailDialog.vue'
import RecipeEditDialog from './components/RecipeEditDialog.vue'
import { getRecipes, getRecipeById, deleteRecipe } from '@/api/recipe'
import { getAllTags } from '@/api/item'
import { useUserStore } from '@/stores/user'
import { useRecipeTree } from '@/composables/useRecipeTree'
import { useSearchDebounce } from '@/composables/useSearchDebounce'
import { getProfessionType } from '@/composables/useProfession'
import { ElMessage, ElMessageBox } from 'element-plus'

const userStore = useUserStore()

// 副职标签
const professionTags = ref([])

// 列表数据
const recipes = ref([])
const loading = ref(false)
const searchQuery = ref('')
const professionType = ref('')
const pageSize = ref(10)
const total = ref(0)

// 详情弹窗
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentRecipe = ref(null)

// 编辑弹窗
const editVisible = ref(false)
const isCreating = ref(false)
const editForm = ref({})

// 配方树
const { itemTreeVisible, itemTreeLoading, itemTreeTitle, itemTreeData, showItemTree, navigateItemTree } = useRecipeTree()

// 搜索防抖
const { currentPage, handleSearchInput } = useSearchDebounce(() => loadRecipes())

const getRowClassName = ({ row }) => row.is_ban === 1 ? 'ban-row' : ''

async function loadRecipes() {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) params.name = searchQuery.value
    if (professionType.value !== '') params.profession_type = parseInt(professionType.value)
    const res = await getRecipes(params)
    recipes.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载配方列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showDetail = async (row) => {
  detailVisible.value = true
  detailLoading.value = true
  currentRecipe.value = null
  try {
    const res = await getRecipeById(row.id)
    currentRecipe.value = res
  } catch (error) {
    console.error('加载配方详情失败:', error)
  } finally {
    detailLoading.value = false
  }
}

const showCreate = () => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  isCreating.value = true
  editForm.value = {
    id: null, name: '', profession_type: null, level_required: 1, vitality_cost: 0,
    material1_id: null, material1_quantity: 0,
    material2_id: null, material2_quantity: 0,
    material3_id: null, material3_quantity: 0,
    lucky_probability: 0, profession_level_bonus: 0,
    result_item_id: null, result_quantity: 1,
    lucky_result_item_id: null, lucky_result_quantity: 0,
    description: '', is_ban: 0
  }
  editVisible.value = true
}

const showEdit = (row) => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  isCreating.value = false
  editForm.value = {
    id: row.id, name: row.name,
    profession_type: row.profession_type || null,
    level_required: row.level_required || 1,
    vitality_cost: row.vitality_cost || 0,
    material1_id: row.material1_id || null,
    material1_quantity: row.material1_quantity || 0,
    material2_id: row.material2_id || null,
    material2_quantity: row.material2_quantity || 0,
    material3_id: row.material3_id || null,
    material3_quantity: row.material3_quantity || 0,
    lucky_probability: Math.round((row.lucky_probability || 0) / 100),
    profession_level_bonus: Math.round((row.profession_level_bonus || 0) / 100),
    result_item_id: row.result_item_id || null,
    result_quantity: row.result_quantity || 1,
    lucky_result_item_id: row.lucky_result_item_id && row.lucky_result_item_id > 0 ? row.lucky_result_item_id : null,
    lucky_result_quantity: row.lucky_result_quantity || 0,
    description: row.description || '',
    is_ban: row.is_ban || 0
  }
  editVisible.value = true
}

const handleDelete = async (row) => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  try {
    await ElMessageBox.confirm('确定要删除这个配方吗？', '警告', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await deleteRecipe(row.id)
    ElMessage.success('删除成功')
    loadRecipes()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

const loadProfessionTags = async () => {
  try {
    const res = await getAllTags({ category: 'profession_type' })
    professionTags.value = (res.items || []).sort((a, b) => a.sort_order - b.sort_order)
  } catch (error) {
    console.error('加载副职类型标签失败:', error)
  }
}

onMounted(() => {
  loadProfessionTags()
  loadRecipes()
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

.recipe-link {
  color: #409eff;
  text-decoration: none;
  cursor: pointer;
}

.recipe-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.recipe-link .el-tag {
  margin-left: 8px;
  vertical-align: middle;
}

::deep(.ban-row) { background-color: #fef0f0 !important; }
::deep(.ban-row:hover > td) { background-color: #fee6e6 !important; }
</style>

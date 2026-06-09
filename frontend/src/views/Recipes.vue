<template>
  <div class="recipes-page">
    <Header />
    
    <el-main>
      <div class="container">
        <h1>配方列表</h1>
        
        <!-- 搜索和筛选 -->
        <el-card class="search-card">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-input 
                v-model="searchQuery" 
                placeholder="搜索配方名称"
                clearable
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
          </el-row>
        </el-card>
        
        <!-- 配方列表 -->
        <el-card class="list-card">
          <el-table :data="recipes" v-loading="loading" stripe>
            <el-table-column prop="name" label="配方名称" min-width="200">
              <template #default="{ row }">
                <span class="recipe-link" @click="showDetail(row)">
                  {{ row.name }}
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
            <el-table-column prop="level_required" label="所需等级" width="100" />
            <el-table-column label="操作" width="250" fixed="right">
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
              @current-change="loadRecipes"
            />
          </div>
        </el-card>
      </div>
    </el-main>
    
    <Footer />
    
    <!-- 配方详情弹窗 -->
    <el-dialog 
      v-model="detailVisible" 
      title="配方详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-loading="detailLoading">
        <el-descriptions v-if="currentRecipe" :column="2" border>
          <el-descriptions-item label="配方名称">{{ currentRecipe.name }}</el-descriptions-item>
          <el-descriptions-item label="分类">{{ currentRecipe.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="副职类型">{{ currentRecipe.profession_type_label || '-' }}</el-descriptions-item>
          <el-descriptions-item label="所需等级">{{ currentRecipe.level_required }}</el-descriptions-item>
          <el-descriptions-item label="制作结果">{{ currentRecipe.result || '-' }}</el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(currentRecipe.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentRecipe?.description" class="description-section">
          <h3>配方描述</h3>
          <p>{{ currentRecipe.description }}</p>
        </div>
        
        <div v-if="currentRecipe" class="materials-section">
          <h3>所需材料</h3>
          <el-table :data="parseMaterials(currentRecipe.materials)" stripe>
            <el-table-column prop="name" label="材料名称" />
            <el-table-column prop="quantity" label="数量" width="100" />
          </el-table>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <!-- 编辑配方弹窗（仅管理员） -->
    <el-dialog 
      v-if="userStore.isAdmin"
      v-model="editVisible" 
      title="编辑配方"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="配方名称" prop="name">
          <el-input v-model="editForm.name" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="editForm.category">
            <el-option label="武器" value="weapon" />
            <el-option label="防具" value="armor" />
            <el-option label="药品" value="potion" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所需等级" prop="level_required">
          <el-input-number v-model="editForm.level_required" :min="1" />
        </el-form-item>
        
        <el-form-item label="制作结果" prop="result">
          <el-input v-model="editForm.result" />
        </el-form-item>
        
        <el-form-item label="配方描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
        
        <el-form-item label="所需材料">
          <el-input 
            v-model="editForm.materials" 
            type="textarea" 
            :rows="5"
            placeholder='JSON格式，例如: [{"name": "材料1", "quantity": 10}]'
          />
        </el-form-item>
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
import { ref, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { getRecipes, getRecipeById, updateRecipe, deleteRecipe } from '@/api/recipe'
import { getAllTags } from '@/api/item'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

// 副职类型标签列表（从tag获取）
const professionTags = ref([])

// 副职类型对应的tag类型
const getProfessionType = (type) => {
  const typeMap = {
    1: 'success',  // 庖丁
    2: 'primary',  // 工匠
    3: 'warning',  // 巧匠
    4: 'danger',   // 玉匠
    5: 'info'      // 书匠
  }
  return typeMap[type] || 'default'
}

const recipes = ref([])
const loading = ref(false)
const searchQuery = ref('')
const professionType = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 详情弹窗相关
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentRecipe = ref(null)

// 编辑弹窗相关
const editVisible = ref(false)
const editLoading = ref(false)
const formRef = ref(null)
const userStore = useUserStore()

const editForm = ref({
  id: null,
  name: '',
  category: '',
  level_required: 1,
  result: '',
  description: '',
  materials: ''
})

const rules = {
  name: [{ required: true, message: '请输入配方名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  result: [{ required: true, message: '请输入制作结果', trigger: 'blur' }]
}

const loadRecipes = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (searchQuery.value) {
      params.name = searchQuery.value
    }
    
    if (professionType.value) {
      params.profession_type = parseInt(professionType.value)
    }
    
    const res = await getRecipes(params)
    recipes.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载配方列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示详情弹窗
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

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 解析材料JSON
const parseMaterials = (materialsStr) => {
  if (!materialsStr) return []
  try {
    return typeof materialsStr === 'string' ? JSON.parse(materialsStr) : materialsStr
  } catch (e) {
    return []
  }
}

// 显示编辑弹窗（仅管理员）
const showEdit = (row) => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }
  
  editForm.value = {
    id: row.id,
    name: row.name,
    category: row.category || '',
    level_required: row.level_required,
    result: row.result || '',
    description: row.description || '',
    materials: typeof row.materials === 'string' ? row.materials : JSON.stringify(row.materials || [])
  }
  editVisible.value = true
}

// 提交编辑
const handleSubmitEdit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      editLoading.value = true
      try {
        await updateRecipe(editForm.value.id, editForm.value)
        ElMessage.success('更新成功')
        editVisible.value = false
        loadRecipes()
      } catch (error) {
        console.error('更新失败:', error)
      } finally {
        editLoading.value = false
      }
    }
  })
}

// 删除配方（仅管理员）
const handleDelete = async (row) => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }
  
  try {
    await ElMessageBox.confirm('确定要删除这个配方吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteRecipe(row.id)
    ElMessage.success('删除成功')
    loadRecipes()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 加载副职类型标签
const loadProfessionTags = async () => {
  try {
    const res = await getAllTags({ category: 'profession_type' })
    professionTags.value = (res.items || []).sort((a, b) => a.value - b.value)
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
.recipes-page {
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

.list-card {
  min-height: 400px;
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

.description-section,
.materials-section {
  margin-top: 20px;
}

.description-section h3,
.materials-section h3 {
  margin-bottom: 10px;
  color: #606266;
  font-size: 16px;
}

.description-section p {
  line-height: 1.8;
  color: #606266;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
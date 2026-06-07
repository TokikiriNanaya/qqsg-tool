<template>
  <div class="admin-page">
    <Header />
    
    <el-main>
      <div class="container">
        <h1>管理后台</h1>
        
        <el-tabs v-model="activeTab">
          <!-- 配方管理 -->
          <el-tab-pane label="配方管理" name="recipes">
            <el-button type="primary" @click="showAddDialog" style="margin-bottom: 20px">
              <el-icon><Plus /></el-icon>
              添加配方
            </el-button>
            
            <el-table :data="recipes" v-loading="loading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="name" label="配方名称" />
              <el-table-column prop="category" label="分类" width="100" />
              <el-table-column prop="level_required" label="等级" width="80" />
              <el-table-column prop="created_at" label="创建时间" width="180">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="handleEdit(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          
          <!-- 用户管理 -->
          <el-tab-pane label="用户管理" name="users">
            <el-table :data="users" v-loading="userLoading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="role" label="角色" width="100" />
              <el-table-column prop="is_active" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '活跃' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-main>
    
    <Footer />
    
    <!-- 添加/编辑配方对话框 -->
    <el-dialog 
      v-model="dialogVisible" 
      :title="isEdit ? '编辑配方' : '添加配方'"
      width="600px"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="配方名称" prop="name">
          <el-input v-model="form.name" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="form.category">
            <el-option label="武器" value="weapon" />
            <el-option label="防具" value="armor" />
            <el-option label="药品" value="potion" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="所需等级" prop="level_required">
          <el-input-number v-model="form.level_required" :min="1" />
        </el-form-item>
        
        <el-form-item label="制作结果" prop="result">
          <el-input v-model="form.result" />
        </el-form-item>
        
        <el-form-item label="配方描述">
          <el-input v-model="form.description" type="textarea" :rows="3" />
        </el-form-item>
        
        <el-form-item label="所需材料">
          <el-input 
            v-model="form.materials" 
            type="textarea" 
            :rows="5"
            placeholder='JSON格式，例如: [{"name": "材料1", "quantity": 10}]'
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { getRecipes, createRecipe, updateRecipe, deleteRecipe } from '@/api/recipe'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('recipes')
const recipes = ref([])
const users = ref([])
const loading = ref(false)
const userLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)

const form = reactive({
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

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadRecipes = async () => {
  loading.value = true
  try {
    const res = await getRecipes({ skip: 0, limit: 100 })
    recipes.value = res
  } catch (error) {
    console.error('加载配方列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showAddDialog = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    name: '',
    category: '',
    level_required: 1,
    result: '',
    description: '',
    materials: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await updateRecipe(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createRecipe(form)
          ElMessage.success('添加成功')
        }
        dialogVisible.value = false
        loadRecipes()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleDelete = async (row) => {
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

onMounted(() => {
  loadRecipes()
})
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
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
</style>

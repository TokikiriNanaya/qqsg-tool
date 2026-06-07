<template>
  <div class="recipe-detail">
    <Header />
    
    <el-main>
      <div class="container" v-loading="loading">
        <el-button @click="$router.back()" style="margin-bottom: 20px">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        
        <el-card v-if="recipe">
          <h1>{{ recipe.name }}</h1>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="分类">{{ recipe.category }}</el-descriptions-item>
            <el-descriptions-item label="所需等级">{{ recipe.level_required }}</el-descriptions-item>
            <el-descriptions-item label="制作结果">{{ recipe.result }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ formatDate(recipe.created_at) }}</el-descriptions-item>
          </el-descriptions>
          
          <div v-if="recipe.description" class="description">
            <h3>配方描述</h3>
            <p>{{ recipe.description }}</p>
          </div>
          
          <div class="materials">
            <h3>所需材料</h3>
            <el-table :data="parseMaterials(recipe.materials)" stripe>
              <el-table-column prop="name" label="材料名称" />
              <el-table-column prop="quantity" label="数量" width="100" />
            </el-table>
          </div>
          
          <div v-if="userStore.isAdmin" class="admin-actions">
            <el-button type="primary" @click="handleEdit">编辑</el-button>
            <el-button type="danger" @click="handleDelete">删除</el-button>
          </div>
        </el-card>
        
        <el-empty v-else description="配方不存在" />
      </div>
    </el-main>
    
    <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { useUserStore } from '@/stores/user'
import { getRecipeById, deleteRecipe } from '@/api/recipe'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const recipe = ref(null)
const loading = ref(false)

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleString('zh-CN')
}

const parseMaterials = (materialsStr) => {
  try {
    return JSON.parse(materialsStr)
  } catch (e) {
    return []
  }
}

const loadRecipe = async () => {
  loading.value = true
  try {
    const res = await getRecipeById(route.params.id)
    recipe.value = res
  } catch (error) {
    console.error('加载配方详情失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEdit = () => {
  // TODO: 实现编辑功能
  ElMessage.info('编辑功能待实现')
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定要删除这个配方吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteRecipe(recipe.value.id)
    ElMessage.success('删除成功')
    router.push('/recipes')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  loadRecipe()
})
</script>

<style scoped>
.recipe-detail {
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

h1 {
  margin-bottom: 20px;
  color: #303133;
}

h3 {
  margin: 20px 0 10px;
  color: #606266;
}

.description {
  margin-top: 20px;
}

.description p {
  line-height: 1.8;
  color: #606266;
}

.materials {
  margin-top: 30px;
}

.admin-actions {
  margin-top: 30px;
  text-align: right;
}
</style>

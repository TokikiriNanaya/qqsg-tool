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
              <el-select v-model="category" placeholder="选择分类" clearable @change="loadRecipes">
                <el-option label="全部" value="" />
                <el-option label="武器" value="weapon" />
                <el-option label="防具" value="armor" />
                <el-option label="药品" value="potion" />
                <el-option label="其他" value="other" />
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
            <el-table-column prop="name" label="配方名称" min-width="150">
              <template #default="{ row }">
                <router-link :to="`/recipes/${row.id}`" class="recipe-link">
                  {{ row.name }}
                </router-link>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="level_required" label="所需等级" width="100" />
            <el-table-column prop="result" label="制作结果" min-width="150" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="$router.push(`/recipes/${row.id}`)">
                  查看详情
                </el-button>
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { getRecipes } from '@/api/recipe'

const recipes = ref([])
const loading = ref(false)
const searchQuery = ref('')
const category = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const loadRecipes = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    if (category.value) {
      params.category = category.value
    }
    
    const res = await getRecipes(params)
    recipes.value = res
    total.value = res.length // TODO: 需要从后端获取总数
  } catch (error) {
    console.error('加载配方列表失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
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
}

.recipe-link:hover {
  color: #66b1ff;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>

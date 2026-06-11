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
                <span v-if="row.lucky_probability > 0">{{ (row.lucky_probability / 10000 * 100).toFixed(1) }}%</span>
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
        <el-descriptions v-if="currentRecipe" :column="1" border>
          <el-descriptions-item label="配方名称">{{ currentRecipe.name }}</el-descriptions-item>
          <el-descriptions-item label="副职类型">{{ currentRecipe.profession_type_label || '-' }}</el-descriptions-item>
          <el-descriptions-item label="所需等级">{{ currentRecipe.level_required }}</el-descriptions-item>
        </el-descriptions>
        
        <div v-if="currentRecipe?.description" class="description-section">
          <h3>配方描述</h3>
          <p>{{ currentRecipe.description }}</p>
        </div>
        
<div v-if="currentRecipe" class="materials-section">
          <h3>所需材料</h3>
          <div class="recipe-tree">
            <!-- 根节点：产物 -->
            <div class="tree-root">
              <div class="tree-node result-node" @click="showItemTree(currentRecipe.result_item_id, currentRecipe.result_item_name)">
                <el-icon><Box /></el-icon>
                <span>{{ currentRecipe.result_item_name || currentRecipe.name }}</span>
                <span v-if="currentRecipe.result_quantity > 1" class="quantity">× {{ currentRecipe.result_quantity }}</span>
              </div>
            </div>
            
            <!-- 连接线（水平） -->
            <div v-if="getRecipeMaterials(currentRecipe).length > 0" class="tree-connector">
              <div class="connector-line"></div>
              <div class="connector-arrow">
                <el-icon><DArrowRight /></el-icon>
              </div>
              <div class="connector-line"></div>
            </div>
            
            <!-- 子节点：材料（左右排列） -->
            <div class="tree-children">
              <div 
                v-for="(material, index) in getRecipeMaterials(currentRecipe)" 
                :key="index"
                class="tree-node material-node"
                @click="showItemTree(material.id, material.name)"
              >
                <el-icon><Grid /></el-icon>
                <span>{{ material.name }}</span>
                <span class="quantity">× {{ material.quantity }}</span>
              </div>
            </div>
          </div>
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
      :title="isCreating ? '新增配方' : '编辑配方'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="editForm" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配方名称" prop="name">
              <el-input v-model="editForm.name" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="副职类型" prop="profession_type">
              <el-select v-model="editForm.profession_type" placeholder="选择副职类型" class="full-width">
                <el-option 
                  v-for="tag in professionTags" 
                  :key="tag.value" 
                  :label="tag.name" 
                  :value="tag.value" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="所需等级">
              <el-input-number v-model="editForm.level_required" :min="1" class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="消耗活力">
              <el-input-number v-model="editForm.vitality_cost" :min="0" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">材料</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料1">
              <el-select 
                v-model="editForm.material1_id" 
                filterable 
                remote
                placeholder="搜索物品"
                :remote-method="(query) => doSearchItems(query, 1)"
                :loading="itemSearchLoading[1]"
                class="full-width"
                clearable
              >
                <el-option
                  v-for="item in itemSearchResults[1]"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料1数量">
              <el-input-number v-model="editForm.material1_quantity" :min="0" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料2">
              <el-select 
                v-model="editForm.material2_id" 
                filterable 
                remote
                placeholder="搜索物品"
                :remote-method="(query) => doSearchItems(query, 2)"
                :loading="itemSearchLoading[2]"
                class="full-width"
                clearable
              >
                <el-option
                  v-for="item in itemSearchResults[2]"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料2数量">
              <el-input-number v-model="editForm.material2_quantity" :min="0" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料3">
              <el-select 
                v-model="editForm.material3_id" 
                filterable 
                remote
                placeholder="搜索物品"
                :remote-method="(query) => doSearchItems(query, 3)"
                :loading="itemSearchLoading[3]"
                class="full-width"
                clearable
              >
                <el-option
                  v-for="item in itemSearchResults[3]"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料3数量">
              <el-input-number v-model="editForm.material3_quantity" :min="0" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">产出</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="产出物品">
              <el-select 
                v-model="editForm.result_item_id" 
                filterable 
                remote
                placeholder="搜索物品"
                :remote-method="(query) => doSearchItems(query, 'result')"
                :loading="itemSearchLoading['result']"
                class="full-width"
                clearable
              >
                <el-option
                  v-for="item in itemSearchResults['result']"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="产出数量">
              <el-input-number v-model="editForm.result_quantity" :min="1" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">幸运合成</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
<el-form-item label="幸运概率(%)">
              <el-input-number v-model="editForm.lucky_probability" :min="0" :max="100" class="full-width" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="副职等级增益(%)">
              <el-input-number v-model="editForm.profession_level_bonus" :min="0" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="幸运产出物品">
              <el-select
                v-model="editForm.lucky_result_item_id"
                filterable
                remote
                placeholder="搜索物品"
                :remote-method="(query) => doSearchItems(query, 'lucky')"
                :loading="itemSearchLoading['lucky']"
                class="full-width"
                clearable
              >
                <el-option
                  v-for="item in itemSearchResults['lucky']"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="幸运产出数量">
              <el-input-number v-model="editForm.lucky_result_quantity" :min="0" class="full-width" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-divider content-position="left">其他</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配方描述">
              <el-input v-model="editForm.description" type="textarea" :rows="2" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否禁用">
              <el-switch v-model="editForm.is_ban" :active-value="1" :inactive-value="0" />
              <span class="ban-hint">{{ editForm.is_ban === 1 ? '禁用后普通用户无法查看此配方' : '' }}</span>
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
    
    <!-- 物品配方树弹窗 -->
    <el-dialog 
      v-model="itemTreeVisible" 
      :title="itemTreeTitle + ' - 配方关系'"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-loading="itemTreeLoading">
        <!-- 制作配方（该物品作为产物的配方） -->
        <div class="item-tree-section">
          <h4><el-icon><Tickets /></el-icon> 制作配方</h4>
          <div v-if="itemTreeData.recipesAsResult.length > 0" class="recipe-cards">
            <div 
              v-for="recipe in itemTreeData.recipesAsResult" 
              :key="recipe.id" 
              class="recipe-card"
              @click="navigateItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
            >
              <div class="recipe-card-header">
                <el-icon><Box /></el-icon>
                <span>{{ recipe.name }}</span>
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
                >{{ recipe.material1_name || '物品' + recipe.material1_id }}×{{ recipe.material1_quantity }}</span>
                <span v-if="recipe.material2_id">, 
                  <span class="material-link" @click.stop="navigateItemTree(recipe.material2_id, recipe.material2_name)">{{ recipe.material2_name || '物品' + recipe.material2_id }}</span>×{{ recipe.material2_quantity }}
                </span>
                <span v-if="recipe.material3_id">, 
                  <span class="material-link" @click.stop="navigateItemTree(recipe.material3_id, recipe.material3_name)">{{ recipe.material3_name || '物品' + recipe.material3_id }}</span>×{{ recipe.material3_quantity }}
                </span>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无制作配方" :image-size="60" />
        </div>
        
        <!-- 可制作配方（该物品作为材料的配方） -->
        <div class="item-tree-section">
          <h4><el-icon><Grid /></el-icon> 可制作配方</h4>
          <div v-if="itemTreeData.recipesByMaterial.length > 0" class="recipe-cards">
            <div 
              v-for="recipe in itemTreeData.recipesByMaterial" 
              :key="recipe.id" 
              class="recipe-card result-card"
              @click="navigateItemTree(recipe.result_item_id, recipe.result_item_name || recipe.name)"
            >
              <div class="recipe-card-header">
                <el-icon><Box /></el-icon>
                <span>{{ recipe.name }}</span>
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
                  @click.stop="navigateItemTree(recipe.material1_id, recipe.material1_name)"
                >{{ recipe.material1_name || '物品' + recipe.material1_id }}×{{ recipe.material1_quantity }}</span>
                <span v-if="recipe.material2_id">, 
                  <span class="material-link" @click.stop="navigateItemTree(recipe.material2_id, recipe.material2_name)">{{ recipe.material2_name || '物品' + recipe.material2_id }}</span>×{{ recipe.material2_quantity }}
                </span>
                <span v-if="recipe.material3_id">, 
                  <span class="material-link" @click.stop="navigateItemTree(recipe.material3_id, recipe.material3_name)">{{ recipe.material3_name || '物品' + recipe.material3_id }}</span>×{{ recipe.material3_quantity }}
                </span>
              </div>
            </div>
          </div>
          <el-empty v-else description="无可制作配方" :image-size="60" />
        </div>
      </div>
      
      <template #footer>
        <el-button @click="itemTreeVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { getRecipes, getRecipeById, updateRecipe, deleteRecipe, getItemRecipeTree, createRecipe } from '@/api/recipe'
import { getAllTags, searchItems } from '@/api/item'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

// 副职类型标签列表（从tag获取）
const professionTags = ref([])

// 物品搜索相关
const allItemsCache = ref([])  // 全局缓存：所有物品列表
const itemSearchResults = ref({
  1: [], 2: [], 3: [], 'result': [], 'lucky': []
})
const itemSearchLoading = ref({
  1: false, 2: false, 3: false, 'result': false, 'lucky': false
})

// 加载所有物品（带缓存）
const loadAllItems = async (forceRefresh = false) => {
  if (!forceRefresh && allItemsCache.value.length > 0) {
    return allItemsCache.value
  }
  try {
    const res = await searchItems('')
    allItemsCache.value = res || []
    return allItemsCache.value
  } catch (error) {
    console.error('加载物品列表失败:', error)
    return []
  }
}

// 搜索物品
const doSearchItems = async (query, key) => {
  // 如果没有输入关键词且已有数据，保留现有数据（用于显示已选物品）
  if (!query && itemSearchResults.value[key].length > 0) {
    return
  }
  
  if (!query) {
    // 搜索空字符串时：从缓存获取所有物品，或请求后端
    itemSearchLoading.value[key] = true
    try {
      const items = await loadAllItems()
      itemSearchResults.value[key] = items
    } catch (error) {
      console.error('搜索物品失败:', error)
    } finally {
      itemSearchLoading.value[key] = false
    }
    return
  }
  
  // 有关键词时：在全量物品中做前端搜索（避免频繁请求后端，响应更快）
  itemSearchLoading.value[key] = true
  try {
    const allItems = await loadAllItems()
    const lowerQuery = query.toLowerCase()
    const filtered = allItems.filter(item => 
      item.name.toLowerCase().includes(lowerQuery) || 
      String(item.id) === query
    )
    itemSearchResults.value[key] = filtered
  } catch (error) {
    // 降级：回退到后端搜索
    try {
      const res = await searchItems(query)
      itemSearchResults.value[key] = res || []
    } catch (e) {
      console.error('搜索物品失败:', e)
    }
  } finally {
    itemSearchLoading.value[key] = false
  }
}

// 获取表格行样式（禁用配方显示红色背景）
const getRowClassName = ({ row }) => {
  return row.is_ban === 1 ? 'ban-row' : ''
}

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

// 物品配方树弹窗相关
const itemTreeVisible = ref(false)
const itemTreeLoading = ref(false)
const itemTreeTitle = ref('')
const itemTreeData = ref({ recipesByMaterial: [], recipesAsResult: [] })
const currentItemId = ref(null)

// 编辑弹窗相关
const editVisible = ref(false)
const editLoading = ref(false)
const formRef = ref(null)
const isCreating = ref(false)
const userStore = useUserStore()

// 搜索防抖
let searchTimer = null
const handleSearchInput = () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    loadRecipes()
  }, 300)
}

const editForm = ref({
  id: null,
  name: '',
  profession_type: null,
  level_required: 1,
  vitality_cost: 0,
  material1_id: null,
  material1_quantity: 0,
  material2_id: null,
  material2_quantity: 0,
  material3_id: null,
  material3_quantity: 0,
  lucky_probability: 0,
  result_item_id: null,
  result_quantity: 1,
  lucky_result_item_id: null,
  lucky_result_quantity: 0,
  profession_level_bonus: 0,
  description: '',
  is_ban: 0
})

const rules = {
  name: [{ required: true, message: '请输入配方名称', trigger: 'blur' }]
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

// 获取配方所需材料列表（供树形结构使用）
const getRecipeMaterials = (recipe) => {
  const materials = []
  
  if (recipe.material1_id && recipe.material1_quantity > 0) {
    materials.push({
      name: recipe.material1_name || `物品${recipe.material1_id}`,
      quantity: recipe.material1_quantity,
      id: recipe.material1_id
    })
  }
  
  if (recipe.material2_id && recipe.material2_quantity > 0) {
    materials.push({
      name: recipe.material2_name || `物品${recipe.material2_id}`,
      quantity: recipe.material2_quantity,
      id: recipe.material2_id
    })
  }
  
  if (recipe.material3_id && recipe.material3_quantity > 0) {
    materials.push({
      name: recipe.material3_name || `物品${recipe.material3_id}`,
      quantity: recipe.material3_quantity,
      id: recipe.material3_id
    })
  }
  
  return materials
}

// 获取配方材料树形结构（根节点为产物，子节点为材料）
const getRecipeTree = (recipe) => {
  const children = []
  
  if (recipe.material1_id && recipe.material1_quantity > 0) {
    children.push({
      label: `${recipe.material1_name || `物品${recipe.material1_id}`} × ${recipe.material1_quantity}`
    })
  }
  
  if (recipe.material2_id && recipe.material2_quantity > 0) {
    children.push({
      label: `${recipe.material2_name || `物品${recipe.material2_id}`} × ${recipe.material2_quantity}`
    })
  }
  
  if (recipe.material3_id && recipe.material3_quantity > 0) {
    children.push({
      label: `${recipe.material3_name || `物品${recipe.material3_id}`} × ${recipe.material3_quantity}`
    })
  }
  
  return [{
    label: recipe.result_item_name || recipe.name || '配方产物',
    children: children.length > 0 ? children : [{ label: '无材料' }]
  }]
}

// 显示物品配方树弹窗
const showItemTree = async (itemId, itemName) => {
  itemTreeTitle.value = itemName
  currentItemId.value = itemId
  itemTreeVisible.value = true
  itemTreeLoading.value = true
  itemTreeData.value = { recipesByMaterial: [], recipesAsResult: [] }
  
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

// 导航到另一个物品的配方树（更新当前弹窗）
const navigateItemTree = async (itemId, itemName) => {
  await showItemTree(itemId, itemName || `物品${itemId}`)
}



// 显示新增弹窗（仅管理员）
const showCreate = async () => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }
  
  isCreating.value = true
  editForm.value = {
    id: null,
    name: '',
    profession_type: null,
    level_required: 1,
    vitality_cost: 0,
    material1_id: null,
    material1_quantity: 0,
    material2_id: null,
    material2_quantity: 0,
    material3_id: null,
    material3_quantity: 0,
    lucky_probability: 0,
    result_item_id: null,
    result_quantity: 1,
    lucky_result_item_id: null,
    lucky_result_quantity: 0,
    profession_level_bonus: 0,
    description: '',
    is_ban: 0
  }
  
  // 加载所有物品到下拉框
  await loadItemsForSelect()
  
  editVisible.value = true
}

// 显示编辑弹窗（仅管理员）
const showEdit = async (row) => {
  if (!userStore.isAdmin) {
    ElMessage.warning('权限不足')
    return
  }
  
  isCreating.value = false
  editForm.value = {
    id: row.id,
    name: row.name,
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
    result_item_id: row.result_item_id || null,
    result_quantity: row.result_quantity || 1,
    lucky_result_item_id: row.lucky_result_item_id && row.lucky_result_item_id > 0 ? row.lucky_result_item_id : null,
    lucky_result_quantity: row.lucky_result_quantity || 0,
    profession_level_bonus: Math.round((row.profession_level_bonus || 0) / 100),
    description: row.description || '',
    is_ban: row.is_ban || 0
  }
  
  // 预加载所有物品到各个下拉框
  await loadItemsForSelect()
  
  editVisible.value = true
}

// 加载所有物品到下拉框（使用缓存，避免重复请求）
const loadItemsForSelect = async () => {
  try {
    const allItems = await loadAllItems()
    
    // 为每个下拉框设置物品列表（共享同一份缓存数据）
    itemSearchResults.value = {
      1: allItems,
      2: allItems,
      3: allItems,
      'result': allItems,
      'lucky': allItems
    }
  } catch (error) {
    console.error('加载物品列表失败:', error)
  }
}

// 提交编辑/创建
const handleSubmitEdit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      editLoading.value = true
      try {
        // 处理null值，转为0；转换概率字段
        const submitData = { ...editForm.value }
        Object.keys(submitData).forEach(key => {
          if (submitData[key] === null || submitData[key] === undefined) {
            submitData[key] = 0
          }
        })
        // 转换幸运概率和副职增益：前端值 × 100 = 数据库存储值
        submitData.lucky_probability = Math.round((submitData.lucky_probability || 0) * 100)
        submitData.profession_level_bonus = Math.round((submitData.profession_level_bonus || 0) * 100)
        
        if (isCreating.value) {
          await createRecipe(submitData)
          ElMessage.success('创建成功')
        } else {
          await updateRecipe(submitData.id, submitData)
          ElMessage.success('更新成功')
        }
        editVisible.value = false
        loadRecipes()
      } catch (error) {
        console.error('操作失败:', error)
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

.admin-actions {
  display: flex;
  justify-content: flex-end;
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

.recipe-link .el-tag {
  margin-left: 8px;
  vertical-align: middle;
}

.ban-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

/* 禁用配方行样式 */
:deep(.ban-row) {
  background-color: #fef0f0 !important;
}

:deep(.ban-row:hover > td) {
  background-color: #fee6e6 !important;
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

/* 树形结构样式 */
.recipe-tree {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px 20px;
  position: relative;
}

.tree-root {
  position: relative;
  z-index: 2;
}

.tree-node {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.result-node {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  min-width: 180px;
  justify-content: center;
}

.result-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.result-node .el-icon {
  font-size: 18px;
}

.result-node .quantity {
  background: rgba(255,255,255,0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.tree-connector {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 10px;
}

.connector-line {
  width: 40px;
  height: 2px;
  background: #dcdfe6;
}

.connector-arrow {
  color: #909399;
  font-size: 16px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.tree-children {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.material-node {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #606266;
  border: 1px solid #dcdfe6;
  min-width: 160px;
  justify-content: center;
}

.material-node:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
  border-color: #409eff;
}

.material-node .el-icon {
  color: #409eff;
}

.material-node .quantity {
  background: #409eff;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

/* 物品配方树弹窗样式 */
.item-tree-section {
  margin-bottom: 20px;
}

.item-tree-section h4 {
  margin-bottom: 15px;
  color: #303133;
  font-size: 14px;
  font-weight: 600;
}

.recipe-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.recipe-card {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.recipe-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #409eff;
}

.recipe-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: 600;
  color: #303133;
}

.recipe-card-header .el-icon {
  color: #667eea;
}

.recipe-card-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.recipe-card-info .level {
  color: #909399;
  font-size: 12px;
}

.recipe-card-materials {
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
}

.material-link {
  color: #409eff;
  cursor: pointer;
  transition: color 0.2s;
}

.material-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.result-card {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-color: #c2e7b0;
}

.result-card .recipe-card-header .el-icon {
  color: #67c23a;
}

.recipe-card-info .quantity {
  background: #67c23a;
  color: white;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 11px;
}

.item-tree-section h4 {
  display: flex;
  align-items: center;
  gap: 6px;
}

.item-tree-section h4 .el-icon {
  color: #909399;
}

/* 编辑表单样式 */
.full-width {
  width: 100%;
}

.item-id {
  color: #909399;
  font-size: 12px;
  margin-left: 8px;
}

:deep(.el-select-dropdown__item) {
  display: flex;
  justify-content: space-between;
}
</style>
<template>
  <div class="admin-page">
    <Header />
    
    <el-main>
      <div class="container">
        <h1>管理后台</h1>
        
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <!-- 标签管理 -->
          <el-tab-pane label="标签管理" name="tags">
            <div class="tag-header">
              <el-button type="primary" @click="showTagForm()">
                <el-icon><Plus /></el-icon>
                添加标签
              </el-button>
              <el-select 
                v-model="tagCategoryFilter" 
                placeholder="按分类筛选" 
                clearable
                filterable
                allow-create
                class="category-select"
                @change="loadTags"
              >
                <el-option 
                  v-for="cat in tagCategories" 
                  :key="cat" 
                  :label="cat" 
                  :value="cat" 
                />
              </el-select>
            </div>
            
            <el-table :data="tags" v-loading="tagLoading" stripe>
              <el-table-column prop="name" label="标签名称" />
              <el-table-column prop="category" label="分类" width="200">
                <template #default="{ row }">
                  <el-tag :type="getCategoryType(row.category)">
                    {{ getCategoryLabel(row.category) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="value" label="映射值" width="100" />
              <el-table-column prop="description" label="描述" width="300"/>
              <el-table-column prop="sort_order" label="排序号" width="100" />
              <el-table-column label="操作" width="180" fixed="right" min-width="80">
                <template #default="{ row }">
                  <el-button size="small" type="primary" @click="showTagForm(row)">
                    编辑
                  </el-button>
                  <el-button size="small" type="danger" @click="handleDeleteTag(row)">
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination">
              <el-pagination
                v-model:current-page="tagCurrentPage"
                v-model:page-size="tagPageSize"
                :total="tagTotal"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="loadTags"
                @size-change="handleTagSizeChange"
              />
            </div>
          </el-tab-pane>
          
          <!-- 用户管理 -->
          <el-tab-pane label="用户管理" name="users">
            <el-table :data="users" v-loading="userLoading" stripe>
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="email" label="邮箱" />
              <el-table-column prop="role" label="角色" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'">
                    {{ row.role === 'admin' ? '管理员' : '普通用户' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.is_active ? 'success' : 'danger'">
                    {{ row.is_active ? '活跃' : '禁用' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150" fixed="right">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    :type="row.is_active ? 'warning' : 'success'"
                    @click="toggleUserStatus(row)"
                  >
                    {{ row.is_active ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="total"
                :page-sizes="[10, 20, 50, 100]"
                layout="total, sizes, prev, pager, next, jumper"
                @current-change="loadUsers"
                @size-change="handleSizeChange"
              />
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-main>
    
    <Footer />
    
    <!-- 标签表单弹窗 -->
    <el-dialog 
      v-model="tagFormVisible" 
      :title="editingTag ? '编辑标签' : '添加标签'"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form :model="tagForm" :rules="tagRules" ref="tagFormRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select v-model="tagForm.category" filterable allow-create>
            <el-option 
              v-for="cat in tagCategories" 
              :key="cat" 
              :label="cat" 
              :value="cat" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="映射值" prop="value">
          <el-input-number v-model="tagForm.value" :min="0" />
          <span class="form-hint">用于数字映射，如副职类型的编号</span>
        </el-form-item>
        
        <el-form-item label="排序号" prop="sort_order">
          <el-input-number v-model="tagForm.sort_order" :min="0" />
          <span class="form-hint">数字越小越靠前</span>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="tagForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="tagFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitTag" :loading="tagSubmitting">
          {{ editingTag ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import { getUsers, updateUserStatus } from '@/api/user'
import { getAllTags, createTag, updateTag, deleteTag } from '@/api/item'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const activeTab = ref('tags')
const users = ref([])
const userLoading = ref(false)

// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 标签管理相关
const tags = ref([])
const tagLoading = ref(false)
const tagCategoryFilter = ref('')
const tagFormVisible = ref(false)
const tagSubmitting = ref(false)
const editingTag = ref(null)
const tagFormRef = ref(null)

// 标签分页相关
const tagCurrentPage = ref(1)
const tagPageSize = ref(10)
const tagTotal = ref(0)

const tagForm = ref({
  id: null,
  name: '',
  category: 'profession_type',
  value: 0,
  sort_order: 0,
  description: ''
})

const tagRules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  value: [{ type: 'number', min: 0, message: '映射值必须大于等于0', trigger: 'change' }]
}

// 从已有标签数据中动态提取分类列表（去重排序）
const tagCategories = computed(() => {
  const categories = [...new Set(tags.value.map(t => t.category).filter(Boolean))]
  return categories.sort()
})

const getCategoryLabel = (category) => {
  return category
}

const getCategoryType = (category) => {
  // 简单哈希映射颜色
  const colorMap = ['', 'success', 'primary', 'warning', 'danger']
  let hash = 0
  for (let i = 0; i < category.length; i++) {
    hash = ((hash << 5) - hash) + category.charCodeAt(i)
    hash |= 0
  }
  return colorMap[Math.abs(hash) % colorMap.length] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadUsers = async () => {
  userLoading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    
    const res = await getUsers(params)
    users.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载用户列表失败:', error)
  } finally {
    userLoading.value = false
  }
}

const loadTags = async () => {
  tagLoading.value = true
  try {
    const params = {
      skip: (tagCurrentPage.value - 1) * tagPageSize.value,
      limit: tagPageSize.value
    }
    if (tagCategoryFilter.value) {
      params.category = tagCategoryFilter.value
    }
    const res = await getAllTags(params)
    tags.value = res.items || []
    tagTotal.value = res.total || 0
  } catch (error) {
    console.error('加载标签列表失败:', error)
  } finally {
    tagLoading.value = false
  }
}

const handleTagSizeChange = (val) => {
  tagPageSize.value = val
  tagCurrentPage.value = 1
  loadTags()
}

const handleTabChange = (tabName) => {
  if (tabName === 'tags') {
    loadTags()
  }else {
    loadUsers()
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadUsers()
}

const toggleUserStatus = async (row) => {
  const action = row.is_active ? '禁用' : '启用'
  
  try {
    await ElMessageBox.confirm(
      `确定要${action}用户 "${row.username}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await updateUserStatus(row.id, { is_active: !row.is_active })
    ElMessage.success(`${action}成功`)
    loadUsers()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(`${action}失败:`, error)
    }
  }
}

const showTagForm = (row = null) => {
  editingTag.value = row
  if (row) {
    tagForm.value = {
      id: row.id,
      name: row.name,
      category: row.category,
      value: row.value || 0,
      sort_order: row.sort_order || 0,
      description: row.description || ''
    }
  } else {
    tagForm.value = {
      id: null,
      name: '',
      category: 'profession_type',
      value: 0,
      sort_order: 0,
      description: ''
    }
  }
  tagFormVisible.value = true
}

const handleSubmitTag = async () => {
  if (!tagFormRef.value) return
  
  await tagFormRef.value.validate(async (valid) => {
    if (valid) {
      tagSubmitting.value = true
      try {
        if (editingTag.value) {
          await updateTag(tagForm.value.id, tagForm.value)
          ElMessage.success('更新成功')
        } else {
          await createTag(tagForm.value)
          ElMessage.success('创建成功')
        }
        tagFormVisible.value = false
        loadTags()
      } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(error.response?.data?.detail || '操作失败')
      } finally {
        tagSubmitting.value = false
      }
    }
  })
}

const handleDeleteTag = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${row.name}" 吗？`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteTag(row.id)
    ElMessage.success('删除成功')
    loadTags()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  if (activeTab.value === 'tags') {
    loadTags()
  } else {
    loadUsers()
  }
})
</script>

<style scoped>
.admin-page {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.tag-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-select {
  width: 200px;
}

.form-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>
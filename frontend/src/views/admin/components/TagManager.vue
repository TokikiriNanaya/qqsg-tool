<template>
  <div>
    <div class="tag-header">
      <el-button type="primary" @click="showTagForm()">
        <el-icon><Plus /></el-icon>
        添加标签
      </el-button>
      <el-select
        v-model="categoryFilter"
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

    <el-table :data="tags" v-loading="loading" stripe>
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="name" label="标签名称" />
      <el-table-column prop="category" label="分类" width="200">
        <template #default="{ row }">
          <el-tag :type="getCategoryType(row.category)">
            {{ row.category }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="value" label="映射值" width="100" />
      <el-table-column prop="description" label="描述" width="300" />
      <el-table-column prop="sort_order" label="排序号" width="100" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="showTagForm(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
        @current-change="loadTags"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 标签表单弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="editingTag ? '编辑标签' : '添加标签'"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form :model="tagForm" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="标签名称" prop="name">
          <el-input v-model="tagForm.name" />
        </el-form-item>
        <el-form-item label="分类" prop="category">
          <el-select v-model="tagForm.category" filterable allow-create>
            <el-option v-for="cat in tagCategories" :key="cat" :label="cat" :value="cat" />
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
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingTag ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAllTags, createTag, updateTag, deleteTag } from '@/api/item'
import { ElMessage, ElMessageBox } from 'element-plus'

const tags = ref([])
const loading = ref(false)
const categoryFilter = ref('')
const formVisible = ref(false)
const submitting = ref(false)
const editingTag = ref(null)
const formRef = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const tagForm = ref({
  id: null, name: '', category: 'profession_type', value: 0, sort_order: 0, description: ''
})

const rules = {
  name: [{ required: true, message: '请输入标签名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  value: [{ type: 'number', min: 0, message: '映射值必须大于等于0', trigger: 'change' }]
}

const tagCategories = computed(() => {
  const categories = [...new Set(tags.value.map(t => t.category).filter(Boolean))]
  return categories.sort()
})

const getCategoryType = (category) => {
  const colorMap = ['', 'success', 'primary', 'warning', 'danger']
  let hash = 0
  for (let i = 0; i < category.length; i++) {
    hash = ((hash << 5) - hash) + category.charCodeAt(i)
    hash |= 0
  }
  return colorMap[Math.abs(hash) % colorMap.length] || 'info'
}

const loadTags = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (categoryFilter.value) params.category = categoryFilter.value
    const res = await getAllTags(params)
    tags.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载标签列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadTags()
}

const showTagForm = (row = null) => {
  editingTag.value = row
  if (row) {
    tagForm.value = {
      id: row.id, name: row.name, category: row.category,
      value: row.value || 0, sort_order: row.sort_order || 0, description: row.description || ''
    }
  } else {
    tagForm.value = {
      id: null, name: '', category: 'profession_type', value: 0, sort_order: 0, description: ''
    }
  }
  formVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitting.value = true
    try {
      if (editingTag.value) {
        await updateTag(tagForm.value.id, tagForm.value)
        ElMessage.success('更新成功')
      } else {
        await createTag(tagForm.value)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
      loadTags()
    } catch (error) {
      console.error('操作失败:', error)
      ElMessage.error(error.response?.data?.detail || '操作失败')
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除标签 "${row.name}" 吗？`, '警告', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await deleteTag(row.id)
    ElMessage.success('删除成功')
    loadTags()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

onMounted(() => loadTags())
</script>

<style scoped>
.tag-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.category-select { width: 200px; }

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.form-hint {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}
</style>

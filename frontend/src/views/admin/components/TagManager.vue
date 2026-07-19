<template>
  <div>
    <div class="dict-header">
      <el-button type="primary" @click="showDictForm()">
        <el-icon><Plus /></el-icon>
        添加字典项
      </el-button>
      <el-select
        v-model="typeFilter"
        placeholder="按类型筛选"
        clearable
        filterable
        class="type-select"
        @change="loadDicts"
      >
        <el-option
          v-for="t in dictTypes"
          :key="t"
          :label="t"
          :value="t"
        />
      </el-select>
    </div>

    <el-table :data="dicts" v-loading="loading" stripe>
      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="dict_type" label="字典类型" width="150">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.dict_type)">
            {{ row.dict_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="label" label="显示名称" />
      <el-table-column prop="code" label="编码" width="100" />
      <el-table-column prop="sort_order" label="排序号" width="100" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 1 ? 'success' : 'danger'" size="small">
            {{ row.status === 1 ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" width="200" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="showDictForm(row)">编辑</el-button>
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
        @current-change="loadDicts"
        @size-change="handleSizeChange"
      />
    </div>

    <!-- 字典表单弹窗 -->
    <el-dialog
      v-model="formVisible"
      :title="editingItem ? '编辑字典项' : '添加字典项'"
      width="500px"
      :close-on-click-modal="true"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="字典类型" prop="dict_type">
          <el-select v-model="form.dict_type" filterable allow-create>
            <el-option v-for="t in dictTypes" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="编码" prop="code" :rules="codeRules">
          <template v-if="editingItem">
            <el-input-number v-model="form.code" :min="0" class="full-width" disabled />
            <span class="form-hint">编码为唯一标识，创建后不可修改</span>
          </template>
          <el-input-number v-else v-model="form.code" :min="0" class="full-width" />
        </el-form-item>
        <el-form-item label="显示名称" prop="label">
          <el-input v-model="form.label" />
        </el-form-item>
        <el-form-item label="排序号">
          <el-input-number v-model="form.sort_order" :min="0" class="full-width" />
          <span class="form-hint">数字越小越靠前</span>
        </el-form-item>
        <el-form-item label="状态">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingItem ? '更新' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getAllDicts, createDict, updateDict, deleteDict } from '@/api/item'
import { ElMessage, ElMessageBox } from 'element-plus'

const dicts = ref([])
const loading = ref(false)
const typeFilter = ref('')
const formVisible = ref(false)
const submitting = ref(false)
const editingItem = ref(null)
const formRef = ref(null)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const form = ref({
  id: null, dict_type: 'job_type', code: 0, label: '', sort_order: 0, remark: '', status: 1
})

const rules = {
  dict_type: [{ required: true, message: '请输入字典类型', trigger: 'blur' }],
  label: [{ required: true, message: '请输入显示名称', trigger: 'blur' }]
}

const codeRules = computed(() => {
  if (editingItem.value) return []
  return [{ type: 'number', required: true, message: '请输入编码', trigger: 'change' }]
})

const dictTypes = computed(() => {
  const types = [...new Set(dicts.value.map(d => d.dict_type).filter(Boolean))]
  return types.sort()
})

const TAG_COLORS = ['primary', 'success', 'warning', 'danger', 'info']

const typeColorMap = computed(() => {
  const map = {}
  dictTypes.value.forEach((type, index) => {
    map[type] = TAG_COLORS[index % TAG_COLORS.length]
  })
  return map
})

const getTypeTagType = (type) => {
  return typeColorMap.value[type] || 'info'
}

const loadDicts = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (typeFilter.value) params.dict_type = typeFilter.value
    const res = await getAllDicts(params)
    dicts.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载字典列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSizeChange = (val) => {
  pageSize.value = val
  currentPage.value = 1
  loadDicts()
}

const showDictForm = (row = null) => {
  editingItem.value = row
  if (row) {
    form.value = {
      id: row.id, dict_type: row.dict_type, code: row.code,
      label: row.label, sort_order: row.sort_order || 0,
      remark: row.remark || '', status: row.status ?? 1
    }
  } else {
    form.value = {
      id: null, dict_type: 'job_type', code: 0, label: '', sort_order: 0, remark: '', status: 1
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
      if (editingItem.value) {
        const { code, ...updateData } = form.value
        await updateDict(form.value.id, updateData)
        ElMessage.success('更新成功')
      } else {
        await createDict(form.value)
        ElMessage.success('创建成功')
      }
      formVisible.value = false
      currentPage.value = 1
      await loadDicts()
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
    await ElMessageBox.confirm(`确定要删除字典项 "${row.label}" 吗？`, '警告', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await deleteDict(row.id)
    ElMessage.success('删除成功')
    currentPage.value = 1
    await loadDicts()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

onMounted(() => loadDicts())
</script>

<style scoped>
.dict-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.type-select { width: 200px; }

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

.full-width { width: 100%; }
</style>

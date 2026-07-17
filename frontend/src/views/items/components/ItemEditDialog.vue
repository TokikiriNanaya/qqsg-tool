<template>
  <el-dialog
    v-if="userStore.isAdmin"
    v-model="visible"
    :title="isCreating ? '新增物品' : '编辑物品'"
    width="700px"
    :close-on-click-modal="true"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="物品名称" prop="name">
            <el-input v-model="form.name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="物品分类">
            <el-input v-model="form.category" placeholder="如：庖丁、工匠" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="默认价格(三国币)">
            <el-input-number v-model="form.default_price" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="军团点">
            <el-input-number v-model="form.juntuan_point" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="背包上限">
            <el-input-number v-model="form.bag_limit" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="仓库上限">
            <el-input-number v-model="form.warehouse_limit" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="24">
          <el-form-item label="物品描述">
            <el-input v-model="form.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-col>
      </el-row>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, ref, reactive, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { createItem, updateItem } from '@/api/item'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  isCreating: { type: Boolean, default: false },
  initForm: { type: Object, default: () => ({}) }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null,
  name: '',
  category: '',
  description: '',
  default_price: null,
  juntuan_point: null,
  bag_limit: null,
  warehouse_limit: null
})

// 弹窗打开时同步外部数据到内部 reactive form
watch(visible, (val) => {
  if (val) {
    Object.assign(form, {
      id: props.initForm.id || null,
      name: props.initForm.name || '',
      category: props.initForm.category || '',
      description: props.initForm.description || '',
      default_price: props.initForm.default_price ?? null,
      juntuan_point: props.initForm.juntuan_point ?? null,
      bag_limit: props.initForm.bag_limit ?? null,
      warehouse_limit: props.initForm.warehouse_limit ?? null
    })
  }
})

const rules = {
  name: [{ required: true, message: '请输入物品名称', trigger: 'blur' }]
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const data = { ...form }
      if (props.isCreating) {
        const { id, ...createData } = data
        await createItem(createData)
        ElMessage.success('创建成功')
      } else {
        const { id, ...updateData } = data
        await updateItem(Number(id), updateData)
        ElMessage.success('更新成功')
      }
      emit('update:modelValue', false)
      emit('saved')
    } catch (error) {
      console.error('操作失败:', error)
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.full-width {
  width: 100%;
}
</style>

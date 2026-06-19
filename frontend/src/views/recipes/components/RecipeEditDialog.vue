<template>
  <el-dialog
    v-if="userStore.isAdmin"
    v-model="visible"
    :title="isCreating ? '新增配方' : '编辑配方'"
    width="800px"
    :close-on-click-modal="true"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="配方名称" prop="name">
            <el-input v-model="form.name" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="副职类型" prop="profession_type">
            <el-select v-model="form.profession_type" placeholder="选择副职类型" class="full-width">
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
            <el-input-number v-model="form.level_required" :min="1" class="full-width" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="消耗活力">
            <el-input-number v-model="form.vitality_cost" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">材料</el-divider>

      <el-row v-for="idx in [1, 2, 3]" :key="idx" :gutter="20">
        <el-col :span="12">
          <el-form-item :label="'材料' + idx">
            <el-select
              :model-value="form['material' + idx + '_id']"
              @update:model-value="val => form['material' + idx + '_id'] = val"
              filterable remote
              placeholder="搜索物品"
              :remote-method="(query) => doSearch(query, idx)"
              :loading="searchLoading[idx]"
              class="full-width"
              clearable
            >
              <el-option
                v-for="item in searchResults[idx]"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item :label="'材料' + idx + '数量'">
            <el-input-number :model-value="form['material' + idx + '_quantity']" @update:model-value="val => form['material' + idx + '_quantity'] = val" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">产出</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="产出物品">
            <el-select
              :model-value="form.result_item_id"
              @update:model-value="val => form.result_item_id = val"
              filterable remote
              placeholder="搜索物品"
              :remote-method="(query) => doSearch(query, 'result')"
              :loading="searchLoading['result']"
              class="full-width"
              clearable
            >
              <el-option
                v-for="item in searchResults['result']"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="产出数量">
            <el-input-number :model-value="form.result_quantity" @update:model-value="val => form.result_quantity = val" :min="1" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">幸运合成</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="幸运概率(%)">
            <el-input-number :model-value="form.lucky_probability" @update:model-value="val => form.lucky_probability = val" :min="0" :max="100" class="full-width" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="副职等级增益(%)">
            <el-input-number :model-value="form.profession_level_bonus" @update:model-value="val => form.profession_level_bonus = val" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="幸运产出物品">
            <el-select
              :model-value="form.lucky_result_item_id"
              @update:model-value="val => form.lucky_result_item_id = val"
              filterable remote
              placeholder="搜索物品"
              :remote-method="(query) => doSearch(query, 'lucky')"
              :loading="searchLoading['lucky']"
              class="full-width"
              clearable
            >
              <el-option
                v-for="item in searchResults['lucky']"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="幸运产出数量">
            <el-input-number :model-value="form.lucky_result_quantity" @update:model-value="val => form.lucky_result_quantity = val" :min="0" class="full-width" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-divider content-position="left">其他</el-divider>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="配方描述">
            <el-input :model-value="form.description" @update:model-value="val => form.description = val" type="textarea" :rows="2" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="是否禁用">
            <el-switch :model-value="form.is_ban" @update:model-value="val => form.is_ban = val" :active-value="1" :inactive-value="0" />
            <span class="ban-hint">{{ form.is_ban === 1 ? '禁用后普通用户无法查看此配方' : '' }}</span>
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
import { createRecipe, updateRecipe } from '@/api/recipe'
import { searchItems } from '@/api/item'
import { ElMessage } from 'element-plus'

const userStore = useUserStore()

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  isCreating: { type: Boolean, default: false },
  initForm: { type: Object, default: () => ({}) },
  professionTags: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const formRef = ref(null)

const form = reactive({
  id: null, name: '', profession_type: null, level_required: 1, vitality_cost: 0,
  material1_id: null, material1_quantity: 0,
  material2_id: null, material2_quantity: 0,
  material3_id: null, material3_quantity: 0,
  lucky_probability: 0, profession_level_bonus: 0,
  result_item_id: null, result_quantity: 1,
  lucky_result_item_id: null, lucky_result_quantity: 0,
  description: '', is_ban: 0
})

const rules = {
  name: [{ required: true, message: '请输入配方名称', trigger: 'blur' }]
}

// 物品搜索
const allItemsCache = ref([])
const searchResults = reactive({ 1: [], 2: [], 3: [], result: [], lucky: [] })
const searchLoading = reactive({ 1: false, 2: false, 3: false, result: false, lucky: false })

const loadAllItems = async (force = false) => {
  if (!force && allItemsCache.value.length > 0) return allItemsCache.value
  try {
    const res = await searchItems('')
    allItemsCache.value = res || []
    return allItemsCache.value
  } catch (e) { console.error('加载物品列表失败:', e); return [] }
}

const doSearch = async (query, key) => {
  if (!query && searchResults[key].length > 0) return
  searchLoading[key] = true
  try {
    if (!query) {
      const items = await loadAllItems()
      searchResults[key] = items
    } else {
      const res = await searchItems(query)
      searchResults[key] = res || []
    }
  } catch (e) { console.error('搜索物品失败:', e); searchResults[key] = [] }
  finally { searchLoading[key] = false }
}

// 预加载所有物品到各下拉框
const preloadItems = async () => {
  try {
    const allItems = await loadAllItems()
    Object.keys(searchResults).forEach(k => { searchResults[k] = allItems })
  } catch (e) { console.error('加载物品列表失败:', e) }
}

// 同步外部 form 数据到内部 reactive
const syncForm = (data) => {
  Object.assign(form, {
    id: data.id ?? null,
    name: data.name ?? '',
    profession_type: data.profession_type ?? null,
    level_required: data.level_required ?? 1,
    vitality_cost: data.vitality_cost ?? 0,
    material1_id: data.material1_id ?? null,
    material1_quantity: data.material1_quantity ?? 0,
    material2_id: data.material2_id ?? null,
    material2_quantity: data.material2_quantity ?? 0,
    material3_id: data.material3_id ?? null,
    material3_quantity: data.material3_quantity ?? 0,
    lucky_probability: data.lucky_probability ?? 0,
    profession_level_bonus: data.profession_level_bonus ?? 0,
    result_item_id: data.result_item_id ?? null,
    result_quantity: data.result_quantity ?? 1,
    lucky_result_item_id: data.lucky_result_item_id ?? null,
    lucky_result_quantity: data.lucky_result_quantity ?? 0,
    description: data.description ?? '',
    is_ban: data.is_ban ?? 0
  })
  preloadItems()
}

// 监听 visible 打开，同步数据
watch(visible, (val) => {
  if (val) syncForm(props.initForm)
})

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      const submitData = { ...form }
      Object.keys(submitData).forEach(key => {
        if (submitData[key] === null || submitData[key] === undefined) submitData[key] = 0
      })
      submitData.lucky_probability = Math.round((submitData.lucky_probability || 0) * 100)
      submitData.profession_level_bonus = Math.round((submitData.profession_level_bonus || 0) * 100)

      if (props.isCreating) {
        await createRecipe(submitData)
        ElMessage.success('创建成功')
      } else {
        await updateRecipe(submitData.id, submitData)
        ElMessage.success('更新成功')
      }
      emit('update:modelValue', false)
      emit('saved')
    } catch (error) { console.error('操作失败:', error) }
    finally { loading.value = false }
  })
}
</script>

<style scoped>
.full-width { width: 100%; }
.ban-hint { margin-left: 10px; color: #909399; font-size: 12px; }
</style>

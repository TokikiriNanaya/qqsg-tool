<template>
  <div class="page-container">
    <Header />

    <el-main>
      <div class="content-wrapper">
        <h1>物品列表</h1>

        <!-- 搜索和筛选 -->
        <el-card class="search-card">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-input
                v-model="searchQuery"
                placeholder="搜索物品名称（支持拼音首字母，如 gh=钙化大骨）"
                clearable
                @input="handleSearchInput"
                @clear="loadItems"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </el-col>
            <el-col :span="6">
              <el-button type="primary" @click="loadItems">搜索</el-button>
            </el-col>
            <el-col v-if="userStore.isAdmin" :span="6" class="admin-actions">
              <el-button type="success" @click="showCreate">
                <el-icon><Plus /></el-icon>
                新增物品
              </el-button>
            </el-col>
          </el-row>
        </el-card>

        <!-- 物品列表 -->
        <el-card class="list-card">
          <el-table :data="items" v-loading="loading" stripe>
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="物品名称" min-width="200">
              <template #default="{ row }">
                <span class="item-link" @click="showDetail(row)">{{ row.name }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="category" label="分类" width="100" />
            <el-table-column prop="default_price" label="默认价格" width="100">
              <template #default="{ row }">
                <span v-if="row.default_price !== null && row.default_price !== undefined">{{ row.default_price }}</span>
                <span v-else class="text-gray">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="bag_limit" label="背包上限" width="100" />
            <el-table-column prop="warehouse_limit" label="仓库上限" width="100" />
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="showDetail(row)">查看详情</el-button>
                <template v-if="userStore.isAdmin">
                  <el-button size="small" type="primary" @click="showEdit(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
                </template>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="total"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="loadItems"
              @size-change="loadItems"
            />
          </div>
        </el-card>
      </div>
    </el-main>

    <Footer />

    <!-- 编辑/新增弹窗 -->
    <ItemEditDialog
      v-model="editVisible"
      :is-creating="isCreating"
      :init-form="editForm"
      @saved="loadItems"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import ItemEditDialog from './components/ItemEditDialog.vue'
import { getItems, deleteItem } from '@/api/item'
import { useUserStore } from '@/stores/user'
import { useSearchDebounce } from '@/composables/useSearchDebounce'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

// 列表数据
const items = ref([])
const loading = ref(false)
const searchQuery = ref('')
const pageSize = ref(10)
const total = ref(0)

// 编辑弹窗
const editVisible = ref(false)
const isCreating = ref(false)
const editForm = ref({})

// 搜索防抖
const { currentPage, handleSearchInput } = useSearchDebounce(() => loadItems())

async function loadItems() {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) params.name = searchQuery.value
    const res = await getItems(params)
    items.value = res.items || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载物品列表失败:', error)
  } finally {
    loading.value = false
  }
}

const showDetail = (row) => {
  const url = router.resolve(`/items/${row.id}`).href
  window.open(url, '_blank')
}

const showCreate = () => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  isCreating.value = true
  editForm.value = {
    id: null, name: '', category: '', description: '',
    default_price: null, bag_limit: 999, warehouse_limit: 9999
  }
  editVisible.value = true
}

const showEdit = (row) => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  isCreating.value = false
  editForm.value = {
    id: row.id, name: row.name, category: row.category || '',
    description: row.description || '', default_price: row.default_price ?? null,
    bag_limit: row.bag_limit || 99, warehouse_limit: row.warehouse_limit || 999
  }
  editVisible.value = true
}

const handleDelete = async (row) => {
  if (!userStore.isAdmin) { ElMessage.warning('权限不足'); return }
  try {
    await ElMessageBox.confirm('确定要删除这个物品吗？', '警告', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await deleteItem(row.id)
    ElMessage.success('删除成功')
    loadItems()
  } catch (error) {
    if (error !== 'cancel') console.error('删除失败:', error)
  }
}

onMounted(() => {
  loadItems()
})
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-main { flex: 1; }

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.content-wrapper h1 {
  margin-bottom: 20px;
  color: #303133;
}

.search-card { margin-bottom: 20px; }

.list-card { min-height: 400px; }

.admin-actions { display: flex; justify-content: flex-end; }

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.item-link {
  color: #409eff;
  text-decoration: none;
  cursor: pointer;
}

.item-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>

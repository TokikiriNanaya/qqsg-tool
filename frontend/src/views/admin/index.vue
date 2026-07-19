<template>
  <div class="page-container">
    <Header />

    <el-main>
      <div class="content-wrapper">
        <h1>管理后台</h1>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="字典管理" name="tags">
            <TagManager />
          </el-tab-pane>
          <el-tab-pane label="用户管理" name="users">
            <UserManager />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-main>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
import TagManager from './components/TagManager.vue'
import UserManager from './components/UserManager.vue'

const activeTab = ref('tags')
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
</style>

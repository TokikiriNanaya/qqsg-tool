<template>
  <div class="home">
    <el-container>
      <el-header>
        <Header />
      </el-header>

      <el-main>
        <div class="hero-section">
          <h1>QQ三国工具</h1>
          <p class="subtitle">快速查询游戏内所有可制作物品的配方</p>

          <el-button type="primary" size="large" @click="$router.push('/recipes')">
            开始查询
          </el-button>
        </div>

        <div class="features">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-card>
                <el-icon size="40"><Search /></el-icon>
                <h3>快速搜索</h3>
                <p>支持按名称、分类快速查找配方</p>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card>
                <el-icon size="40"><List /></el-icon>
                <h3>详细材料清单</h3>
                <p>查看每个配方所需的完整材料列表</p>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card>
                <el-icon size="40"><User /></el-icon>
                <h3>用户贡献</h3>
                <p>注册用户可以分享自己的配方发现</p>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-main>

      <el-footer>
        <Footer />
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import Header from '@/components/Header.vue'
import Footer from '@/components/Footer.vue'
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.el-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-header {
  padding: 0;
  flex-shrink: 0;
}

.el-main {
  flex: 1;
}

.hero-section {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  margin-bottom: 40px;
}

.hero-section h1 {
  font-size: 48px;
  margin-bottom: 20px;
}

.subtitle {
  font-size: 20px;
  margin-bottom: 30px;
  opacity: 0.9;
}

.features {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.el-card {
  text-align: center;
  padding: 20px;
  height: 100%;
}

.el-card h3 {
  margin: 20px 0 10px;
}

.el-card p {
  color: #666;
}

.el-icon {
  color: #667eea;
}

.el-footer {
  padding: 0;
}
</style>

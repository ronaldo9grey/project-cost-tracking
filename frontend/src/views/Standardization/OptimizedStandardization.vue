<template>
  <div class="standardization-container" :class="`theme-${currentTheme}`">
    <!-- 主题切换器 -->
    <div class="theme-switcher">
      <el-button-group>
        <el-button 
          :type="currentTheme === 'flat' ? 'primary' : 'default'"
          @click="setTheme('flat')"
        >
          扁平风格
        </el-button>
        <el-button 
          :type="currentTheme === 'dark' ? 'primary' : 'default'"
          @click="setTheme('dark')"
        >
          深色主题
        </el-button>
        <el-button 
          :type="currentTheme === 'colorful' ? 'primary' : 'default'"
          @click="setTheme('colorful')"
        >
          彩色主题
        </el-button>
      </el-button-group>
    </div>

    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">标准化管理</h1>
      <div class="header-actions">
        <el-button @click="resetAnimation" circle>
          <el-icon><RefreshIcon /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 一级卡片容器 -->
      <div class="module-cards">
        <div
          v-for="module in modules"
          :key="module.key"
          class="module-card"
          :data-type="getModuleType(module.key)"
          :class="{ active: activeModule === module.key }"
          @click="switchModule(module.key)"
        >
          <div class="card-header">
            <div class="card-image">
              <img 
                :src="module.image" 
                :alt="module.title"
                @error="handleImageError"
              />
            </div>
            <div class="card-info">
              <h3 class="card-title">{{ module.title }}</h3>
              <p class="card-description">{{ module.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 内容展示区 -->
      <div class="content-area">
        <!-- 项目标准流程 -->
        <div v-show="activeModule === 'project-process'" class="content-section">
          <h2 class="section-title-main">项目标准流程</h2>
          <div class="process-flow-container">
            <div
              v-for="(stage, stageIndex) in projectProcessData"
              :key="stage.projectStage"
              class="project-stage-card"
              :class="{
                active: activeStageIndex === stageIndex,
                [`stage-${stageIndex + 1}`]: true
              }"
            >
              <div class="stage-header" @click="toggleStage(stageIndex)">
                <div class="stage-header-content">
                  <div class="stage-number">{{ stageIndex + 1 }}</div>
                  <div class="stage-info">
                    <h3 class="stage-title">{{ stage.projectStage }}</h3>
                    <div class="stage-meta">
                      <span class="stage-cycle">{{ stage.totalCycle }}</span>
                      <span class="stage-count">{{ stage.processes.length }}个流程</span>
                    </div>
                  </div>
                </div>
                <div class="stage-toggle">
                  <div class="toggle-icon">{{ activeStageIndex === stageIndex ? '−' : '+' }}</div>
                </div>
              </div>

              <div class="stage-content">
                <div class="stage-prerequisites">
                  <span class="prerequisites-label">前置条件:</span>
                  <span class="prerequisites-value">{{ stage.prerequisites }}</span>
                </div>
              </div>

              <div 
                v-if="activeStageIndex === stageIndex"
                class="expanded-processes"
              >
                <div class="expanded-title">详细流程 ({{ stage.processes.length }}项)</div>
                <div class="process-list">
                  <div
                    v-for="(process, processIndex) in stage.processes"
                    :key="processIndex"
                    class="process-item"
                  >
                    <div class="process-header">
                      <div class="process-number">{{ stageIndex + 1 }}.{{ processIndex + 1 }}</div>
                      <div class="process-details">
                        <div class="process-name">{{ process.name }}</div>
                        <div class="process-meta">
                          <span class="process-role">{{ process.role }}</span>
                          <span class="process-cycle">{{ process.cycle }}</span>
                        </div>
                      </div>
                    </div>
                    <div class="process-deliverables">
                      <span class="deliverables-label">交付成果:</span>
                      <span class="deliverables-text">{{ process.deliverables }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 成本管理预算 -->
        <div v-show="activeModule === 'cost-budget'" class="content-section">
          <h2 class="section-title-main">成本管理预算</h2>
          
          <!-- 核心成本 -->
          <div class="cost-section priority-core">
            <div class="section-banner">
              <div class="priority-indicator core"></div>
              <h3 class="section-title">核心成本</h3>
              <el-tag type="danger" size="large">最重要</el-tag>
            </div>
            <div class="cost-cards-grid core-cards">
              <div
                v-for="item in costData.core"
                :key="item.id"
                class="cost-card-highlight"
              >
                <div class="cost-card-header">
                  <div class="cost-icon">
                    <div class="icon-circle bg-core">💰</div>
                  </div>
                  <div class="cost-info">
                    <h4 class="cost-title">{{ item.name }}</h4>
                    <el-tag size="small" type="danger" class="cost-tag">核心</el-tag>
                  </div>
                </div>
                <div class="cost-card-body">
                  <div class="cost-detail-item">
                    <span class="detail-label">标准费率:</span>
                    <span class="detail-value rate-highlight">{{ item.rate }}</span>
                  </div>
                  <div class="cost-detail-item">
                    <span class="detail-label">计算方式:</span>
                    <span class="detail-value">{{ item.method }}</span>
                  </div>
                  <div class="cost-detail-item">
                    <span class="detail-label">详细说明:</span>
                    <span class="detail-value">{{ item.description }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 主要成本 -->
          <div class="cost-section priority-major">
            <div class="section-banner">
              <div class="priority-indicator major"></div>
              <h3 class="section-title">主要成本</h3>
              <el-tag type="warning" size="large">很重要</el-tag>
            </div>
            <div class="cost-cards-grid major-cards">
              <div
                v-for="item in costData.major"
                :key="item.id"
                class="cost-card-highlight"
              >
                <div class="cost-card-header">
                  <div class="cost-icon">
                    <div class="icon-circle bg-major">📊</div>
                  </div>
                  <div class="cost-info">
                    <h4 class="cost-title">{{ item.name }}</h4>
                    <el-tag size="small" type="warning" class="cost-tag">主要</el-tag>
                  </div>
                </div>
                <div class="cost-card-body">
                  <div class="cost-detail-item">
                    <span class="detail-label">标准费率:</span>
                    <span class="detail-value rate-highlight">{{ item.rate }}</span>
                  </div>
                  <div class="cost-detail-item">
                    <span class="detail-label">计算方式:</span>
                    <span class="detail-value">{{ item.method }}</span>
                  </div>
                  <div class="cost-detail-item">
                    <span class="detail-label">详细说明:</span>
                    <span class="detail-value">{{ item.description }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 配套和支持成本 -->
          <div class="cost-section priority-secondary">
            <div class="section-banner">
              <div class="priority-indicator secondary"></div>
              <h3 class="section-title">配套与支持成本</h3>
              <el-tag type="info" size="large">配套支持</el-tag>
            </div>
            <div class="cost-cards-grid secondary-cards">
              <div
                v-for="item in costData.secondary"
                :key="item.id"
                class="cost-card-highlight"
              >
                <div class="cost-card-header">
                  <div class="cost-icon">
                    <div class="icon-circle bg-secondary">🔧</div>
                  </div>
                  <div class="cost-info">
                    <h4 class="cost-title">{{ item.name }}</h4>
                    <el-tag size="small" type="info" class="cost-tag">配套</el-tag>
                  </div>
                </div>
                <div class="cost-card-body">
                  <div class="cost-detail-item">
                    <span class="detail-label">标准费率:</span>
                    <span class="detail-value rate-highlight">{{ item.rate }}</span>
                  </div>
                  <div class="cost-detail-item">
                    <span class="detail-label">计算方式:</span>
                    <span class="detail-value">{{ item.method }}</span>
                  </div>
                  <div class="cost-detail-item">
                    <span class="detail-label">详细说明:</span>
                    <span class="detail-value">{{ item.description }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 设计费标准 -->
        <div v-show="activeModule === 'design-fee'" class="content-section">
          <h2 class="section-title-main">设计费标准</h2>
          <div class="design-fee-container">
            <div class="design-fee-group group-a">
              <div class="group-header">
                <div class="group-icon">
                  <div class="icon-circle bg-class-a">⚡</div>
                </div>
                <h3 class="group-title">A类 节能改造项目</h3>
                <el-tag type="success" size="medium" class="group-tag">节能环保</el-tag>
              </div>
              <div class="design-fee-grid">
                <div
                  v-for="item in getDesignFeeByCategory('A类 节能改造项目')"
                  :key="item.category + item.complexity"
                  class="design-fee-card"
                >
                  <div class="design-card-header">
                    <div class="design-icon">
                      <div class="icon-circle design-bg">💡</div>
                    </div>
                    <div class="design-info">
                      <h4 class="design-category">{{ item.complexity }}</h4>
                      <span class="design-note">{{ item.note }}</span>
                    </div>
                  </div>
                  <div class="design-card-body">
                    <div class="design-detail-item">
                      <span class="detail-label">基准费率:</span>
                      <span class="detail-value rate-highlight">{{ item.rate }}</span>
                    </div>
                    <div class="design-detail-item">
                      <span class="detail-label">计算单位:</span>
                      <span class="detail-value">{{ item.unit }}</span>
                    </div>
                    <div class="design-detail-item">
                      <span class="detail-label">计算方法:</span>
                      <span class="detail-value">{{ item.calculation }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 绩效考核 -->
        <div v-show="activeModule === 'performance'" class="content-section">
          <h2 class="section-title-main">绩效考核</h2>
          
          <div class="performance-section pm-section">
            <div class="section-banner">
              <div class="priority-indicator pm"></div>
              <h3 class="section-title">项目经理绩效考核</h3>
              <el-tag type="danger" size="large">核心角色</el-tag>
            </div>
            <div class="performance-card-highlight pm-card">
              <div class="performance-card-header">
                <div class="performance-icon">
                  <div class="icon-circle bg-pm">👔</div>
                </div>
                <h4 class="performance-title">项目经理绩效标准</h4>
              </div>
              <div class="performance-metrics">
                <div class="metric-item">
                  <span class="metric-label">项目完成率:</span>
                  <span class="metric-value highlight-metric">≥ 95%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">成本控制:</span>
                  <span class="metric-value highlight-metric">± 5%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">客户满意度:</span>
                  <span class="metric-value highlight-metric">≥ 4.5分</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Refresh as RefreshIcon } from '@element-plus/icons-vue'

// 主题管理
const currentTheme = ref('flat')

const setTheme = (theme: string) => {
  currentTheme.value = theme
}

// 标准化管理模块数据
const modules = reactive([
  {
    key: 'project-process',
    title: '项目标准流程',
    description: '完整的项目管理流程规范',
    icon: 'Document',
    image: '/info/iso.png'
  },
  {
    key: 'cost-budget',
    title: '成本管理预算',
    description: '成本控制与预算管理标准',
    icon: 'Money',
    image: '/info/cb.png'
  },
  {
    key: 'design-fee',
    title: '设计费标准',
    description: '设计费用计算与费率标准',
    icon: 'Setting',
    image: '/info/sjs.png'
  },
  {
    key: 'performance',
    title: '绩效考核',
    description: '项目绩效评估与考核体系',
    icon: 'Star',
    image: '/info/kpi.png'
  }
])

// 当前活跃模块
const activeModule = ref('project-process')

// 当前展开的阶段索引
const activeStageIndex = ref(0)

// 获取模块类型
const getModuleType = (moduleKey: string) => {
  const typeMap: Record<string, string> = {
    'project-process': 'process',
    'cost-budget': 'cost',
    'design-fee': 'design',
    'performance': 'performance'
  }
  return typeMap[moduleKey] || 'default'
}

// 项目流程数据
const projectProcessData = reactive([
  {
    projectStage: '项目前置',
    prerequisites: '1. 业务年度计划\n2. 业务调研需求',
    totalCycle: '23天',
    processes: [
      {
        name: '项目方案及概算',
        role: '项目经理',
        cycle: '7天',
        deliverables: '1.项目初步方案\n2.项目方案评审报告\n3.立项报告\n4.项目定价会议纪要\n5.EPC合同'
      }
    ]
  }
])

// 成本管理数据
const costData = reactive({
  core: [
    {
      id: 1,
      name: '设计费',
      rate: '2.0%-6.0%',
      method: '按项目类型及技术复杂系数计算',
      description: '技术咨询与调研、方案设计、评审、详细设计，软件编程及调试、预算与文件编制、现场技术服务、外聘专家/机构费等'
    },
    {
      id: 2,
      name: '项目管理费',
      rate: '按工时预算',
      method: 'P7岗800元/8h，P6及以下岗600元/8h',
      description: '项目业务办理、差旅费、项目施工及现场管理、售后服务'
    }
  ],
  major: [
    {
      id: 3,
      name: '设备材料采购费',
      rate: '合同金额+质保材料费(3-5%)',
      method: '按采购合同累计核算',
      description: '招标采购及集中采购，按合同金额+质保材料费（3-5%合同总额）'
    },
    {
      id: 4,
      name: '安装调试费',
      rate: '按项目方案编制',
      method: '按签订的安装合同累计核算',
      description: '组装施工、安装调试、试运行、劳务外包'
    }
  ],
  secondary: [
    {
      id: 5,
      name: '现场技术服务费',
      rate: '设计费用构成',
      method: '设计费用内包含',
      description: '设计交底，施工配合、现场设计变更处理（基础次数内）'
    },
    {
      id: 6,
      name: '外聘专家/机构费',
      rate: '按合同协议',
      method: '第三方机构或专家咨询费',
      description: '为特定技术难题聘请的外部专家咨询费'
    }
  ]
})

// 设计费数据
const designFeeData = reactive([
  {
    category: 'A类 节能改造项目',
    complexity: '投资额 I≤30万',
    rate: '4.5%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '涉及工艺优化、能源系统集成'
  }
])

// 模块切换函数
const switchModule = (moduleKey: string) => {
  activeModule.value = moduleKey
}

// 阶段展开/收起切换
const toggleStage = (stageIndex: number) => {
  if (activeStageIndex.value === stageIndex) {
    activeStageIndex.value = -1
  } else {
    activeStageIndex.value = stageIndex
  }
}

// 根据分类获取设计费数据
const getDesignFeeByCategory = (category: string) => {
  return designFeeData.filter(item => item.category === category)
}

// 重置动画
const resetAnimation = () => {
  // 重置动画效果
}

// 图片错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIGZpbGw9IiM2YjczODAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIj7lm77nianohq8uIzwvdGV4dD48L3N2Zz4='
}

// 生命周期
onMounted(() => {
  console.log('标准化管理组件已挂载')
})
</script>

<style scoped>
/* 导入不同的主题样式 */
@import './styles/flat-theme.css';
@import './styles/dark-theme.css';

/* 主题切换器 */
.theme-switcher {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  background: white;
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.theme-switcher .el-button {
  font-size: 12px;
  padding: 6px 12px;
}

/* 优先级指示器 */
.priority-indicator {
  width: 4px;
  height: 24px;
  border-radius: 2px;
  margin-right: 8px;
}

.priority-indicator.core {
  background: linear-gradient(135deg, #dc2626, #ef4444);
}

.priority-indicator.major {
  background: linear-gradient(135deg, #d97706, #f59e0b);
}

.priority-indicator.secondary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
}

.priority-indicator.pm {
  background: linear-gradient(135deg, #dc2626, #ef4444);
}

/* 主题特定的调整 */
.theme-flat {
  --primary-bg: #f8fafc;
  --card-bg: white;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: #e2e8f0;
}

.theme-dark {
  --primary-bg: #0f172a;
  --card-bg: #334155;
  --text-primary: #f1f5f9;
  --text-secondary: #94a3b8;
  --border-color: #334155;
}

.theme-colorful {
  --primary-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --card-bg: rgba(255, 255, 255, 0.95);
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --border-color: rgba(255, 255, 255, 0.3);
}

.theme-colorful .standardization-container {
  background: var(--primary-bg);
}

.theme-colorful .main-content {
  background: var(--card-bg);
  backdrop-filter: blur(10px);
}
</style>
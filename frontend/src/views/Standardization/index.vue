<template>
  <div class="standardization-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">项目标准</h1>
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
        <div v-show="activeModule === 'project-standard'" class="content-section">
          <h2 class="section-title-main">项目标准流程</h2>
          <div class="process-flow-container">
            <!-- 独立的阶段卡片 -->
            <div
              v-for="(stage, stageIndex) in projectProcessData"
              :key="stage.projectStage"
              class="project-stage-card"
              :class="{
                active: activeStageIndex === stageIndex,
                [`stage-${stageIndex + 1}`]: true
              }"
            >
              <!-- 卡片头部（始终显示） -->
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

              <!-- 卡片内容（可展开） -->
              <div class="stage-content">
                <div class="stage-prerequisites">
                  <span class="prerequisites-label">前置条件:</span>
                  <span class="prerequisites-value">{{ stage.prerequisites }}</span>
                </div>
              </div>

              <!-- 展开的流程列表 -->
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
              <div class="dancing-flag">
                <div class="flagpole"></div>
                <div class="flag"></div>
              </div>
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
              <div class="dancing-flag">
                <div class="flagpole"></div>
                <div class="flag"></div>
              </div>
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
              <div class="dancing-flag">
                <div class="flagpole"></div>
                <div class="flag"></div>
              </div>
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
            <!-- A类节能改造项目 -->
            <div class="design-fee-group group-a">
              <div class="group-header">
                <div class="group-icon">
                  <div class="icon-circle bg-class-a">⚡</div>
                </div>
                <h3 class="group-title">A类 节能改造项目</h3>
                <el-tag type="success" size="medium" class="group-tag priority-tag-a">节能环保</el-tag>
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
                      <span class="detail-label">技术复杂系数:</span>
                      <span class="detail-value coefficient-highlight">{{ item.technicalCoefficient }}</span>
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

            <!-- B类装备改善项目 -->
            <div class="design-fee-group group-b">
              <div class="group-header">
                <div class="group-icon">
                  <div class="icon-circle bg-class-b">🔧</div>
                </div>
                <h3 class="group-title">B类 装备改善项目</h3>
                <el-tag type="warning" size="medium" class="group-tag priority-tag-b">装备升级</el-tag>
              </div>
              <div class="design-fee-grid">
                <div
                  v-for="item in getDesignFeeByCategory('B类 装备改善项目')"
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
                      <span class="detail-label">技术复杂系数:</span>
                      <span class="detail-value coefficient-highlight">{{ item.technicalCoefficient }}</span>
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

            <!-- C类安全及综合性技改项目 -->
            <div class="design-fee-group group-c">
              <div class="group-header">
                <div class="group-icon">
                  <div class="icon-circle bg-class-c">🛡️</div>
                </div>
                <h3 class="group-title">C类 安全及综合性技改项目</h3>
                <el-tag type="danger" size="medium" class="group-tag priority-tag-c">安全保障</el-tag>
              </div>
              <div class="design-fee-grid">
                <div
                  v-for="item in getDesignFeeByCategory('C类 安全及综合性技改项目')"
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
                      <span class="detail-label">技术复杂系数:</span>
                      <span class="detail-value coefficient-highlight">{{ item.technicalCoefficient }}</span>
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

          <!-- 技术复杂系数说明 -->
          <div class="technical-complexity-section">
            <div class="section-banner">
              <div class="priority-indicator complex"></div>
              <h3 class="section-title">技术复杂系数说明</h3>
              <el-tag type="info" size="large">重要参考</el-tag>
            </div>
            <div class="complexity-explanation">
              <div class="complexity-factor">
                <h4>K1：技术创新度（0.9-1.3）</h4>
                <p>采用全新工艺、技术或材料的程度</p>
              </div>
              <div class="complexity-factor">
                <h4>K2：设计条件复杂性（0.9-1.2）</h4>
                <p>现场条件限制、不停产施工、多专业交叉程度</p>
              </div>
              <div class="complexity-factor">
                <h4>K3：设计深度要求（0.9-1.2）</h4>
                <p>是否需要三维设计、仿真模拟、数字化交付等</p>
              </div>
              <div class="complexity-formula">
                <strong>总K值 = K1 × K2 × K3</strong>
                <span class="formula-note">取值区间见各项目类型详细说明</span>
              </div>
            </div>
          </div>

          <!-- 设计费用构成说明 -->
          <div class="fee-composition-section">
            <div class="section-banner">
              <div class="priority-indicator composition"></div>
              <h3 class="section-title">设计费用构成</h3>
              <el-tag type="warning" size="large">费用明细</el-tag>
            </div>
            <div class="composition-list">
              <div class="composition-item">
                <span class="composition-number">1</span>
                <div class="composition-content">
                  <h4>技术咨询与调研费</h4>
                  <p>项目前期调研、现场勘察、数据收集、可行性研究分析</p>
                </div>
              </div>
              <div class="composition-item">
                <span class="composition-number">2</span>
                <div class="composition-content">
                  <h4>方案设计费</h4>
                  <p>技术路线比选、方案编制、技术经济论证</p>
                </div>
              </div>
              <div class="composition-item">
                <span class="composition-number">3</span>
                <div class="composition-content">
                  <h4>评审费</h4>
                  <p>组织内部技术评审、外部专家评审会产生的费用</p>
                </div>
              </div>
              <div class="composition-item">
                <span class="composition-number">4</span>
                <div class="composition-content">
                  <h4>详细设计费</h4>
                  <p>工艺包设计、施工图设计、三维建模、软件编程、控制系统逻辑设计等</p>
                </div>
              </div>
              <div class="composition-item">
                <span class="composition-number">5</span>
                <div class="composition-content">
                  <h4>预算与文件编制费</h4>
                  <p>项目投资预算编制、技术规范书、招标技术文件编制</p>
                </div>
              </div>
              <div class="composition-item">
                <span class="composition-number">6</span>
                <div class="composition-content">
                  <h4>现场技术服务费</h4>
                  <p>设计交底、施工配合、现场设计变更处理（基础次数内）</p>
                </div>
              </div>
              <div class="composition-item">
                <span class="composition-number">7</span>
                <div class="composition-content">
                  <h4>外聘专家/机构费</h4>
                  <p>为特定技术难题聘请的外部专家咨询费</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 绩效考核 -->
        <div v-show="activeModule === 'performance'" class="content-section">
          <h2 class="section-title-main">绩效考核</h2>
          
          <!-- 基于真实数据的绩效考核 -->
          <div class="performance-section">
            <div class="section-banner">
              <div class="priority-indicator pm"></div>
              <h3 class="section-title">项目管理绩效考核体系</h3>
              <el-tag type="danger" size="large">核心标准</el-tag>
            </div>
            
            <!-- 角色绩效考核卡片 -->
            <div class="performance-cards-container">
              <div
                v-for="(roleData, roleKey) in performanceData"
                :key="roleKey"
                class="role-performance-card"
                :class="`role-${roleKey.replace(/\s+/g, '').toLowerCase()}`"
              >
                <div class="role-card-header">
                  <div class="role-icon">
                    <div class="icon-circle" :class="`bg-role-${roleKey.replace(/\s+/g, '').toLowerCase()}`">
                      {{ roleData.icon }}
                    </div>
                  </div>
                  <div class="role-info">
                    <h4 class="role-title">{{ roleData.role }}</h4>
                    <el-tag :type="roleData.color" size="medium">{{ roleData.dimensions.length }}个维度</el-tag>
                  </div>
                </div>
                
                <div class="dimensions-container">
                  <div
                    v-for="dimension in roleData.dimensions"
                    :key="dimension.name"
                    class="dimension-card"
                    :data-type="dimension.name.includes('硬指标') ? 'hard' : dimension.name.includes('软实力') ? 'soft' : dimension.name.includes('团队与贡献') ? 'team' : dimension.name.includes('协作与执行') ? 'collaboration' : 'other'"
                  >
                    <div class="dimension-header">
                      <h5 class="dimension-title">{{ dimension.name }}</h5>
                      <div class="dimension-weight">
                        <el-tag size="small" type="info">{{ (dimension.weight * 100).toFixed(0) }}%权重</el-tag>
                      </div>
                    </div>
                    
                    <div class="kpi-list">
                      <div
                        v-for="kpi in dimension.kpis"
                        :key="kpi"
                        class="kpi-item"
                      >
                        <div class="kpi-content">
                          <span class="kpi-text">{{ kpi }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="data-source">
                      <span class="source-label">数据来源:</span>
                      <span class="source-text">{{ dimension.dataSource }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 绩效等级划分 -->
          <div class="performance-section grade-section">
            <div class="section-banner">
              <div class="dancing-flag">
                <div class="flagpole"></div>
                <div class="flag"></div>
              </div>
              <h3 class="section-title">绩效等级划分标准</h3>
              <el-tag type="danger" size="large">评级标准</el-tag>
            </div>
            <div class="grade-cards">
              <div
                v-for="item in gradeData"
                :key="item.grade"
                class="grade-card"
                :class="`grade-${item.grade.replace('级', '').toLowerCase()}`"
              >
                <div class="grade-header">
                  <div class="grade-icon">
                    <div class="icon-circle" :class="`bg-grade-${item.grade.replace('级', '').toLowerCase()}`">
                      {{ item.grade }}
                    </div>
                  </div>
                  <div class="grade-info">
                    <span class="grade-score">{{ item.score }}</span>
                    <span class="grade-bonus">{{ item.bonus }}</span>
                  </div>
                </div>
                <div class="grade-description">
                  <span class="description-text">{{ item.description }}</span>
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

// 项目标准模块数据
const modules = reactive([
  {
    key: 'project-standard',
    title: '项目标准',
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
const activeModule = ref('project-standard')

// 当前展开的阶段索引（-1表示全部关闭）
const activeStageIndex = ref(-1)

// 获取模块类型
const getModuleType = (moduleKey: string) => {
  const typeMap: Record<string, string> = {
    'project-standard': 'process',
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
      },
      {
        name: '方案评审',
        role: '技术负责人',
        cycle: '3天',
        deliverables: '评审报告'
      },
      {
        name: '项目立项',
        role: '项目经理',
        cycle: '10天',
        deliverables: '立项文件'
      },
      {
        name: 'EPC合同签订',
        role: '商务/项目经理',
        cycle: '10天',
        deliverables: 'EPC合同'
      }
    ]
  },
  {
    projectStage: '项目推进',
    prerequisites: '1. EPC合同签订\n2. 项目定价',
    totalCycle: '40天',
    processes: [
      {
        name: '图纸设计',
        role: '技术负责人',
        cycle: '10天',
        deliverables: '1.项目设计图\n2.设计图/预算审查审批流程\n3.招标需求审批流程单\n4.招标公告\n5.招标文件\n6.技术任务书\n7.招标资格审查报告\n8.评标报告\n9.中标通知书\n10.采购合同\n11.施工合同\n12.系统软件编码备份'
      },
      {
        name: '图纸/预算审查',
        role: '技术负责人',
        cycle: '4天',
        deliverables: '审查报告'
      },
      {
        name: '招标需求审批',
        role: '商务负责人',
        cycle: '7天',
        deliverables: '审批文件'
      },
      {
        name: '招标启动',
        role: '商务负责人',
        cycle: '1天',
        deliverables: '招标启动文件'
      },
      {
        name: '技术任务书审查',
        role: '技术负责人',
        cycle: '3天',
        deliverables: '技术任务书'
      },
      {
        name: '招标公告',
        role: '商务负责人',
        cycle: '5天',
        deliverables: '招标公告'
      },
      {
        name: '招标资格审查',
        role: '商务负责人',
        cycle: '1天',
        deliverables: '资格审查报告'
      },
      {
        name: '开标评标',
        role: '商务负责人',
        cycle: '1天',
        deliverables: '评标报告'
      },
      {
        name: '中标通知书',
        role: '商务负责人',
        cycle: '5天',
        deliverables: '中标通知书'
      },
      {
        name: '采购合同签订',
        role: '商务/项目负责人',
        cycle: '10天',
        deliverables: '采购合同'
      }
    ]
  },
  {
    projectStage: '项目实施',
    prerequisites: '采购/施工合同签订',
    totalCycle: '按采购合同',
    processes: [
      {
        name: '设备到货',
        role: '项目经理',
        cycle: '按采购合同',
        deliverables: '1.设备到货签收单\n2.项目施工方案及安全预案\n3.施工作业票\n4.施工报告\n5.施工会议纪要\n6.设备技术档案\n7.系统操作手册\n8.项目试运行交付单\n9.项目验收报告\n10.项目评估报告'
      },
      {
        name: '施工方案评审',
        role: '技术负责人',
        cycle: '3天',
        deliverables: '施工方案'
      },
      {
        name: '安装',
        role: '现场负责人',
        cycle: '按采购合同',
        deliverables: '安装记录'
      },
      {
        name: '调试',
        role: '技术负责人',
        cycle: '按采购合同',
        deliverables: '调试报告'
      },
      {
        name: '项目交付运行',
        role: '技术负责人',
        cycle: '5天',
        deliverables: '交付文件'
      },
      {
        name: '项目验收',
        role: '项目经理',
        cycle: '按采购合同',
        deliverables: '验收报告'
      },
      {
        name: '项目评估',
        role: '项目经理',
        cycle: '验收后40天',
        deliverables: '评估报告'
      }
    ]
  },
  {
    projectStage: '项目质保',
    prerequisites: '项目终验报告',
    totalCycle: '按质保周期',
    processes: [
      {
        name: '设备/配件质保',
        role: '项目经理',
        cycle: '按质保周期',
        deliverables: '1.项目技术服务登记表\n2.质保记录表'
      },
      {
        name: '技术支持',
        role: '工程师',
        cycle: '按质保周期',
        deliverables: '技术支撑记录'
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
    note: '涉及工艺优化、能源系统集成',
    technicalCoefficient: 'K = 1.0-1.3'
  },
  {
    category: 'A类 节能改造项目',
    complexity: '30万<I≤200万',
    rate: '3.5%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '中型节能改造',
    technicalCoefficient: 'K = 1.0-1.4'
  },
  {
    category: 'A类 节能改造项目',
    complexity: '200万<I',
    rate: '2.0%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '大型节能系统改造',
    technicalCoefficient: 'K = 1.0-1.5'
  },
  {
    category: 'B类 装备改善项目',
    complexity: 'I≤100万',
    rate: '5.0%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '单一设备升级、换代',
    technicalCoefficient: 'K = 1.0-1.2'
  },
  {
    category: 'B类 装备改善项目',
    complexity: '100万<I≤300万',
    rate: '4.0%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '多设备升级、换代',
    technicalCoefficient: 'K = 1.0-1.3'
  },
  {
    category: 'B类 装备改善项目',
    complexity: '300万<I',
    rate: '3.0%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '生产线整体装备升级',
    technicalCoefficient: 'K = 1.0-1.4'
  },
  {
    category: 'C类 安全及综合性技改项目',
    complexity: 'I≤30万',
    rate: '5.5%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '涉及标准符合性、安全系统设计',
    technicalCoefficient: 'K = 1.0-1.2'
  },
  {
    category: 'C类 安全及综合性技改项目',
    complexity: '30万<I≤200万',
    rate: '4.5%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '生产流程安全系统技改或升级',
    technicalCoefficient: 'K = 1.0-1.3'
  },
  {
    category: 'C类 安全及综合性技改项目',
    complexity: '200万<I',
    rate: '3.5%',
    unit: '设备+安装',
    calculation: '按技改项目类型及技术复杂系数计算',
    note: '全厂性安全系统升级',
    technicalCoefficient: 'K = 1.0-1.4'
  }
])

// 绩效等级数据
const gradeData = reactive([
  {
    grade: 'S级',
    score: '≥ 95分',
    description: '超越期望，表现卓越',
    bonus: '超额完成目标，有突出贡献'
  },
  {
    grade: 'A级',
    score: '85-94分',
    description: '达成期望，表现优秀',
    bonus: '全面达成目标，部分超出'
  },
  {
    grade: 'B级',
    score: '75-84分',
    description: '基本达成期望，表现良好',
    bonus: '基本达成目标，无重大失误'
  },
  {
    grade: 'C级',
    score: '60-74分',
    description: '主要目标基本达成，存在需改进项',
    bonus: '合格'
  },
  {
    grade: 'D级',
    score: '< 60分',
    description: '目标达成差，存在重大失误',
    bonus: '待改进'
  }
])

// 绩效考核数据 - 基于Excel真实数据
const performanceData = reactive({
  项目经理: {
    role: '项目经理',
    icon: '👔',
    color: 'danger',
    dimensions: [
      {
        name: '项目成果（硬指标）',
        weight: 0.5,
        kpis: [
          '项目目标达成率（20%）：对比《项目任务书》，核心性能指标达成情况',
          '项目成本偏差率（10%）：（实际总成本 - 批准预算）/ 批准预算。目标：-5% ~ +3%',
          '项目进度偏差率（10%）：（实际工期 - 计划工期）/ 计划工期。目标：≤ 5%',
          '项目质量与安全（10%）：一次性验收通过率；项目期内安全责任事故发生次数（目标：0）'
        ],
        dataSource: '验收报告、测试数据'
      },
      {
        name: '过程管理（软实力）',
        weight: 0.3,
        kpis: [
          '流程与制度遵从度（10%）：是否严格遵循立项、评审、变更、验收等关键流程',
          '风险管理与问题解决（7%）：风险识别及时性、应对措施有效性；重大问题闭环解决率',
          '文档与信息管理（7%）：项目文档的完整性、准确性与及时归档率',
          '沟通与协调（6%）：内外部沟通是否顺畅有效，干系人满意度'
        ],
        dataSource: 'PMO过程审计记录、风险登记册、项目文档库检查'
      },
      {
        name: '团队与贡献',
        weight: 0.2,
        kpis: [
          '团队建设与赋能（8%）：对项目成员的指导与培养情况',
          '知识沉淀与创新（6%）：主动进行项目复盘，输出可复用的经验或技术成果',
          '资源利用效率（6%）：对项目内外部资源的统筹与优化利用情况'
        ],
        dataSource: '成员反馈、培训记录、后评估报告、知识库贡献'
      }
    ]
  },
  项目核心人员: {
    role: '项目核心人员',
    icon: '⚡',
    color: 'warning',
    dimensions: [
      {
        name: '任务交付（硬指标）',
        weight: 0.6,
        kpis: [
          '个人任务完成率与质量（30%）：分配的专业任务（如设计、调试）是否按时、按质完成',
          '技术问题解决贡献（30%）：在解决项目关键技术难题中的具体作用与成果'
        ],
        dataSource: '项目经理评价（70%）、技术负责人/PMO评价（30%）'
      },
      {
        name: '协作与执行（软实力）',
        weight: 0.4,
        kpis: [
          '协作精神与主动性（20%）：在跨专业协作中的配合度与主动担当意识',
          '规范遵守与纪律性（10%）：遵守项目纪律、安全规范、设计标准等情况',
          '学习与成长（10%）：在项目中技能提升、知识分享的表现'
        ],
        dataSource: '项目经理评价（50%）、项目经理/PMO评价（30%）、团队成员互评（20%）'
      }
    ]
  }
})

// 模块切换函数
const switchModule = (moduleKey: string) => {
  activeModule.value = moduleKey
}

// 阶段展开/收起切换
const toggleStage = (stageIndex: number) => {
  if (activeStageIndex.value === stageIndex) {
    activeStageIndex.value = -1  // 收起
  } else {
    activeStageIndex.value = stageIndex  // 展开
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
  console.log('项目标准组件已挂载')
})
</script>

<style scoped>
/* 扁平化清新主题 */
.standardization-container {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
  color: #1e293b;
}

/* 页面头部 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

/* 一级卡片容器 */
.module-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.module-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 2px solid transparent;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.module-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #3b82f6;
}

.module-card.active {
  border-color: #3b82f6;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.15);
}

/* 卡片类型颜色区分 */
.module-card[data-type="process"] {
  border-left: 4px solid #3b82f6;
}

.module-card[data-type="cost"] {
  border-left: 4px solid #10b981;
}

.module-card[data-type="design"] {
  border-left: 4px solid #f59e0b;
}

.module-card[data-type="performance"] {
  border-left: 4px solid #ef4444;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-image {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
}

.card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-info {
  flex: 1;
}

.card-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: #1e293b;
}

.card-description {
  font-size: 0.9rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

/* 内容区 */
.content-area {
  background: #f8fafc;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #e2e8f0;
}

.content-section {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
}

.section-title-main {
  color: #1e293b;
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0 0 30px 0;
  text-align: center;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 16px;
}

/* 舞动旗帜动画 */
.dancing-flag {
  position: relative;
  display: inline-block;
  margin-right: 10px;
}

.flagpole {
  width: 2px;
  height: 30px;
  background: #333;
  position: relative;
  animation: flagpoleSway 2s ease-in-out infinite;
}

.flag {
  position: absolute;
  top: 0;
  left: 2px;
  width: 20px;
  height: 15px;
  background: linear-gradient(45deg, #ff4757, #ff6b7a);
  border-radius: 0 4px 4px 0;
  animation: flagWave 1.5s ease-in-out infinite;
}

@keyframes flagpoleSway {
  0%, 100% { transform: rotate(-2deg); }
  50% { transform: rotate(2deg); }
}

@keyframes flagWave {
  0%, 100% { transform: translateX(0) skewY(0deg); }
  25% { transform: translateX(2px) skewY(1deg); }
  50% { transform: translateX(4px) skewY(0deg); }
  75% { transform: translateX(2px) skewY(-1deg); }
}

/* 成本管理样式 */
.cost-section {
  margin-bottom: 40px;
}

.section-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px 20px;
  border-radius: 8px;
  border: 1px solid;
}

.priority-core .section-banner {
  background: #fef2f2;
  border-color: #fecaca;
}

.priority-major .section-banner {
  background: #fffbeb;
  border-color: #fed7aa;
}

.priority-secondary .section-banner {
  background: #f0f9ff;
  border-color: #bae6fd;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
  color: #1e293b;
}

.cost-grid {
  display: grid;
  gap: 16px;
}

.core-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.major-grid {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.secondary-grid {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.cost-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.cost-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.cost-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.cost-header h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
}

.cost-details p {
  margin: 8px 0;
  font-size: 0.9rem;
  color: #475569;
  line-height: 1.5;
}

/* 流程卡片样式 */
.process-flow-container {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.project-stage-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.project-stage-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.15);
}

.project-stage-card.active {
  border-color: #3b82f6;
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(147, 197, 253, 0.02));
}

.stage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 8px 0;
}

.stage-header-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.stage-number {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.stage-info {
  flex: 1;
}

.stage-title {
  margin: 0 0 6px 0;
  color: #1e293b;
  font-size: 1.3rem;
  font-weight: 600;
}

.stage-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.stage-cycle {
  color: #f59e0b;
  font-size: 0.9rem;
  font-weight: 500;
}

.stage-count {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 500;
}

.stage-toggle {
  flex-shrink: 0;
}

.toggle-icon {
  width: 32px;
  height: 32px;
  background: #f1f5f9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  font-size: 1.2rem;
  font-weight: bold;
  transition: all 0.2s ease;
}

.project-stage-card:hover .toggle-icon {
  background: #e2e8f0;
  color: #475569;
}

.stage-content {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.stage-prerequisites {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.prerequisites-label {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 600;
}

.prerequisites-value {
  color: #1e293b;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-line;
}

/* 展开的流程样式 */
.expanded-processes {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
  animation: expandDown 0.3s ease-out;
}

@keyframes expandDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.expanded-title {
  color: #1e293b;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 12px;
}

.process-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.process-item {
  background: #f8fafc;
  border-radius: 8px;
  padding: 12px;
  border-left: 3px solid #3b82f6;
  transition: all 0.2s ease;
}

.process-item:hover {
  background: #f1f5f9;
  border-left-color: #1d4ed8;
}

.process-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.process-number {
  width: 22px;
  height: 22px;
  background: #3b82f6;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.7rem;
  font-weight: 600;
  flex-shrink: 0;
}

.process-details {
  flex: 1;
}

.process-name {
  color: #1e293b;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 2px;
}

.process-meta {
  display: flex;
  gap: 12px;
}

.process-role {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 500;
}

.process-cycle {
  color: #f59e0b;
  font-size: 0.8rem;
  font-weight: 500;
}

.process-deliverables {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.deliverables-label {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 500;
}

.deliverables-text {
  color: #475569;
  font-size: 0.85rem;
  line-height: 1.4;
  white-space: pre-line;
}

/* 成本卡片样式 */
.cost-cards-grid {
  display: grid;
  gap: 16px;
}

.core-cards {
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
}

.major-cards {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.secondary-cards {
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.cost-card-highlight {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.priority-core .cost-card-highlight {
  border-color: #fecaca;
}

.priority-core .cost-card-highlight:hover {
  border-color: #dc2626;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
}

.priority-major .cost-card-highlight {
  border-color: #fed7aa;
}

.priority-major .cost-card-highlight:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.15);
}

.priority-secondary .cost-card-highlight {
  border-color: #bae6fd;
}

.priority-secondary .cost-card-highlight:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.cost-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.cost-icon {
  flex-shrink: 0;
}

.icon-circle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: white;
}

.bg-core {
  background: linear-gradient(135deg, #dc2626, #ef4444);
}

.bg-major {
  background: linear-gradient(135deg, #d97706, #f59e0b);
}

.bg-secondary {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
}

.cost-info {
  flex: 1;
}

.cost-title {
  margin: 0 0 4px 0;
  color: #1e293b;
  font-size: 1.2rem;
  font-weight: 600;
}

.cost-tag {
  margin: 0;
}

.cost-card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cost-detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  color: #64748b;
  font-size: 0.9rem;
  font-weight: 500;
}

.detail-value {
  color: #1e293b;
  font-size: 0.95rem;
  line-height: 1.4;
}

.rate-highlight {
   color: #dc2626 !important;
   font-weight: 700 !important;
   font-size: 1.1rem !important;
 }

/* 设计费容器样式 */
.design-fee-container {
  margin-top: 20px;
}

.design-fee-group {
  margin-bottom: 24px;
  border-radius: 16px;
  overflow: hidden;
}

.group-a {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.08), rgba(74, 222, 128, 0.04));
  border: 2px solid rgba(34, 197, 94, 0.15);
}

.group-b {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(251, 191, 36, 0.04));
  border: 2px solid rgba(245, 158, 11, 0.15);
}

.group-c {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(248, 113, 113, 0.04));
  border: 2px solid rgba(239, 68, 68, 0.15);
}

.group-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: #f8fafc;
}

.group-icon {
  flex-shrink: 0;
}

.bg-class-a {
  background: linear-gradient(135deg, #22c55e, #4ade80);
  color: white;
}

.bg-class-b {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: white;
}

.bg-class-c {
  background: linear-gradient(135deg, #ef4444, #f87171);
  color: white;
}

.group-title {
  margin: 0;
  color: #1e293b;
  font-size: 1.2rem;
  font-weight: 600;
  flex: 1;
}

.group-tag {
  margin: 0;
}

/* 重点标签突出显示 */
.priority-tag-a {
  background: linear-gradient(135deg, #16a34a, #22c55e) !important;
  color: white !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  padding: 6px 12px !important;
  border: 2px solid #15803d !important;
  box-shadow: 0 4px 8px rgba(34, 197, 94, 0.3), 0 0 0 3px rgba(34, 197, 94, 0.1) !important;
  animation: priority-glow-a 3s ease-in-out infinite !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

.priority-tag-b {
  background: linear-gradient(135deg, #ea580c, #f97316) !important;
  color: white !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  padding: 6px 12px !important;
  border: 2px solid #c2410c !important;
  box-shadow: 0 4px 8px rgba(249, 115, 22, 0.3), 0 0 0 3px rgba(249, 115, 22, 0.1) !important;
  animation: priority-glow-b 3s ease-in-out infinite !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

.priority-tag-c {
  background: linear-gradient(135deg, #dc2626, #ef4444) !important;
  color: white !important;
  font-weight: 700 !important;
  font-size: 0.9rem !important;
  padding: 6px 12px !important;
  border: 2px solid #b91c1c !important;
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3), 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
  animation: priority-glow-c 3s ease-in-out infinite !important;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2) !important;
}

/* 重点标签发光动画 */
@keyframes priority-glow-a {
  0%, 100% {
    box-shadow: 0 4px 8px rgba(34, 197, 94, 0.3), 0 0 0 3px rgba(34, 197, 94, 0.1);
  }
  50% {
    box-shadow: 0 6px 16px rgba(34, 197, 94, 0.5), 0 0 0 5px rgba(34, 197, 94, 0.2);
  }
}

@keyframes priority-glow-b {
  0%, 100% {
    box-shadow: 0 4px 8px rgba(249, 115, 22, 0.3), 0 0 0 3px rgba(249, 115, 22, 0.1);
  }
  50% {
    box-shadow: 0 6px 16px rgba(249, 115, 22, 0.5), 0 0 0 5px rgba(249, 115, 22, 0.2);
  }
}

@keyframes priority-glow-c {
  0%, 100% {
    box-shadow: 0 4px 8px rgba(239, 68, 68, 0.3), 0 0 0 3px rgba(239, 68, 68, 0.1);
  }
  50% {
    box-shadow: 0 6px 16px rgba(239, 68, 68, 0.5), 0 0 0 5px rgba(239, 68, 68, 0.2);
  }
}

.design-fee-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  padding: 20px;
}

.design-fee-card {
  background: white;
  border-radius: 12px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.design-fee-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.15);
}

.design-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}

.design-icon {
  flex-shrink: 0;
}

.design-bg {
  background: linear-gradient(135deg, #ec4899, #f472b6);
  color: white;
}

.design-info {
  flex: 1;
}

.design-category {
  margin: 0 0 4px 0;
  color: #1e293b;
  font-size: 1.1rem;
  font-weight: 600;
}

.design-note {
  color: #64748b;
  font-size: 0.85rem;
  line-height: 1.3;
}

.complexity-tag {
  margin: 0;
}

.design-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.design-icon {
  flex-shrink: 0;
}

.design-bg {
  background: linear-gradient(135deg, #ec4899, #f472b6);
  color: white;
}

.design-info {
  flex: 1;
}

.design-category {
  margin: 0 0 4px 0;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.complexity-tag {
  margin: 0;
}

.design-card-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.design-detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* 技术复杂系数突出显示 */
.coefficient-highlight {
  color: #7c3aed;
  font-weight: 700;
  font-size: 0.95rem;
  background: rgba(124, 58, 237, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(124, 58, 237, 0.3);
}

/* 技术复杂系数说明区域 */
.technical-complexity-section {
  margin-bottom: 24px;
}

.complexity-explanation {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.complexity-factor {
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.complexity-factor h4 {
  margin: 0 0 8px 0;
  color: #7c3aed;
  font-size: 1rem;
  font-weight: 600;
}

.complexity-factor p {
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.4;
}

.complexity-formula {
  grid-column: 1 / -1;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-radius: 8px;
  padding: 16px;
  border: 2px solid #7c3aed;
  text-align: center;
}

.complexity-formula strong {
  font-size: 1.2rem;
  color: #7c3aed;
  display: block;
  margin-bottom: 8px;
}

.formula-note {
  color: #64748b;
  font-size: 0.9rem;
}

/* 设计费用构成说明区域 */
.fee-composition-section {
  margin-bottom: 24px;
}

.composition-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.composition-item {
  display: flex;
  gap: 16px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.composition-item:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.15);
}

.composition-number {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1rem;
  box-shadow: 0 2px 4px rgba(245, 158, 11, 0.3);
}

.composition-content h4 {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 1.1rem;
  font-weight: 600;
}

.composition-content p {
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.4;
}

/* 绩效卡片样式 */
.performance-card-highlight {
  background: white;
  border-radius: 8px;
  padding: 24px;
  border: 1px solid #fecaca;
  margin-top: 20px;
  transition: all 0.2s ease;
}

.performance-card-highlight:hover {
  border-color: #dc2626;
  box-shadow: 0 4px 8px rgba(220, 38, 38, 0.15);
}

.performance-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.performance-icon {
  flex-shrink: 0;
}

.bg-pm {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: white;
}

.performance-title {
  margin: 0;
  color: #1e293b;
  font-size: 1.3rem;
  font-weight: 600;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.metric-label {
  color: #64748b;
  font-size: 1rem;
  font-weight: 500;
}

.metric-value {
  color: #1e293b;
  font-weight: 600;
  font-size: 1rem;
}

.highlight-metric {
  color: #dc2626 !important;
  font-weight: 700 !important;
  font-size: 1.1rem !important;
}

/* 绩效等级卡片样式 */
.grade-cards {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 12px;
  margin-top: 20px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.grade-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
  min-height: 120px;
}

.grade-s .grade-card {
  border-color: #bbf7d0;
}

.grade-s .grade-card:hover {
  border-color: #22c55e;
  box-shadow: 0 4px 8px rgba(34, 197, 94, 0.15);
}

.grade-a .grade-card {
  border-color: #bfdbfe;
}

.grade-a .grade-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.15);
}

.grade-b .grade-card {
  border-color: #fed7aa;
}

.grade-b .grade-card:hover {
  border-color: #f59e0b;
  box-shadow: 0 4px 8px rgba(245, 158, 11, 0.15);
}

.grade-c .grade-card {
  border-color: #fdba74;
}

.grade-c .grade-card:hover {
  border-color: #f97316;
  box-shadow: 0 4px 8px rgba(249, 115, 22, 0.15);
}

.grade-d .grade-card {
  border-color: rgba(239, 68, 68, 0.4);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(248, 113, 113, 0.08));
}

.grade-d .grade-card:hover {
  border-color: rgba(239, 68, 68, 0.7);
  transform: translateY(-4px);
  box-shadow: 0 12px 35px rgba(239, 68, 68, 0.25);
}

.grade-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.grade-icon {
  flex-shrink: 0;
}

.bg-grade-s {
  background: linear-gradient(135deg, #16a34a, #22c55e);
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
}

.bg-grade-a {
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
}

.bg-grade-b {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
}

.bg-grade-c {
  background: linear-gradient(135deg, #ea580c, #f97316);
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
}

.bg-grade-d {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: white;
  font-size: 1.2rem;
  font-weight: 700;
}

.grade-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.grade-score {
  color: #1e293b;
  font-size: 0.9rem;
  font-weight: 600;
  white-space: nowrap;
}

.grade-bonus {
  color: #dc2626;
  font-size: 0.8rem;
  font-weight: 600;
  white-space: nowrap;
}

.grade-description {
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.description-text {
  color: #475569;
  font-size: 0.75rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 确保表格边框可见 */
:deep(.el-table td) {
  border-color: #e2e8f0 !important;
}

:deep(.el-table th.is-leaf) {
  border-color: #e2e8f0 !important;
}

/* 绩效样式 */
.performance-section {
  margin-bottom: 40px;
}

.performance-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}

.performance-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e2e8f0;
}

.performance-card h4 {
  margin: 0 0 15px 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: #1e293b;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e2e8f0;
}

.metric-item:last-child {
  border-bottom: none;
}

.metric-label {
  color: #64748b;
  font-size: 0.9rem;
}

.metric-value {
  color: #1e293b;
  font-weight: 600;
  font-size: 0.9rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .standardization-container {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
    padding: 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .main-content {
    padding: 20px;
  }
  
  .module-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .content-area {
    padding: 16px;
  }
  
  .cost-cards-grid,
  .performance-grid {
    grid-template-columns: 1fr;
  }
  
  .cost-cards-grid.core-cards {
    grid-template-columns: 1fr;
  }
  
  .cost-cards-grid.major-cards {
    grid-template-columns: 1fr;
  }
  
  .cost-cards-grid.secondary-cards {
    grid-template-columns: 1fr;
  }
  
  .stage-title {
    font-size: 1.1rem;
  }
  
  .cost-title {
    font-size: 1.1rem;
  }
}

/* 绩效卡片新样式 */
.performance-cards-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.role-performance-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
}

.role-performance-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
}

.role-card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.role-icon {
  flex-shrink: 0;
}

.role-info {
  flex: 1;
}

.role-title {
  margin: 0 0 8px 0;
  color: #1e293b;
  font-size: 1.4rem;
  font-weight: 700;
}

.dimensions-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dimension-card {
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  border: 1px solid #e2e8f0;
}

.dimension-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.dimension-title {
  margin: 0;
  color: #1e293b;
  font-size: 1.1rem;
  font-weight: 600;
}

.kpi-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.kpi-item {
  background: white;
  border-radius: 6px;
  padding: 10px 12px;
  border-left: 3px solid #3b82f6;
}

.kpi-content {
  display: flex;
  align-items: flex-start;
}

.kpi-text {
  color: #475569;
  font-size: 0.9rem;
  line-height: 1.5;
}

.data-source {
  padding: 8px 0;
  border-top: 1px solid #e2e8f0;
}

.source-label {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 500;
  margin-right: 8px;
}

.source-text {
  color: #475569;
  font-size: 0.8rem;
  line-height: 1.4;
}

/* 维度权重重点标识 */
.dimension-weight {
  display: flex;
  align-items: center;
}

.dimension-weight .el-tag {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.dimension-weight .el-tag:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* 硬指标权重特殊标识 */
.dimension-card[data-type="hard"] .dimension-weight .el-tag {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: white;
  border: 2px solid #b91c1c;
  animation: pulse-red 2s infinite;
}

/* 软实力权重特殊标识 */
.dimension-card[data-type="soft"] .dimension-weight .el-tag {
  background: linear-gradient(135deg, #7c3aed, #a855f7);
  color: white;
  border: 2px solid #6d28d9;
  animation: pulse-purple 2s infinite;
}

/* 团队与贡献权重样式 */
.dimension-card[data-type="team"] .dimension-weight .el-tag {
  background: linear-gradient(135deg, #059669, #10b981);
  color: white;
  border: 2px solid #047857;
}

/* 协作与执行权重样式 */
.dimension-card[data-type="collaboration"] .dimension-weight .el-tag {
  background: linear-gradient(135deg, #ea580c, #f97316);
  color: white;
  border: 2px solid #c2410c;
}

/* 动画效果 */
@keyframes pulse-red {
  0%, 100% {
    box-shadow: 0 2px 4px rgba(220, 38, 38, 0.2);
  }
  50% {
    box-shadow: 0 2px 4px rgba(220, 38, 38, 0.4), 0 0 0 4px rgba(220, 38, 38, 0.1);
  }
}

@keyframes pulse-purple {
  0%, 100% {
    box-shadow: 0 2px 4px rgba(124, 58, 237, 0.2);
  }
  50% {
    box-shadow: 0 2px 4px rgba(124, 58, 237, 0.4), 0 0 0 4px rgba(124, 58, 237, 0.1);
  }
}

/* 角色图标颜色 */
.bg-role-项目经理 {
  background: linear-gradient(135deg, #dc2626, #ef4444);
  color: white;
}

.bg-role-项目核心人员 {
  background: linear-gradient(135deg, #d97706, #f59e0b);
  color: white;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .performance-cards-container {
    gap: 16px;
  }
  
  .role-performance-card {
    padding: 16px;
  }
  
  .role-card-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .dimension-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .kpi-item {
    padding: 8px 10px;
  }
  
  /* 绩效等级卡片移动端优化 */
  .grade-cards {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  
  .grade-card {
    padding: 12px;
    min-height: 100px;
  }
  
  .grade-score {
    font-size: 0.9rem;
  }
  
  .grade-bonus {
    font-size: 0.8rem;
  }
  
  .description-text {
    font-size: 0.75rem;
  }
}
</style>
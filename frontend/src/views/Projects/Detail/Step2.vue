<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>项目详情 - 成本设定</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>项目详情</el-breadcrumb-item>
            <el-breadcrumb-item>成本设定</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="1" align-center>
        <el-step title="基本信息" description="查看项目基本信息和合同信息" />
        <el-step title="成本设定" description="查看四大成本设置" />
        <el-step title="任务设定" description="查看项目任务设置" />
        <el-step title="文档管理" description="查看项目文档" />
      </el-steps>
      
      <div class="cost-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading">
          <el-icon class="is-loading"><Loading /></el-icon> 加载中...
        </div>
        
        <!-- 错误状态 -->
        <div v-if="error" class="error">
          <el-alert :title="error" type="error" :closable="false" />
        </div>
        
        <!-- 主要内容 -->
        <div v-if="!loading && !error" class="results">
          <!-- 成本类型选项卡 -->
        <el-tabs v-model="activeTab" type="card" class="cost-tabs">
          <!-- 物料成本 -->
          <el-tab-pane label="物料成本" name="material">
            <div class="cost-type-section">
              <div class="section-header">
                <h3>物料成本管理</h3>
              </div>
              
              <!-- 成本统计 -->
              <div class="cost-statistics">
                <el-row :gutter="20" style="margin-bottom: 15px;">
                  <el-col :span="6">
                    <el-statistic 
                      title="成本预算合计" 
                      :value="materialBudgetTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #0288d1;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本实际合计" 
                      :value="materialActualTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #388e3c;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本偏差" 
                      :value="materialCostVariance" 
                      prefix="¥" 
                      :precision="2" 
                      :class="materialCostVariance > 0 ? 'statistic-red' : (materialCostVariance < 0 ? 'statistic-green' : '')"
                    />
                  </el-col>
                </el-row>
              </div>
              
              <el-table :data="materialCosts" border style="width: 100%" fit class="cost-table">
                <el-table-column type="index" label="序号" width="80" align="center" />
                <el-table-column prop="material_name" label="物料名称" min-width="180" :show-overflow-tooltip="false" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.material_name || '-' }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="specification" label="规格" min-width="160" :show-overflow-tooltip="false" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.specification || '-' }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="unit" label="单位" width="80" min-width="80" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.unit || '-' }}
                    </div>
                  </template>
                </el-table-column>
                
                <!-- 预算成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #0288d1; font-weight: bold;">成本预算</div>
                  </template>
                  <el-table-column min-width="90" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">数量</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        {{ scope.row.budget_quantity || 0 }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">单价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        ¥{{ Number(scope.row.budget_unit_price || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="160" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        ¥{{ Number(scope.row.budget_total || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <!-- 实际成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #388e3c; font-weight: bold;">成本实际</div>
                  </template>
                  <el-table-column min-width="90" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">数量</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        {{ scope.row.actual_quantity || 0 }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">单价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        ¥{{ Number(scope.row.actual_unit_price || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="160" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        ¥{{ Number(scope.row.actual_total || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <!-- 外包成本 -->
          <el-tab-pane label="外包成本" name="outsourcing">
            <div class="cost-type-section">
              <div class="section-header">
                <h3>外包成本管理</h3>
              </div>
              
              <!-- 成本统计 -->
              <div class="cost-statistics">
                <el-row :gutter="20" style="margin-bottom: 15px;">
                  <el-col :span="6">
                    <el-statistic 
                      title="成本预算合计" 
                      :value="outsourcingBudgetTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #0288d1;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本实际合计" 
                      :value="outsourcingActualTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #388e3c;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本偏差" 
                      :value="outsourcingCostVariance" 
                      prefix="¥" 
                      :precision="2" 
                      :class="outsourcingCostVariance > 0 ? 'statistic-red' : (outsourcingCostVariance < 0 ? 'statistic-green' : '')"
                    />
                  </el-col>
                </el-row>
              </div>
              
              <el-table :data="outsourcingCosts" border style="width: 100%" fit class="cost-table">
                <el-table-column type="index" label="序号" width="80" align="center" />
                <el-table-column prop="service_type" label="服务类型" min-width="150" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.service_type || '-' }}
                    </div>
                  </template>
                </el-table-column>
                
                <!-- 预算成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #0288d1; font-weight: bold;">成本预算</div>
                  </template>
                  <el-table-column min-width="200" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">服务内容</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        {{ scope.row.budget_description || '-' }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        ¥{{ Number(scope.row.budget_amount || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <!-- 实际成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #388e3c; font-weight: bold;">成本实际</div>
                  </template>
                  <el-table-column min-width="200" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">服务内容</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        {{ scope.row.actual_description || '-' }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        ¥{{ Number(scope.row.actual_amount || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column prop="remark" label="备注" min-width="200" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.remark || '-' }}
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <!-- 间接成本 -->
          <el-tab-pane label="间接成本" name="indirect">
            <div class="cost-type-section">
              <div class="section-header">
                <h3>间接成本管理</h3>
              </div>
              
              <!-- 成本统计 -->
              <div class="cost-statistics">
                <el-row :gutter="20" style="margin-bottom: 15px;">
                  <el-col :span="6">
                    <el-statistic 
                      title="成本预算合计" 
                      :value="indirectBudgetTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #0288d1;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本实际合计" 
                      :value="indirectActualTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #388e3c;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本偏差" 
                      :value="indirectCostVariance" 
                      prefix="¥" 
                      :precision="2" 
                      :class="indirectCostVariance > 0 ? 'statistic-red' : (indirectCostVariance < 0 ? 'statistic-green' : '')"
                    />
                  </el-col>
                </el-row>
              </div>
              
              <el-table :data="indirectCosts" border style="width: 100%" fit class="cost-table">
                <el-table-column type="index" label="序号" width="80" align="center" />
                <el-table-column prop="cost_type" label="成本类型" min-width="150" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.cost_type || '-' }}
                    </div>
                  </template>
                </el-table-column>
                
                <!-- 预算成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #0288d1; font-weight: bold;">成本预算</div>
                  </template>
                  <el-table-column min-width="200" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">服务内容</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        {{ scope.row.budget_description || '-' }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        ¥{{ Number(scope.row.budget_amount || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <!-- 实际成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #388e3c; font-weight: bold;">成本实际</div>
                  </template>
                  <el-table-column min-width="200" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">服务内容</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        {{ scope.row.actual_description || '-' }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        ¥{{ Number(scope.row.actual_amount || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column prop="remark" label="备注" min-width="200" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.remark || '-' }}
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <!-- 人力成本 -->
          <el-tab-pane label="人力成本" name="labor">
            <div class="cost-type-section">
              <div class="section-header">
                <h3>人力成本管理</h3>
              </div>
              
              <!-- 成本统计 -->
              <div class="cost-statistics">
                <el-row :gutter="20" style="margin-bottom: 15px;">
                  <el-col :span="6">
                    <el-statistic 
                      title="成本预算合计" 
                      :value="laborBudgetTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #0288d1;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本实际合计" 
                      :value="laborActualTotal" 
                      prefix="¥" 
                      :precision="2" 
                      style="color: #388e3c;"
                    />
                  </el-col>
                  <el-col :span="6">
                    <el-statistic 
                      title="成本偏差" 
                      :value="laborCostVariance" 
                      prefix="¥" 
                      :precision="2" 
                      :class="laborCostVariance > 0 ? 'statistic-red' : (laborCostVariance < 0 ? 'statistic-green' : '')"
                    />
                  </el-col>
                </el-row>
              </div>
              
              <el-table :data="laborCosts" border style="width: 100%" fit class="cost-table">
                <el-table-column type="index" label="序号" width="80" align="center" />
                <el-table-column prop="personnel_name" label="人员姓名" min-width="150" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.personnel_name || '-' }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="department" label="部门" min-width="120" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.department || '-' }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="position" label="职位" min-width="120" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.position || '-' }}
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="hourly_rate" label="每小时费用" min-width="120" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      ¥{{ Number(scope.row.hourly_rate || 0).toFixed(2) }}
                    </div>
                  </template>
                </el-table-column>
                
                <!-- 预算成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #0288d1; font-weight: bold;">成本预算</div>
                  </template>
                  <el-table-column min-width="100" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">工时</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        {{ scope.row.budget_hours || 0 }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="120" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1; padding: 8px;">
                        ¥{{ Number(scope.row.budget_total || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <!-- 实际成本列 -->
                <el-table-column align="center">
                  <template #header>
                    <div style="color: #388e3c; font-weight: bold;">成本实际</div>
                  </template>
                  <el-table-column min-width="100" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">工时</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        {{ scope.row.actual_hours || 0 }}
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="120" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c; padding: 8px;">
                        ¥{{ Number(scope.row.actual_total || 0).toFixed(2) }}
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column prop="remark" label="备注" min-width="200" align="center">
                  <template #default="scope">
                    <div style="padding: 8px;">
                      {{ scope.row.remark || '-' }}
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="goBack">返回项目列表</el-button>
          <el-button @click="handlePrevious">查看上一步</el-button>
          <el-button type="primary" @click="handleNext">查看下一步</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getProjectCosts } from '@/api/project'

// 财务格式化函数
const formatToFinancial = (value: any): string => {
  if (value === null || value === undefined || value === '') return '0.00'
  const num = parseFloat(value)
  return isNaN(num) ? '0.00' : num.toFixed(2)
}

const router = useRouter()
const route = useRoute()

// 获取项目ID
const projectId = computed(() => route.params.id as string)

// 当前活跃的选项卡
const activeTab = ref('material')

// 各类成本数据
const materialCosts = ref<any[]>([])
const outsourcingCosts = ref<any[]>([])
const indirectCosts = ref<any[]>([])
const laborCosts = ref<any[]>([])

// 加载状态
const loading = ref(false)
const error = ref('')

// 数据处理函数
const processMaterialCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  console.log('DEBUG: [Step2页面] 原始物料成本数据:', data)
  
  // 按物料名称、规格、单位分组
  const groupedCosts: Record<string, any> = {}
  
  data.forEach((cost: any) => {
    console.log('DEBUG: [Step2页面] 处理单条成本记录:', {
      name: cost.name,
      specification: cost.specification,
      unit: cost.unit,
      quantity: cost.quantity,
      unit_price: cost.unit_price,
      total_price: cost.total_price,
      cost_type: cost.cost_type
    })
    
    // 创建分组键：物料名称_规格_单位
    const groupKey = `${cost.name || ''}_${cost.specification || ''}_${cost.unit || ''}`
    console.log('DEBUG: [Step2页面] 生成的分组键:', groupKey)
    
    if (!groupedCosts[groupKey]) {
      groupedCosts[groupKey] = {
        name: cost.name || '',
        specification: cost.specification || '',
        unit: cost.unit || '',
        budget: null, // 预算数据
        actual: null  // 实际数据
      }
      console.log('DEBUG: [Step2页面] 创建新分组:', groupedCosts[groupKey])
    } else {
      console.log('DEBUG: [Step2页面] 使用现有分组:', groupedCosts[groupKey])
    }
    
    // 尝试匹配成本类型，处理可能的编码问题
    const costType = cost.cost_type || ''
    const isBudget = costType === '预算' || costType.includes('预')
    const isActual = costType === '实际' || costType.includes('实')
    
    // 根据cost_type区分预算和实际数据
    if (isBudget) {
      groupedCosts[groupKey].budget = cost
      console.log('DEBUG: [Step2页面] 设置预算数据:', cost)
    } else if (isActual) {
      groupedCosts[groupKey].actual = cost
      console.log('DEBUG: [Step2页面] 设置实际数据:', cost)
    }
  })
  
  console.log('DEBUG: [Step2页面] 最终分组结果:', groupedCosts)
  
  // 将分组后的数据转换为前端期望的格式，合并预算和实际数据到一行
  return Object.values(groupedCosts).map((group: any, index: number) => {
    // 获取预算和实际数据
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
    console.log('DEBUG: [Step2页面] 物料数据详情:', {
      groupKey: `${group.name}_${group.specification}_${group.unit}`,
      budgetData: budgetData,
      actualData: actualData
    })
    
    // 使用字段名和逻辑
    const materialName = group.name || ''
    const specification = group.specification || ''
    const unit = group.unit || ''
    
    // 从预算和实际数据中提取数值，确保正确处理数据库中的numeric类型
    const budgetQuantity = parseFloat(budgetData.quantity || 0)
    const budgetUnitPrice = parseFloat(budgetData.unit_price || 0)
    const budgetTotal = parseFloat(budgetData.total_price || 0) || (budgetQuantity * budgetUnitPrice)
    
    const actualQuantity = parseFloat(actualData.quantity || 0)
    const actualUnitPrice = parseFloat(actualData.unit_price || 0)
    const actualTotal = parseFloat(actualData.total_price || 0) || (actualQuantity * actualUnitPrice)
    
    console.log('DEBUG: [Step2页面] 转换后物料数据:', {
      materialName: materialName,
      specification: specification,
      unit: unit,
      budget: {
        quantity: budgetQuantity,
        unitPrice: budgetUnitPrice,
        total: budgetTotal
      },
      actual: {
        quantity: actualQuantity,
        unitPrice: actualUnitPrice,
        total: actualTotal
      }
    })
    
    return {
      id: index + 1,
      material_name: materialName,
      specification: specification,
      unit: unit,
      // 预算成本字段
      budget_quantity: budgetQuantity,
      budget_quantity_display: budgetQuantity.toString(), // 数量不需要货币格式化
      budget_unit_price: budgetUnitPrice,
      budget_unit_price_display: formatToFinancial(budgetUnitPrice),
      budget_total: budgetTotal,
      budget_total_display: formatToFinancial(budgetTotal),
      // 实际成本字段
      actual_quantity: actualQuantity,
      actual_quantity_display: actualQuantity.toString(),
      actual_unit_price: actualUnitPrice,
      actual_unit_price_display: formatToFinancial(actualUnitPrice),
      actual_total: actualTotal,
      actual_total_display: formatToFinancial(actualTotal),
      // 其他字段
      remark: budgetData.remark || actualData.remark || ''
    }
  })
}

const processOutsourcingCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  console.log('DEBUG: [Step2页面] 原始外包成本数据:', data)
  
  // 按服务类型分组，然后区分预算和实际数据
  const groupedCosts: Record<string, { budget: any; actual: any }> = {}
  
  data.forEach((cost: any) => {
    const serviceType = cost.service_type || ''
    
    if (!groupedCosts[serviceType]) {
      groupedCosts[serviceType] = { budget: null, actual: null }
    }
    
    if (cost.cost_type === '预算') {
      groupedCosts[serviceType].budget = cost
    } else if (cost.cost_type === '实际') {
      groupedCosts[serviceType].actual = cost
    }
  })
  
  console.log('DEBUG: [Step2页面] 按服务类型分组后的外包成本数据:', groupedCosts)
  
  // 将分组后的数据转换为前端期望的格式
  return Object.values(groupedCosts).map((group: any, index: number) => {
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
    console.log('DEBUG: [Step2页面] 外包成本详情:', {
      pairIndex: index,
      budget: {
        costId: budgetData.cost_id,
        serviceType: budgetData.service_type,
        description: budgetData.description,
        costType: budgetData.cost_type,
        totalPrice: budgetData.total_price
      },
      actual: {
        costId: actualData.cost_id,
        serviceType: actualData.service_type,
        description: actualData.description,
        costType: actualData.cost_type,
        totalPrice: actualData.total_price
      }
    })
    
    // 服务类型优先使用预算数据的，预算没有则使用实际的
    const serviceType = budgetData.service_type || actualData.service_type || ''
    
    // 确保description字段能正确映射到budget_description和actual_description
    // 预算数据的description
    const budgetDescription = budgetData.description || ''
    // 实际数据的description
    const actualDescription = actualData.description || ''
    
    console.log('DEBUG: [Step2页面] 外包成本字段映射:', {
      serviceType: serviceType,
      budgetDescription: budgetDescription,
      actualDescription: actualDescription
    })
    
    return {
      id: index + 1, // 使用索引作为id
      service_type: serviceType,
      // 预算成本字段
      budget_description: budgetDescription,
      budget_amount: parseFloat(budgetData.total_price || 0),
      budget_amount_display: formatToFinancial(parseFloat(budgetData.total_price || 0)),
      // 实际成本字段
      actual_description: actualDescription,
      actual_amount: parseFloat(actualData.total_price || 0),
      actual_amount_display: formatToFinancial(parseFloat(actualData.total_price || 0)),
      // 其他字段
      remark: budgetData.remark || actualData.remark || ''
    }
  })
}

const processIndirectCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  console.log('DEBUG: [Step2页面] 原始间接成本数据:', data)
  
  // 按成本类型分组，然后区分预算和实际数据
  const groupedCosts: Record<string, { budget: any; actual: any }> = {}  
  
  data.forEach((cost: any) => {
    const costType = cost.cost_type || ''
    
    if (!groupedCosts[costType]) {
      groupedCosts[costType] = { budget: null, actual: null }
    }
    
    // 判断是预算还是实际数据
    const isBudget = cost.cost_type_flag === '预算' || cost.cost_type_flag === 'B' || cost.cost_type_flag === 0
    const isActual = cost.cost_type_flag === '实际' || cost.cost_type_flag === 'A' || cost.cost_type_flag === 1
    
    if (isBudget) {
      groupedCosts[costType].budget = cost
    } else if (isActual) {
      groupedCosts[costType].actual = cost
    }
  })
  
  console.log('DEBUG: [Step2页面] 按成本类型分组后的间接成本数据:', groupedCosts)
  
  // 将分组后的数据转换为前端期望的格式
  return Object.values(groupedCosts).map((group: any, index: number) => {
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
    console.log('DEBUG: [Step2页面] 间接成本详情:', {
      pairIndex: index,
      budget: {
        costId: budgetData.cost_id,
        costType: budgetData.cost_type,
        costTypeFlag: budgetData.cost_type_flag,
        description: budgetData.description,
        amount: budgetData.amount,
        totalPrice: budgetData.total_price
      },
      actual: {
        costId: actualData.cost_id,
        costType: actualData.cost_type,
        costTypeFlag: actualData.cost_type_flag,
        description: actualData.description,
        amount: actualData.amount,
        totalPrice: actualData.total_price
      }
    })
    
    // 成本类型：优先使用预算数据的，预算没有则使用实际的
    const costType = budgetData.cost_type || actualData.cost_type || ''
    
    // 服务内容：预算和实际分别使用各自的description字段
    const budgetDescription = budgetData.description || ''
    const actualDescription = actualData.description || ''
    
    // 金额：优先使用预算数据的amount字段，预算没有则使用实际的amount字段
    const budgetAmount = parseFloat(budgetData.amount || budgetData.total_price || 0)
    const actualAmount = parseFloat(actualData.amount || actualData.total_price || 0)
    
    console.log('DEBUG: [Step2页面] 间接成本字段映射:', {
      costType: costType,
      budgetDescription: budgetDescription,
      actualDescription: actualDescription,
      budgetAmount: budgetAmount,
      actualAmount: actualAmount
    })
    
    return {
      id: index + 1, // 使用索引作为id
      cost_type: costType,
      // 预算成本字段
      budget_description: budgetDescription,
      budget_amount: budgetAmount,
      budget_amount_display: formatToFinancial(budgetAmount),
      // 实际成本字段
      actual_description: actualDescription,
      actual_amount: actualAmount,
      actual_amount_display: formatToFinancial(actualAmount),
      // 其他字段
      remark: budgetData.remark || actualData.remark || ''
    }
  })
}

const processLaborCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  console.log('DEBUG: [Step2页面] 原始人力成本数据:', data)
  
  // 1. 确保数据为数组格式
  const laborData = Array.isArray(data) ? data : []
  
  console.log('DEBUG: [Step2页面] 处理后的人力成本数据长度:', laborData.length)
  
  // 2. 将数据转换为前端期望的格式
  return laborData.map((cost: any, index: number) => {
    console.log('DEBUG: [Step2页面] 人力成本详情:', {
      index: index,
      rawData: cost,
      personnelName: cost.personnel_name,
      department: cost.department,
      position: cost.position,
      hourlyRate: cost.hourly_rate,
      budgetHours: cost.budget_hours,
      budgetCost: cost.budget_cost,
      actualHours: cost.actual_hours,
      actualCost: cost.actual_cost
    })
    
    // 员工姓名：使用personnel_name字段
    const personnelName = cost.personnel_name || ''
    
    // 部门：使用department字段
    const department = cost.department || ''
    
    // 职位：使用position字段
    const position = cost.position || ''
    
    // 时薪：优先使用hourly_rate字段
    const hourlyRate = parseFloat(cost.hourly_rate || 0)
    
    // 预算工时：优先使用budget_hours字段
    const budgetHours = parseFloat(cost.budget_hours || 0)
    
    // 实际工时：优先使用actual_hours字段
    const actualHours = parseFloat(cost.actual_hours || 0)
    
    // 预算总成本：优先使用budget_cost字段，如果没有则计算
    const budgetTotal = parseFloat(cost.budget_cost || 0) || (budgetHours * hourlyRate)
    
    // 实际总成本：优先使用actual_cost字段，如果没有则计算
    const actualTotal = parseFloat(cost.actual_cost || 0) || (actualHours * hourlyRate)
    
    console.log('DEBUG: [Step2页面] 人力成本字段映射:', {
      personnelName: personnelName,
      department: department,
      position: position,
      hourlyRate: hourlyRate,
      budgetHours: budgetHours,
      actualHours: actualHours,
      budgetTotal: budgetTotal,
      actualTotal: actualTotal
    })
    
    return {
      id: index + 1, // 使用索引作为id
      personnel_name: personnelName,
      department: department,
      position: position,
      hourly_rate: hourlyRate,
      // 预算成本字段
      budget_hours: budgetHours,
      budget_cost: budgetTotal,
      // 实际成本字段
      actual_hours: actualHours,
      actual_cost: actualTotal,
      // 其他字段
      remark: cost.remark || ''
    }
  })
}

// 计算各类成本的统计数据
const materialBudgetTotal = computed(() => {
  return materialCosts.value.reduce((total, cost) => {
    return total + (Number(cost.budget_total) || 0)
  }, 0)
})

const materialActualTotal = computed(() => {
  return materialCosts.value.reduce((total, cost) => {
    return total + (Number(cost.actual_total) || 0)
  }, 0)
})

const materialCostVariance = computed(() => {
  return materialActualTotal.value - materialBudgetTotal.value
})

const outsourcingBudgetTotal = computed(() => {
  return outsourcingCosts.value.reduce((total, cost) => {
    return total + (Number(cost.budget_amount) || 0)
  }, 0)
})

const outsourcingActualTotal = computed(() => {
  return outsourcingCosts.value.reduce((total, cost) => {
    return total + (Number(cost.actual_amount) || 0)
  }, 0)
})

const outsourcingCostVariance = computed(() => {
  return outsourcingActualTotal.value - outsourcingBudgetTotal.value
})

const indirectBudgetTotal = computed(() => {
  return indirectCosts.value.reduce((total, cost) => {
    return total + (Number(cost.budget_amount) || 0)
  }, 0)
})

const indirectActualTotal = computed(() => {
  return indirectCosts.value.reduce((total, cost) => {
    return total + (Number(cost.actual_amount) || 0)
  }, 0)
})

const indirectCostVariance = computed(() => {
  return indirectActualTotal.value - indirectBudgetTotal.value
})

const laborBudgetTotal = computed(() => {
  return laborCosts.value.reduce((total, cost) => {
    return total + (Number(cost.budget_total) || 0)
  }, 0)
})

const laborActualTotal = computed(() => {
  return laborCosts.value.reduce((total, cost) => {
    return total + (Number(cost.actual_total) || 0)
  }, 0)
})

const laborCostVariance = computed(() => {
  return laborActualTotal.value - laborBudgetTotal.value
})

// 获取项目成本数据
const fetchProjectCosts = async () => {
  loading.value = true
  error.value = ''
  
  try {
    console.log('Step2 - 开始获取项目成本数据, 项目ID:', projectId.value)
    
    const response = await getProjectCosts(projectId.value)
    
    console.log('Step2 - API返回的原始数据:', response)
    
    // 初始化成本详情数据 - 注意API返回的字段名
    const data = response.data || response
    
    console.log('Step2 - 原始API数据结构:', data)
    
    // 使用新的数据处理函数处理各类成本数据
    materialCosts.value = processMaterialCosts(data.material_costs || [])
    outsourcingCosts.value = processOutsourcingCosts(data.outsourcing_costs || [])
    indirectCosts.value = processIndirectCosts(data.indirect_costs || [])
    laborCosts.value = processLaborCosts(data.labor_costs || [])
    
    console.log('Step2 - 处理后的成本数据:', {
      material: materialCosts.value.length,
      labor: laborCosts.value.length,
      outsourcing: outsourcingCosts.value.length,
      indirect: indirectCosts.value.length,
      sample_material: materialCosts.value[0] || null,
      sample_outsourcing: outsourcingCosts.value[0] || null,
      sample_indirect: indirectCosts.value[0] || null,
      sample_labor: laborCosts.value[0] || null
    })
    
    // 如果没有数据，显示提示信息
    if (materialCosts.value.length === 0 && 
        outsourcingCosts.value.length === 0 && 
        indirectCosts.value.length === 0 && 
        laborCosts.value.length === 0) {
      ElMessage.warning('暂无成本数据，请检查项目ID或数据是否正确')
    } else {
      ElMessage.success('成本数据加载成功')
    }
  } catch (err: any) {
    console.error('获取项目成本数据失败:', err)
    error.value = err.message || '获取项目成本数据失败'
    ElMessage.error('获取项目成本数据失败')
  } finally {
    loading.value = false
  }
}

// 跳转到上一步
const handlePrevious = () => {
  router.push({
    name: 'ProjectDetailBasic',
    params: { id: projectId.value }
  })
}

// 跳转到下一步
const handleNext = () => {
  router.push({
    name: 'ProjectDetailGantt',
    params: { id: projectId.value }
  })
}

// 返回项目列表
const goBack = () => {
  router.push('/projects')
}

// 初始化
onMounted(() => {
  fetchProjectCosts()
})
</script>

<style scoped>
.project-create-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.project-create-card {
  margin: 0 auto;
  max-width: 1600px;
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.cost-container {
  margin-top: 30px;
}

.cost-tabs {
  margin-bottom: 20px;
}

.cost-type-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.cost-table {
  margin-top: 10px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 40px;
  padding: 20px 0;
  border-top: 1px solid #e4e7ed;
  background-color: #fafafa;
}

:deep(.el-steps) {
  margin: 30px 0;
}

/* 修改非当前步骤的文字颜色为蓝色 */
:deep(.el-step__title) {
  color: #409EFF !important;
}

:deep(.el-step__description) {
  color: #409EFF !important;
}

/* 当前步骤使用默认颜色 */
:deep(.el-step.is-success .el-step__title),
:deep(.el-step.is-success .el-step__description),
:deep(.el-step.is-active .el-step__title),
:deep(.el-step.is-active .el-step__description) {
  color: inherit !important;
}

/* 成本统计样式 */
.cost-statistics {
  margin-bottom: 20px;
  background-color: #fafafa;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

/* 统计数字颜色样式 */
:deep(.statistic-orange .el-statistic__content) {
  color: #ff7d00;
  font-weight: bold;
}

:deep(.statistic-blue .el-statistic__content) {
  color: #1890ff;
  font-weight: bold;
}

:deep(.statistic-green .el-statistic__content) {
  color: #52c41a;
  font-weight: bold;
}

:deep(.statistic-red .el-statistic__content) {
  color: #ff4d4f;
  font-weight: bold;
}

/* 预算成本列样式 */
:deep(.el-table .budget-cell) {
  color: #0288d1 !important;
}

:deep(.el-table .budget-cell .el-input__inner) {
  color: #0288d1 !important;
}

:deep(.el-table .budget-header),
:deep(.el-table th.budget-header .cell) {
  color: #0288d1 !important;
  font-weight: bold !important;
}

/* 实际成本列样式 */
:deep(.el-table .actual-cell) {
  color: #388e3c !important;
}

:deep(.el-table .actual-cell .el-input__inner) {
  color: #388e3c !important;
}

:deep(.el-table .actual-header),
:deep(.el-table th.actual-header .cell) {
  color: #388e3c !important;
  font-weight: bold !important;
}

/* 表头居中 */
:deep(.el-table th .cell) {
  text-align: center;
}

/* 只读样式 */
:deep(.el-table .cell) {
  background-color: transparent;
  color: #606266;
}
</style>
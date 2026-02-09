<template>
  <div class="cost-api-test-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>成本数据测试 - 项目81（只读模式）</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>成本数据测试</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="1" align-center>
        <el-step title="基本信息" description="查看项目基本信息" />
        <el-step title="成本数据" description="显示四大成本的预算和实际值（只读）" />
        <el-step title="任务数据" description="显示项目任务信息" />
        <el-step title="文档数据" description="显示项目文档信息" />
      </el-steps>
      
      <div class="test-section">
        <el-button type="primary" @click="testCostAPI" :loading="loading">
          <el-icon><Refresh /></el-icon>
          重新加载成本数据
        </el-button>
        <el-button @click="clearResults">
          <el-icon><Delete /></el-icon>
          清空结果
        </el-button>
      </div>
      
      <div v-if="loading" class="loading">
        <el-icon class="is-loading"><Loading /></el-icon> 加载中...
      </div>
      
      <div v-if="error" class="error">
        <el-alert :title="error" type="error" :closable="false" />
      </div>
      
      <div v-if="processedData" class="results">
        <div class="cost-container">
          <!-- 成本类型选项卡 -->
          <el-tabs v-model="activeTab" type="card" class="cost-tabs">
            <!-- 物料成本 -->
            <el-tab-pane label="物料成本" name="material">
              <div class="cost-type-section">
                <div class="section-header">
                  <h3>物料成本管理（只读）</h3>
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
                      <span>{{ scope.row.material_name }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="specification" label="规格" min-width="160" :show-overflow-tooltip="false" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.specification }}</span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="unit" label="单位" width="80" min-width="80" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.unit }}</span>
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
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_quantity_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="150" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">单价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_unit_price_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">总价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_total_display }}</span>
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
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_quantity_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="150" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">单价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_unit_price_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">总价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_total_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <el-table-column prop="remark" label="备注" min-width="150" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.remark }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            
            <!-- 外包成本 -->
            <el-tab-pane label="外包成本" name="outsourcing">
              <div class="cost-type-section">
                <div class="section-header">
                  <h3>外包成本管理（只读）</h3>
                </div>
                
                <div class="cost-statistics">
                  <el-row :gutter="20" style="margin-bottom: 15px;">
                    <el-col :span="6">
                      <el-statistic 
                        title="外包预算合计" 
                        :value="outsourcingBudgetTotal" 
                        prefix="¥" 
                        :precision="2" 
                        style="color: #0288d1;"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="外包实际合计" 
                        :value="outsourcingActualTotal" 
                        prefix="¥" 
                        :precision="2" 
                        style="color: #388e3c;"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="外包偏差" 
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
                  <el-table-column prop="service_type" label="服务类型" min-width="180" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.service_type }}</span>
                    </template>
                  </el-table-column>
                  
                  <!-- 预算成本列 -->
                  <el-table-column align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">外包预算</div>
                    </template>
                    <el-table-column min-width="250" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">服务内容</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_description }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">金额</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_amount_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <!-- 实际成本列 -->
                  <el-table-column align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">外包实际</div>
                    </template>
                    <el-table-column min-width="250" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">服务内容</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_description }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">金额</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_amount_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <el-table-column prop="remark" label="备注" min-width="150" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.remark }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            
            <!-- 间接成本 -->
            <el-tab-pane label="间接成本" name="indirect">
              <div class="cost-type-section">
                <div class="section-header">
                  <h3>间接成本管理（只读）</h3>
                </div>
                
                <div class="cost-statistics">
                  <el-row :gutter="20" style="margin-bottom: 15px;">
                    <el-col :span="6">
                      <el-statistic 
                        title="间接预算合计" 
                        :value="indirectBudgetTotal" 
                        prefix="¥" 
                        :precision="2" 
                        style="color: #0288d1;"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="间接实际合计" 
                        :value="indirectActualTotal" 
                        prefix="¥" 
                        :precision="2" 
                        style="color: #388e3c;"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="间接偏差" 
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
                  <el-table-column prop="cost_type" label="成本类型" min-width="180" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.cost_type }}</span>
                    </template>
                  </el-table-column>
                  
                  <!-- 预算成本列 -->
                  <el-table-column align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">间接预算</div>
                    </template>
                    <el-table-column min-width="250" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">服务内容</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_description }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">金额</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_amount_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <!-- 实际成本列 -->
                  <el-table-column align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">间接实际</div>
                    </template>
                    <el-table-column min-width="250" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">服务内容</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_description }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">金额</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_amount_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <el-table-column prop="remark" label="备注" min-width="150" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.remark }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            
            <!-- 人力成本 -->
            <el-tab-pane label="人力成本" name="labor">
              <div class="cost-type-section">
                <div class="section-header">
                  <h3>人力成本管理（只读）</h3>
                </div>
                
                <div class="cost-statistics">
                  <el-row :gutter="20" style="margin-bottom: 15px;">
                    <el-col :span="6">
                      <el-statistic 
                        title="人力预算合计" 
                        :value="laborBudgetTotal" 
                        prefix="¥" 
                        :precision="2" 
                        style="color: #0288d1;"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="人力实际合计" 
                        :value="laborActualTotal" 
                        prefix="¥" 
                        :precision="2" 
                        style="color: #388e3c;"
                      />
                    </el-col>
                    <el-col :span="6">
                      <el-statistic 
                        title="人力偏差" 
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
                  <el-table-column prop="employee_name" label="人员姓名" min-width="150" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.employee_name }}</span>
                    </template>
                  </el-table-column>
                  
                  <!-- 预算成本列 -->
                  <el-table-column align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">人力预算</div>
                    </template>
                    <el-table-column min-width="120" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">工时</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_hours_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="120" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">单价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.hourly_rate_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #0288d1; font-weight: bold;">总价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #0288d1;">
                          <span>{{ scope.row.budget_cost_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <!-- 实际成本列 -->
                  <el-table-column align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">人力实际</div>
                    </template>
                    <el-table-column min-width="120" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">工时</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_hours_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="120" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">单价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.hourly_rate_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column min-width="160" align="center">
                      <template #header>
                        <div style="color: #388e3c; font-weight: bold;">总价</div>
                      </template>
                      <template #default="scope">
                        <div style="color: #388e3c;">
                          <span>{{ scope.row.actual_cost_display }}</span>
                        </div>
                      </template>
                    </el-table-column>
                  </el-table-column>
                  
                  <el-table-column prop="remark" label="备注" min-width="150" align="center">
                    <template #default="scope">
                      <span>{{ scope.row.remark }}</span>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
        
        <div class="raw-data">
          <h3>完整API响应数据</h3>
          <pre>{{ JSON.stringify(results, null, 2) }}</pre>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getProjectCosts } from '@/api/project'
import { 
  Refresh,
  Delete,
  Loading
} from '@element-plus/icons-vue'

// 财务格式化函数 - 从编辑场景复制
const formatToFinancial = (value: any): string => {
  if (value === null || value === undefined || value === '') return '0.00'
  const num = parseFloat(value)
  return isNaN(num) ? '0.00' : num.toFixed(2)
}

const loading = ref(false)
const error = ref('')
const results = ref<any>(null)
const processedData = ref<any>(null)
const activeTab = ref('material')

// 数据处理函数 - 从编辑场景Step2复制
const processMaterialCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  console.log('DEBUG: [测试页面] 原始物料成本数据:', data)
  
  // 按物料名称、规格、单位分组
  const groupedCosts: Record<string, any> = {}
  
  data.forEach((cost: any) => {
    console.log('DEBUG: [测试页面] 处理单条成本记录:', {
      name: cost.name,
      specification: cost.specification,
      unit: cost.unit,
      quantity: cost.quantity,
      unit_price: cost.unit_price,
      total_price: cost.total_price,
      cost_type: cost.cost_type
    })
    
    // 创建分组键：物料名称_规格_单位（使用编辑场景的字段名）
    const groupKey = `${cost.name || ''}_${cost.specification || ''}_${cost.unit || ''}`
    console.log('DEBUG: [测试页面] 生成的分组键:', groupKey)
    
    if (!groupedCosts[groupKey]) {
      groupedCosts[groupKey] = {
        name: cost.name || '',
        specification: cost.specification || '',
        unit: cost.unit || '',
        budget: null, // 预算数据
        actual: null  // 实际数据
      }
      console.log('DEBUG: [测试页面] 创建新分组:', groupedCosts[groupKey])
    } else {
      console.log('DEBUG: [测试页面] 使用现有分组:', groupedCosts[groupKey])
    }
    
    // 根据cost_type区分预算和实际数据（使用编辑场景的逻辑）
    if (cost.cost_type === '预算') {
      groupedCosts[groupKey].budget = cost
      console.log('DEBUG: [测试页面] 设置预算数据:', cost)
    } else if (cost.cost_type === '实际') {
      groupedCosts[groupKey].actual = cost
      console.log('DEBUG: [测试页面] 设置实际数据:', cost)
    }
  })
  
  console.log('DEBUG: [测试页面] 最终分组结果:', groupedCosts)
  
  // 将分组后的数据转换为前端期望的格式，合并预算和实际数据到一行
  return Object.values(groupedCosts).map((group: any, index: number) => {
    // 获取预算和实际数据
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
    console.log('DEBUG: [测试页面] 物料数据详情:', {
      groupKey: `${group.name}_${group.specification}_${group.unit}`,
      budgetData: budgetData,
      actualData: actualData
    })
    
    // 使用编辑场景中的字段名和逻辑
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
    
    console.log('DEBUG: [测试页面] 转换后物料数据:', {
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
  
  console.log('DEBUG: [测试页面] 原始外包成本数据:', data)
  
  // 1. 严格按照cost_id排序（照搬编辑场景逻辑）
  const sortedCosts = [...data].sort((a: any, b: any) => {
    return a.cost_id - b.cost_id
  })
  
  console.log('DEBUG: [测试页面] 按cost_id排序后的外包成本数据:', sortedCosts)
  
  // 2. 两两组队拼接数据，严格按照cost_id顺序配对
  const pairedOutsourcing: any[] = []
  
  // 遍历排序后的数据，两两组队
  for (let i = 0; i < sortedCosts.length; i += 2) {
    // 获取当前对的预算和实际数据
    const budgetCost = sortedCosts[i] || null
    const actualCost = sortedCosts[i + 1] || null
    
    console.log('DEBUG: [测试页面] 外包成本配对:', {
      index: i,
      budgetCost: budgetCost,
      actualCost: actualCost
    })
    
    // 确保至少有预算或实际数据
    if (budgetCost || actualCost) {
      pairedOutsourcing.push({
        budget: budgetCost,
        actual: actualCost
      })
    }
  }
  
  console.log('DEBUG: [测试页面] 两两组队后的外包成本数据:', pairedOutsourcing)
  
  // 3. 将配对后的数据转换为前端期望的格式
  return pairedOutsourcing.map((pair: any, index: number) => {
    const budgetData = pair.budget || {}
    const actualData = pair.actual || {}
    
    console.log('DEBUG: [测试页面] 外包成本详情:', {
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
    
    console.log('DEBUG: [测试页面] 外包成本字段映射:', {
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
  
  console.log('DEBUG: [测试页面] 原始间接成本数据:', data)
  console.log('DEBUG: [测试页面] 间接成本原始数据详情:', {
    dataLength: data.length,
    dataStructure: data.map((item: any) => ({
      cost_id: item.cost_id,
      cost_type: item.cost_type,
      amount: item.amount,
      description: item.description,
      descriptionType: typeof item.description,
      descriptionLength: item.description ? item.description.length : 0
    }))
  })
  
  // 1. 严格按照cost_id排序
  const sortedIndirect = [...data].sort((a: any, b: any) => {
    return a.cost_id - b.cost_id
  })
  
  console.log('DEBUG: [测试页面] 按cost_id排序后的间接成本数据:', sortedIndirect)
  
  // 2. 两两组队拼接数据，根据cost_type区分预算和实际（照搬编辑场景逻辑）
  const pairedIndirect: any[] = []
  
  // 遍历排序后的数据，两两组队
  for (let i = 0; i < sortedIndirect.length; i += 2) {
    // 获取当前两条记录，确保完整保留所有字段
    const firstCost = sortedIndirect[i] ? { ...sortedIndirect[i] } : null
    const secondCost = sortedIndirect[i + 1] ? { ...sortedIndirect[i + 1] } : null
    
    console.log('DEBUG: [测试页面] 间接成本配对:', {
      index: i,
      firstCost: firstCost,
      secondCost: secondCost
    })
    
    // 确定预算和实际数据
    let budgetCost = null
    let actualCost = null
    
    // 处理当前记录，确保完整保留所有字段
    if (firstCost) {
      if (firstCost.cost_type_flag === '预算' || firstCost.cost_type_flag === 'B') {
        budgetCost = firstCost
      } else {
        actualCost = firstCost
      }
    }
    
    // 处理下一条记录，确保完整保留所有字段
    if (secondCost) {
      if (secondCost.cost_type_flag === '预算' || secondCost.cost_type_flag === 'B') {
        budgetCost = secondCost
      } else {
        actualCost = secondCost
      }
    }
    
    console.log('DEBUG: [测试页面] 间接成本预算/实际分配:', {
      budgetCost: budgetCost,
      actualCost: actualCost
    })
    
    // 确保至少有预算或实际数据
    if (budgetCost || actualCost) {
      pairedIndirect.push({
        budget: budgetCost,
        actual: actualCost
      })
    }
  }
  
  console.log('DEBUG: [测试页面] 两两组队后的间接成本数据:', pairedIndirect)
  
  // 3. 将配对后的数据转换为前端期望的格式
  return pairedIndirect.map((pair: any, index: number) => {
    const budgetData = pair.budget || {}
    const actualData = pair.actual || {}
    
    console.log('DEBUG: [测试页面] 间接成本详情:', {
      pairIndex: index,
      budgetData: {
        costId: budgetData.cost_id,
        costType: budgetData.cost_type,
        description: budgetData.description,
        descriptionType: typeof budgetData.description,
        descriptionLength: budgetData.description ? budgetData.description.length : 0,
        amount: budgetData.amount
      },
      actualData: {
        costId: actualData.cost_id,
        costType: actualData.cost_type,
        description: actualData.description,
        descriptionType: typeof actualData.description,
        descriptionLength: actualData.description ? actualData.description.length : 0,
        amount: actualData.amount
      }
    })
    
    // 成本类型优先使用预算数据的，预算没有则使用实际的
    const costType = budgetData.cost_type || actualData.cost_type || ''
    
    // 照搬编辑场景的强匹配逻辑：从原始API响应中查找对应记录
    const originalBudgetRecord = data.find((cost: any) => cost.cost_id === budgetData.cost_id)
    const originalActualRecord = data.find((cost: any) => cost.cost_id === actualData.cost_id)
    
    // 从原始记录中获取description字段，确保强匹配
    const budgetDescription = originalBudgetRecord?.description || ''
    const actualDescription = originalActualRecord?.description || ''
    
    console.log('DEBUG: [测试页面] 间接成本description强匹配:', {
      pairIndex: index,
      budgetData: {
        costId: budgetData.cost_id,
        costType: budgetData.cost_type,
        amount: budgetData.amount,
        originalDescription: originalBudgetRecord?.description,
        originalDescriptionType: typeof originalBudgetRecord?.description,
        originalDescriptionLength: originalBudgetRecord?.description ? originalBudgetRecord.description.length : 0
      },
      actualData: {
        costId: actualData.cost_id,
        costType: actualData.cost_type,
        amount: actualData.amount,
        originalDescription: originalActualRecord?.description,
        originalDescriptionType: typeof originalActualRecord?.description,
        originalDescriptionLength: originalActualRecord?.description ? originalActualRecord.description.length : 0
      },
      mapped: {
        budgetDescription: budgetDescription,
        actualDescription: actualDescription,
        budgetDescriptionType: typeof budgetDescription,
        actualDescriptionType: typeof actualDescription
      }
    })
    
    console.log('DEBUG: [测试页面] 间接成本字段映射:', {
      costType: costType,
      budgetDescription: budgetDescription,
      actualDescription: actualDescription
    })
    
    console.log('DEBUG: [测试页面] 最终间接成本对象创建:', {
      id: index + 1,
      costType: costType,
      budgetDescription: budgetDescription,
      budgetAmount: budgetData.amount,
      budgetAmountParsed: parseFloat(budgetData.amount || 0),
      actualDescription: actualDescription,
      actualAmount: actualData.amount,
      actualAmountParsed: parseFloat(actualData.amount || 0),
      originalBudgetData: originalBudgetRecord,
      originalActualData: originalActualRecord
    })
    
    return {
      id: index + 1,
      cost_type: costType,
      // 预算成本字段
      budget_description: budgetDescription,
      budget_amount: parseFloat(budgetData.amount || 0),
      budget_amount_display: formatToFinancial(parseFloat(budgetData.amount || 0)),
      // 实际成本字段
      actual_description: actualDescription,
      actual_amount: parseFloat(actualData.amount || 0),
      actual_amount_display: formatToFinancial(parseFloat(actualData.amount || 0)),
      // 其他字段
      remark: budgetData.remark || actualData.remark || ''
    }
  })
}

const processLaborCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  return data.map((item: any) => ({
    employee_name: item.employee_name,
    hourly_rate: parseFloat(item.hourly_rate) || 0,
    hourly_rate_display: formatToFinancial(item.hourly_rate),
    budget_hours: parseFloat(item.budget_hours) || 0,
    budget_hours_display: formatToFinancial(item.budget_hours),
    budget_cost: parseFloat(item.budget_cost) || 0,
    budget_cost_display: formatToFinancial(item.budget_cost),
    actual_hours: parseFloat(item.actual_hours) || 0,
    actual_hours_display: formatToFinancial(item.actual_hours),
    actual_cost: parseFloat(item.actual_cost) || 0,
    actual_cost_display: formatToFinancial(item.actual_cost),
    remark: item.remark || ''
  }))
}

// 计算处理后的数据
const materialCosts = computed(() => {
  if (!processedData.value?.material_costs) return []
  return processMaterialCosts(processedData.value.material_costs)
})

const outsourcingCosts = computed(() => {
  if (!processedData.value?.outsourcing_costs) return []
  return processOutsourcingCosts(processedData.value.outsourcing_costs)
})

const indirectCosts = computed(() => {
  if (!processedData.value?.indirect_costs) return []
  return processIndirectCosts(processedData.value.indirect_costs)
})

const laborCosts = computed(() => {
  if (!processedData.value?.labor_costs) return []
  return processLaborCosts(processedData.value.labor_costs)
})

// 统计数据计算
const materialBudgetTotal = computed(() => {
  return materialCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.budget_total) || 0), 0)
})

const materialActualTotal = computed(() => {
  return materialCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.actual_total) || 0), 0)
})

const materialCostVariance = computed(() => {
  return materialActualTotal.value - materialBudgetTotal.value
})

const outsourcingBudgetTotal = computed(() => {
  return outsourcingCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.budget_amount) || 0), 0)
})

const outsourcingActualTotal = computed(() => {
  return outsourcingCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.actual_amount) || 0), 0)
})

const outsourcingCostVariance = computed(() => {
  return outsourcingActualTotal.value - outsourcingBudgetTotal.value
})

const indirectBudgetTotal = computed(() => {
  return indirectCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.budget_amount) || 0), 0)
})

const indirectActualTotal = computed(() => {
  return indirectCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.actual_amount) || 0), 0)
})

const indirectCostVariance = computed(() => {
  return indirectActualTotal.value - indirectBudgetTotal.value
})

const laborBudgetTotal = computed(() => {
  return laborCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.budget_cost) || 0), 0)
})

const laborActualTotal = computed(() => {
  return laborCosts.value.reduce((sum: number, item: any) => sum + (parseFloat(item.actual_cost) || 0), 0)
})

const laborCostVariance = computed(() => {
  return laborActualTotal.value - laborBudgetTotal.value
})

const testCostAPI = async () => {
  loading.value = true
  error.value = ''
  results.value = null
  processedData.value = null
  
  try {
    console.log('开始测试成本API数据加载...')
    
    // 使用项目ID 81进行测试
    const response = await getProjectCosts(81)
    
    console.log('API响应:', response)
    
    // 处理API响应结构
    const costData = response.data || response
    results.value = costData
    processedData.value = costData
    
    console.log('处理后的成本数据:', costData)
    console.log('API数据处理完成:', {
      material_costs: costData.material_costs?.length || 0,
      labor_costs: costData.labor_costs?.length || 0,
      outsourcing_costs: costData.outsourcing_costs?.length || 0,
      indirect_costs: costData.indirect_costs?.length || 0
    })
    
    if (!costData || Object.keys(costData).length === 0) {
      error.value = 'API返回数据为空'
      return
    }
    
    // 检查四大成本类型是否存在
    const costTypes = ['material_costs', 'labor_costs', 'outsourcing_costs', 'indirect_costs']
    const missingTypes = costTypes.filter(type => !costData[type] || costData[type].length === 0)
    
    if (missingTypes.length > 0) {
      console.warn('缺失的成本类型:', missingTypes)
    }
    
  } catch (err: any) {
    console.error('测试成本API失败:', err)
    error.value = err.message || '未知错误'
  } finally {
    loading.value = false
  }
}

const clearResults = () => {
  results.value = null
  processedData.value = null
  error.value = ''
}

// 导出所有响应式数据和方法
defineExpose({
  loading,
  error,
  results,
  processedData,
  activeTab,
  materialCosts,
  outsourcingCosts,
  indirectCosts,
  laborCosts,
  materialBudgetTotal,
  materialActualTotal,
  materialCostVariance,
  outsourcingBudgetTotal,
  outsourcingActualTotal,
  outsourcingCostVariance,
  indirectBudgetTotal,
  indirectActualTotal,
  indirectCostVariance,
  laborBudgetTotal,
  laborActualTotal,
  laborCostVariance,
  testCostAPI,
  clearResults
})
</script>

<style scoped>
.cost-api-test-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.loading {
  text-align: center;
  padding: 20px;
  font-size: 16px;
}

.error {
  margin-bottom: 20px;
}

.results {
  margin-top: 20px;
}

.summary {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  padding: 10px 0;
}

.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
}

.data-preview {
  margin-bottom: 30px;
}

.data-preview h4 {
  color: #409EFF;
  margin-top: 20px;
  margin-bottom: 10px;
}

.raw-data {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.raw-data h3 {
  margin-bottom: 15px;
  color: #303133;
}

pre {
  background-color: #fff;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.4;
}
</style>
<template>
  <div class="project-detail-container">
    <el-card shadow="hover" class="project-detail-card">
      <template #header>
        <div class="card-header">
          <h2>{{ formData.name }} - 详情</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
        <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
        <el-breadcrumb-item>{{ formData.name }}</el-breadcrumb-item>
        <el-breadcrumb-item>{{ getStepTitle(currentStep) }}</el-breadcrumb-item>
      </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="currentStep" align-center>
        <el-step 
          title="基本信息" 
          description="查看项目基本信息和合同信息" 
          @click="goToStep(0)"
          :class="{ 'clickable-step': true }"
        />
        <el-step 
          title="成本设定" 
          description="查看项目成本信息" 
          @click="goToStep(1)"
          :class="{ 'clickable-step': true }"
        />
        <el-step 
          title="任务设定" 
          description="查看项目任务" 
          @click="goToStep(2)"
          :class="{ 'clickable-step': true }"
        />
        <el-step 
          title="文档管理" 
          description="查看项目文档" 
          @click="goToStep(3)"
          :class="{ 'clickable-step': true }"
        />
      </el-steps>
      
      <div class="form-container">
        <!-- Step 1: 基本信息 -->
        <div v-show="currentStep === 0" class="step-content">
          <el-form
            ref="projectForm"
            :model="formData"
            label-width="120px"
            class="project-form"
          >
            <el-row :gutter="20">
              <el-col :span="12">
                <el-divider content-position="left">基本信息</el-divider>
                <el-form-item label="项目详情">
                  <el-input v-model="formData.describe" type="textarea" placeholder="项目详情信息" rows="3" :readonly="isReadOnly" />
                </el-form-item>
                
                <el-form-item label="项目名称">
                  <el-input v-model="formData.name" :readonly="isReadOnly" />
                </el-form-item>
                
                <el-form-item label="项目状态">
                  <el-select v-model="formData.status" :disabled="isReadOnly">
                    <el-option label="规划中" value="规划中" />
                    <el-option label="进行中" value="进行中" />
                    <el-option label="提前完成" value="提前完成" />
                    <el-option label="已完成" value="已完成" />
                    <el-option label="延期完成" value="延期完成" />
                    <el-option label="已延期" value="已延期" />
                    <el-option label="已暂停" value="已暂停" />
                    <el-option label="已取消" value="已取消" />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="项目经理">
                  <el-select v-model="formData.leader" :disabled="isReadOnly">
                    <el-option
                      v-for="personnel in personnelList"
                      :key="personnel.id"
                      :label="personnel.name"
                      :value="personnel.name"
                    />
                  </el-select>
                </el-form-item>
                
                <el-form-item label="开始日期">
                  <el-date-picker
                    v-model="formData.start_date"
                    type="date"
                    style="width: 100%;"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
                
                <el-form-item label="计划结束日期">
                  <el-date-picker
                    v-model="formData.end_date"
                    type="date"
                    style="width: 100%;"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
              
              <el-col :span="12">
                <el-divider content-position="left">合同信息</el-divider>
                
                <el-form-item label="合同编号">
                  <el-input v-model="formData.contract_no" :readonly="isReadOnly" />
                </el-form-item>
                
                <el-form-item label="合同签订日期">
                  <el-date-picker
                    v-model="formData.contract_date"
                    type="date"
                    style="width: 100%;"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
                
                <el-form-item label="合同金额">
                  <el-input 
                    v-model="displayData.contract_amount" 
                    :readonly="isReadOnly"
                  >
                    <template #prepend>¥</template>
                  </el-input>
                </el-form-item>
                
                <el-form-item label="税率">
                  <el-input 
                    v-model="formData.tax_rate" 
                    :readonly="isReadOnly"
                  />
                </el-form-item>
                
                <el-form-item label="营业收入">
                  <el-input 
                    v-model="displayData.revenue" 
                    :readonly="isReadOnly"
                  >
                    <template #prepend>¥</template>
                  </el-input>
                </el-form-item>
                
                <el-form-item label="目标利润">
                  <el-input 
                    v-model="displayData.target_profit" 
                    :readonly="isReadOnly"
                  >
                    <template #prepend>¥</template>
                  </el-input>
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </div>
        
        <!-- Step 2: 成本设定 -->
        <div v-show="currentStep === 1" class="step-content">
          <div class="cost-container">
            <!-- 成本类型选项卡 -->
            <el-tabs v-model="activeCostTab" type="card" class="cost-tabs">
              <!-- 物料成本 -->
              <el-tab-pane label="物料成本" name="material">
                <div class="cost-type-section">
                  <div class="section-header">
                    <h3>物料成本详情</h3>
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
                        <span>{{ scope.row.material_name || '-' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="specification" label="规格" min-width="160" :show-overflow-tooltip="false" align="center">
                      <template #default="scope">
                        <span>{{ scope.row.specification || '-' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="unit" label="单位" width="80" min-width="80" align="center">
                      <template #default="scope">
                        <span>{{ scope.row.unit || '-' }}</span>
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
                            <span>{{ scope.row.budget_quantity_display || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="150" align="center">
                        <template #header>
                          <div style="color: #0288d1; font-weight: bold;">单价</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #0288d1;">
                            <span v-if="scope.row.budget_unit_price_display">¥ {{ scope.row.budget_unit_price_display }}</span>
                            <span v-else>-</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="160" align="center">
                        <template #header>
                          <div style="color: #0288d1; font-weight: bold;">总价</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #0288d1;">
                            <span v-if="scope.row.budget_total_display">¥ {{ scope.row.budget_total_display }}</span>
                            <span v-else>-</span>
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
                            <span>{{ scope.row.actual_quantity_display || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="150" align="center">
                        <template #header>
                          <div style="color: #388e3c; font-weight: bold;">单价</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #388e3c;">
                            <span v-if="scope.row.actual_unit_price_display">¥ {{ scope.row.actual_unit_price_display }}</span>
                            <span v-else>-</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="160" align="center">
                        <template #header>
                          <div style="color: #388e3c; font-weight: bold;">总价</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #388e3c;">
                            <span v-if="scope.row.actual_total_display">¥ {{ scope.row.actual_total_display }}</span>
                            <span v-else>-</span>
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
                    <h3>外包成本详情</h3>
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
                        <span>{{ scope.row.service_type || '-' }}</span>
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
                          <div style="color: #0288d1;">
                            <span>{{ scope.row.budget_description || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="150" align="center">
                        <template #header>
                          <div style="color: #0288d1; font-weight: bold;">金额</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #0288d1;">
                            <span v-if="scope.row.budget_amount_display">¥ {{ scope.row.budget_amount_display }}</span>
                            <span v-else>-</span>
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
                          <div style="color: #388e3c;">
                            <span>{{ scope.row.actual_description || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="150" align="center">
                        <template #header>
                          <div style="color: #388e3c; font-weight: bold;">金额</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #388e3c;">
                            <span v-if="scope.row.actual_amount_display">¥ {{ scope.row.actual_amount_display }}</span>
                            <span v-else>-</span>
                          </div>
                        </template>
                      </el-table-column>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
              
              <!-- 间接成本 -->
              <el-tab-pane label="间接成本" name="indirect">
                <div class="cost-type-section">
                  <div class="section-header">
                    <h3>间接成本详情</h3>
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
                        <span>{{ scope.row.cost_type || '-' }}</span>
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
                          <div style="color: #0288d1;">
                            <span>{{ scope.row.budget_description || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="150" align="center">
                        <template #header>
                          <div style="color: #0288d1; font-weight: bold;">金额</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #0288d1;">
                            <span v-if="scope.row.budget_amount_display">¥ {{ scope.row.budget_amount_display }}</span>
                            <span v-else>-</span>
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
                          <div style="color: #388e3c;">
                            <span>{{ scope.row.actual_description || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="150" align="center">
                        <template #header>
                          <div style="color: #388e3c; font-weight: bold;">金额</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #388e3c;">
                            <span v-if="scope.row.actual_amount_display">¥ {{ scope.row.actual_amount_display }}</span>
                            <span v-else>-</span>
                          </div>
                        </template>
                      </el-table-column>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
              
              <!-- 人力成本 -->
              <el-tab-pane label="人力成本" name="labor">
                <div class="cost-type-section">
                  <div class="section-header">
                    <h3>人力成本详情</h3>
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
                        <span>{{ scope.row.personnel_name || '-' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="department" label="部门" min-width="120" align="center">
                      <template #default="scope">
                        <span>{{ scope.row.department || '-' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="position" label="职位" min-width="120" align="center">
                      <template #default="scope">
                        <span>{{ scope.row.position || '-' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column prop="hourly_rate" label="每小时费用" min-width="120" align="center">
                      <template #default="scope">
                        <div style="color: #000;">
                          <span v-if="scope.row.budget_hourly_rate_display">¥ {{ scope.row.budget_hourly_rate_display }}</span>
                          <span v-else>-</span>
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
                          <div style="color: #0288d1;">
                            <span>{{ scope.row.budget_hours_display || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="120" align="center">
                        <template #header>
                          <div style="color: #0288d1; font-weight: bold;">总价</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #0288d1;">
                            <span v-if="scope.row.budget_total_display">¥ {{ scope.row.budget_total_display }}</span>
                            <span v-else>-</span>
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
                          <div style="color: #388e3c;">
                            <span>{{ scope.row.actual_hours_display || '-' }}</span>
                          </div>
                        </template>
                      </el-table-column>
                      <el-table-column min-width="120" align="center">
                        <template #header>
                          <div style="color: #388e3c; font-weight: bold;">总价</div>
                        </template>
                        <template #default="scope">
                          <div style="color: #388e3c;">
                            <span v-if="scope.row.actual_total_display">¥ {{ scope.row.actual_total_display }}</span>
                            <span v-else>-</span>
                          </div>
                        </template>
                      </el-table-column>
                    </el-table-column>
                  </el-table>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
        </div>
        
        <!-- Step 3: 任务设定 -->
        <div v-show="currentStep === 2" class="step-content">
          <div class="gantt-container">
            <!-- 任务管理标题和操作 -->
            <div class="panel-header">
              <h3>任务管理</h3>
              <div class="panel-actions">
                <el-button type="info" @click="openGanttDialog">
                  <el-icon><DataAnalysis /></el-icon>
                  甘特图展示
                </el-button>
              </div>
            </div>
            
            <!-- 任务管理和甘特图合并表格 -->
            <!-- 使用Element Plus的树形表格功能，通过tree-props配置 -->
            <el-table 
              :data="treeTasks" 
              border 
              fit
              style="width: 100%" 
              class="task-gantt-table"
              :key="treeDataKey"
              row-key="task_id"
              v-loading="taskLoading"
              element-loading-text="加载中..."
              element-loading-spinner="el-icon-loading"
              element-loading-background="rgba(255, 255, 255, 0.8)"
            >
              <!-- 序号列（第一列） -->
              <el-table-column label="序号" width="100">
                <template #default="scope">
                  {{ scope.row.task_id.replace(`${projectId}_`, '') }}
                </template>
              </el-table-column>
              <!-- 任务名称列（第二列自动显示缩进和展开/折叠图标） -->
              <el-table-column prop="task_name" label="任务名称" min-width="160" show-overflow-tooltip :tree-props="{ children: 'children', hasChildren: 'hasChildren' }" />
              <el-table-column label="状态" width="120">
                <template #default="scope">
                  <el-tag :type="getTaskProgressStatusType(getTaskProgressStatus(scope.row))">
                    {{ getTaskProgressStatus(scope.row) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="assignee" label="资源分配" min-width="90" show-overflow-tooltip />
              <el-table-column label="开始日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.start_date) }}
                </template>
              </el-table-column>
              <el-table-column label="计划结束日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.end_date) }}
                </template>
              </el-table-column>
              <el-table-column label="实际结束日期" width="120">
                <template #default="scope">
                  {{ formatDate(scope.row.actual_end_date) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button type="primary" size="small" @click="showTaskDetail(scope.row)">
                    <el-icon><View /></el-icon>
                    详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
        
        <!-- 甘特图展示对话框 -->
        <el-dialog
          v-model="ganttDialogVisible"
          title="甘特图展示"
          width="90%"
          fullscreen
        >
          <div class="gantt-dialog-content">
            <!-- 甘特图内容将在这里展示 -->
            <div class="gantt-table-container">
              <!-- 使用新的甘特图组件 -->
              <gantt-chart :tasks="treeTasks" />
            </div>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="ganttDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>
        
        <!-- 任务明细对话框 -->
        <el-dialog
          v-model="taskDetailDialogVisible"
          :title="taskDetailDialogTitle"
          width="800px"
        >
          <el-form ref="taskForm" :model="taskFormData" label-width="120px" :rules="taskRules">
            <!-- 第一部分：基本信息组 -->
            <el-divider content-position="left">基本信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="任务名称" prop="task_name">
                  <el-input v-model="taskFormData.task_name" placeholder="请输入任务名称" :disabled="isReadOnly" />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="8">
                <el-form-item label="当前状态" prop="status">
                  <el-select v-model="taskFormData.status" placeholder="请选择状态" disabled>
                    <el-option label="未开始" value="未开始" />
                    <el-option label="进行中" value="进行中" />
                    <el-option label="已完成" value="已完成" />
                    <el-option label="已暂停" value="已暂停" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="资源分配" prop="assignee">
                  <el-select 
                    v-model="taskFormData.assignee" 
                    placeholder="请选择人员（可多选）"
                    multiple
                    collapse-tags
                    :disabled="isReadOnly"
                  >
                    <el-option
                      v-for="personnel in personnelList"
                      :key="personnel.id"
                      :label="personnel.name"
                      :value="personnel.name"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="实际结束日期" prop="actual_end_date">
                  <el-date-picker
                    v-model="taskFormData.actual_end_date"
                    type="date"
                    placeholder="选择实际结束日期"
                    style="width: 100%;"
                    disabled
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="开始日期" prop="start_date">
                  <el-date-picker
                    v-model="taskFormData.start_date"
                    type="date"
                    placeholder="选择开始日期"
                    style="width: 100%;"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="计划结束日期" prop="end_date">
                  <el-date-picker
                    v-model="taskFormData.end_date"
                    type="date"
                    placeholder="选择计划结束日期"
                    style="width: 100%;"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 第二部分：进度信息组 -->
            <el-divider content-position="left">进度信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="计划工时（小时）" prop="planned_hours">
                  <el-input v-model="taskFormData.planned_hours" placeholder="自动计算" readonly />
                </el-form-item>
              </el-col>
              <el-col :span="12">
                <el-form-item label="实际工时（小时）" prop="actual_hours">
                  <el-input v-model="taskFormData.actual_hours" placeholder="自动计算" readonly />
                </el-form-item>
              </el-col>
            </el-row>
            
            <!-- 第三部分：说明信息组 -->
            <el-divider content-position="left">说明信息</el-divider>
            <el-row :gutter="20">
              <el-col :span="12">
                <el-form-item label="考评" prop="evaluation">
                  <el-input 
                    v-model="taskFormData.evaluation" 
                    placeholder="请输入考评分数"
                    type="number"
                    :step="0.1"
                    :min="0"
                    :max="100"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="考评说明" prop="evaluation_desc">
                  <el-input 
                    v-model="taskFormData.evaluation_desc" 
                    placeholder="请输入考评说明"
                    type="textarea"
                    :rows="2"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="进展/根因" prop="progress_rootcause">
                  <el-input 
                    v-model="taskFormData.progress_rootcause" 
                    placeholder="请输入进展/根因"
                    type="textarea"
                    :rows="2"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="措施/结果" prop="measures_results">
                  <el-input 
                    v-model="taskFormData.measures_results" 
                    placeholder="请输入措施/结果"
                    type="textarea"
                    :rows="2"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            
            <el-row :gutter="20">
              <el-col :span="24">
                <el-form-item label="备注" prop="remark">
                  <el-input 
                    v-model="taskFormData.remark" 
                    placeholder="请输入备注"
                    type="textarea"
                    :rows="2"
                    :disabled="isReadOnly"
                  />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="taskDetailDialogVisible = false">关闭</el-button>
            </span>
          </template>
        </el-dialog>
        
        <!-- Step 4: 文档管理 -->
        <div v-show="currentStep === 3" class="step-content">
          <el-row :gutter="20">
            <el-col :span="24">
              <div class="document-container">
                <!-- 任务选择和文档列表区域 -->
                <div class="main-content">
                  <div class="left-panel">
                    <div class="panel-header">
                      <h3>任务列表</h3>
                      <el-input
                        v-model="taskFilter"
                        placeholder="搜索任务"
                        prefix-icon="Search"
                        style="width: 180px;"
                        :disabled="isReadOnly"
                      />
                    </div>
                    
                    <el-tree
                      :data="filteredTasks"
                      :props="taskTreeProps"
                      node-key="task_id"
                      highlight-current
                      default-expand-all
                      class="task-tree"
                      @node-click="handleTaskClick"
                    />
                  </div>
                  
                  <div class="right-panel">
                    <div class="panel-header">
                      <h3>文档管理<span v-if="selectedTaskName"> - {{ selectedTaskName }}</span></h3>
                    </div>
                    
                    <!-- 文档列表 -->
                    <div class="document-list">
                      <el-table :data="currentDocuments" border style="width: 100%" class="document-table">
                        <el-table-column prop="file_name" label="文档名称" min-width="300" />
                        <el-table-column prop="file_type" label="文件类型" width="120">
                          <template #default="scope">
                            <el-tag :type="getFileColorByType(scope.row.file_type)">
                              {{ getFileTypeText(scope.row.file_type) }}
                            </el-tag>
                          </template>
                        </el-table-column>
                        <el-table-column prop="file_size" label="文件大小" width="120">
                          <template #default="scope">
                            {{ formatFileSize(scope.row.file_size) }}
                          </template>
                        </el-table-column>
                        <el-table-column prop="uploader_name" label="上传人" width="120" />
                        <el-table-column label="操作" width="100">
                          <template #default="scope">
                            <el-button type="primary" size="small" @click="downloadDocument(scope.row)">
                              <el-icon><Download /></el-icon>
                              下载
                            </el-button>
                          </template>
                        </el-table-column>
                      </el-table>
                    </div>
                    
                    <!-- 文档上传区域 - 仅在非只读模式下显示 -->
                    <el-upload
                      v-if="!isReadOnly"
                      ref="upload"
                      action="#"
                      :auto-upload="true"
                      :multiple="true"
                      :http-request="handleUpload"
                      :show-file-list="false"
                      class="document-upload"
                      :disabled="isReadOnly"
                    >
                      <el-button type="primary" :disabled="isReadOnly">
                        <el-icon><Plus /></el-icon>
                        文件上传
                      </el-button>
                      <div slot="tip" class="el-upload__tip">
                        支持上传 PDF、Word、Excel、PPT、图片等格式文件
                      </div>
                    </el-upload>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>

        <!-- 文档预览对话框 -->
        <el-dialog
          v-model="previewDialogVisible"
          :title="previewDocumentTitle"
          width="800px"
          fullscreen
        >
          <div class="document-preview">
            <div class="preview-content">
              <!-- 这里应该根据文件类型显示不同的预览内容 -->
              <div v-if="previewDocumentType === 'image'" class="image-preview">
                <el-image
                  :src="previewDocumentUrl"
                  fit="contain"
                  style="width: 100%; height: 100%;"
                />
              </div>
              <div v-else-if="previewDocumentType === 'pdf'" class="pdf-preview">
                <iframe
                  :src="previewDocumentUrl"
                  style="width: 100%; height: 600px; border: none;"
                />
              </div>
              <div v-else class="other-preview">
                <el-alert
                  title="该文件类型暂不支持在线预览，请下载后查看"
                  type="info"
                  show-icon
                />
                <el-button type="primary" style="margin-top: 20px;" @click="downloadDocument(previewDocumentData)">
                  <el-icon><Download /></el-icon>
                  下载文件
                </el-button>
              </div>
            </div>
          </div>
        </el-dialog>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="handleBackToList">返回列表</el-button>
          <div class="step-buttons">
            <el-button v-if="currentStep > 0" @click="handlePrevious">上一步</el-button>
            <el-button v-if="currentStep < 3" type="primary" @click="handleNext" style="margin-left: 10px;">下一步</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Download, DataAnalysis, Delete, Plus, View } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import GanttChart from '@/components/GanttChart.vue'
import {
  getProjectDetail,
  getProjectTasks,
  getProjectCosts,
  getProjectDocuments,
  getProjectTaskAttachments,
  type Project,
  type Task,
  type ProjectCosts
} from '../../api/project'

const router = useRouter()
const route = useRoute()

// 项目ID - 从路由参数获取（响应式计算属性）
const projectId = computed(() => {
  const id = route.params.id
  if (id) {
    const parsed = Number(id)
    return isNaN(parsed) ? 0 : parsed
  }
  return 0
})

// 获取项目ID（兼容性函数）
const getProjectId = () => {
  return projectId.value
}

// 根据路由参数确定当前步骤
const getStepFromRoute = (stepParam?: string): number => {
  console.log(`[DEBUG] getStepFromRoute - 输入参数: ${stepParam}`)
  if (!stepParam) {
    console.log(`[DEBUG] getStepFromRoute - 无参数，返回0`)
    return 0
  }
  const stepMap: { [key: string]: number } = {
    'basic': 0,
    'cost': 1,
    'gantt': 2,
    'documents': 3
  }
  const result = stepMap[stepParam] ?? 0
  console.log(`[DEBUG] getStepFromRoute - ${stepParam} 映射到 ${result}`)
  return result
}

// 定义只读模式
const isReadOnly = ref(true)

// 从路径中解析步骤信息
const getStepFromPath = (): number => {
  const path = route.path
  console.log(`[DEBUG] getStepFromPath - 当前路径: ${path}`)
  
  // 从路径中提取step部分
  const pathSegments = path.split('/')
  const stepSegment = pathSegments[pathSegments.length - 1]
  console.log(`[DEBUG] getStepFromPath - 路径段: ${stepSegment}`)
  
  return getStepFromRoute(stepSegment)
}

// 当前步骤 - 从路由路径获取
const getCurrentStep = () => {
  console.log(`[DEBUG] 初始化 currentStep - route.params:`, route.params, 'route.path:', route.path)
  const step = getStepFromPath()
  console.log(`[DEBUG] getCurrentStep - 计算结果: ${step}`)
  return step
}

const currentStep = ref(getCurrentStep())

// 统一监听路由变化，更新当前步骤
watch(() => {
  const currentId = route.params.id
  const currentPath = route.path
  return { id: currentId, path: currentPath }
}, (newRoute, oldRoute) => {
  console.log(`[DEBUG] 路由变化 - 新参数:`, newRoute, '旧参数:', oldRoute)
  
  // 第一次调用时oldRoute可能为undefined
  if (!oldRoute) {
    console.log(`[DEBUG] 第一次调用，跳过比较`)
    const stepValue = getStepFromPath()
    console.log(`[DEBUG] 从路径解析步骤: ${stepValue}`)
    currentStep.value = stepValue
    console.log(`[DEBUG] currentStep 更新为: ${currentStep.value}`)
    return
  }
  
  // 如果项目ID或路径发生变化，更新步骤
  if (newRoute.path !== oldRoute.path || newRoute.id !== oldRoute.id) {
    const stepValue = getStepFromPath()
    console.log(`[DEBUG] 从路径解析步骤: ${stepValue}`)
    currentStep.value = stepValue
    console.log(`[DEBUG] currentStep 更新为: ${currentStep.value}`)
  }
}, { immediate: true })

// 加载状态变量定义
const loading = ref(false)
const taskLoading = ref(false)
const documentLoading = ref(false)

// 成本详情数据变量定义
const materialCosts = ref<any[]>([])
const outsourcingCosts = ref<any[]>([])
const laborCosts = ref<any[]>([])
const indirectCosts = ref<any[]>([])

// 表单数据
const formData = ref({
  id: null as number | null,
  name: '',
  describe: '',
  status: '',
  leader: '',
  start_date: null as Date | null,
  end_date: null as Date | null,
  // 合同信息
  contract_no: '',
  contract_date: null as Date | null,
  contract_amount: 0,
  tax_rate: 0,
  revenue: 0,
  target_profit: 0
})

// 显示数据（用于格式化显示）
const displayData = ref({
  contract_amount: '0',
  revenue: '0',
  target_profit: '0'
})

// 项目任务列表
const tasks = ref<Task[]>([])

// 树形结构的任务列表，用于展开/折叠功能
const treeTasks = computed(() => {
  // 创建任务ID到任务对象的映射
  const taskMap = new Map<string, any>()
  const rootTasks: any[] = []
  
  // 首先将所有任务放入映射中，确保每个任务都有children数组
  tasks.value.forEach(task => {
    const taskWithChildren = {
      ...task,
      children: [] as any[],
      hasChildren: false
    }
    // 检查任务是否有子任务
    taskWithChildren.hasChildren = tasks.value.some(t => t.parent_task_id === task.task_id)
    taskMap.set(task.task_id, taskWithChildren)
  })
  
  // 然后构建树形结构
  tasks.value.forEach(task => {
    if (task.parent_task_id && taskMap.has(task.parent_task_id)) {
      // 如果有父任务，将其添加到父任务的children数组中
      const parentTask = taskMap.get(task.parent_task_id)
      const childTask = taskMap.get(task.task_id)
      parentTask.children.push(childTask)
      // 确保父任务的hasChildren属性为true
      parentTask.hasChildren = true
    } else {
      // 没有父任务的是根任务
      rootTasks.push(taskMap.get(task.task_id))
    }
  })
  
  return rootTasks
})

// 用于触发表格重新渲染的key
const treeDataKey = ref(0)

// 任务明细对话框
const taskDetailDialogVisible = ref(false)
const taskDetailDialogTitle = ref('任务明细')
const taskForm = ref()

// 任务表单数据
const taskFormData = ref({
  task_id: '',
  project_id: '',
  task_name: '',
  parent_task_id: '',
  task_level: 1,
  assignee: [] as string[],
  assignee_id: '',
  start_date: '',
  end_date: '',
  actual_end_date: null,
  status: '未开始',
  progress: 0,
  planned_hours: 0,
  actual_hours: 0,
  evaluation: '',
  evaluation_desc: '',
  progress_rootcause: '',
  measures_results: '',
  remark: '',
  leaf_node: 1,
  hasChildren: false,
  created_by: 'current_user'
})

// 任务验证规则
const taskRules = ref({
  task_name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  assignee: [{ required: true, message: '请选择资源分配', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'blur' }],
  end_date: [{ required: true, message: '请选择计划结束日期', trigger: 'blur' }]
})

// 打开甘特图对话框
const openGanttDialog = () => {
  ganttDialogVisible.value = true
}

// 显示任务明细
const showTaskDetail = (row: any) => {
  taskDetailDialogTitle.value = '任务明细'
  // 转换assignee为数组格式
  const assigneeArray = row.assignee ? 
    (typeof row.assignee === 'string' ? row.assignee.split(',') : row.assignee) : []
  
  taskFormData.value = {
    ...row,
    assignee: assigneeArray as string[],
    hasChildren: row.hasChildren || false
  }
  taskDetailDialogVisible.value = true
}

// 项目成本汇总
const projectCost = ref({
  project_id: 0,
  material_cost: 0,
  labor_cost: 0,
  outsourcing_cost: 0,
  indirect_cost: 0,
  total_cost: 0
})

// 项目文档列表
const documents = ref<any[]>([])

// 获取项目详情
const fetchProjectDetails = async () => {
  if (!projectId.value) return
  try {
    loading.value = true
    const response = await getProjectDetail(projectId.value)
    formData.value = response
  } catch (error) {
    console.error('获取项目详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 获取项目任务列表
const fetchProjectTasks = async () => {
  if (!projectId.value) return
  try {
    taskLoading.value = true
    const response = await getProjectTasks(projectId.value)
    console.log('[DEBUG] 原始任务数据:', response)
    // 检查response是否包含data字段（处理SuccessResponse包装）
    const tasksData = response.data || response
    console.log('[DEBUG] 处理后的任务数据:', tasksData)
    // 直接将响应数据赋值给tasks，因为后端返回的格式已经是前端需要的
    tasks.value = Array.isArray(tasksData) ? tasksData : []
    console.log('[DEBUG] 最终任务数据:', tasks.value)
    // 更新treeDataKey，触发表格重新渲染
    treeDataKey.value++
  } catch (error) {
    console.error('获取项目任务列表失败:', error)
    tasks.value = []
  } finally {
    taskLoading.value = false
  }
}

// 获取项目成本汇总
const fetchProjectCosts = async () => {
  console.log('[DEBUG] fetchProjectCosts 开始执行')
  if (!projectId.value) {
    console.log('[DEBUG] fetchProjectCosts: 项目ID为空，返回')
    return
  }
  
  console.log(`[DEBUG] fetchProjectCosts: 项目ID为 ${projectId.value}`)
  
  try {
    console.log('[DEBUG] fetchProjectCosts: 开始调用getProjectCosts API')
    const response = await getProjectCosts(projectId.value)
    
    console.log('[DEBUG] fetchProjectCosts: API调用成功，响应:', response)
    
    // 处理API响应结构：{code: 200, message: "成功", data: {...}}
    const costData = response.data || response
    
    console.log('[DEBUG] 原始成本数据:', costData)
    
    // 初始化成本详情数据（从data对象中获取），并使用处理函数格式化
    materialCosts.value = processMaterialCosts(costData.material_costs || [])
    outsourcingCosts.value = processOutsourcingCosts(costData.outsourcing_costs || [])
    laborCosts.value = processLaborCosts(costData.labor_costs || [])
    indirectCosts.value = processIndirectCosts(costData.indirect_costs || [])
    
    console.log('[DEBUG] 处理后物料成本:', materialCosts.value)
    console.log('[DEBUG] 处理后外包成本:', outsourcingCosts.value)
    console.log('[DEBUG] 处理后人力成本:', laborCosts.value)
    console.log('[DEBUG] 处理后间接成本:', indirectCosts.value)
    
    // 计算成本汇总数据
    const materialTotal = materialCosts.value.reduce((sum, item) => sum + (item.budget_total || 0) + (item.actual_total || 0), 0)
    const laborTotal = laborCosts.value.reduce((sum, item) => sum + (item.budget_total || 0) + (item.actual_total || 0), 0)
    const outsourcingTotal = outsourcingCosts.value.reduce((sum, item) => sum + (item.budget_amount || 0) + (item.actual_amount || 0), 0)
    const indirectTotal = indirectCosts.value.reduce((sum, item) => sum + (item.budget_amount || 0) + (item.actual_amount || 0), 0)
    
    projectCost.value = {
      project_id: projectId.value,
      material_cost: materialTotal,
      labor_cost: laborTotal,
      outsourcing_cost: outsourcingTotal,
      indirect_cost: indirectTotal,
      total_cost: materialTotal + laborTotal + outsourcingTotal + indirectTotal
    }
    
    console.log('[DEBUG] 成本数据加载完成:', projectCost.value)
  } catch (error) {
    console.error('获取项目成本汇总失败:', error)
    // 失败时设置默认值，避免页面崩溃
    projectCost.value = {
      project_id: projectId.value,
      material_cost: 0,
      labor_cost: 0,
      outsourcing_cost: 0,
      indirect_cost: 0,
      total_cost: 0
    }
    materialCosts.value = []
    outsourcingCosts.value = []
    laborCosts.value = []
    indirectCosts.value = []
  }
}

// 获取项目文档列表
const fetchProjectDocuments = async () => {
  if (!projectId.value) return
  try {
    documentLoading.value = true
    // 调用API获取项目文档
    const response = await getProjectDocuments(projectId.value)
    documents.value = response || []
    console.log(`[DEBUG] 文档数据加载完成，共 ${documents.value.length} 个文档`)
  } catch (error) {
    console.error('获取项目文档列表失败:', error)
    // 即使获取失败，也不显示demo数据
    documents.value = []
  } finally {
    documentLoading.value = false
  }
}

// 监听项目ID变化，重新加载数据
watch(projectId, async (newProjectId, oldProjectId) => {
  if (newProjectId && newProjectId !== oldProjectId) {
    console.log(`[DEBUG] 项目ID变化: ${oldProjectId} -> ${newProjectId}`)
    // 重新加载基本信息（总是需要）
    await fetchProjectDetails()
    initDisplayData()
    // 总是加载成本数据，无论当前步骤是什么
    console.log('[DEBUG] 项目ID变化，总是加载成本数据...')
    await fetchProjectCosts()
  }
}, { immediate: true })

// 监听步骤变化，按需加载数据
watch(currentStep, async (newStep, oldStep) => {
  if (!projectId.value) return
  
  console.log(`[DEBUG] 步骤变化: ${oldStep} -> ${newStep}`)
  
  // 根据当前步骤加载对应的数据
  switch (newStep) {
    case 0: // 基本信息
      // 基本信息已经在projectId变化时加载过了
      break
    case 1: // 成本设定
      console.log('[DEBUG] 步骤变化为1（成本设定），projectCost.value:', projectCost.value)
      console.log('[DEBUG] projectCost.value是否为空:', !projectCost.value)
      console.log('[DEBUG] projectCost.value的keys:', projectCost.value ? Object.keys(projectCost.value) : [])
      console.log('[DEBUG] projectCost.value的keys长度:', projectCost.value ? Object.keys(projectCost.value).length : 0)
      
      // 不管projectCost.value是什么，都重新加载成本数据
      console.log('[DEBUG] 强制加载成本数据...')
      await fetchProjectCosts()
      break
    case 2: // 任务设定
      console.log('[DEBUG] 步骤变化为2（任务设定），强制加载任务数据...')
      // 强制加载任务数据，无论tasks.value是否为空
      await fetchProjectTasks()
      break
    case 3: // 文档管理
      if (!documents.value || documents.value.length === 0) {
        console.log('[DEBUG] 加载文档数据...')
        await fetchProjectDocuments()
      }
      break
  }
})

// 成本类型选项卡激活项
const activeCostTab = ref('material')

// 格式化数字为金融格式
const formatToFinancial = (value: any): string => {
  if (value === null || value === undefined || value === '') {
    return ''
  }
  const num = parseFloat(value)
  if (isNaN(num)) {
    return ''
  }
  return num.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 数据处理函数 - 物料成本
const processMaterialCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  // 按物料名称、规格、单位分组
  const groupedCosts: Record<string, any> = {}
  
  data.forEach((cost: any) => {
    // 创建分组键：物料名称_规格_单位
    const groupKey = `${cost.name || ''}_${cost.specification || ''}_${cost.unit || ''}`
    
    if (!groupedCosts[groupKey]) {
      groupedCosts[groupKey] = {
        name: cost.name || '',
        specification: cost.specification || '',
        unit: cost.unit || '',
        budget: null, // 预算数据
        actual: null  // 实际数据
      }
    }
    
    // 尝试匹配成本类型，处理可能的编码问题
    const costType = cost.cost_type || ''
    const isBudget = costType === '预算' || costType.includes('预')
    const isActual = costType === '实际' || costType.includes('实')
    
    // 根据cost_type区分预算和实际数据
    if (isBudget) {
      groupedCosts[groupKey].budget = cost
    } else if (isActual) {
      groupedCosts[groupKey].actual = cost
    }
  })
  
  // 将分组后的数据转换为前端期望的格式，合并预算和实际数据到一行
  return Object.values(groupedCosts).map((group: any, index: number) => {
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
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

// 数据处理函数 - 外包成本
const processOutsourcingCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
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
  
  // 将分组后的数据转换为前端期望的格式
  return Object.values(groupedCosts).map((group: any, index: number) => {
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
    // 服务类型优先使用预算数据的，预算没有则使用实际的
    const serviceType = budgetData.service_type || actualData.service_type || ''
    
    // 确保description字段能正确映射到budget_description和actual_description
    const budgetDescription = budgetData.description || ''
    const actualDescription = actualData.description || ''
    
    return {
      id: index + 1,
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

// 数据处理函数 - 间接成本
const processIndirectCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
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
  
  // 将分组后的数据转换为前端期望的格式
  return Object.values(groupedCosts).map((group: any, index: number) => {
    const budgetData = group.budget || {}
    const actualData = group.actual || {}
    
    // 成本类型：优先使用预算数据的，预算没有则使用实际的
    const costType = budgetData.cost_type || actualData.cost_type || ''
    
    // 服务内容：预算和实际分别使用各自的description字段
    const budgetDescription = budgetData.description || ''
    const actualDescription = actualData.description || ''
    
    // 金额：优先使用预算数据的amount字段，预算没有则使用实际的amount字段
    const budgetAmount = parseFloat(budgetData.amount || budgetData.total_price || 0)
    const actualAmount = parseFloat(actualData.amount || actualData.total_price || 0)
    
    return {
      id: index + 1,
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

// 数据处理函数 - 人力成本
const processLaborCosts = (data: any[]) => {
  if (!data || !Array.isArray(data)) return []
  
  // 直接映射人力成本数据，因为它已经是按角色分组的格式
  return data.map((cost: any, index: number) => {
    return {
      id: index + 1,
      personnel_name: cost.employee_name || '',
      department: cost.department || '',
      position: cost.position || '',
      hourly_rate: parseFloat(cost.hourly_rate || 0),
      // 预算成本字段
      budget_hourly_rate: parseFloat(cost.hourly_rate || 0),
      budget_hourly_rate_display: formatToFinancial(parseFloat(cost.hourly_rate || 0)),
      budget_hours: parseFloat(cost.budget_hours || 0),
      budget_hours_display: parseFloat(cost.budget_hours || 0).toString(),
      budget_cost: parseFloat(cost.budget_cost || 0),
      budget_total_display: formatToFinancial(parseFloat(cost.budget_cost || 0)),
      // 实际成本字段
      actual_hourly_rate: parseFloat(cost.hourly_rate || 0),
      actual_hourly_rate_display: formatToFinancial(parseFloat(cost.hourly_rate || 0)),
      actual_hours: parseFloat(cost.actual_hours || 0),
      actual_hours_display: parseFloat(cost.actual_hours || 0).toString(),
      actual_cost: parseFloat(cost.actual_cost || 0),
      actual_total_display: formatToFinancial(parseFloat(cost.actual_cost || 0)),
      // 其他字段
      remark: cost.remark || ''
    }
  })
}

// 初始化显示数据
const initDisplayData = () => {
  displayData.value.contract_amount = formatToFinancial(formData.value.contract_amount)
  displayData.value.revenue = formatToFinancial(formData.value.revenue)
  displayData.value.target_profit = formatToFinancial(formData.value.target_profit)
}

// 人员列表（用于合同负责人选择）
const personnelList = ref<any[]>([])

// 文档管理相关数据
const taskFilter = ref('')
const selectedTaskName = ref('')
const selectedTaskId = ref<string | number | null>(null)
const currentDocuments = ref<any[]>([])
const taskTreeProps = {
  children: 'children',
  label: 'task_name'
}

// 过滤后的任务列表
const filteredTasks = computed(() => {
  if (!taskFilter.value) {
    // 直接使用treeTasks作为任务树的数据源
    return treeTasks.value
  }
  
  const filterTasks = (tasks: any[]): any[] => {
    return tasks.filter(task => 
      task.task_name.toLowerCase().includes(taskFilter.value.toLowerCase())
    ).map(task => ({
      ...task,
      children: task.children ? filterTasks(task.children) : []
    })).filter(task => 
      task.task_name.toLowerCase().includes(taskFilter.value.toLowerCase()) ||
      (task.children && task.children.length > 0)
    )
  }
  
  return filterTasks(treeTasks.value)
})

// 文档预览相关
const previewDialogVisible = ref(false)
const previewDocumentTitle = ref('')
const previewDocumentUrl = ref('')
const previewDocumentType = ref('')
const previewDocumentData = ref<any>(null)

// 图表实例
let costDistributionChart: echarts.ECharts | null = null
let costComparisonChart: echarts.ECharts | null = null
let ganttChart: echarts.ECharts | null = null

// 计算属性
const materialBudgetTotal = computed(() => {
  return materialCosts.value.reduce((total, item) => total + (item.budget_total || 0), 0)
})

const materialActualTotal = computed(() => {
  return materialCosts.value.reduce((total, item) => total + (item.actual_total || 0), 0)
})

const materialCostVariance = computed(() => {
  return materialActualTotal.value - materialBudgetTotal.value
})

const outsourcingBudgetTotal = computed(() => {
  return outsourcingCosts.value.reduce((total, item) => total + (item.budget_amount || 0), 0)
})

const outsourcingActualTotal = computed(() => {
  return outsourcingCosts.value.reduce((total, item) => total + (item.actual_amount || 0), 0)
})

const outsourcingCostVariance = computed(() => {
  return outsourcingActualTotal.value - outsourcingBudgetTotal.value
})

const laborBudgetTotal = computed(() => {
  return laborCosts.value.reduce((total, item) => total + (item.budget_total || 0), 0)
})

const laborActualTotal = computed(() => {
  return laborCosts.value.reduce((total, item) => total + (item.actual_total || 0), 0)
})

const laborCostVariance = computed(() => {
  return laborActualTotal.value - laborBudgetTotal.value
})

const indirectBudgetTotal = computed(() => {
  return indirectCosts.value.reduce((total, item) => total + (item.budget_amount || 0), 0)
})

const indirectActualTotal = computed(() => {
  return indirectCosts.value.reduce((total, item) => total + (item.actual_amount || 0), 0)
})

const indirectCostVariance = computed(() => {
  return indirectActualTotal.value - indirectBudgetTotal.value
})

// 获取项目ID
const getInitialProjectId = () => {
  const id = route.params.id
  if (id) {
    const parsed = Number(id)
    return isNaN(parsed) ? 0 : parsed
  }
  return 0
}

// 获取步骤标题
const getStepTitle = (step: number): string => {
  switch (step) {
    case 0:
      return '基本信息'
    case 1:
      return '成本设定'
    case 2:
      return '任务设定'
    case 3:
      return '文档管理'
    default:
      return '基本信息'
  }
}

// 跳转到指定步骤
const goToStep = async (step: number) => {
  try {
    console.log(`[DEBUG] 点击切换到步骤: ${step}`)
    
    // 检查步骤有效性
    if (step < 0 || step > 3) {
      console.warn(`[DEBUG] 无效的步骤号: ${step}`)
      return
    }
    
    // 根据步骤确定路由路径
    const stepRoutes = ['basic', 'cost', 'gantt', 'documents']
    const projectId = route.params.id
    const routePath = `/projects/${projectId}/${stepRoutes[step]}`
    
    console.log(`[DEBUG] 当前路由参数:`, route.params)
    console.log(`[DEBUG] 项目ID:`, projectId)
    console.log(`[DEBUG] 目标路径:`, routePath)
    
    // 进行路由跳转
    console.log(`[DEBUG] 开始路由跳转...`)
    const result = await router.push(routePath)
    
    // 检查跳转结果
    if (result) {
      console.log(`[DEBUG] 路由跳转成功:`, result)
    } else {
      console.log(`[DEBUG] 路由跳转完成`)
    }
  } catch (error) {
    console.error(`[DEBUG] 路由跳转失败:`, error)
  }
}

// 甘特图任务相关数据
const ganttTaskData = ref<any[]>([])

const ganttDialogVisible = ref(false)

// 返回项目列表
const handleBackToList = () => {
  router.push('/projects')
}

// 任务点击处理
const handleTaskClick = (data: any) => {
  console.log('DEBUG: [文档管理] 点击任务:', data)
  selectedTaskName.value = data.task_name
  selectedTaskId.value = data.task_id
  
  // 获取任务对应的文档数据
  if (data.task_id) {
    fetchTaskDocuments(data.task_id)
  } else {
    currentDocuments.value = []
  }
}

// 获取任务对应的文档
const fetchTaskDocuments = async (taskId: string) => {
  try {
    const response = await getProjectTaskAttachments(projectId.value, taskId)
    currentDocuments.value = response || []
    console.log(`[DEBUG] 任务 ${taskId} 的文档数据加载完成，共 ${currentDocuments.value.length} 个文档`)
  } catch (error) {
    console.error(`获取任务 ${taskId} 的文档失败:`, error)
    currentDocuments.value = []
  }
}

// 文件上传处理
const handleUpload = (options: any) => {
  console.log('DEBUG: [文档管理] 开始上传文件:', options.file)
  // 这里应该实现实际的文件上传逻辑
  ElMessage.success('文件上传成功')
}

// 文档下载
const downloadDocument = (documentData: any) => {
  console.log('DEBUG: [文档管理] 开始下载文档:', documentData)
  
  if (!documentData.file_data) {
    ElMessage.error('文档数据不存在，无法下载')
    return
  }
  
  try {
    // 确保使用全局的window.document对象，避免Proxy对象问题
    const globalDocument = window.document
    if (!globalDocument) {
      throw new Error('document对象不可用')
    }
    
    const fileName = documentData.file_name || documentData.attachment_name || '未命名文件'
    console.log('DEBUG: [文档管理] 文件名:', fileName)
    console.log('DEBUG: [文档管理] 文件类型:', documentData.file_type)
    
    // 获取文件内容
    const fileContent = documentData.file_data
    
    // 配置MIME类型
    const mimeTypeMap: Record<string, string> = {
      'pdf': 'application/pdf',
      'doc': 'application/msword',
      'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'xls': 'application/vnd.ms-excel',
      'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'ppt': 'application/vnd.ms-powerpoint',
      'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'jpg': 'image/jpeg',
      'jpeg': 'image/jpeg',
      'png': 'image/png',
      'gif': 'image/gif',
      'txt': 'text/plain',
      'md': 'text/markdown',
      'other': 'application/octet-stream'
    }
    
    const fileType = documentData.file_type || 'other'
    const mimeType = mimeTypeMap[fileType]
    
    // 检查是否为Base64编码
    let finalContent = fileContent
    let isBase64 = false
    
    // 检查是否包含base64前缀
    if (fileContent.includes('base64,')) {
      console.log('DEBUG: [文档管理] 检测到带前缀的Base64编码')
      isBase64 = true
      // 提取Base64数据部分
      finalContent = fileContent.split(',')[1] || fileContent
    } else if (/^[A-Za-z0-9+/=]+$/.test(fileContent.replace(/\s/g, '')) && fileContent.length % 4 === 0) {
      console.log('DEBUG: [文档管理] 检测到纯Base64编码')
      isBase64 = true
      finalContent = fileContent
    }
    
    console.log('DEBUG: [文档管理] Base64检测结果:', isBase64)
    
    let blob: Blob
    
    if (isBase64) {
      console.log('DEBUG: [文档管理] 处理Base64编码内容')
      // Base64解码
      const binaryString = window.atob(finalContent)
      const bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
      blob = new Blob([bytes], { type: mimeType })
    } else {
      console.log('DEBUG: [文档管理] 处理原始文本内容')
      // 直接使用文本内容创建Blob
      blob = new Blob([finalContent], { type: mimeType })
    }
    
    console.log('DEBUG: [文档管理] Blob创建成功，大小:', blob.size, '类型:', blob.type)
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    
    // 使用全局document对象创建a标签
    const link = globalDocument.createElement('a')
    link.href = url
    link.download = fileName
    link.style.display = 'none'
    
    // 关键：将a标签添加到全局document的body中
    globalDocument.body.appendChild(link)
    
    // 触发点击事件
    link.click()
    
    // 延迟清理资源，确保下载完成
    setTimeout(() => {
      // 移除a标签
      globalDocument.body.removeChild(link)
      // 清理URL资源
      URL.revokeObjectURL(url)
      console.log('DEBUG: [文档管理] 资源清理完成')
    }, 2000) // 2秒延迟，确保Chrome完成下载
    
    ElMessage.success(`文档 ${fileName} 下载成功`)
  } catch (error) {
    console.error('DEBUG: [文档管理] 文档下载失败:', error)
    console.error('DEBUG: [文档管理] 错误详情:', error instanceof Error ? error.message : String(error))
    
    // 简化错误处理，直接提示用户
    ElMessage.error(`文档下载失败: ${error instanceof Error ? error.message : '未知错误'}`)
  }
}

// 文档删除
const deleteDocument = (document: any) => {
  console.log('DEBUG: [文档管理] 开始删除文档:', document)
  
  ElMessageBox.confirm(
    `确定要删除文档 "${document.file_name}" 吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // 这里应该实现实际的删除逻辑
    currentDocuments.value = currentDocuments.value.filter(doc => doc.attachment_id !== document.attachment_id)
    ElMessage.success('文档删除成功')
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 获取文件类型文本
const getFileTypeText = (fileType: string | undefined | null) => {
  const typeMap: Record<string, string> = {
    'pdf': 'PDF',
    'docx': 'Word',
    'xlsx': 'Excel',
    'pptx': 'PPT',
    'image': '图片',
    'txt': '文本'
  }
  // 添加容错处理，当fileType为undefined或null时，返回默认值
  if (!fileType) {
    return '其他'
  }
  return typeMap[fileType] || fileType.toUpperCase()
}

// 获取文件类型颜色
const getFileColorByType = (fileType: string | undefined | null) => {
  const typeMap: Record<string, string> = {
    'pdf': 'danger',
    'docx': 'primary',
    'xlsx': 'success',
    'pptx': 'warning',
    'image': 'info',
    'txt': 'info'
  }
  // 添加容错处理，当fileType为undefined或null时，返回默认值
  if (!fileType) {
    return 'info'
  }
  return typeMap[fileType] || 'info'
}

// 格式化文件大小
const formatFileSize = (bytes: number | undefined | null) => {
  if (!bytes || bytes === 0) return '0 B'
  // 确保bytes是数字类型
  const numBytes = typeof bytes === 'number' ? bytes : parseFloat(String(bytes))
  if (isNaN(numBytes)) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(numBytes) / Math.log(k))
  return parseFloat((numBytes / Math.pow(k, i)).toFixed(2)) + ' ' + (sizes[i] || 'B')
}

// 显示甘特图
const showGantt = () => {
  ganttDialogVisible.value = true
  nextTick(() => {
    initGantt()
  })
}

// 甘特图相关方法
const initGantt = () => {
  const ganttContainer = document.getElementById('ganttContainer')
  if (!ganttContainer) return

  // 清空容器
  ganttContainer.innerHTML = ''

  // 创建甘特图HTML结构
  const ganttHtml = createGanttHtml()
  ganttContainer.innerHTML = ganttHtml
}

const createGanttHtml = () => {
  let html = `
    <div class="gantt-chart">
      <div class="gantt-header">
        <div class="gantt-task-column">任务名称</div>
        <div class="gantt-timeline">
  `

  // 生成时间轴
  const startDate = new Date('2024-01-01')
  const endDate = new Date('2024-04-30')
  const totalDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24))

  for (let i = 0; i <= totalDays; i++) {
    const currentDate = new Date(startDate)
    currentDate.setDate(startDate.getDate() + i)
    const dayClass = currentDate.getDay() === 0 || currentDate.getDay() === 6 ? 'weekend' : ''
    html += `<div class="gantt-day ${dayClass}">${currentDate.getMonth() + 1}/${currentDate.getDate()}</div>`
  }

  html += `
        </div>
      </div>
      <div class="gantt-body">
  `

  // 生成任务行
  ganttTaskData.value.forEach((task, index) => {
    html += createTaskRow(task, index, startDate, totalDays)
    // 如果有子任务，也显示
    if (task.children) {
      task.children.forEach((childTask, childIndex) => {
        html += createTaskRow(childTask, `${index}-${childIndex}`, startDate, totalDays, true)
      })
    }
  })

  html += `
      </div>
    </div>
  `

  return html
}

const createTaskRow = (task, index, startDate, totalDays, isChild = false) => {
  const taskStartDate = new Date(task.startDate)
  const taskEndDate = new Date(task.endDate)
  const startOffset = Math.ceil((taskStartDate - startDate) / (1000 * 60 * 60 * 24))
  const duration = Math.ceil((taskEndDate - taskStartDate) / (1000 * 60 * 60 * 24))
  
  const left = (startOffset / totalDays) * 100
  const width = (duration / totalDays) * 100

  const statusClass = task.status === '已完成' ? 'completed' : task.status === '进行中' ? 'in-progress' : 'not-started'
  const indentClass = isChild ? 'child-task' : ''

  return `
    <div class="gantt-row ${indentClass}">
      <div class="gantt-task-cell">
        <span class="task-name">${task.name}</span>
        <span class="task-assignee">${task.assignee || ''}</span>
      </div>
      <div class="gantt-bar-container">
        <div class="gantt-bar ${statusClass}" style="left: ${left}%; width: ${width}%;">
          <span class="task-progress">${task.progress}%</span>
        </div>
      </div>
    </div>
  `
}

const closeGanttDialog = () => {
  ganttDialogVisible.value = false
}

// 上一步
const handlePrevious = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

// 下一步
const handleNext = () => {
  // 如果当前在Step1（基本信息），跳转到成本设定页面
  if (currentStep.value === 0) {
    currentStep.value = 1
  } else if (currentStep.value < 3) {
    currentStep.value++
  }
}

// 格式化日期
const formatDate = (date: string | Date | null) => {
  if (!date) return '未设置'
  try {
    const formattedDate = new Date(date)
    if (isNaN(formattedDate.getTime())) {
      return '未设置'
    }
    return formattedDate.toLocaleDateString()
  } catch (error) {
    console.error('格式化日期失败:', error)
    return '未设置'
  }
}

// 格式化数字
const formatNumber = (num: number) => {
  if (!num) return '0'
  return num.toLocaleString()
}

// 根据开始日期、计划结束日期、实际完成日期获取任务进度状态
const getTaskProgressStatus = (task: any) => {
  // 添加容错处理，确保task存在
  if (!task) return '未设置'
  
  const today = new Date()
  
  // 容错处理：确保start_date和end_date存在且有效
  if (!task.start_date || !task.end_date) {
    return '未设置'
  }
  
  try {
    const startDate = new Date(task.start_date)
    const plannedEndDate = new Date(task.end_date)
    const actualEndDate = task.actual_end_date ? new Date(task.actual_end_date) : null
    
    // 检查日期是否有效
    if (isNaN(startDate.getTime()) || isNaN(plannedEndDate.getTime())) {
      return '未设置'
    }
    
    // 未开始
    if (today < startDate) {
      return '未开始'
    }
    
    // 已完成
    if (actualEndDate && !isNaN(actualEndDate.getTime())) {
      // 已完成：实际完成日期 = 计划结束日期
      if (actualEndDate.toDateString() === plannedEndDate.toDateString()) {
        return '已完成'
      }
      // 提前完成：实际完成日期 < 计划结束日期
      else if (actualEndDate < plannedEndDate) {
        return '提前完成'
      }
      // 延期完成：实际完成日期 > 计划结束日期
      else {
        return '延期完成'
      }
    }
    
    // 进行中：当前日期 <= 计划结束日期
    if (today <= plannedEndDate) {
      return '进行中'
    }
    
    // 已延期：当前日期 > 计划结束日期
    return '已延期'
  } catch (error) {
    console.error('获取任务状态失败:', error)
    return '未设置'
  }
}

// 根据任务进度状态获取标签类型
const getTaskProgressStatusType = (status: string) => {
  const statusMap: any = {
    '未开始': 'info',
    '进行中': 'primary',
    '已完成': 'success',
    '已延期': 'danger',
    '提前完成': 'success',
    '延期完成': 'warning'
  }
  return statusMap[status] || 'default'
}

// 根据状态获取标签类型
const getStatusType = (status: string) => {
  const statusMap: any = {
    '规划中': 'info',
    '进行中': 'primary',
    '已完成': 'success',
    '提前完成': 'success',
    '延期完成': 'warning',
    '已延期': 'warning',
    '已暂停': 'danger',
    '已取消': 'danger',
    'todo': 'info',
    'in_progress': 'primary',
    'done': 'success',
    'blocked': 'danger'
  }
  return statusMap[status] || 'default'
}

// 根据状态获取文本
const getStatusText = (status: string) => {
  const statusTextMap: any = {
    'todo': '待处理',
    'in_progress': '进行中',
    'done': '已完成',
    'blocked': '已阻塞'
  }
  return statusTextMap[status] || status
}

// 根据成本偏差获取标签类型
const getCostVarianceType = (variance: number) => {
  if (variance > 0) return 'success'
  if (variance < 0) return 'danger'
  return 'info'
}

// 根据进度获取进度条状态
const getProgressStatus = (progress: number) => {
  if (progress === 100) return 'success'
  if (progress < 30) return 'exception'
  return ''
}

// 下载文档 - 已在前面定义

// 初始化成本分布图表
const initCostDistributionChart = () => {
  nextTick(() => {
    const chartDom = document.getElementById('costDistributionChart')
    if (chartDom) {
      costDistributionChart = echarts.init(chartDom)
      updateCostDistributionChart()
    }
  })
}

// 更新成本分布图表
const updateCostDistributionChart = () => {
  if (!costDistributionChart) return
  
  const option = {
    title: {
      text: '成本分布',
      left: 'center',
      top: 20,
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      top: 'middle',
      data: ['物料成本', '人力成本', '外包成本', '间接成本']
    },
    series: [
      {
        name: '成本分布',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: projectCost.value.material_cost, name: '物料成本' },
          { value: projectCost.value.labor_cost, name: '人力成本' },
          { value: projectCost.value.outsourcing_cost, name: '外包成本' },
          { value: projectCost.value.indirect_cost, name: '间接成本' }
        ]
      }
    ]
  }
  
  costDistributionChart.setOption(option)
}

// 初始化成本对比图表
const initCostComparisonChart = () => {
  nextTick(() => {
    const chartDom = document.getElementById('costComparisonChart')
    if (chartDom) {
      costComparisonChart = echarts.init(chartDom)
      updateCostComparisonChart()
    }
  })
}

// 更新成本对比图表
const updateCostComparisonChart = () => {
  if (!costComparisonChart) return
  
  const option = {
    title: {
      text: '成本对比（预算 vs 实际）',
      left: 'center',
      top: 20,
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['预算', '实际'],
      top: 50
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['物料成本', '人力成本', '外包成本', '间接成本', '总成本']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '预算',
        type: 'bar',
        data: [
          projectCost.value.material_cost,
          projectCost.value.labor_cost,
          projectCost.value.outsourcing_cost,
          projectCost.value.indirect_cost,
          projectCost.value.total_cost
        ]
      },
      {
        name: '实际',
        type: 'bar',
        data: [
          projectCost.value.material_cost,
          projectCost.value.labor_cost,
          projectCost.value.outsourcing_cost,
          projectCost.value.indirect_cost,
          projectCost.value.total_cost
        ]
      }
    ]
  }
  
  costComparisonChart.setOption(option)
}

// 初始化甘特图
const initGanttChart = () => {
  nextTick(() => {
    const chartDom = document.getElementById('ganttChart')
    if (chartDom) {
      ganttChart = echarts.init(chartDom)
      updateGanttChart()
    }
  })
}

// 更新甘特图
const updateGanttChart = () => {
  if (!ganttChart) return
  
  const ganttData = tasks.value.map(task => ({
    name: task.name,
    value: [
      0,
      new Date(task.start_date).getTime(),
      new Date(task.end_date).getTime(),
      task.progress
    ],
    itemStyle: {
      color: getStatusColor(task.status)
    }
  }))
  
  const option = {
    title: {
      text: '项目任务甘特图',
      left: 'center',
      top: 20,
      textStyle: {
        fontSize: 16
      }
    },
    tooltip: {
      formatter: function(params: any) {
        return params.name + '<br/>' +
               '开始: ' + echarts.format.formatTime('yyyy-MM-dd', params.value[1]) + '<br/>' +
               '结束: ' + echarts.format.formatTime('yyyy-MM-dd', params.value[2]) + '<br/>' +
               '进度: ' + params.value[3] + '%'
      }
    },
    grid: {
      height: '60%',
      top: 80
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: '{MM}-{dd}'
      }
    },
    yAxis: {
      type: 'category',
      data: ganttData.map(item => item.name),
      axisLabel: {
        fontSize: 12,
        formatter: function(value: string) {
          return value.length > 15 ? value.substring(0, 15) + '...' : value
        }
      }
    },
    series: [
      {
        name: '任务',
        type: 'custom',
        renderItem: function(params: any, api: any) {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const height = api.size([0, 1])[1] * 0.6
          
          // 计算进度条的位置和长度
          const progress = api.value(3) / 100
          const progressEnd = api.coord([api.value(1) + (api.value(2) - api.value(1)) * progress, categoryIndex])
          
          // 任务背景
          const rectShape = {
            x: start[0],
            y: start[1] - height / 2,
            width: end[0] - start[0],
            height: height,
            fill: '#f0f0f0',
            stroke: '#ccc',
            lineWidth: 1,
            borderRadius: 4
          }
          
          // 进度条
          const progressShape = {
            x: start[0],
            y: start[1] - height / 2,
            width: progressEnd[0] - start[0],
            height: height,
            fill: api.visual('color'),
            borderRadius: 4
          }
          
          // 任务名称标签
          const labelShape = {
            type: 'text',
            x: start[0] + 5,
            y: start[1] + height / 4,
            text: api.value(0),
            fontSize: 12,
            fill: '#333',
            overflow: 'truncate',
            width: end[0] - start[0] - 10
          }
          
          return {
            type: 'group',
            children: [
              { type: 'rect', shape: rectShape },
              { type: 'rect', shape: progressShape },
              labelShape
            ]
          }
        },
        encode: {
          x: [1, 2],
          y: 0
        },
        data: ganttData
      }
    ]
  }
  
  ganttChart.setOption(option)
}

// 根据任务状态获取颜色
const getStatusColor = (status: string) => {
  const statusColorMap: Record<string, string> = {
    'todo': '#5470c6',
    'in_progress': '#91cc75',
    'done': '#fac858',
    'blocked': '#ee6666'
  }
  return statusColorMap[status] || '#5470c6'
}

// 监听成本数据变化，更新图表
watch(
  [projectCost, formData],
  () => {
    if (currentStep.value === 1) {
      updateCostDistributionChart()
      updateCostComparisonChart()
    }
  },
  { deep: true }
)

// 监听表单数据变化，更新显示数据
watch(
  formData,
  () => {
    initDisplayData()
  },
  { deep: true }
)

// 监听任务数据变化，更新甘特图
watch(
  tasks,
  () => {
    if (currentStep.value === 2) {
      updateGanttChart()
    }
  },
  { deep: true }
)

onMounted(async () => {
  await Promise.all([
    fetchProjectDetails(),
    fetchProjectTasks(),
    // fetchProjectCosts() - 移除成本数据加载，只在currentStep === 1时按需加载
    fetchProjectDocuments()
  ])
  
  // 初始化显示数据
  initDisplayData()
  
  // 初始化图表
  setTimeout(() => {
    initCostDistributionChart()
    initCostComparisonChart()
    initGanttChart()
  }, 100)
})

// 监听窗口大小变化，调整图表大小
window.addEventListener('resize', () => {
  costDistributionChart?.resize()
  costComparisonChart?.resize()
  ganttChart?.resize()
})
</script>

<style scoped>
.project-detail-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

.project-detail-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.form-container {
  margin-top: 30px;
}

.step-content {
  padding: 20px 0;
  min-height: 400px;
}

.cost-summary {
  text-align: center;
}

.cost-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.cost-value {
  font-size: 24px;
  font-weight: bold;
  color: #1890ff;
}

.cost-value.total-cost {
  color: #f56c6c;
}

.cost-value.variance {
  color: inherit;
}

.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.clickable-step {
  cursor: pointer;
}

.clickable-step:hover {
  color: #409eff;
}

:deep(.el-steps) {
  margin-bottom: 30px;
}

/* 步骤指示器蓝色主题 */
:deep(.el-step__title) {
  color: #409eff;
}

:deep(.el-step__description) {
  color: #909399;
}

:deep(.el-step.is-process .el-step__title) {
  color: #409eff;
}

:deep(.el-step.is-process .el-step__description) {
  color: #c0c4cc;
}

:deep(.el-step.is-finish .el-step__title) {
  color: #409eff;
}

:deep(.el-step.is-finish .el-step__description) {
  color: #409eff;
}

:deep(.el-step.is-wait .el-step__title) {
  color: #c0c4cc;
}

:deep(.el-step.is-wait .el-step__description) {
  color: #c0c4cc;
}

:deep(.el-descriptions__label) {
  font-weight: bold;
  width: 120px;
}

:deep(.el-descriptions__content) {
  color: #606266;
}

:deep(.el-table) {
  margin-top: 0;
}

:deep(.el-card__header) {
  background-color: #fafafa;
}

:deep(.el-divider__text) {
  color: #303133;
  font-weight: bold;
}

/* 文档管理样式 */
.document-container {
  margin-top: 0;
}

.main-content {
  display: flex;
  gap: 20px;
  height: 500px;
}

.left-panel {
  flex: 0 0 300px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  overflow: hidden;
}

.right-panel {
  flex: 1;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.panel-header h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
  font-weight: 600;
}

.task-tree {
  height: calc(100% - 40px);
  overflow: auto;
}

.document-list {
  flex: 1;
  overflow: auto;
  margin-bottom: 16px;
}

.document-table {
  min-height: 200px;
}

.document-upload {
  margin-top: 16px;
  padding: 16px;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  text-align: center;
}

.document-preview {
  height: 100%;
  overflow: auto;
}

.preview-content {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.image-preview,
.pdf-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.other-preview {
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
    height: auto;
  }
  
  .left-panel {
    flex: none;
    height: 200px;
  }
  
  .right-panel {
    flex: none;
    min-height: 300px;
  }
}
</style>
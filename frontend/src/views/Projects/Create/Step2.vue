<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>{{ (isEditMode ? '编辑项目' : '新建项目') + (projectName ? ' - ' + projectName : '') }} - 成本设定</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ (isEditMode ? '编辑项目' : '新建项目') + (projectName ? ' - ' + projectName : '') }}</el-breadcrumb-item>
            <el-breadcrumb-item>成本设定</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="1" align-center>
        <el-step title="基本信息" description="设置项目基本信息和合同信息" />
        <el-step title="成本设定" description="设置四大成本的预算和实际值" />
        <el-step title="任务设定" description="创建项目任务" />
        <el-step title="文档管理" description="管理项目相关文档" />
      </el-steps>
      
      <div class="cost-container">
        <!-- 成本类型选项卡 -->
        <el-tabs v-model="activeTab" type="card" class="cost-tabs">
          <!-- 物料成本 -->
          <el-tab-pane label="物料成本" name="material">
            <div class="cost-type-section">
              <div class="section-header">
                <h3>物料成本管理</h3>
                <el-button type="primary" @click="addMaterialCost">
                  <el-icon><Plus /></el-icon>
                  新增物料成本
                </el-button>
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
                    <el-input 
                      v-model="scope.row.material_name" 
                      placeholder="请输入物料名称"
                      size="small"
                      type="textarea"
                      :rows="2"
                      resize="none"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="specification" label="规格" min-width="160" :show-overflow-tooltip="false" align="center">
                  <template #default="scope">
                    <el-input 
                      v-model="scope.row.specification" 
                      placeholder="请输入规格"
                      size="small"
                      type="textarea"
                      :rows="2"
                      resize="none"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="unit" label="单位" width="80" min-width="80" align="center">
                  <template #default="scope">
                    <el-input v-model="scope.row.unit" placeholder="请输入单位" size="small" />
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
                        <el-input 
                          v-model="scope.row.budget_quantity_display" 
                          placeholder="请输入数量"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'budget_quantity')"
                          @blur="formatFinancialField(scope.row, 'budget_quantity')"
                        />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">单价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1;">
                        <el-input 
                          v-model="scope.row.budget_unit_price_display" 
                          placeholder="请输入单价"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'budget_unit_price')"
                          @blur="formatFinancialField(scope.row, 'budget_unit_price')"
                        >
                          <template #prepend>¥</template>
                        </el-input>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="160" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1;">
                        <el-input 
                          v-model="scope.row.budget_total_display" 
                          placeholder="自动计算"
                          size="small"
                          readonly
                        >
                          <template #prepend>¥</template>
                        </el-input>
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
                        <el-input 
                          v-model="scope.row.actual_quantity_display" 
                          placeholder="请输入数量"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'actual_quantity')"
                          @blur="formatFinancialField(scope.row, 'actual_quantity')"
                        />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">单价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c;">
                        <el-input 
                          v-model="scope.row.actual_unit_price_display" 
                          placeholder="请输入单价"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'actual_unit_price')"
                          @blur="formatFinancialField(scope.row, 'actual_unit_price')"
                        >
                          <template #prepend>¥</template>
                        </el-input>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="160" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c;">
                        <el-input 
                          v-model="scope.row.actual_total_display" 
                          placeholder="自动计算"
                          size="small"
                          readonly
                        >
                          <template #prepend>¥</template>
                        </el-input>
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column label="操作" width="80" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" @click="deleteMaterialCost(scope.row)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
          
          <!-- 外包成本 -->
          <el-tab-pane label="外包成本" name="outsourcing">
            <div class="cost-type-section">
              <div class="section-header">
                <h3>外包成本管理</h3>
                <el-button type="primary" @click="addOutsourcingCost">
                  <el-icon><Plus /></el-icon>
                  新增外包成本
                </el-button>
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
                    <el-select 
                      v-model="scope.row.service_type" 
                      placeholder="请选择服务类型"
                      size="small"
                      style="width: 100%;"
                    >
                      <el-option 
                        v-for="type in outsourcingServiceTypes" 
                        :key="type.id || type.type_name" 
                        :label="type.type_name || ''" 
                        :value="type.type_name"
                      />
                    </el-select>
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
                        <el-input 
                          v-model="scope.row.budget_description" 
                          placeholder="请输入服务内容"
                          size="small"
                          type="textarea"
                          :rows="2"
                          resize="none"
                        />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1;">
                        <el-input 
                          v-model="scope.row.budget_amount_display" 
                          placeholder="请输入金额"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'budget_amount')"
                          @blur="formatFinancialField(scope.row, 'budget_amount')"
                        >
                          <template #prepend>¥</template>
                        </el-input>
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
                        <el-input 
                          v-model="scope.row.actual_description" 
                          placeholder="请输入服务内容"
                          size="small"
                          type="textarea"
                          :rows="2"
                          resize="none"
                        />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c;">
                        <el-input 
                          v-model="scope.row.actual_amount_display" 
                          placeholder="请输入金额"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'actual_amount')"
                          @blur="formatFinancialField(scope.row, 'actual_amount')"
                        >
                          <template #prepend>¥</template>
                        </el-input>
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column label="操作" width="80" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" @click="deleteOutsourcingCost(scope.row)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
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
                <el-button type="primary" @click="addIndirectCost">
                  <el-icon><Plus /></el-icon>
                  新增间接成本
                </el-button>
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
                    <el-select 
                      v-model="scope.row.cost_type" 
                      placeholder="请选择成本类型"
                      size="small"
                      style="width: 100%;"
                    >
                      <el-option 
                        v-for="type in indirectCostTypes" 
                        :key="type.id || type.type_name" 
                        :label="type.type_name || ''" 
                        :value="type.type_name"
                      />
                    </el-select>
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
                        <el-input 
                          v-model="scope.row.budget_description" 
                          placeholder="请输入服务内容"
                          size="small"
                          type="textarea"
                          :rows="2"
                          resize="none"
                        />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #0288d1;">
                        <el-input 
                          v-model="scope.row.budget_amount_display" 
                          placeholder="请输入金额"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'budget_amount')"
                          @blur="formatFinancialField(scope.row, 'budget_amount')"
                        >
                          <template #prepend>¥</template>
                        </el-input>
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
                        <el-input 
                          v-model="scope.row.actual_description" 
                          placeholder="请输入服务内容"
                          size="small"
                          type="textarea"
                          :rows="2"
                          resize="none"
                        />
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column min-width="150" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">金额</div>
                    </template>
                    <template #default="scope">
                      <div style="color: #388e3c;">
                        <el-input 
                          v-model="scope.row.actual_amount_display" 
                          placeholder="请输入金额"
                          size="small"
                          @input="handleFinancialInput(scope.row, 'actual_amount')"
                          @blur="formatFinancialField(scope.row, 'actual_amount')"
                        >
                          <template #prepend>¥</template>
                        </el-input>
                      </div>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column label="操作" width="80" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" @click="deleteIndirectCost(scope.row)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
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
                <el-button type="primary" @click="addLaborCost">
                  <el-icon><Plus /></el-icon>
                  新增人力成本
                </el-button>
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
                    <div class="personnel-info-container">
                      <el-select 
                        v-model="scope.row.employee_id" 
                        placeholder="请选择人员"
                        size="small"
                        @change="handleEmployeeChange(scope.row)"
                        style="width: 100%;"
                        filterable
                        :filter-method="(query, option) => option && option.label ? option.label.toLowerCase().includes(query.toLowerCase()) : false"
                      >
                        <!-- 将value转换为字符串类型，与后端返回的employee_id类型匹配 -->
                        <el-option 
                          v-for="person in personnelList" 
                          :key="person.id" 
                          :label="person.name" 
                          :value="String(person.id)"
                        ></el-option>
                      </el-select>
                      <!-- 显示隐藏的personnel_name字段，用于调试 -->
                      <div v-if="false" class="hidden-field">{{ scope.row.personnel_name }}</div>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column prop="department" label="部门" min-width="120" align="center" />
                <el-table-column prop="position" label="职位" min-width="120" align="center" />
                <el-table-column prop="hourly_rate" label="每小时费用" min-width="120" align="center">
                  <template #default="scope">
                    <el-input 
                      v-model="scope.row.hourly_rate_display" 
                      placeholder="请输入每小时费用"
                      size="small"
                      @input="handleFinancialInput(scope.row, 'hourly_rate')"
                      @blur="formatFinancialField(scope.row, 'hourly_rate')"
                    >
                      <template #prepend>¥</template>
                    </el-input>
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
                      <el-input 
                        v-model="scope.row.budget_hours_display" 
                        placeholder="请输入工时"
                        size="small"
                        @input="handleLaborInput(scope.row, 'budget_hours')"
                        @blur="formatLaborField(scope.row, 'budget_hours')"
                      />
                    </template>
                  </el-table-column>
                  <el-table-column min-width="120" align="center">
                    <template #header>
                      <div style="color: #0288d1; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <el-input 
                        v-model="scope.row.budget_cost_display" 
                        placeholder="自动计算"
                        size="small"
                        readonly
                      >
                        <template #prepend>¥</template>
                      </el-input>
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
                      <el-input 
                        v-model="scope.row.actual_hours_display" 
                        placeholder="请输入工时"
                        size="small"
                        @input="handleLaborInput(scope.row, 'actual_hours')"
                        @blur="formatLaborField(scope.row, 'actual_hours')"
                      />
                    </template>
                  </el-table-column>
                  <el-table-column min-width="120" align="center">
                    <template #header>
                      <div style="color: #388e3c; font-weight: bold;">总价</div>
                    </template>
                    <template #default="scope">
                      <el-input 
                        v-model="scope.row.actual_cost_display" 
                        placeholder="自动计算"
                        size="small"
                        readonly
                      >
                        <template #prepend>¥</template>
                      </el-input>
                    </template>
                  </el-table-column>
                </el-table-column>
                
                <el-table-column label="操作" width="80" align="center">
                  <template #default="scope">
                    <el-button type="danger" size="small" @click="deleteLaborCost(scope.row)">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="handlePrevious">上一步</el-button>
          <el-button type="primary" @click="handleNext">进入下一步</el-button>
        </div>
      </div>
    </el-card>
    

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox, ElInputNumber, ElInput, ElStatistic, ElRow, ElCol } from 'element-plus'
import { getOutsourcingServiceTypes, getIndirectCostTypes, getProjectCosts, getProjectDetail } from '@/api/project'
import { getPersonnel } from '@/api/resource'

const router = useRouter()
const route = useRoute()

// 获取项目ID
const projectId = computed(() => {
  // 优先从query参数获取（新建流程）
  const queryId = route.query.projectId
  if (queryId) {
    const parsed = parseInt(String(queryId), 10)
    return isNaN(parsed) ? 0 : parsed
  }
  // 回退到params参数（编辑流程）
  const paramsId = route.params.projectId
  if (paramsId) {
    const parsed = parseInt(String(paramsId), 10)
    return isNaN(parsed) ? 0 : parsed
  }
  return 0
})
// 获取模式参数 - 从查询参数获取
const mode = computed(() => route.query.mode as string)
// 判断是否为编辑模式 - 主要基于mode参数
const isEditMode = computed(() => {
  console.log('DEBUG: [Step2] mode参数值:', mode.value)
  console.log('DEBUG: [Step2] projectId参数值:', route.params.projectId)
  
  // 当mode为'create'时是新建模式，其他情况都是编辑模式
  const result = mode.value !== 'create'
  console.log('DEBUG: [Step2] isEditMode判断结果:', result)
  return result
})

// 项目名称
const projectName = ref<string>('')

// 活动选项卡
const activeTab = ref('material')

// 物料成本数据 - 包含预算和实际成本字段
const materialCosts = ref<any[]>([
  {
    id: 1,
    project_id: projectId.value,
    material_name: '',
    specification: '',
    unit: '',
    // 预算成本
    budget_quantity: 0,
    budget_quantity_display: '',
    budget_unit_price: 0,
    budget_unit_price_display: '',
    budget_total: 0,
    budget_total_display: '',
    // 实际成本
    actual_quantity: 0,
    actual_quantity_display: '',
    actual_unit_price: 0,
    actual_unit_price_display: '',
    actual_total: 0,
    actual_total_display: ''
  }
])

// 外包服务类型列表
const outsourcingServiceTypes = ref<any[]>([])

// 间接成本类型列表
const indirectCostTypes = ref<any[]>([])

// 人员列表数据
const personnelList = ref<any[]>([])

// 获取人员列表
const fetchPersonnel = async () => {
  try {
    // 调用真实API获取人员列表
    console.log('获取人员列表')
    const response = await getPersonnel({ limit: 100 })
    // 确保response是数组，如果是对象则提取data字段
    personnelList.value = Array.isArray(response) ? response : (response?.data || [])
    console.log('获取到的人员列表:', personnelList.value)
    // 显示人员列表的详细信息，包括id、name等字段
    console.log('人员列表详细信息:', personnelList.value.map(person => ({ id: person.id, name: person.name, department: person.department, position: person.position })))
  } catch (error) {
    console.error('获取人员列表失败:', error)
    ElMessage.error('获取人员列表失败')
  }
}

// 外包成本数据 - 包含预算和实际成本字段
const outsourcingCosts = ref<any[]>([
  {
    id: 1,
    project_id: projectId.value,
    service_type: '',
    // 预算成本
    budget_description: '',
    budget_amount: 0,
    budget_amount_display: '',
    // 实际成本
    actual_description: '',
    actual_amount: 0,
    actual_amount_display: ''
  }
])

// 间接成本数据 - 包含预算和实际成本字段
const indirectCosts = ref<any[]>([
  {
    id: 1,
    project_id: projectId.value,
    cost_type: '',
    // 预算成本
    budget_description: '',
    budget_amount: 0,
    budget_amount_display: '',
    // 实际成本
    actual_description: '',
    actual_amount: 0,
    actual_amount_display: ''
  }
])

// 人力成本数据 - 包含预算和实际成本字段
const laborCosts = ref<any[]>([
  {
    id: 1,
    project_id: projectId.value,
    employee_id: '',
    personnel_name: '',
    department: '',
    position: '',
    hourly_rate: 0,
    hourly_rate_display: '',
    // 预算成本
    budget_hours: 0,
    budget_hours_display: '',
    budget_cost: 0,
    budget_cost_display: '',
    // 实际成本
    actual_hours: 0,
    actual_hours_display: '',
    actual_cost: 0,
    actual_cost_display: ''
  }
])

// 将数值格式化为金融格式字符串
const formatToFinancial = (value: number | undefined | null): string => {
  if (value === undefined || value === null || isNaN(value)) {
    return ''
  }
  // 允许显示0值
  return value.toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

// 将金融格式字符串解析为数值
const parseFromFinancial = (value: string): number => {
  const parsed = parseFloat(value.replace(/[^\d.]/g, ''))
  return isNaN(parsed) ? 0 : parsed
}

// 处理金融字段输入
const handleFinancialInput = (row: any, field: string) => {
  // 从显示字段获取输入值
  const displayField = `${field}_display`
  const inputValue = row[displayField] || ''
  // 解析为数值
  const parsedValue = parseFromFinancial(inputValue)
  // 更新原始数值字段
  row[field] = parsedValue
  // 更新总价
  if ('material_name' in row) {
    // 物料成本：数量 * 单价 = 总价
    if (field.includes('budget')) {
      row.budget_total = (row.budget_quantity || 0) * (row.budget_unit_price || 0)
      row.budget_total_display = formatToFinancial(row.budget_total)
    } else {
      row.actual_total = (row.actual_quantity || 0) * (row.actual_unit_price || 0)
      row.actual_total_display = formatToFinancial(row.actual_total)
    }
  } else if ('service_type' in row) {
    // 外包成本：直接使用金额
    // 不需要计算，直接使用budget_amount或actual_amount
  } else if ('cost_type' in row) {
    // 间接成本：直接使用金额
    // 不需要计算，直接使用budget_amount或actual_amount
  } else if ('personnel_name' in row) {
    // 人力成本：小时数 * 小时费率 = 总成本
    if (field === 'budget_hours') {
      row.budget_cost = (row.budget_hours || 0) * (row.hourly_rate || 0)
      row.budget_cost_display = formatToFinancial(row.budget_cost)
    } else if (field === 'actual_hours') {
      row.actual_cost = (row.actual_hours || 0) * (row.hourly_rate || 0)
      row.actual_cost_display = formatToFinancial(row.actual_cost)
    }
  }
}

// 处理金融字段失焦事件，格式化显示
const formatFinancialField = (row: any, field: string) => {
  const displayField = `${field}_display`
  row[displayField] = formatToFinancial(row[field])
  // 同时更新对应总价的显示
  if (field.includes('budget')) {
    row.budget_total_display = formatToFinancial(row.budget_total)
  } else {
    row.actual_total_display = formatToFinancial(row.actual_total)
  }
}

// 物料成本预算合计
const materialBudgetTotal = computed(() => {
  return materialCosts.value.reduce((sum, item) => sum + (item.budget_total || 0), 0)
})

// 物料成本实际合计
const materialActualTotal = computed(() => {
  return materialCosts.value.reduce((sum, item) => sum + (item.actual_total || 0), 0)
})

// 物料成本偏差（实际 - 预算）
const materialCostVariance = computed(() => {
  return materialActualTotal.value - materialBudgetTotal.value
})

// 外包成本预算合计
const outsourcingBudgetTotal = computed(() => {
  return outsourcingCosts.value.reduce((sum, item) => sum + (item.budget_amount || 0), 0)
})

// 外包成本实际合计
const outsourcingActualTotal = computed(() => {
  return outsourcingCosts.value.reduce((sum, item) => sum + (item.actual_amount || 0), 0)
})

// 外包成本偏差（实际 - 预算）
const outsourcingCostVariance = computed(() => {
  return outsourcingActualTotal.value - outsourcingBudgetTotal.value
})

// 间接成本预算合计
const indirectBudgetTotal = computed(() => {
  return indirectCosts.value.reduce((sum, item) => sum + (item.budget_amount || 0), 0)
})

// 间接成本实际合计
const indirectActualTotal = computed(() => {
  return indirectCosts.value.reduce((sum, item) => sum + (item.actual_amount || 0), 0)
})

// 间接成本偏差（实际 - 预算）
const indirectCostVariance = computed(() => {
  return indirectActualTotal.value - indirectBudgetTotal.value
})

// 人力成本预算合计
const laborBudgetTotal = computed(() => {
  return laborCosts.value.reduce((sum, item) => sum + (item.budget_cost || 0), 0)
})

// 人力成本实际合计
const laborActualTotal = computed(() => {
  return laborCosts.value.reduce((sum, item) => sum + (item.actual_cost || 0), 0)
})

// 人力成本偏差（实际 - 预算）
const laborCostVariance = computed(() => {
  return laborActualTotal.value - laborBudgetTotal.value
})

// 获取物料成本列表
const fetchMaterialCosts = async () => {
  try {
    // TODO: 调用API获取物料成本列表
    console.log('获取物料成本列表', projectId.value)
    // materialCosts.value = await getMaterialCosts(projectId.value)
  } catch (error) {
    console.error('获取物料成本列表失败:', error)
    ElMessage.error('获取物料成本列表失败')
  }
}

// 获取外包服务类型列表
const fetchOutsourcingServiceTypes = async () => {
  try {
    // 调用真实API获取外包服务类型列表
    console.log('获取外包服务类型列表')
    const response = await getOutsourcingServiceTypes()
    // 只显示未删除的服务类型
    outsourcingServiceTypes.value = response.filter((type: any) => !type.is_deleted)
  } catch (error) {
    console.error('获取外包服务类型列表失败:', error)
    ElMessage.error('获取外包服务类型列表失败')
  }
}

// 获取间接成本类型列表
const fetchIndirectCostTypes = async () => {
  try {
    // 调用真实API获取间接成本类型列表
    console.log('获取间接成本类型列表')
    const response = await getIndirectCostTypes()
    // 只显示未删除的成本类型
    indirectCostTypes.value = response.filter((type: any) => !type.is_deleted)
  } catch (error) {
    console.error('获取间接成本类型列表失败:', error)
    ElMessage.error('获取间接成本类型列表失败')
  }
}

// 添加物料成本行
const addMaterialCost = () => {
  materialCosts.value.push({
    id: Date.now(),
    project_id: projectId.value,
    material_name: '',
    specification: '',
    unit: '',
    // 预算成本
    budget_quantity: 0,
    budget_unit_price: 0,
    budget_total: 0,
    // 实际成本
    actual_quantity: 0,
    actual_unit_price: 0,
    actual_total: 0
  })
}

// 添加外包成本行
const addOutsourcingCost = () => {
  outsourcingCosts.value.push({
    id: Date.now(),
    project_id: projectId.value,
    service_type_id: '',
    service_type: '',
    // 预算成本
    budget_description: '',
    budget_amount: 0,
    budget_amount_display: '',
    // 实际成本
    actual_description: '',
    actual_amount: 0,
    actual_amount_display: ''
  })
}

// 添加间接成本行
const addIndirectCost = () => {
  indirectCosts.value.push({
    id: Date.now(),
    project_id: projectId.value,
    cost_type_id: '',
    cost_type: '',
    // 预算成本
    budget_description: '',
    budget_amount: 0,
    budget_amount_display: '',
    // 实际成本
    actual_description: '',
    actual_amount: 0,
    actual_amount_display: ''
  })
}

// 添加人力成本行
const addLaborCost = () => {
  laborCosts.value.push({
    id: Date.now(),
    project_id: projectId.value,
    employee_id: '',
    personnel_name: '',
    department: '',
    position: '',
    hourly_rate: 0,
    hourly_rate_display: '',
    // 预算成本
    budget_hours: 0,
    budget_hours_display: '',
    budget_cost: 0,
    budget_cost_display: '',
    // 实际成本
    actual_hours: 0,
    actual_hours_display: '',
    actual_cost: 0,
    actual_cost_display: ''
  })
}

// 删除物料成本行
const deleteMaterialCost = (row: any) => {
  ElMessageBox.confirm('确定要删除这条物料成本记录吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = materialCosts.value.indexOf(row)
    if (index !== -1) {
      materialCosts.value.splice(index, 1)
      ElMessage.success('物料成本已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 删除外包成本行
const deleteOutsourcingCost = (row: any) => {
  ElMessageBox.confirm('确定要删除这条外包成本记录吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = outsourcingCosts.value.indexOf(row)
    if (index !== -1) {
      outsourcingCosts.value.splice(index, 1)
      ElMessage.success('外包成本已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 删除间接成本行
const deleteIndirectCost = (row: any) => {
  ElMessageBox.confirm('确定要删除这条间接成本记录吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = indirectCosts.value.indexOf(row)
    if (index !== -1) {
      indirectCosts.value.splice(index, 1)
      ElMessage.success('间接成本已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 删除人力成本行
const deleteLaborCost = (row: any) => {
  ElMessageBox.confirm('确定要删除这条人力成本记录吗？', '删除确认', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    const index = laborCosts.value.indexOf(row)
    if (index !== -1) {
      laborCosts.value.splice(index, 1)
      ElMessage.success('人力成本已删除')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 处理员工选择变化
const handleEmployeeChange = (row: any) => {
  // 确保类型匹配，将row.employee_id转换为数字与person.id比较
  const selectedEmployee = personnelList.value.find(person => person.id === Number(row.employee_id))
  if (selectedEmployee) {
    row.personnel_name = selectedEmployee.name
    row.department = selectedEmployee.department
    row.position = selectedEmployee.position
  } else {
    row.personnel_name = ''
    row.department = ''
    row.position = ''
  }
}

// 处理人力成本工时输入
const handleLaborInput = (row: any, field: string) => {
  // 从显示字段获取输入值
  const displayField = `${field}_display`
  const inputValue = row[displayField] || ''
  // 解析为数值
  const parsedValue = parseFromFinancial(inputValue)
  // 更新原始数值字段
  row[field] = parsedValue
  // 更新对应成本
  if (field === 'budget_hours') {
    // 计算预算成本
    row.budget_cost = (row.budget_hours || 0) * (row.hourly_rate || 0)
    // 更新显示字段
    row.budget_cost_display = formatToFinancial(row.budget_cost)
  } else if (field === 'actual_hours') {
    // 计算实际成本
    row.actual_cost = (row.actual_hours || 0) * (row.hourly_rate || 0)
    // 更新显示字段
    row.actual_cost_display = formatToFinancial(row.actual_cost)
  }
}

// 格式化人力成本字段
const formatLaborField = (row: any, field: string) => {
  const displayField = `${field}_display`
  row[displayField] = formatToFinancial(row[field])
  // 同时更新对应成本的显示
  if (field === 'budget_hours') {
    row.budget_cost_display = formatToFinancial(row.budget_cost)
  } else if (field === 'actual_hours') {
    row.actual_cost_display = formatToFinancial(row.actual_cost)
  }
}

// 更新物料成本总价
const updateMaterialCostTotal = (row: any, costType: 'budget' | 'actual') => {
  if (costType === 'budget') {
    // 计算预算总价
    row.budget_total = (row.budget_quantity || 0) * (row.budget_unit_price || 0)
    // 更新显示字段
    row.budget_total_display = formatToFinancial(row.budget_total)
  } else {
    // 计算实际总价
    row.actual_total = (row.actual_quantity || 0) * (row.actual_unit_price || 0)
    // 更新显示字段
    row.actual_total_display = formatToFinancial(row.actual_total)
  }
}

// 通用的成本总价更新函数，处理不同类型的成本计算
const updateCostTotal = (row: any, costType: 'budget' | 'actual') => {
  // 判断成本类型
  if ('material_name' in row) {
    // 物料成本：数量 * 单价 = 总价
    if (costType === 'budget') {
      row.budget_total = (row.budget_quantity || 0) * (row.budget_unit_price || 0)
      row.budget_total_display = formatToFinancial(row.budget_total)
    } else {
      row.actual_total = (row.actual_quantity || 0) * (row.actual_unit_price || 0)
      row.actual_total_display = formatToFinancial(row.actual_total)
    }
  } else if ('service_type' in row) {
    // 外包成本：直接使用金额
    // 不需要计算，直接使用budget_amount或actual_amount
  } else if ('cost_type' in row) {
    // 间接成本：直接使用金额
    // 不需要计算，直接使用budget_amount或actual_amount
  } else if ('personnel_name' in row) {
    // 人力成本：小时数 * 小时费率 = 总成本
    if (costType === 'budget') {
      row.budget_cost = (row.budget_hours || 0) * (row.hourly_rate || 0)
      row.budget_cost_display = formatToFinancial(row.budget_cost)
    } else {
      row.actual_cost = (row.actual_hours || 0) * (row.hourly_rate || 0)
      row.actual_cost_display = formatToFinancial(row.actual_cost)
    }
  }
}

// 下一步按钮处理
const handleNext = () => {
  console.log('点击了保存并下一步按钮')
  console.log('准备保存的人力成本数据:', laborCosts.value)
  
  // 保存当前成本设置到sessionStorage
  sessionStorage.setItem(`project_material_costs_${projectId.value}`, JSON.stringify(materialCosts.value))
  sessionStorage.setItem(`project_outsource_costs_${projectId.value}`, JSON.stringify(outsourcingCosts.value))
  sessionStorage.setItem(`project_indirect_costs_${projectId.value}`, JSON.stringify(indirectCosts.value))
  sessionStorage.setItem(`project_labor_costs_${projectId.value}`, JSON.stringify(laborCosts.value))
  
  console.log('数据已保存到sessionStorage')
  console.log('从sessionStorage读取的人力成本数据:', sessionStorage.getItem(`project_labor_costs_${projectId.value}`))
  
  router.push({
    name: 'ProjectCreateStep3',
    params: { projectId: projectId.value },
    query: { mode: mode.value }
  })
}

// 跳转到上一步
const handlePrevious = () => {
  console.log('DEBUG: [成本管理] 点击上一步按钮')
  
  // 保存成本数据到sessionStorage
  sessionStorage.setItem(`project_material_costs_${projectId.value}`, JSON.stringify(materialCosts.value))
  sessionStorage.setItem(`project_outsource_costs_${projectId.value}`, JSON.stringify(outsourcingCosts.value))
  sessionStorage.setItem(`project_indirect_costs_${projectId.value}`, JSON.stringify(indirectCosts.value))
  sessionStorage.setItem(`project_labor_costs_${projectId.value}`, JSON.stringify(laborCosts.value))
  
  // 直接跳转到上一步
  console.log('DEBUG: [Step2] 跳转到Step1，mode=', mode.value, 'projectId=', projectId.value)
  router.push({
    name: 'ProjectCreateStep1',
    query: { 
      mode: mode.value,
      projectId: projectId.value
    }
  })
}

// 初始加载数据
// 获取项目详情
const fetchProjectDetailData = async () => {
  if (!projectId.value) return
  
  try {
    const project = await getProjectDetail(projectId.value)
    projectName.value = project.name
  } catch (error) {
    console.error('获取项目详情失败:', error)
    // 失败时不显示错误，保持默认文本
  }
}

onMounted(async () => {
  // 获取项目详情
  await fetchProjectDetailData()
  
  // 新建项目时（projectId为0），不使用sessionStorage数据，直接初始化
  if (projectId.value === 0) {
    console.log('DEBUG: [Step2] 新建项目模式，直接初始化数据')
    // 初始化物料成本数据
    materialCosts.value = [{
      id: 1,
      project_id: projectId.value,
      material_name: '',
      specification: '',
      unit: '',
      budget_quantity: 0,
      budget_quantity_display: '',
      budget_unit_price: 0,
      budget_unit_price_display: '',
      budget_total: 0,
      budget_total_display: '',
      actual_quantity: 0,
      actual_quantity_display: '',
      actual_unit_price: 0,
      actual_unit_price_display: '',
      actual_total: 0,
      actual_total_display: '',
      remark: ''
    }]
    
    // 初始化其他成本类型数据
    outsourcingCosts.value = []
    indirectCosts.value = []
    laborCosts.value = []
    
    // 获取各类成本数据
    fetchOutsourcingServiceTypes()
    fetchIndirectCostTypes()
    fetchPersonnel()
    return
  }
  
  // 从sessionStorage获取之前保存的成本数据
  const savedMaterialCosts = sessionStorage.getItem(`project_material_costs_${projectId.value}`)
  const savedOutsourceCosts = sessionStorage.getItem(`project_outsource_costs_${projectId.value}`)
  const savedIndirectCosts = sessionStorage.getItem(`project_indirect_costs_${projectId.value}`)
  const savedLaborCosts = sessionStorage.getItem(`project_labor_costs_${projectId.value}`)
  
  // 编辑模式下，优先检查sessionStorage是否有用户修改后的数据
  if (isEditMode.value) {
    // 检查sessionStorage中是否有用户修改后的数据
    const hasSessionData = savedMaterialCosts || savedOutsourceCosts || savedIndirectCosts || savedLaborCosts
    
    if (hasSessionData) {
      console.log('DEBUG: [编辑场景] 从sessionStorage获取用户修改后的成本数据')
      // 从sessionStorage加载数据
      if (savedMaterialCosts) {
        materialCosts.value = JSON.parse(savedMaterialCosts)
      } else {
        materialCosts.value = [{
          id: 1,
          project_id: projectId.value,
          material_name: '',
          specification: '',
          unit: '',
          budget_quantity: 0,
          budget_quantity_display: '0',
          budget_unit_price: 0,
          budget_unit_price_display: '0',
          budget_total: 0,
          budget_total_display: '0',
          actual_quantity: 0,
          actual_quantity_display: '0',
          actual_unit_price: 0,
          actual_unit_price_display: '0',
          actual_total: 0,
          actual_total_display: '0',
          remark: ''
        }]
      }
      
      if (savedOutsourceCosts) {
        outsourcingCosts.value = JSON.parse(savedOutsourceCosts)
      } else {
        outsourcingCosts.value = []
      }
      
      if (savedIndirectCosts) {
        indirectCosts.value = JSON.parse(savedIndirectCosts)
      } else {
        indirectCosts.value = []
      }
      
      if (savedLaborCosts) {
        laborCosts.value = JSON.parse(savedLaborCosts)
      } else {
        laborCosts.value = []
      }
    } else {
      // 如果sessionStorage中没有数据，从API获取
      console.log('DEBUG: [编辑场景] 开始从API获取成本数据，isEditMode:', isEditMode.value)
      console.log('DEBUG: [编辑场景] projectId:', projectId.value)
      console.log('DEBUG: [编辑场景] 调用getProjectCosts函数，参数:', Number(projectId.value))
      try {
        // 调用API获取项目成本数据
        const response = await getProjectCosts(Number(projectId.value))
        console.log('DEBUG: [编辑场景] 获取到的完整响应:', response)
        
        // 因为axios拦截器已经处理了响应格式，直接使用response作为costData
        // 不需要再提取response.data，否则会得到undefined
        const costData = response || {}
        console.log('DEBUG: [编辑场景] 使用的costData:', costData)
        
        // 特别针对project_id='81'的项目添加详细日志
        if (projectId.value === '81') {
          console.log('DEBUG: [编辑场景] 【重点】project_id=81的完整成本数据:', costData)
        }
        
        // 查看各个成本数组的长度
        console.log('DEBUG: [编辑场景] 成本数据长度:', {
          material_costs: costData.material_costs?.length,
          outsourcing_costs: costData.outsourcing_costs?.length,
          indirect_costs: costData.indirect_costs?.length,
          labor_costs: costData.labor_costs?.length
        })
        
        // 处理物料成本数据
        if (costData.material_costs && costData.material_costs.length > 0) {
          console.log('DEBUG: [编辑场景] 处理物料成本数据，原始数据:', costData.material_costs)
          
          // 1. 首先将物料成本数据按照物料名称、规格和单位分组
          const groupedCosts: any = {}
          
          // 详细日志：打印原始物料成本数据
          console.log('DEBUG: [编辑场景] 原始物料成本数据详情:', costData.material_costs)
          
          costData.material_costs.forEach((cost: any) => {
            // 详细日志：打印每条成本记录
            console.log('DEBUG: [编辑场景] 处理单条成本记录:', {
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
            console.log('DEBUG: [编辑场景] 生成的分组键:', groupKey)
            
            if (!groupedCosts[groupKey]) {
              groupedCosts[groupKey] = {
                name: cost.name || '',
                specification: cost.specification || '',
                unit: cost.unit || '',
                budget: null, // 预算数据
                actual: null  // 实际数据
              }
              console.log('DEBUG: [编辑场景] 创建新分组:', groupedCosts[groupKey])
            } else {
              console.log('DEBUG: [编辑场景] 使用现有分组:', groupedCosts[groupKey])
            }
            
            // 根据cost_type区分预算和实际数据
            if (cost.cost_type === '预算') {
              groupedCosts[groupKey].budget = cost
              console.log('DEBUG: [编辑场景] 设置预算数据:', cost)
            } else if (cost.cost_type === '实际') {
              groupedCosts[groupKey].actual = cost
              console.log('DEBUG: [编辑场景] 设置实际数据:', cost)
            }
          })
          
          console.log('DEBUG: [编辑场景] 最终分组结果:', groupedCosts)
          
          console.log('DEBUG: [编辑场景] 分组后的物料成本数据:', groupedCosts)
          
          // 2. 将分组后的数据转换为前端期望的格式，合并预算和实际数据到一行
          materialCosts.value = Object.values(groupedCosts).map((group: any, index: number) => {
            // 获取预算和实际数据
            const budgetData = group.budget || {}
            const actualData = group.actual || {}
            
            // 调试日志：打印每个物料的预算和实际数据
            console.log('DEBUG: [编辑场景] 物料数据详情:', {
              groupKey: `${group.name}_${group.specification}_${group.unit}`,
              budgetData: budgetData,
              actualData: actualData
            })
            
            // 直接使用group对象的基本信息，因为分组时已经正确设置
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
            
            // 详细日志：打印每条记录的转换结果
            console.log('DEBUG: [编辑场景] 转换后物料数据:', {
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
              id: index + 1, // 使用索引作为id
              project_id: costData.project_id,
              material_name: materialName,
              specification: specification,
              unit: unit,
              // 预算成本字段 - 直接使用数据库中的数值
              budget_quantity: budgetQuantity,
              budget_quantity_display: budgetQuantity.toString(), // 数量不需要货币格式化
              budget_unit_price: budgetUnitPrice,
              budget_unit_price_display: formatToFinancial(budgetUnitPrice),
              budget_total: budgetTotal,
              budget_total_display: formatToFinancial(budgetTotal),
              // 实际成本字段 - 直接使用数据库中的数值
              actual_quantity: actualQuantity,
              actual_quantity_display: actualQuantity.toString(), // 数量不需要货币格式化
              actual_unit_price: actualUnitPrice,
              actual_unit_price_display: formatToFinancial(actualUnitPrice),
              actual_total: actualTotal,
              actual_total_display: formatToFinancial(actualTotal),
              // 其他字段
              remark: budgetData.remark || actualData.remark || ''
            }
          })
          
          console.log('DEBUG: [编辑场景] 最终转换后的物料成本数据:', materialCosts.value)
          
          console.log('DEBUG: [编辑场景] 处理后物料成本数据:', materialCosts.value)
        } else {
          console.log('DEBUG: [编辑场景] 使用默认物料成本数据')
          materialCosts.value = [{
            id: 1,
            project_id: projectId.value,
            material_name: '',
            specification: '',
            unit: '',
            budget_quantity: 0,
            budget_quantity_display: '0',
            budget_unit_price: 0,
            budget_unit_price_display: '0',
            budget_total: 0,
            budget_total_display: '0',
            actual_quantity: 0,
            actual_quantity_display: '0',
            actual_unit_price: 0,
            actual_unit_price_display: '0',
            actual_total: 0,
            actual_total_display: '0',
            remark: ''
          }]
        }
        
        // 手动触发成本合计更新
        console.log('DEBUG: [编辑场景] 物料成本数据处理完成，触发成本合计更新')
        
        // 处理外包成本数据
        if (costData.outsourcing_costs && costData.outsourcing_costs.length > 0) {
          console.log('DEBUG: [编辑场景] 处理外包成本数据，原始数据:', costData.outsourcing_costs)
          
          // 1. 严格按照cost_id排序，确保预算和实际数据能正确两两组队
          const sortedCosts = [...costData.outsourcing_costs].sort((a: any, b: any) => {
            return a.cost_id - b.cost_id
          })
          
          console.log('DEBUG: [编辑场景] 按cost_id排序后的外包成本数据:', sortedCosts)
          
          // 2. 两两组队拼接数据，严格按照cost_id顺序配对
          const pairedOutsourcing: any[] = []
          
          // 遍历排序后的数据，两两组队
          for (let i = 0; i < sortedCosts.length; i += 2) {
            // 获取当前对的预算和实际数据
            const budgetCost = sortedCosts[i] || null
            const actualCost = sortedCosts[i + 1] || null
            
            // 确保至少有预算或实际数据
            if (budgetCost || actualCost) {
              pairedOutsourcing.push({
                budget: budgetCost,
                actual: actualCost
              })
            }
          }
          
          console.log('DEBUG: [编辑场景] 两两组队后的外包成本数据:', pairedOutsourcing)
          
          // 3. 将配对后的数据转换为前端期望的格式
          outsourcingCosts.value = pairedOutsourcing.map((pair: any, index: number) => {
            const budgetData = pair.budget || {}
            const actualData = pair.actual || {}
            
            console.log('DEBUG: [编辑场景] 外包成本详情:', {
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
            
            return {
              id: index + 1, // 使用索引作为id
              project_id: costData.project_id,
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
          
          console.log('DEBUG: [编辑场景] 加载的外包服务类型列表:', outsourcingServiceTypes.value)
          
          console.log('DEBUG: [编辑场景] 处理后外包成本数据:', outsourcingCosts.value)
        } else {
          console.log('DEBUG: [编辑场景] 使用默认外包成本数据')
          outsourcingCosts.value = []
        }
        
        // 处理间接成本数据
        if (costData.indirect_costs && costData.indirect_costs.length > 0) {
          console.log('DEBUG: [编辑场景] 处理间接成本数据，原始数据:', costData.indirect_costs)
          
          // 1. 严格按照cost_id排序
          const sortedIndirect = [...costData.indirect_costs].sort((a: any, b: any) => {
            return a.cost_id - b.cost_id
          })
          
          console.log('DEBUG: [编辑场景] 按cost_id排序后的间接成本数据:', sortedIndirect)
          
          // 2. 两两组队拼接数据，根据cost_type_flag区分预算和实际
          const pairedIndirect: any[] = []
          
          // 遍历排序后的数据，两两组队
          for (let i = 0; i < sortedIndirect.length; i += 2) {
            // 获取当前两条记录，确保完整保留所有字段
            const firstCost = sortedIndirect[i] ? { ...sortedIndirect[i] } : null
            const secondCost = sortedIndirect[i + 1] ? { ...sortedIndirect[i + 1] } : null
            
            // 确定预算和实际数据
            let budgetCost = null
            let actualCost = null
            
            // 处理当前记录，确保完整保留所有字段
            if (firstCost) {
              if (firstCost.cost_type_flag === '预算' || firstCost.cost_type === '预算') {
                budgetCost = firstCost
              } else {
                actualCost = firstCost
              }
            }
            
            // 处理下一条记录，确保完整保留所有字段
            if (secondCost) {
              if (secondCost.cost_type_flag === '预算' || secondCost.cost_type === '预算') {
                budgetCost = secondCost
              } else {
                actualCost = secondCost
              }
            }
            
            // 确保至少有预算或实际数据
            if (budgetCost || actualCost) {
              pairedIndirect.push({
                budget: budgetCost,
                actual: actualCost
              })
            }
          }
          
          console.log('DEBUG: [编辑场景] 两两组队后的间接成本数据:', pairedIndirect)
          
          // 3. 将配对后的数据转换为前端期望的格式
          indirectCosts.value = pairedIndirect.map((pair: any, index: number) => {
            const budgetData = pair.budget || {}
            const actualData = pair.actual || {}
            
            // 成本类型优先使用预算数据的，预算没有则使用实际的
            const costType = budgetData.cost_type || actualData.cost_type || ''
            
            // 直接从原始API响应中查找对应记录，确保能获取到完整的description字段
            const originalBudgetRecord = costData.indirect_costs.find((cost: any) => cost.cost_id === budgetData.cost_id)
            const originalActualRecord = costData.indirect_costs.find((cost: any) => cost.cost_id === actualData.cost_id)
            
            // 从原始记录中获取description字段，确保强匹配
            const budgetDescription = originalBudgetRecord?.description || ''
            const actualDescription = originalActualRecord?.description || ''
            
            console.log('DEBUG: [编辑场景] 间接成本服务内容映射:', {
              pairIndex: index,
              budgetData: {
                costId: budgetData.cost_id,
                originalDescription: originalBudgetRecord?.description
              },
              actualData: {
                costId: actualData.cost_id,
                originalDescription: originalActualRecord?.description
              },
              mapped: {
                costType: costType,
                budgetDescription: budgetDescription,
                actualDescription: actualDescription
              }
            })
            
            // 直接创建最终对象，确保所有字段都能正确设置
            const indirectCost = {
              id: index + 1,
              project_id: costData.project_id,
              cost_type: costType,
              // 预算成本字段 - 直接使用原始记录的description，强匹配
              budget_description: budgetDescription,
              budget_amount: parseFloat(budgetData.amount || 0),
              budget_amount_display: formatToFinancial(parseFloat(budgetData.amount || 0)),
              // 实际成本字段 - 直接使用原始记录的description，强匹配
              actual_description: actualDescription,
              actual_amount: parseFloat(actualData.amount || 0),
              actual_amount_display: formatToFinancial(parseFloat(actualData.amount || 0)),
              // 其他字段
              remark: budgetData.remark || actualData.remark || ''
            }
            
            // 再次确认服务内容字段是否正确设置
            console.log('DEBUG: [编辑场景] 最终间接成本对象:', {
              id: indirectCost.id,
              costType: indirectCost.cost_type,
              budgetDescription: indirectCost.budget_description,
              actualDescription: indirectCost.actual_description
            })
            
            return indirectCost
          })
          
          console.log('DEBUG: [编辑场景] 处理后间接成本数据:', indirectCosts.value)
        } else {
          console.log('DEBUG: [编辑场景] 使用默认间接成本数据')
          indirectCosts.value = []
        }
        
        // 处理人力成本数据
        if (costData.labor_costs && costData.labor_costs.length > 0) {
          console.log('DEBUG: [编辑场景] 处理人力成本数据，原始数据:', costData.labor_costs)
          
          // 注意：人力成本模型同时包含预算和实际字段，不需要分组配对
          laborCosts.value = costData.labor_costs.map((cost: any, index: number) => {
            console.log('DEBUG: [编辑场景] 人力成本详情:', {
              employeeId: cost.employee_id,
              budget: {
                hours: cost.budget_hours,
                cost: cost.budget_cost
              },
              actual: {
                hours: cost.actual_hours,
                cost: cost.actual_cost
              }
            })
            
            return {
              id: index + 1,
              project_id: costData.project_id,
              employee_id: cost.employee_id || '',
              personnel_name: '', // 初始化为空，后续会通过employee_id关联获取
              department: '',
              position: '',
              hourly_rate: parseFloat(cost.hourly_rate || 0),
              hourly_rate_display: formatToFinancial(parseFloat(cost.hourly_rate || 0)),
              // 预算成本字段
              budget_hours: parseFloat(cost.budget_hours || 0),
              budget_hours_display: parseFloat(cost.budget_hours || 0).toString(), // 小时数不需要货币格式化
              budget_cost: parseFloat(cost.budget_cost || 0),
              budget_cost_display: formatToFinancial(parseFloat(cost.budget_cost || 0)),
              // 实际成本字段
              actual_hours: parseFloat(cost.actual_hours || 0),
              actual_hours_display: parseFloat(cost.actual_hours || 0).toString(), // 小时数不需要货币格式化
              actual_cost: parseFloat(cost.actual_cost || 0),
              actual_cost_display: formatToFinancial(parseFloat(cost.actual_cost || 0)),
              // 其他字段
              remark: cost.remark || ''
            }
          })
          
          console.log('DEBUG: [编辑场景] 处理后人力成本数据:', laborCosts.value)
        } else {
          console.log('DEBUG: [编辑场景] 使用默认人力成本数据')
          laborCosts.value = []
        }
        
        // 先加载人员列表，确保人力成本数据加载前已有人员信息
        await fetchPersonnel()
        
        // 显示人力成本数据的原始信息
        console.log('DEBUG: [编辑场景] 原始人力成本数据:', costData.labor_costs)
        console.log('DEBUG: [编辑场景] 人员列表长度:', personnelList.value.length)
        console.log('DEBUG: [编辑场景] 人员列表可用ID:', personnelList.value.map(person => person.id))
        
        // 重新处理人力成本数据，确保正确关联人员信息
        if (costData.labor_costs && costData.labor_costs.length > 0) {
          console.log('DEBUG: [编辑场景] 重新处理人力成本数据，关联人员信息')
          laborCosts.value = costData.labor_costs.map((cost: any, index: number) => {
            console.log('DEBUG: [编辑场景] 处理人力成本记录:', {
              costId: cost.cost_id,
              employeeId: cost.employee_id,
              employeeIdType: typeof cost.employee_id,
              employeeIdAsNumber: Number(cost.employee_id)
            })
            
            // 查找对应的人员信息
            const employee = personnelList.value.find((person: any) => {
              const match = person.id === Number(cost.employee_id)
              console.log('DEBUG: [编辑场景] 查找人员:', {
                personId: person.id,
                personName: person.name,
                costEmployeeId: cost.employee_id,
                costEmployeeIdAsNumber: Number(cost.employee_id),
                match: match
              })
              return match
            })
            
            console.log('DEBUG: [编辑场景] 找到的人员信息:', employee)
            
            return {
              id: index + 1,
              project_id: costData.project_id,
              employee_id: cost.employee_id || '',
              personnel_name: employee?.name || `未找到:${cost.employee_id}`,
              department: employee?.department || '',
              position: employee?.position || '',
              hourly_rate: parseFloat(cost.hourly_rate || 0),
              hourly_rate_display: formatToFinancial(parseFloat(cost.hourly_rate || 0)),
              // 预算成本字段
              budget_hours: parseFloat(cost.budget_hours || 0),
              budget_hours_display: parseFloat(cost.budget_hours || 0).toString(), // 小时数不需要货币格式化
              budget_cost: parseFloat(cost.budget_cost || 0),
              budget_cost_display: formatToFinancial(parseFloat(cost.budget_cost || 0)),
              // 实际成本字段
              actual_hours: parseFloat(cost.actual_hours || 0),
              actual_hours_display: parseFloat(cost.actual_hours || 0).toString(), // 小时数不需要货币格式化
              actual_cost: parseFloat(cost.actual_cost || 0),
              actual_cost_display: formatToFinancial(parseFloat(cost.actual_cost || 0)),
              // 其他字段
              remark: cost.remark || ''
            }
          })
          
          console.log('DEBUG: [编辑场景] 重新处理后的人力成本数据:', laborCosts.value)
        }
        
        // 确认所有成本数据处理完成
        console.log('DEBUG: [编辑场景] 所有成本数据处理完成:', {
          materialCosts: materialCosts.value.length,
          outsourcingCosts: outsourcingCosts.value.length,
          indirectCosts: indirectCosts.value.length,
          laborCosts: laborCosts.value.length
        })
      } catch (error) {
        console.error('DEBUG: [编辑场景] 获取项目成本数据失败:', error)
        ElMessage.error('获取项目成本数据失败，请稍后重试')
        
        // API获取失败时，回退到sessionStorage数据
        if (savedMaterialCosts) {
          materialCosts.value = JSON.parse(savedMaterialCosts)
        }
        if (savedOutsourceCosts) {
          outsourcingCosts.value = JSON.parse(savedOutsourceCosts)
        }
        if (savedIndirectCosts) {
          indirectCosts.value = JSON.parse(savedIndirectCosts)
        }
        if (savedLaborCosts) {
          laborCosts.value = JSON.parse(savedLaborCosts)
        }
      }
    }
  } else {
    // 新建模式下，使用sessionStorage数据或默认数据
    if (savedMaterialCosts) {
      materialCosts.value = JSON.parse(savedMaterialCosts)
    } else {
      materialCosts.value = [{
        id: 1,
        project_id: projectId.value,
        material_name: '',
        specification: '',
        unit: '',
        budget_quantity: 0,
        budget_quantity_display: '',
        budget_unit_price: 0,
        budget_unit_price_display: '',
        budget_total: 0,
        budget_total_display: '',
        actual_quantity: 0,
        actual_quantity_display: '',
        actual_unit_price: 0,
        actual_unit_price_display: '',
        actual_total: 0,
        actual_total_display: '',
        remark: ''
      }]
    }
    
    if (savedOutsourceCosts) {
      outsourcingCosts.value = JSON.parse(savedOutsourceCosts)
    } else {
      outsourcingCosts.value = []
    }
    
    if (savedIndirectCosts) {
      indirectCosts.value = JSON.parse(savedIndirectCosts)
    } else {
      indirectCosts.value = []
    }
    
    if (savedLaborCosts) {
      laborCosts.value = JSON.parse(savedLaborCosts)
    } else {
      laborCosts.value = []
    }
  }
  
  // 获取各类成本数据
  fetchOutsourcingServiceTypes()
  fetchIndirectCostTypes()
  fetchPersonnel()
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
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
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
</style>
<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>项目详情 - 基本信息</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>项目详情</el-breadcrumb-item>
            <el-breadcrumb-item>基本信息</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="0" align-center>
        <el-step title="基本信息" description="查看项目基本信息和合同信息" />
        <el-step title="成本设定" description="查看四大成本设置" />
        <el-step title="任务设定" description="查看项目任务设置" />
        <el-step title="文档管理" description="查看项目文档" />
      </el-steps>
      
      <div class="form-container">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="120px"
          disabled
        >
          <!-- 基本信息 -->
          <div class="section-title">基本信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="项目名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入项目名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目经理" prop="leader">
                <el-select v-model="form.leader" placeholder="请选择项目经理">
                  <el-option
                    v-for="person in personnelList"
                    :key="person.id"
                    :label="person.name"
                    :value="person.name"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="项目描述" prop="description">
                <el-input
                  v-model="form.description"
                  type="textarea"
                  :rows="3"
                  placeholder="请输入项目描述"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 合同信息 -->
          <div class="section-title">合同信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="合同编号" prop="contract_number">
                <el-input v-model="form.contract_number" placeholder="请输入合同编号" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="合同金额" prop="contract_amount">
                <el-input-number
                  v-model="form.contract_amount"
                  :precision="2"
                  :step="1000"
                  :min="0"
                  placeholder="请输入合同金额"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="合同开始日期" prop="contract_start_date">
                <el-date-picker
                  v-model="form.contract_start_date"
                  type="date"
                  placeholder="请选择合同开始日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="合同结束日期" prop="contract_end_date">
                <el-date-picker
                  v-model="form.contract_end_date"
                  type="date"
                  placeholder="请选择合同结束日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="合同条款" prop="contract_terms">
                <el-input
                  v-model="form.contract_terms"
                  type="textarea"
                  :rows="4"
                  placeholder="请输入合同条款"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 项目时间 -->
          <div class="section-title">项目时间</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="计划开始日期" prop="start_date">
                <el-date-picker
                  v-model="form.start_date"
                  type="date"
                  placeholder="请选择计划开始日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="计划结束日期" prop="end_date">
                <el-date-picker
                  v-model="form.end_date"
                  type="date"
                  placeholder="请选择计划结束日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 预算信息 -->
          <div class="section-title">预算信息</div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="总预算" prop="budget_total_cost">
                <el-input-number
                  v-model="form.budget_total_cost"
                  :precision="2"
                  :step="1000"
                  :min="0"
                  placeholder="请输入总预算"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="预计利润率" prop="profit_margin">
                <el-input-number
                  v-model="form.profit_margin"
                  :precision="2"
                  :step="0.5"
                  :min="0"
                  :max="100"
                  placeholder="请输入预计利润率"
                  style="width: 100%;"
                />
                <template #append>%</template>
              </el-form-item>
            </el-col>
          </el-row>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <el-button @click="goBack">返回项目列表</el-button>
            <el-button type="primary" @click="handleNext">查看下一步</el-button>
          </div>
        </el-form>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPersonnel, type Personnel } from '../../../api/resource'
import { getProjectDetail } from '../../../api/project'

const router = useRouter()
const route = useRoute()

// 获取项目ID
const projectId = computed(() => route.params.id as string)

// 人员列表数据
const personnelList = ref<Personnel[]>([])

// 表单数据
const form = ref({
  name: '',
  leader: '',
  description: '',
  contract_number: '',
  contract_amount: 0,
  contract_start_date: '',
  contract_end_date: '',
  contract_terms: '',
  start_date: '',
  end_date: '',
  budget_total_cost: 0,
  profit_margin: 0
})

// 表单验证规则
const rules = {
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' }
  ],
  leader: [
    { required: true, message: '请选择项目经理', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入项目描述', trigger: 'blur' }
  ],
  start_date: [
    { required: true, message: '请选择计划开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择计划结束日期', trigger: 'change' }
  ],
  budget_total_cost: [
    { required: true, message: '请输入总预算', trigger: 'blur' }
  ]
}

// 获取项目详情
const fetchProjectDetail = async () => {
  try {
    const project = await getProjectDetail(Number(projectId))
    
    // 填充表单数据
    form.value = {
      name: project.name || '',
      leader: project.leader || '',
      description: project.description || '',
      contract_number: project.contract_number || '',
      contract_amount: project.contract_amount || 0,
      contract_start_date: project.contract_start_date || '',
      contract_end_date: project.contract_end_date || '',
      contract_terms: project.contract_terms || '',
      start_date: project.start_date || '',
      end_date: project['计划结束日期'] || '',
      budget_total_cost: project.budget_total_cost || 0,
      profit_margin: project.profit_margin || 0
    }
  } catch (error) {
    console.error('获取项目详情失败:', error)
    ElMessage.error('获取项目详情失败')
  }
}

// 获取人员列表
const fetchPersonnel = async () => {
  try {
    const response = await getPersonnel({
      limit: 1000 // 获取所有人员
    })
    personnelList.value = response
  } catch (error) {
    console.error('获取人员列表失败:', error)
    ElMessage.error('获取人员列表失败')
  }
}

// 跳转到下一步
const handleNext = () => {
  router.push({
    name: 'ProjectDetailCost',
    params: { id: projectId.value }
  })
}

// 返回项目列表
const goBack = () => {
  router.push('/projects')
}

// 初始化
onMounted(async () => {
  await Promise.all([
    fetchPersonnel(),
    fetchProjectDetail()
  ])
})
</script>

<style scoped>
.project-create-container {
  padding: 20px;
}

.project-create-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin: 30px 0 15px 0;
  color: #303133;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.form-container {
  max-width: 1000px;
  margin: 0 auto;
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

/* 只读样式 */
:deep(.el-input.is-disabled .el-input__inner),
:deep(.el-textarea.is-disabled .el-textarea__inner),
:deep(.el-select.is-disabled .el-input__inner),
:deep(.el-input-number.is-disabled .el-input__inner) {
  background-color: #f5f7fa;
  border-color: #e4e7ed;
  color: #606266;
}
</style>
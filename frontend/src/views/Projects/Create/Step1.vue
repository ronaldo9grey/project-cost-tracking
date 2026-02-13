<template>
  <div class="project-create-container">
    <el-card shadow="hover" class="project-create-card">
      <template #header>
        <div class="card-header">
          <h2>{{ isEditMode ? `编辑项目 - ${formData.name}` : formData.name ? `新建项目 - ${formData.name}` : '新建项目' }} - 基本信息</h2>
          <el-breadcrumb separator="/" separator-class="el-icon-arrow-right">
            <el-breadcrumb-item :to="{ path: '/projects' }">项目管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ isEditMode ? `编辑项目 - ${formData.name}` : formData.name ? `新建项目 - ${formData.name}` : '新建项目' }}</el-breadcrumb-item>
            <el-breadcrumb-item>基本信息</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <!-- 步骤指示器 -->
      <el-steps :active="0" align-center>
        <el-step title="基本信息" description="设置项目基本信息和合同信息" />
        <el-step title="成本设定" description="设置四大成本的预算和实际值" />
        <el-step title="任务设定" description="创建项目任务" />
        <el-step title="文档管理" description="管理项目相关文档" />
      </el-steps>
      
      <div class="form-container">
        <el-form
          ref="projectForm"
          :model="formData"
          label-width="120px"
          :rules="formRules"
          class="project-form"
        >
          <el-row :gutter="20">
            <el-col :span="12">
              <el-divider content-position="left">基本信息</el-divider>
              <el-form-item label="项目名称" prop="name" required>
                <el-input v-model="formData.name" placeholder="请输入项目名称" />
              </el-form-item>
              
              <el-form-item label="项目描述">
                <el-input
                  v-model="formData.describe"
                  type="textarea"
                  placeholder="请输入项目描述"
                  rows="3"
                />
              </el-form-item>
              
              <el-form-item label="项目状态" required>
                <el-select v-model="formData.status" placeholder="请选择项目状态">
                  <el-option label="规划中" value="规划中" />
                  <el-option label="进行中" value="进行中" />
                  <el-option label="已完成" value="已完成" />
                  <el-option label="已暂停" value="已暂停" />
                  <el-option label="已取消" value="已取消" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="项目经理" prop="leader" required>
                <el-select 
                  v-model="formData.leader" 
                  placeholder="请输入员工ID或姓名搜索"
                  filterable
                  :filter-method="filterPersonnel"
                  remote
                  :remote-method="remoteSearchPersonnel"
                  clearable
                >
                  <el-option
                    v-for="person in filteredPersonnel"
                    :key="person.id"
                    :label="getPersonnelDisplayName(person)"
                    :value="person.employee_id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="项目进度" prop="progress" required>
                <el-slider
                  v-model="formData.progress"
                  :format-tooltip="formatProgress"
                  :step="5"
                  :min="0"
                  :max="100"
                />
                <div class="progress-display">{{ formData.progress }}%</div>
              </el-form-item>
              
              <el-form-item label="开始日期" prop="start_date" required>
                <el-date-picker
                  v-model="formData.start_date"
                  type="date"
                  placeholder="选择项目开始日期"
                  style="width: 100%;"
                />
              </el-form-item>
              
              <el-form-item label="结束日期" prop="end_date" required>
                <el-date-picker
                  v-model="formData.end_date"
                  type="date"
                  placeholder="选择项目结束日期"
                  style="width: 100%;"
                />
              </el-form-item>
            </el-col>
            
            <el-col :span="12">
              <el-divider content-position="left">合同信息</el-divider>
              
              <el-form-item label="合同编号" prop="contract_no" required>
                <el-input v-model="formData.contract_no" placeholder="请输入合同编号" />
              </el-form-item>
              
              <el-form-item label="合同签订日期" prop="contract_date" required>
                <el-date-picker
                  v-model="formData.contract_date"
                  type="date"
                  placeholder="选择合同签订日期"
                  style="width: 100%;"
                />
              </el-form-item>
              
              <el-form-item label="合同金额" prop="contract_amount" required>
                <el-input 
                  v-model="displayData.contract_amount" 
                  placeholder="请输入合同金额"
                  @input="handleFinancialInput('contract_amount', displayData.contract_amount)"
                  @blur="handleFinancialBlur('contract_amount')"
                >
                  <template #prepend>¥</template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="税率" prop="tax_rate" required>
                <el-input 
                  v-model="formData.tax_rate" 
                  placeholder="请输入税率（%）" 
                  type="number" 
                  min="0" 
                  max="100"
                  @input="calculateRevenue"
                />
              </el-form-item>
              
              <el-form-item label="营业收入" prop="revenue" required>
                <el-input 
                  v-model="displayData.revenue" 
                  placeholder="自动计算" 
                  readonly
                >
                  <template #prepend>¥</template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="目标利润" prop="target_profit" required>
                <el-input 
                  v-model="displayData.target_profit" 
                  placeholder="请输入目标利润"
                  @input="handleFinancialInput('target_profit', displayData.target_profit)"
                  @blur="handleFinancialBlur('target_profit')"
                >
                  <template #prepend>¥</template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
        
        <!-- 操作按钮 -->
        <div class="action-buttons">
          <el-button @click="handleBackToList">返回列表</el-button>
          <el-button type="primary" @click="handleNext">保存并进入下一步</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { createProject, updateProject, getProjectDetail, checkProjectName, type ProjectCreate, type ProjectUpdate } from '../../../api/project'
import { getPersonnel, type Personnel } from '../../../api/resource'

const router = useRouter()
const route = useRoute()

// 表单引用
const projectForm = ref()

// 人员列表数据
const personnelList = ref<Personnel[]>([])

// 过滤后的人员列表（用于项目经理选择）
const filteredPersonnel = ref<Personnel[]>([])

// 表单数据 - 存储原始数值用于计算和验证
const formData = ref({
  id: null as number | null,
  name: '',
  describe: '',
  status: '规划中',
  leader: '', // 存储员工ID
  start_date: null as Date | null,
  end_date: null as Date | null,
  // 合同信息
  contract_no: '',
  contract_date: null as Date | null,
  contract_amount: 0,
  tax_rate: 13,
  revenue: 0,
  target_profit: 0,
  progress: 0
})

// 原始数据 - 用于比较数据是否发生变化
const originalFormData = ref<typeof formData.value>({
  id: null,
  name: '',
  describe: '',
  status: '规划中',
  leader: '', // 存储员工ID
  start_date: null,
  end_date: null,
  contract_no: '',
  contract_date: null,
  contract_amount: 0,
  tax_rate: 13,
  revenue: 0,
  target_profit: 0,
  progress: 0
})

// 显示数据 - 用于显示格式化的金融字段
const displayData = ref({
  contract_amount: '',
  revenue: '',
  target_profit: ''
})

// 初始化显示数据
const initDisplayData = () => {
  displayData.value.contract_amount = formatToFinancial(formData.value.contract_amount)
  displayData.value.revenue = formatToFinancial(formData.value.revenue)
  displayData.value.target_profit = formatToFinancial(formData.value.target_profit)
}

// 表单验证规则
const formRules = ref({
  name: [
    { required: true, message: '请输入项目名称', trigger: 'blur' },
    { min: 1, max: 200, message: '项目名称长度在 1 到 200 个字符', trigger: 'blur' },
    {
      validator: async (rule: any, value: string, callback: any) => {
        if (value) {
          // 如果是编辑模式且项目名称未发生变化，则跳过重复检查
          if (isEditMode.value && value === originalFormData.value.name) {
            callback()
            return
          }
          
          try {
            // 调用专门的API检查项目名称是否重复，编辑模式下排除自己
            const response = await checkProjectName(value, isEditMode.value ? projectId.value : undefined)
            if (response.exists) {
              callback(new Error('项目名称重复，请重新输入'))
            } else {
              callback()
            }
          } catch (error) {
            console.error('检查项目名称失败:', error)
            callback(new Error('检查项目名称失败，请重试'))
          }
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  leader: [
    { required: true, message: '请选择项目经理', trigger: 'change' }
  ],
  status: [
    { required: true, message: '请选择项目状态', trigger: 'change' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' },
    {
      validator: (rule: any, value: Date | null, callback: any) => {
        if (value && formData.value.start_date && value <= formData.value.start_date) {
          callback(new Error('结束日期必须晚于开始日期'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  contract_no: [
    { required: true, message: '请输入合同编号', trigger: 'blur' }
  ],
  contract_date: [
    { required: true, message: '请选择合同签订日期', trigger: 'change' }
  ],
  contract_amount: [
    { required: true, message: '请输入合同金额', trigger: 'blur' },
    {
      validator: (rule: any, value: number, callback: any) => {
        if (value <= 0) {
          callback(new Error('合同金额必须大于0'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  tax_rate: [
    { required: true, message: '请输入税率', trigger: 'blur' },
    {
      validator: (rule: any, value: number, callback: any) => {
        if (value < 0 || value > 100) {
          callback(new Error('税率必须在0-100之间'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  revenue: [
    { required: true, message: '营业收入不能为空', trigger: 'blur' }
  ],
  target_profit: [
    { required: true, message: '请输入目标利润', trigger: 'blur' }
  ],
  progress: [
    { required: true, message: '请设置项目进度', trigger: 'change' }
  ]
})

// 计算属性
const isEditMode = computed(() => !!projectId.value)
const projectId = computed(() => route.params.projectId ? parseInt(route.params.projectId as string) : null)

// 过滤后的人员列表（用于项目经理选择）
const personnelFilter = ref('')
const personnelSearchLoading = ref(false)

// 过滤人员列表（用于下拉框本地过滤）
const filterPersonnel = (query: string) => {
  if (!query) {
    filteredPersonnel.value = personnelList.value
    return
  }
  
  const lowerQuery = query.toLowerCase()
  filteredPersonnel.value = personnelList.value.filter(person => 
    person.name.toLowerCase().includes(lowerQuery) ||
    (person.employee_id && person.employee_id.toLowerCase().includes(lowerQuery))
  )
}

// 远程搜索人员列表
const remoteSearchPersonnel = async (query: string) => {
  if (!query || query.trim().length < 1) {
    filteredPersonnel.value = personnelList.value
    return
  }
  
  personnelSearchLoading.value = true
  try {
    const response = await getPersonnel({ 
      limit: 50,
      name: query,
      employee_id: query
    })
    
    // 如果响应是SuccessResponse格式，提取data
    const personnelData = response.data ? response.data : response
    
    filteredPersonnel.value = personnelData || []
  } catch (error) {
    console.error('搜索人员失败:', error)
    ElMessage.error('搜索人员失败')
    filteredPersonnel.value = []
  } finally {
    personnelSearchLoading.value = false
  }
}

// 获取人员显示名称
const getPersonnelDisplayName = (person: Personnel): string => {
  return `${person.employee_id} - ${person.name}`
}

// 格式化进度显示
const formatProgress = (val: number) => {
  return `${val}%`
}

// 格式化金融数值为带逗号的格式
const formatToFinancial = (value: number | string): string => {
  if (!value || value === 0) return ''
  const num = typeof value === 'string' ? parseFloat(value) : value
  return num.toLocaleString('zh-CN', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

// 格式化日期
const parseDate = (dateStr: string | null): Date | null => {
  if (!dateStr) return null
  const date = new Date(dateStr)
  return isNaN(date.getTime()) ? null : date
}

// 格式化日期为字符串
const formatDate = (date: Date | null): string | null => {
  if (!date) return null
  return date.toISOString().split('T')[0]
}

// 处理金融字段输入
const handleFinancialInput = (field: string, displayValue: string) => {
  // 移除所有非数字和小数点的字符
  const cleanValue = displayValue.replace(/[^\d.]/g, '')
  // 转换为数字
  const numValue = parseFloat(cleanValue) || 0
  
  // 更新表单数据
  formData.value[field as keyof typeof formData.value] = numValue
  
  // 重新格式化显示
  if (field === 'contract_amount') {
    calculateRevenue()
  }
}

// 处理金融字段失焦
const handleFinancialBlur = (field: string) => {
  const value = formData.value[field as keyof typeof formData.value] as number
  displayData.value[field] = formatToFinancial(value)
}

// 计算营业收入
const calculateRevenue = () => {
  const contractAmount = formData.value.contract_amount || 0
  const taxRate = formData.value.tax_rate || 0
  const revenue = contractAmount / (1 + taxRate / 100)
  
  formData.value.revenue = revenue
  displayData.value.revenue = formatToFinancial(revenue)
}

// 获取人员列表
const fetchPersonnel = async () => {
  try {
    const response = await getPersonnel({ limit: 1000 })
    // 如果响应是SuccessResponse格式，提取data
    personnelList.value = response.data ? response.data : response
    filteredPersonnel.value = personnelList.value
  } catch (error) {
    console.error('获取人员列表失败:', error)
    ElMessage.error('获取人员列表失败')
  }
}

// 检查数据是否有变化
const hasChanges = computed(() => {
  return JSON.stringify(formData.value) !== JSON.stringify(originalFormData.value)
})

// 处理下一步
const handleNext = async () => {
  if (!projectForm.value) return

  await projectForm.value.validate(async (valid: boolean) => {
    if (!valid) {
      ElMessage.error('请检查表单信息')
      return
    }

    try {
      const projectData = prepareProjectData()
      
      if (isEditMode.value && projectId.value) {
        // 更新项目
        await updateProject(projectId.value, projectData)
        ElMessage.success('项目更新成功')
      } else {
        // 创建项目
        const response = await createProject(projectData)
        if (response && response.id) {
          // 保存项目ID到路由参数
          router.replace({
            name: 'ProjectCreateStep2',
            params: { projectId: response.id.toString() }
          })
          ElMessage.success('项目创建成功')
          return
        }
      }

      // 如果是编辑模式或者创建成功后，进入下一步
      if (projectId.value) {
        router.push({
          name: 'ProjectCreateStep2',
          params: { projectId: projectId.value.toString() }
        })
      }
    } catch (error) {
      console.error('保存项目失败:', error)
      ElMessage.error('保存项目失败')
    }
  })
}

// 准备项目数据
const prepareProjectData = (): ProjectCreate | ProjectUpdate => {
  return {
    name: formData.value.name,
    describe: formData.value.describe,
    status: formData.value.status,
    leader: formData.value.leader,
    start_date: formatDate(formData.value.start_date)!,
    end_date: formatDate(formData.value.end_date)!,
    contract_no: formData.value.contract_no,
    contract_date: formatDate(formData.value.contract_date)!,
    contract_amount: formData.value.contract_amount,
    tax_rate: formData.value.tax_rate,
    revenue: formData.value.revenue,
    target_profit: formData.value.target_profit,
    progress: formData.value.progress
  }
}

// 返回项目列表
const handleBackToList = () => {
  router.push('/projects')
}

// 初始化表单数据
const initFormData = () => {
  // 初始化显示数据
  initDisplayData()
  
  // 设置默认人员（当前登录用户）
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
  if (currentUser.employee_name) {
    formData.value.leader = currentUser.employee_name
  }
}

// 加载项目详情（编辑模式）
const loadProjectDetail = async () => {
  if (!isEditMode.value || !projectId.value) return

  try {
    const project = await getProjectDetail(projectId.value)
    
    // 填充表单数据
    formData.value = {
      id: project.id,
      name: project.name,
      describe: project.describe || '',
      status: project.status,
      leader: project.leader, // 这里存储的是员工ID
      start_date: parseDate(project.start_date),
      end_date: parseDate(project.end_date),
      contract_no: project.contract_no,
      contract_date: parseDate(project.contract_date),
      contract_amount: project.contract_amount,
      tax_rate: project.tax_rate,
      revenue: project.revenue,
      target_profit: project.target_profit,
      progress: project.progress || 0
    }
    
    // 如果有项目经理信息，需要找到对应的人员记录
    if (project.leader && personnelList.value.length > 0) {
      const selectedPerson = personnelList.value.find(p => p.employee_id === project.leader)
      if (selectedPerson) {
        // 确保过滤列表中包含当前选中的经理
        if (!filteredPersonnel.value.find(p => p.employee_id === selectedPerson.employee_id)) {
          filteredPersonnel.value.push(selectedPerson)
        }
      }
    }
    
    // 保存原始数据用于比较，直接赋值，保持Date对象类型
    originalFormData.value = {
      ...formData.value,
      start_date: formData.value.start_date ? new Date(formData.value.start_date) : null,
      end_date: formData.value.end_date ? new Date(formData.value.end_date) : null,
      contract_date: formData.value.contract_date ? new Date(formData.value.contract_date) : null
    }
    
    // 初始化显示数据
    initDisplayData()
  } catch (error) {
    console.error('加载项目详情失败:', error)
    ElMessage.error('加载项目详情失败')
    // 如果加载失败，返回项目列表
    router.push('/projects')
  }
}

// 组件挂载时初始化
onMounted(async () => {
  await Promise.all([
    fetchPersonnel(),
    isEditMode.value ? loadProjectDetail() : Promise.resolve()
  ])
  
  // 如果不是编辑模式，初始化表单数据
  if (!isEditMode.value) {
    initFormData()
  }
})
</script>

<style scoped>
.project-create-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.project-create-card {
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
  font-size: 20px;
  font-weight: 500;
}

.form-container {
  margin-top: 30px;
}

.project-form {
  margin-bottom: 30px;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
}

.progress-display {
  margin-left: 15px;
  color: #409EFF;
  font-weight: 500;
  min-width: 50px;
  text-align: center;
}

.el-divider {
  margin-bottom: 20px;
}

.el-divider__text {
  color: #409EFF;
  font-weight: 600;
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .project-create-container {
    padding: 10px;
  }
  
  .el-row {
    margin: 0 !important;
  }
  
  .el-col {
    margin-bottom: 20px;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
}

/* 步骤指示器样式 */
:deep(.el-step__title) {
  font-size: 14px;
}

:deep(.el-step__description) {
  font-size: 12px;
  margin-top: 5px;
}

/* 当前步骤使用默认颜色 */
:deep(.el-step.is-success .el-step__title),
:deep(.el-step.is-success .el-step__description),
:deep(.el-step.is-active .el-step__title),
:deep(.el-step.is-active .el-step__description) {
  color: inherit !important;
}
</style>
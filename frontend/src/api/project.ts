import request from './axios'

// 项目相关API

export interface Project {
  id: number
  name: string
  describe: string
  start_date: string
  "计划结束日期": string
  "实际结束日期"?: string
  budget_total_cost: number
  actual_total_cost: number
  contract_amount: number
  status: string
  progress: number
  leader: string
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
    name: string
    describe: string
    start_date: string | null
    end_date: string | null
    status: string
    leader: string
    // 合同信息
    contract_no: string
    contract_date: string | null
    contract_amount: number
    tax_rate: number
    revenue: number
    target_profit: number
}

export interface ProjectUpdate {
    name?: string
    describe?: string
    start_date?: string | null
    end_date?: string | null
    status?: string
    progress?: number
    leader?: string
    // 合同信息
    contract_no?: string
    contract_date?: string | null
    contract_amount?: number
    tax_rate?: number
    revenue?: number
    target_profit?: number
}

// 任务相关接口
export interface Task {
  task_id: number
  project_id: number
  project_name?: string
  task_name: string
  start_date: string
  end_date: string
  actual_end_date?: string
  difdays?: number
  completed?: boolean
  progress?: number
  assignee?: string
  create_time?: string
  update_time?: string
}

export interface TaskCreate {
  task_name: string
  start_date: string
  end_date: string
  assignee?: string
  progress?: number
}

/**
 * 获取项目列表
 * @param params 查询参数
 */
export const getProjects = (params?: { page?: number; size?: number; status?: string; name?: string }) => {
  return request.get<{ items: Project[]; total: number; page: number; size: number; total_pages: number }>('v1/projects/', { params })
}

/**
 * 检查项目名称是否已存在
 * @param name 项目名称
 * @param excludeId 排除的项目ID（用于编辑模式）
 */
export const checkProjectName = (name: string, excludeId?: number) => {
  return request.get<{ exists: boolean; message: string }>(`v1/projects/check-name/${name}`, {
    params: excludeId ? { exclude_id: excludeId } : {},
    cache: false // 移除缓存，确保每次都获取最新结果
  })
}

/**
 * 获取项目详情
 * @param projectId 项目ID
 */
export const getProjectDetail = (projectId: number) => {
  return request.get<Project>(`v1/projects/${projectId}/`, {
    cache: true // 添加缓存
  })
}

/**
 * 创建项目
 * @param project 项目信息
 */
export const createProject = (project: ProjectCreate) => {
  return request.post<{ id: number }>('v1/projects/', project)
}

/**
 * 更新项目
 * @param projectId 项目ID
 * @param project 项目信息
 */
export const updateProject = (projectId: number, project: ProjectUpdate) => {
  return request.put<Project>(`v1/projects/${projectId}/`, project)
}

/**
 * 删除项目
 * @param projectId 项目ID
 */
export const deleteProject = (projectId: number) => {
  return request.delete(`v1/projects/${projectId}/`)
}

/**
 * 获取项目任务列表
 * @param projectId 项目ID
 */
export const getProjectTasks = (projectId: number) => {
  return request.get<Task[]>(`v1/projects/${projectId}/tasks/`, {
    cache: false // 禁用缓存，确保获取最新数据
  })
}

/**
 * 获取所有项目的任务列表（用于看板）
 */
export const getAllTasks = () => {
  return request.get<Task[]>('v1/projects/tasks', {
    cache: false // 禁用缓存，确保获取最新数据
  })
}

/**
 * 创建项目任务
 * @param projectId 项目ID
 * @param task 任务信息
 */
export const createProjectTask = (projectId: number, task: TaskCreate) => {
  return request.post<Task>(`v1/projects/${projectId}/tasks/`, task)
}

/**
 * 获取项目成本汇总
 * @param projectId 项目ID
 */
export const getProjectCosts = (projectId: number) => {
  return request.get(`v1/projects/${projectId}/costs/`, {
    cache: false // 禁用缓存，确保获取最新数据
  })
}

/**
 * 获取项目概览统计
 */
export const getProjectOverviewStatistics = () => {
  return request.get<{ total_projects: number; status_counts: Record<string, number>; total_contract_amount: number; total_budget_cost: number; total_actual_cost: number; cost_variance: number; avg_progress: number }>(`v1/projects/statistics/overview`, {
    cache: true // 添加缓存
  })
}

/**
 * 获取外包服务类型列表
 */
export const getOutsourcingServiceTypes = () => {
  return request.get(`v1/resource/outsourcing-service-types/`, {
    cache: true // 添加缓存
  })
}

/**
 * 获取间接成本类型列表
 */
export const getIndirectCostTypes = () => {
  return request.get(`v1/resource/indirect-cost-types/`, {
    cache: true // 添加缓存
  })
}

/**
 * 批量创建项目任务
 * @param tasks 任务列表
 */
export const batchCreateProjectTasks = (tasks: { project_id: number; task_name: string; start_date: string; end_date: string; assignee?: string; progress?: number }[]) => {
  return request.post(`v1/projects/tasks/batch`, tasks)
}

/**
 * 批量上传任务附件
 * @param attachments 附件列表
 */
export const batchUploadTaskAttachments = (attachments: { task_id: number; file_name: string; file_url: string; file_size?: number }[]) => {
  return request.post(`v1/projects/task-attachments/batch`, attachments)
}

/**
 * 批量创建材料成本
 * @param costs 成本列表
 */
export const batchCreateMaterialCosts = (costs: { project_id: number; material_id: string; quantity: number; unit_price: number; total_cost: number; cost_date: string }[]) => {
  return request.post(`v1/cost/material/batch`, costs)
}

/**
 * 批量创建人工成本
 * @param costs 成本列表
 */
export const batchCreateLaborCosts = (costs: { project_id: number; employee_id: string; work_date: string; hours: number; hourly_rate: number; total_cost: number }[]) => {
  return request.post(`v1/cost/labor/batch`, costs)
}

/**
 * 批量创建外包成本
 * @param costs 成本列表
 */
export const batchCreateOutsourcingCosts = (costs: { project_id: number; service_type_id: number; cost_amount: number; cost_date: string; description?: string }[]) => {
  return request.post(`v1/cost/outsourcing/batch`, costs)
}

/**
 * 批量创建间接成本
 * @param costs 成本列表
 */
export const batchCreateIndirectCosts = (costs: { project_id: number; cost_type_id: number; cost_amount: number; cost_date: string; description?: string }[]) => {
  return request.post(`v1/cost/indirect/batch`, costs)
}

/**
 * 获取任务附件列表
 * @param projectId 项目ID
 * @param taskId 任务ID
 */
export const getTaskAttachments = (projectId: number, taskId: number) => {
  return request.get(`v1/projects/${projectId}/task-attachments/${taskId}`, {
    cache: false // 禁用缓存，确保获取最新数据
  })
}

/**
 * 获取项目文档列表
 * @param projectId 项目ID
 */
export const getProjectDocuments = (projectId: number) => {
  return request.get(`v1/projects/${projectId}/documents/`, {
    cache: false // 禁用缓存，确保获取最新数据
  })
}

/**
 * 批量创建项目任务附件
 * @param attachments 附件列表
 */
export const batchCreateProjectTaskAttachments = (attachments: { task_id: number; file_name: string; file_url: string; file_size?: number }[]) => {
  return request.post(`v1/projects/task-attachments/batch`, attachments)
}

/**
 * 获取项目任务附件列表
 * @param projectId 项目ID
 * @param taskId 任务ID
 */
export const getProjectTaskAttachments = (projectId: number, taskId: number) => {
  return request.get(`v1/projects/${projectId}/task-attachments/${taskId}`, {
    cache: false // 禁用缓存，确保获取最新数据
  })
}
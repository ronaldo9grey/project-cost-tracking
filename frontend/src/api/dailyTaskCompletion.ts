import request from '@/api/axios'

// 日清表接口类型定义
export interface DailyTaskCompletion {
  id?: number
  report_id?: number
  project_id?: string
  project_name?: string
  task_id?: string
  task_name?: string
  task_source: string
  start_time?: string
  end_time?: string
  hours_spent: number
  planned_hours: number
  progress_status: string
  progress_percentage: number
  delay_hours: number
  work_content: string
  key_work_tracking?: string
  result?: string
  measures?: string
  self_evaluation?: string
  supervisor_evaluation?: string
  evaluation_comment?: string
  tomorrow_plan?: string
  status: string
  is_key_work: boolean
  create_time?: string
  update_time?: string
  is_deleted?: boolean
}

export interface DailyTaskCompletionCreate {
  report_id: number
  project_id?: string
  project_name?: string
  task_id?: string
  task_name?: string
  task_source?: string
  start_time?: string
  end_time?: string
  hours_spent?: number
  planned_hours?: number
  progress_status?: string
  progress_percentage?: number
  delay_hours?: number
  work_content: string
  key_work_tracking?: string
  result?: string
  measures?: string
  self_evaluation?: string
  supervisor_evaluation?: string
  evaluation_comment?: string
  tomorrow_plan?: string
  status?: string
  is_key_work?: boolean
}

export interface DailyTaskCompletionUpdate {
  id?: number
  report_id?: number
  project_id?: string
  project_name?: string
  task_id?: string
  task_name?: string
  task_source?: string
  start_time?: string
  end_time?: string
  hours_spent?: number
  planned_hours?: number
  progress_status?: string
  progress_percentage?: number
  delay_hours?: number
  work_content?: string
  key_work_tracking?: string
  result?: string
  measures?: string
  self_evaluation?: string
  supervisor_evaluation?: string
  evaluation_comment?: string
  tomorrow_plan?: string
  status?: string
  is_key_work?: boolean
}

export interface DailyTaskCompletionListResponse {
  items: DailyTaskCompletion[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface MyTaskItem {
  task_id: string
  task_name: string
  project_id: string
  project_name: string
}

export interface MyTaskResponse {
  items: MyTaskItem[]
  total: number
  message: string
}

export interface ReportSummary {
  total_hours: number
  completed_tasks: number
  ongoing_tasks: number
  key_works: number
  average_progress: number
}

export interface ReportSummaryResponse {
  report_id: number
  summary: ReportSummary
  message: string
}

// 创建日清表记录
export const createDailyTaskCompletion = (data: DailyTaskCompletionCreate): Promise<DailyTaskCompletion> => {
  return request.post<DailyTaskCompletion>('v1/daily-task-completion', data).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 获取日清表记录列表
export const getDailyTaskCompletions = (params?: {
  report_date?: string
  start_date?: string
  end_date?: string
  status?: string
  page?: number
  size?: number
}): Promise<DailyTaskCompletionListResponse> => {
  return request.get<DailyTaskCompletionListResponse>('v1/daily-task-completion', { params }).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 获取指定日报的日清表记录
export const getTaskCompletionsByReport = (reportId: number): Promise<DailyTaskCompletion[]> => {
  return request.get<DailyTaskCompletion[]>(`v1/daily-task-completion/report/${reportId}`).then(response => {
    // 后端直接返回数组，不需要.data
    return response as any
  })
}

// 获取日清表记录详情
export const getDailyTaskCompletion = (taskCompletionId: number): Promise<DailyTaskCompletion> => {
  return request.get<DailyTaskCompletion>(`v1/daily-task-completion/${taskCompletionId}`).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 更新日清表记录
export const updateDailyTaskCompletion = (taskCompletionId: number, data: DailyTaskCompletionUpdate): Promise<DailyTaskCompletion> => {
  return request.put<DailyTaskCompletion>(`v1/daily-task-completion/${taskCompletionId}`, data).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 删除日清表记录
export const deleteDailyTaskCompletion = (taskCompletionId: number): Promise<{ message: string }> => {
  return request.delete<{ message: string }>(`v1/daily-task-completion/${taskCompletionId}`).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 批量创建日清表记录
export const bulkCreateTaskCompletions = (reportId: number, taskCompletions: DailyTaskCompletionCreate[]): Promise<DailyTaskCompletion[]> => {
  return request.post<DailyTaskCompletion[]>(`v1/daily-task-completion/report/${reportId}/bulk`, taskCompletions).then(response => {
    // 后端直接返回数组，不需要.data
    return response as any
  })
}

// 获取我的任务列表（用于任务选择器）
export const getMyTasksAvailable = (params?: {
  status?: string
  keyword?: string
  limit?: number
}): Promise<MyTaskResponse> => {
  return request.get<MyTaskResponse>('v1/daily-task-completion/my-tasks/available', { params }).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 获取日报汇总信息
export const getReportSummary = (reportId: number): Promise<ReportSummaryResponse> => {
  return request.get<ReportSummaryResponse>(`v1/daily-task-completion/report/${reportId}/summary`).then(response => {
    // 后端直接返回对象，不需要.data
    return response as any
  })
}

// 快速添加日清表记录
export const quickAddTaskCompletion = (reportId: number, quickData: {
  work_content: string
  task_name?: string
  project_name?: string
  hours_spent?: number
  progress_percentage?: number
  status?: string
  is_key_work?: boolean
}): Promise<DailyTaskCompletion[]> => {
  return request.post<DailyTaskCompletion[]>(`v1/daily-task-completion/quick-add/${reportId}`, quickData).then(response => {
    // 后端直接返回数组，不需要.data
    return response as any
  })
}
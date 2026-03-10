import request from './unifiedApi'

export interface MyTask {
  task_id: string
  task_name: string
  project_id: string
  project_name: string
  assignee: string
  assignee_id: string
  start_date: string
  end_date: string
  status: string
  progress: number
}

export interface DailyReport {
  id: number
  report_date: string
  employee_id: string
  employee_name: string
  tomorrow_plan: string
  work_target: string
  key_work_tracking: string
  planned_hours: number
  actual_hours: number
  status: string
  submitted_at: string
  create_time: string
  update_time: string
}

// 工作事项接口
export interface WorkItem {
  key: string
  id?: number
  report_id?: number
  project_id?: string
  project_name?: string
  task_id?: string
  task_name?: string
  work_content: string
  start_time?: string
  end_time?: string
  hours_spent?: number
  progress_status?: string
  progress_percentage?: number
  result?: string
  measures?: string
  evaluation?: string
}

// 主表创建接口（只包含基本信息）
export interface DailyReportCreate {
  report_date: string
  employee_id?: string
  employee_name?: string
  work_target?: string
  key_work_tracking?: string
  tomorrow_plan?: string
  planned_hours?: number
}

// 完整日报创建接口（包含工作事项）
export interface DailyReportWithItems {
  report: DailyReportCreate
  work_items: WorkItem[]
}

export interface DailyReportListResponse {
  items: DailyReport[]
  total: number
  page: number
  size: number
  total_pages: number
}

export interface DailyReportEvaluate {
  supervisor_score: number
  supervisor_comment?: string
}

export const getMyTasks = (params?: { status?: string; keyword?: string }) => {
  return request.get<MyTask[]>('v1/daily-report/my-tasks', { params }).then(response => {
    // 后端直接返回数组，不需要.data
    return Array.isArray(response) ? response : []
  })
}

export const getMyReports = (params?: {
  report_date?: string
  start_date?: string
  end_date?: string
  status?: string
  page?: number
  size?: number
}) => {
  // 真实API调用 - 连接后端数据库
  return request.get<DailyReportListResponse>('v1/daily-report/my-reports', { params })
}

export const getDailyReport = (reportId: number) => {
  return request.get<DailyReport>(`v1/daily-report/my-reports/${reportId}`)
}

export const createDailyReport = (report: DailyReportCreate) => {
  return request.post<DailyReport>('v1/daily-report/my-reports', report)
}

// 创建包含工作事项的完整日报
export const createDailyReportWithItems = (reportWithItems: DailyReportWithItems) => {
  return request.post<DailyReport>('v1/daily-report/my-reports/with-items', reportWithItems)
}

// 更新工作事项
export const updateWorkItems = (reportId: number, workItems: WorkItem[]) => {
  return request.post(`v1/daily-report/my-reports/${reportId}/work-items`, { work_items: workItems })
}

export const updateDailyReport = (reportId: number, report: Partial<DailyReportCreate>) => {
  return request.put<DailyReport>(`v1/daily-report/my-reports/${reportId}`, report)
}

export const submitDailyReport = (reportId: number) => {
  return request.post<DailyReport>(`v1/daily-report/my-reports/${reportId}/submit`)
}

export const deleteDailyReport = (reportId: number) => {
  return request.delete(`v1/daily-report/my-reports/${reportId}`)
}

export const getPendingReports = (params?: { page?: number; size?: number }) => {
  return request.get<DailyReportListResponse>('v1/daily-report/pending-reports', { params })
}

export const evaluateDailyReport = (reportId: number, evaluation: DailyReportEvaluate) => {
  return request.post<DailyReport>(`v1/daily-report/pending-reports/${reportId}/evaluate`, evaluation)
}

export const getSupervisorInfo = (employeeId: string) => {
  return request.get(`v1/daily-report/supervisor-info/${employeeId}`)
}

// ===== 附件管理相关API =====

// 附件接口
export interface DailyReportAttachment {
  id: number
  report_id: number
  file_name: string
  file_data: string
  file_size: number
  file_type: string
  uploader_id: string
  uploader_name: string
  uploaded_at: string
}

// 获取日报附件列表
export const getDailyReportAttachments = (reportId: number) => {
  return request.get<DailyReportAttachment[]>(`v1/daily-report/attachments/${reportId}`)
}

// 获取单个附件详情
export const getDailyReportAttachment = (attachmentId: number) => {
  return request.get<DailyReportAttachment>(`v1/daily-report/attachment/${attachmentId}`)
}

// 上传附件
export const uploadDailyReportAttachment = (reportId: number, file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return request.post<DailyReportAttachment>(`v1/daily-report/attachments/${reportId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 删除附件
export const deleteDailyReportAttachment = (attachmentId: number) => {
  return request.delete(`v1/daily-report/attachments/${attachmentId}`)
}

// 下载附件
export const downloadDailyReportAttachment = (attachmentId: number) => {
  return request.get(`v1/daily-report/attachments/${attachmentId}/download`, {
    responseType: 'blob'
  })
}

// 预览附件
export const previewDailyReportAttachment = (attachmentId: number) => {
  return request.get(`v1/daily-report/attachments/${attachmentId}/preview`)
}

// ===== 日报分析相关API =====

// 获取分析概览数据
export const getAnalysisOverview = (params: {
  start_date?: string
  end_date?: string
  project_id?: string
}) => {
  return request.get(`v1/daily-report/analysis/overview`, { params })
}

// 获取工时趋势数据
export const getHoursTrend = (params: {
  start_date: string
  end_date: string
  group_by?: 'day' | 'week' | 'month'
  project_id?: string
}) => {
  return request.get(`v1/daily-report/analysis/hours-trend`, { params })
}

// 获取项目工时分布数据
export const getProjectDistribution = (params: {
  start_date?: string
  end_date?: string
  limit?: number
}) => {
  return request.get(`v1/daily-report/analysis/project-distribution`, { params })
}

// 获取人员工时排名数据
export const getEmployeeRanking = (params: {
  start_date?: string
  end_date?: string
  limit?: number
  project_id?: string
}) => {
  return request.get(`v1/daily-report/analysis/employee-ranking`, { params })
}

// 获取任务完成率分析数据
export const getTaskCompletion = (params: {
  start_date?: string
  end_date?: string
  project_id?: string
}) => {
  return request.get(`v1/daily-report/analysis/task-completion`, { params })
}

// 获取评价分析数据
export const getEvaluationAnalysis = (params: {
  start_date?: string
  end_date?: string
  project_id?: string
}) => {
  return request.get(`v1/daily-report/analysis/evaluation`, { params })
}

// 获取项目列表
export const getAnalysisProjectList = () => {
  return request.get(`v1/daily-report/analysis/projects`)
}

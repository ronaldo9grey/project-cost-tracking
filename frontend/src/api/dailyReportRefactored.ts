// 重构版日报API接口
// 基于正确的数据库拆分设计

import request from './axios'

// 工作事项接口
export interface WorkItem {
  id?: number
  report_id: number
  project_id?: string
  project_name?: string
  task_id?: string
  task_name?: string
  hours_spent: number
  progress_status?: string
  progress_percentage?: number
  delay_hours?: number
  improvement_result?: string
  key_work_tracking?: string
  work_content?: string
  start_time?: string
  end_time?: string
  result?: string
  measures?: string
  evaluation?: string
}

// 评价接口
export interface Evaluation {
  id?: number
  report_id: number
  supervisor_score?: number
  supervisor_comment?: string
  supervisor_id?: string
  supervisor_name?: string
  evaluated_at?: string
}

// 重构版日报接口
export interface RefactoredDailyReport {
  id: number
  report_date: string
  employee_id: string
  employee_name: string
  
  // 主表基本信息
  work_target?: string
  key_work_tracking?: string
  tomorrow_plan?: string
  planned_hours?: number
  status: string
  submitted_at?: string
  create_time: string
  update_time: string
  
  // 关联表数据
  work_items: WorkItem[]
  evaluations: Evaluation[]
}

// 创建/更新接口
export interface RefactoredDailyReportCreate {
  report_date: string
  work_target?: string
  key_work_tracking?: string
  tomorrow_plan?: string
  planned_hours?: number
  work_items: WorkItem[]
}

// API函数

/**
 * 获取我的任务列表
 */
export const getMyTasks = (params?: { status?: string; keyword?: string }) => {
  return request.get('/api/v1/daily-report/legacy/my-tasks', { params }).then(response => {
    return Array.isArray(response) ? response : []
  })
}

/**
 * 获取我的日报列表
 */
export const getMyReports = (params?: {
  report_date?: string
  start_date?: string
  end_date?: string
  status?: string
  page?: number
  size?: number
}) => {
  return request.get('/api/v1/daily-report/my-reports', { params })
}

/**
 * 创建重构版日报
 */
export const createRefactoredDailyReport = (report: RefactoredDailyReportCreate) => {
  return request.post<RefactoredDailyReport>('/api/v1/daily-report/v2/reports', report)
}

/**
 * 更新重构版日报
 */
export const updateRefactoredDailyReport = (reportId: number, report: Partial<RefactoredDailyReportCreate>) => {
  return request.put<RefactoredDailyReport>(`/api/v1/daily-report/v2/reports/${reportId}`, report)
}

/**
 * 获取重构版日报详情
 */
export const getRefactoredDailyReport = (reportId: number) => {
  return request.get<RefactoredDailyReport>(`/api/v1/daily-report/v2/reports/${reportId}`)
}

/**
 * 提交重构版日报
 */
export const submitRefactoredDailyReport = (reportId: number) => {
  return request.post<RefactoredDailyReport>(`/api/v1/daily-report/v2/reports/${reportId}/submit`)
}

/**
 * 添加工作事项
 */
export const addWorkItem = (reportId: number, workItem: WorkItem) => {
  return request.post(`/api/v1/daily-report/refactored/${reportId}/work-items`, workItem)
}

/**
 * 更新工作事项
 */
export const updateWorkItem = (reportId: number, workItemId: number, workItem: WorkItem) => {
  return request.put(`/api/v1/daily-report/refactored/${reportId}/work-items/${workItemId}`, workItem)
}

/**
 * 删除工作事项
 */
export const deleteWorkItem = (reportId: number, workItemId: number) => {
  return request.delete(`/api/v1/daily-report/refactored/${reportId}/work-items/${workItemId}`)
}

/**
 * 添加评价
 */
export const addEvaluation = (reportId: number, evaluation: Evaluation) => {
  return request.post(`/api/v1/daily-report/refactored/${reportId}/evaluations`, evaluation)
}

/**
 * 更新评价
 */
export const updateEvaluation = (reportId: number, evaluationId: number, evaluation: Evaluation) => {
  return request.put(`/api/v1/daily-report/refactored/${reportId}/evaluations/${evaluationId}`, evaluation)
}

/**
 * 删除评价
 */
export const deleteEvaluation = (reportId: number, evaluationId: number) => {
  return request.delete(`/api/v1/daily-report/refactored/${reportId}/evaluations/${evaluationId}`)
}

// 保持向后兼容的原有API
export const getDailyReport = (reportId: number) => {
  return request.get(`/api/v1/daily-report/my-reports/${reportId}/`)
}

export const createDailyReport = (report: any) => {
  return request.post('/api/v1/daily-report/my-reports', report)
}

export const updateDailyReport = (reportId: number, report: any) => {
  return request.put(`/api/v1/daily-report/my-reports/${reportId}/`, report)
}

export const submitDailyReport = (reportId: number) => {
  return request.post(`/api/v1/daily-report/my-reports/${reportId}/submit`)
}

export const deleteDailyReport = (reportId: number) => {
  return request.delete(`/api/v1/daily-report/my-reports/${reportId}/`)
}
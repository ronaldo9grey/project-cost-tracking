import request from './unifiedApi'

// 日报评价相关接口

export interface ReportItem {
  work_content: string
  start_time: string
  end_time: string
  result: string
  evaluation: string
}

export interface ReportEvaluation {
  supervisor_score: number
  supervisor_comment: string
  supervisor_id: string
  supervisor_name: string
  evaluated_at: string
}

export interface DailyReport {
  id: number
  report_date: string
  employee_id: string
  employee_name: string
  department: string
  position: string
  tomorrow_plan: string
  planned_hours: number
  work_items: ReportItem[]
  evaluation: ReportEvaluation | null
}

export interface EvaluationStats {
  pending: number
  evaluated: number
  progress: number
}

export interface EvaluateRequest {
  report_id: number
  supervisor_score: number
  supervisor_comment: string
}

/**
 * 获取管辖员工的日报列表
 * @param params 查询参数
 */
export const getSubordinateReports = (params?: {
  supervisor_id?: string
  employee_name?: string
  department?: string
  start_date?: string
  end_date?: string
}) => {
  return request.get<DailyReport[]>('/api/v1/daily-report-evaluation/subordinate-reports', { params })
}

/**
 * 获取评价统计数据
 */
export const getEvaluationStats = (params?: {
  supervisor_id?: string
}) => {
  return request.get<EvaluationStats>('/api/v1/daily-report-evaluation/stats', { params })
}

/**
 * 评价日报
 * @param evaluation 评价信息
 */
export const evaluateDailyReport = (evaluation: EvaluateRequest) => {
  return request.post('/api/v1/daily-report-evaluation/evaluate', evaluation)
}

/**
 * 获取日报详情
 * @param reportId 日报ID
 */
export const getReportDetail = (reportId: number) => {
  return request.get<DailyReport>(`/api/v1/daily-report-evaluation/reports/${reportId}`)
}

/**
 * 获取评价历史
 * @param params 查询参数
 */
export const getEvaluationHistory = (params?: {
  employee_id?: string
  start_date?: string
  end_date?: string
  page?: number
  limit?: number
}) => {
  return request.get<{
    items: ReportEvaluation[]
    total: number
    page: number
    limit: number
  }>('/api/v1/daily-report-evaluation/history', { params })
}

/**
 * 更新评价
 * @param evaluationId 评价ID
 * @param evaluation 评价信息
 */
export const updateEvaluation = (evaluationId: number, evaluation: Partial<EvaluateRequest>) => {
  return request.put(`/api/v1/daily-report-evaluation/evaluations/${evaluationId}`, evaluation)
}

/**
 * 删除评价
 * @param evaluationId 评价ID
 */
export const deleteEvaluation = (evaluationId: number) => {
  return request.delete(`/api/v1/daily-report-evaluation/evaluations/${evaluationId}`)
}

// 路由配置
export const DailyReportEvaluationRoutes = {
  SUBORDINATE_REPORTS: '/subordinate-reports',
  EVALUATION_STATS: '/stats',
  EVALUATE: '/evaluate',
  REPORT_DETAIL: '/reports',
  EVALUATION_HISTORY: '/history',
  UPDATE_EVALUATION: '/evaluations',
  DELETE_EVALUATION: '/evaluations'
}
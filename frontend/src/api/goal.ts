import request from './unifiedApi'

// ========== 月度目标接口定义 ==========

export interface MonthlyGoal {
  id: number
  month: string
  title: string
  description?: string
  content?: string
  status: 'draft' | 'published' | 'completed'
  progress: number
  progress_rate?: number
  planned_hours: number
  actual_hours: number
  creator_id: string
  user_id?: string
  creator_name: string
  user_name?: string
  published_at?: string
  created_at: string
  updated_at: string
  weekly_goal_count?: number
}

export interface MonthlyGoalCreate {
  month: string
  title: string
  description?: string
  planned_hours: number
}

export interface MonthlyGoalUpdate {
  month?: string
  title?: string
  description?: string
  planned_hours?: number
}

export interface MonthlyGoalProgressUpdate {
  progress: number
}

export interface MonthlyGoalListResponse {
  items: MonthlyGoal[]
  total: number
  page: number
  size: number
}

// ========== 周目标接口定义 ==========

export interface WeeklyGoal {
  id: number
  goal_id: number
  week_number: number
  title: string
  description?: string
  content?: string
  status: 'pending' | 'in_progress' | 'completed'
  progress: number
  progress_rate?: number
  planned_hours: number
  actual_hours: number
  start_date: string
  end_date: string
  created_at: string
  updated_at: string
}

export interface WeeklyGoalCreate {
  week_number: number
  title: string
  description?: string
  planned_hours: number
  start_date: string
  end_date: string
}

export interface WeeklyGoalUpdate {
  week_number?: number
  title?: string
  description?: string
  planned_hours?: number
  start_date?: string
  end_date?: string
}

export interface WeeklyGoalCurrent {
  monthly_goal: MonthlyGoal
  weekly_goal: WeeklyGoal | null
}

// ========== 日报目标关联接口定义 ==========

export interface DailyReportGoal {
  id: number
  report_id: number
  weekly_goal_id: number
  goal_title: string
  work_content: string
  hours_spent: number
  progress_contribution: number
  created_at: string
  updated_at: string
}

export interface DailyReportGoalCreate {
  weekly_goal_id: number
  work_content: string
  hours_spent: number
  progress_contribution: number
}

export interface DailyReportGoalUpdate {
  weekly_goal_id?: number
  work_content?: string
  hours_spent?: number
  progress_contribution?: number
}

// ========== API函数 - 月度目标 ==========

/**
 * 获取月度目标列表
 */
export const getMonthlyGoals = (params?: {
  month?: string
  status?: string
  page?: number
  size?: number
}) => {
  return request.get<MonthlyGoalListResponse>('v1/monthly-goals', { params })
}

/**
 * 获取月度目标详情
 */
export const getMonthlyGoal = (id: number) => {
  return request.get<MonthlyGoal>(`v1/monthly-goals/${id}`)
}

/**
 * 创建月度目标
 */
export const createMonthlyGoal = (data: MonthlyGoalCreate) => {
  return request.post<MonthlyGoal>('v1/monthly-goals', data)
}

/**
 * 更新月度目标
 */
export const updateMonthlyGoal = (id: number, data: MonthlyGoalUpdate) => {
  return request.put<MonthlyGoal>(`v1/monthly-goals/${id}`, data)
}

/**
 * 删除月度目标
 */
export const deleteMonthlyGoal = (id: number) => {
  return request.delete(`v1/monthly-goals/${id}`)
}

/**
 * 发布月度目标
 */
export const publishMonthlyGoal = (id: number) => {
  return request.put<MonthlyGoal>(`v1/monthly-goals/${id}/publish`)
}

/**
 * 更新月度目标进度
 */
export const updateMonthlyGoalProgress = (id: number, progress: number) => {
  return request.put<MonthlyGoal>(`v1/monthly-goals/${id}/progress`, { progress })
}

/**
 * 从项目任务自动生成目标
 */
export const generateGoalsFromTasks = (year: number) => {
  return request.post<{
    message: string
    data: {
      year: number
      user_id: string
      user_name: string
      generated_months: Array<{
        month: string
        status: string
        monthly_goal_id?: number
        title?: string
        task_count?: number
        weekly_goals?: Array<{ week_number: number; title: string }>
        reason?: string
        error?: string
      }>
      total_tasks: number
      errors: string[]
    }
  }>(`v1/monthly-goals/generate-from-tasks?year=${year}`)
}

// ========== API函数 - 周目标 ==========

/**
 * 获取月度目标下的周目标列表
 */
export const getWeeklyGoals = (goalId: number) => {
  return request.get<WeeklyGoal[]>(`v1/monthly-goals/${goalId}/weeks`)
}

/**
 * 创建周目标
 */
export const createWeeklyGoal = (goalId: number, data: WeeklyGoalCreate) => {
  return request.post<WeeklyGoal>(`v1/monthly-goals/${goalId}/weeks`, data)
}

/**
 * 获取当前周目标
 */
export const getCurrentWeeklyGoal = () => {
  return request.get<WeeklyGoalCurrent>('v1/weekly-goals/current')
}

/**
 * 更新周目标
 */
export const updateWeeklyGoal = (id: number, data: WeeklyGoalUpdate) => {
  return request.put<WeeklyGoal>(`v1/weekly-goals/${id}`, data)
}

/**
 * 删除周目标
 */
export const deleteWeeklyGoal = (id: number) => {
  return request.delete(`v1/weekly-goals/${id}`)
}

// ========== API函数 - 日报目标关联 ==========

/**
 * 获取日报关联的目标列表
 */
export const getDailyReportGoals = (reportId: number) => {
  return request.get<DailyReportGoal[]>(`v1/daily-reports/${reportId}/goals`)
}

/**
 * 为日报添加目标关联
 */
export const createDailyReportGoal = (reportId: number, data: DailyReportGoalCreate) => {
  return request.post<DailyReportGoal>(`v1/daily-reports/${reportId}/goals`, data)
}

/**
 * 批量为日报添加目标关联
 */
export const batchCreateDailyReportGoals = (reportId: number, items: DailyReportGoalCreate[]) => {
  return request.post<DailyReportGoal[]>(`v1/daily-reports/${reportId}/goals/batch`, { items })
}

/**
 * 更新日报目标关联
 */
export const updateDailyReportGoal = (id: number, data: DailyReportGoalUpdate) => {
  return request.put<DailyReportGoal>(`v1/daily-report-goals/${id}`, data)
}

/**
 * 删除日报目标关联
 */
export const deleteDailyReportGoal = (id: number) => {
  return request.delete(`v1/daily-report-goals/${id}`)
}

/**
 * 批量更新日报目标关联
 */
export const batchUpdateDailyReportGoals = (reportId: number, items: DailyReportGoalUpdate[]) => {
  return request.put<DailyReportGoal[]>(`v1/daily-reports/${reportId}/goals/batch`, { items })
}

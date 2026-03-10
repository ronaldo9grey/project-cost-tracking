import axios from './axios'

// 项目跟踪API接口 - 基于优化后的项目跟踪表结构
export const projectTrackingApi = {
  // 获取项目跟踪列表 - 直接查询原始表
  getProjectTrackings(params?: {
    project_name?: string
    status?: string
    page?: number
    limit?: number
    sort_by?: string
    sort_order?: 'asc' | 'desc'
  }) {
    return axios.get('v1/project-tracking-list', { params })
  },

  // 获取项目跟踪详情 - 包含所有关联数据
  getProjectTrackingDetail(trackingId: number) {
    return axios.get(`v1/project-tracking/projects/${trackingId}/detail`)
  },

  // 获取项目甘特图数据
  getProjectGanttData(projectId: string) {
    return axios.get(`v1/project-tracking/${projectId}/gantt`)
  },

  // 获取项目任务跟踪列表 - 基于task_trackings表
  getTaskTrackings(trackingId: number) {
    return axios.get(`v1/project-tracking/projects/${trackingId}/tasks`)
  },

  // 获取CDE评价信息 - 基于优化后的task_cde_evaluations视图
  getCDEEvaluations(trackingId: number, params?: {
    start_date?: string
    end_date?: string
    min_score?: number
    max_score?: number
  }) {
    return axios.get(`v1/project-tracking/projects/${trackingId}/cde-evaluations`, { params })
  },

  // 获取进度趋势数据 - 用于图表展示
  getProgressTrend(trackingId: number, params?: {
    period?: 'week' | 'month' | 'quarter'
    start_date?: string
    end_date?: string
  }) {
    return axios.get(`v1/project-tracking/projects/${trackingId}/progress-trend`, { params })
  },

  // 获取风险分析数据
  getRiskAnalysis(trackingId: number) {
    return axios.get(`v1/project-tracking/projects/${trackingId}/risk-analysis`)
  },

  // 更新项目跟踪状态
  updateProjectTracking(trackingId: number, data: {
    tracking_status?: string
    overall_progress?: number
    risk_level?: string
    priority_level?: string
    notes?: string
  }) {
    return axios.put(`v1/project-tracking/projects/${trackingId}`, data)
  },

  // 更新任务跟踪状态
  updateTaskTracking(taskTrackingId: number, data: {
    status?: string
    current_progress?: number
    delay_days?: number
    risk_level?: string
    notes?: string
  }) {
    return axios.put(`v1/project-tracking/tasks/${taskTrackingId}`, data)
  },

  // 手动刷新统计数据
  refreshTrackingStats(trackingId?: number) {
    if (trackingId) {
      return axios.post(`v1/project-tracking/projects/${trackingId}/refresh-stats`)
    } else {
      return axios.post('v1/project-tracking/refresh-all-stats')
    }
  },

  // 获取项目跟踪统计概览
  getTrackingOverview() {
    return axios.get('v1/project-tracking/overview')
  },

  // 获取延迟项目列表
  getDelayedProjects(params?: {
    delay_threshold?: number
    page?: number
    limit?: number
  }) {
    return axios.get('v1/project-tracking/delayed-projects', { params })
  },

  // 获取高风险项目列表
  getHighRiskProjects(params?: {
    risk_level?: '高' | '中'
    page?: number
    limit?: number
  }) {
    return axios.get('v1/project-tracking/high-risk-projects', { params })
  },

  // 获取项目任务跟踪列表
  getTrackingTasks(trackingId: number) {
    return axios.get(`v1/project-tracking/project-trackings/${trackingId}/tasks`)
  },

  // 获取任务关联的日报
  getTaskRelatedReports(taskId: string) {
    return axios.get(`v1/project-tracking/task-trackings/${taskId}/reports`)
  },

  // 获取CDE评价提醒
  getCDEAlerts(trackingId: number, unreadOnly?: boolean) {
    return axios.get(`v1/project-tracking/project-trackings/${trackingId}/cde-alerts`, {
      params: { unread_only: unreadOnly }
    })
  },

  // 标记通知为已读
  markNotificationRead(notificationId: number) {
    return axios.put(`v1/project-tracking/notifications/${notificationId}/read`)
  }
}

// 类型定义
export interface ProjectTracking {
  id: number
  project_id: string
  project_name: string
  overall_progress: number
  tracking_status: string
  total_tasks: number
  completed_tasks: number
  total_reports: number
  cde_evaluations: number
  risk_level: string
  priority_level: string
  last_update_time: string
  create_time: string
  update_time: string
}

export interface TaskTracking {
  id: number
  tracking_id: number
  task_id: string
  task_name: string
  assignee: string
  assignee_id?: string
  planned_start?: string
  planned_end?: string
  actual_start?: string
  actual_end?: string
  current_progress: number
  delay_days: number
  related_reports_count: number
  cde_evaluation_count: number
  status: string
  priority_level: string
  risk_level: string
  create_time: string
  update_time: string
}

export interface TaskReportLink {
  id: number
  task_tracking_id: number
  report_id: number
  work_item_id: number
  employee_id: string
  employee_name: string
  report_date: string
  work_content: string
  hours_spent: number
  progress_contribution: number
  has_cde_evaluation: boolean
  cde_evaluation_score?: number
  cde_evaluation_content?: string
  create_time: string
  update_time: string
}

export interface TrackingNotification {
  id: number
  tracking_id: number
  notification_type: string
  priority_level: string
  title: string
  content: string
  related_task_id?: string
  related_report_id?: number
  recipient_id: string
  recipient_name: string
  recipient_role?: string
  is_read: boolean
  is_sent: boolean
  sent_time?: string
  push_methods?: string
  create_time: string
}

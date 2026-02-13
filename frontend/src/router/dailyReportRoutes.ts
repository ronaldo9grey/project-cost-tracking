// 日报系统路由配置
import type { RouteRecordRaw } from 'vue-router'

export const dailyReportRoutes: RouteRecordRaw[] = [
  // 重构版日报路由
  {
    path: '/daily-report-enhanced',
    name: 'DailyReportEnhancedList',
    component: () => import('../views/DailyReportList/index.vue'), // 重用现有列表组件
    meta: {
      title: '我的日报（重构版）'
    }
  },
  {
    path: '/daily-report-enhanced/create',
    name: 'DailyReportEnhancedCreate',
    component: () => import('../views/DailyReportEdit/RefactoredDailyReportEdit.vue'),
    meta: {
      title: '新建日报（重构版）'
    }
  },
  {
    path: '/daily-report-enhanced/:id/edit',
    name: 'DailyReportEnhancedEdit',
    component: () => import('../views/DailyReportEdit/RefactoredDailyReportEdit.vue'),
    meta: {
      title: '编辑日报（重构版）'
    },
    props: true
  },
  {
    path: '/daily-report-enhanced/:id/view',
    name: 'DailyReportEnhancedView',
    component: () => import('../views/DailyReportDetail/index.vue'),
    meta: {
      title: '查看日报（重构版）'
    },
    props: true
  },
  
  // 将原有日报路由指向重构版组件
  {
    path: '/daily-report/create',
    name: 'DailyReportCreate',
    component: () => import('../views/DailyReportEdit/RefactoredDailyReportEdit.vue'),
    meta: {
      title: '新建日报'
    }
  },
  {
    path: '/daily-report/:id/edit',
    name: 'DailyReportEdit',
    component: () => import('../views/DailyReportEdit/RefactoredDailyReportEdit.vue'),
    meta: {
      title: '编辑日报'
    },
    props: true
  },
  {
    path: '/daily-report/:id/view',
    name: 'DailyReportDetail',
    component: () => import('../views/DailyReportDetail/index.vue'),
    meta: {
      title: '查看日报'
    },
    props: true
  },
  {
    path: '/daily-report/:id/evaluate',
    name: 'DailyReportEvaluate',
    component: () => import('../views/DailyReportEvaluationDetail/index.vue'),
    meta: {
      title: '评价日报'
    },
    props: true
  },
  {
    path: '/daily-report/attachment/preview/:id',
    name: 'DailyReportAttachmentPreview',
    component: () => import('../views/DailyReportAttachment/Preview.vue'),
    meta: {
      title: '附件预览'
    },
    props: true
  },
  
  // 日清表路由 - 集成版任务管理界面
  {
    path: '/daily-task-completion',
    name: 'DailyTaskCompletionList',
    component: () => import('../views/DailyTaskCompletion/IntegratedDailyTaskView.vue'),
    meta: {
      title: '日清表 - 任务管理'
    }
  },
  {
    path: '/daily-task-completion/create',
    name: 'DailyTaskCompletionCreate',
    component: () => import('../views/DailyTaskCompletion/IntegratedDailyTaskView.vue'),
    meta: {
      title: '新建日清表'
    }
  },
  {
    path: '/daily-task-completion/:id/edit',
    name: 'DailyTaskCompletionEdit',
    component: () => import('../views/DailyTaskCompletion/IntegratedDailyTaskView.vue'),
    meta: {
      title: '编辑日清表'
    },
    props: true
  },
  
  // 日报附件管理路由
  {
    path: '/daily-report/:id/attachments',
    name: 'DailyReportAttachment',
    component: () => import('../views/DailyReportAttachment/index.vue'),
    meta: {
      title: '附件管理'
    },
    props: true
  },

  // 日报数据分析路由
  {
    path: '/daily-report/analysis',
    name: 'DailyReportAnalysis',
    component: () => import('../views/DailyReportAnalysis/index.vue'),
    meta: {
      title: '日报数据分析'
    }
  },

  // 日报分析调试页面
  {
    path: '/daily-report/analysis/debug',
    name: 'DailyReportAnalysisDebug',
    component: () => import('../views/DailyReportAnalysis/debug.vue'),
    meta: {
      title: '日报分析调试'
    }
  }
]

// 可选：在原有路由基础上添加切换按钮
// 让用户可以在旧版和增强版之间切换
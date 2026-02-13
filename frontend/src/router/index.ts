import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { getToken, removeToken } from '../api/auth'
import { dailyReportRoutes } from './dailyReportRoutes'

// 路由配置数组
const routes: RouteRecordRaw[] = [
  ...dailyReportRoutes,
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login/index.vue'),
    meta: {
      title: '登录'
    }
  },
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard/index.vue'),
    meta: {
      title: '项目看板'
    }
  },
  {
    path: '/project-cards',
    name: 'ProjectCards',
    component: () => import('../views/ProjectBoard/index.vue'),
    meta: {
      title: '项目卡片'
    }
  },
  {
    path: '/projects',
    name: 'Projects',
    component: () => import('../views/Projects/index.vue'),
    meta: {
      title: '项目管理'
    }
  },
  {
    path: '/projects/create',
    name: 'ProjectCreateStep1',
    component: () => import('../views/Projects/Create/Step1.vue'),
    meta: { title: '新建项目 - 基本信息' },
    props: true
  },
  {
    path: '/projects/create/:projectId',
    name: 'ProjectEditStep1',
    component: () => import('../views/Projects/Create/Step1.vue'),
    meta: { title: '编辑项目 - 基本信息' },
    props: true
  },
  {
    path: '/projects/:id',
    redirect: to => `/projects/${to.params.id}/basic`
  },
  {
    path: '/projects/:id/basic',
    name: 'ProjectDetailBasic',
    component: () => import('../views/Projects/ProjectDetail.vue'),
    meta: {
      title: '项目详情 - 基本信息'
    }
  },
  {
    path: '/projects/:id/cost',
    name: 'ProjectDetailCost',
    component: () => import('../views/Projects/ProjectDetail.vue'),
    meta: {
      title: '项目详情 - 成本设定'
    }
  },
  {
    path: '/projects/:id/gantt',
    name: 'ProjectDetailGantt',
    component: () => import('../views/Projects/ProjectDetail.vue'),
    meta: {
      title: '项目详情 - 任务设定'
    }
  },
  {
    path: '/projects/:id/documents',
    name: 'ProjectDetailDocuments',
    component: () => import('../views/Projects/ProjectDetail.vue'),
    meta: {
      title: '项目详情 - 文档管理'
    }
  },

  {
    path: '/projects/:projectId/create/cost',
    name: 'ProjectCreateStep2',
    component: () => import('../views/Projects/Create/Step2.vue'),
    meta: {
      title: '新建项目 - 成本设定'
    }
  },
  {
    path: '/projects/:projectId/create/gantt',
    name: 'ProjectCreateStep3',
    component: () => import('../views/Projects/Create/Step3.vue'),
    meta: {
      title: '新建项目 - 甘特图设定'
    }
  },
  {
    path: '/projects/:projectId/create/documents',
    name: 'ProjectCreateStep4',
    component: () => import('../views/Projects/Create/Step4.vue'),
    meta: {
      title: '新建项目 - 文档管理'
    }
  },
  {
    path: '/cost-analysis',
    name: 'CostAnalysis',
    component: () => import('../views/CostAnalysis/index.vue'),
    meta: {
      title: '成本分析'
    }
  },
  {
    path: '/supplier-performance',
    name: 'SupplierPerformance',
    component: () => import('../views/SupplierPerformance/index.vue'),
    meta: {
      title: '履约分析'
    }
  },
  {
    path: '/resource-management',
    name: 'ResourceManagement',
    component: () => import('../views/ResourceManagement/index.vue'),
    meta: {
      title: '资源管理'
    }
  },
  {
    path: '/project-tracking',
    name: 'ProjectTracking',
    component: () => import('../views/ProjectTracking/RealDataProjectTracking.vue'),
    meta: {
      title: '项目跟踪'
    }
  },
  {
    path: '/project-tracking/:trackingId',
    name: 'ProjectTrackingDetail',
    component: () => import('../views/ProjectTracking/Detail.vue'),
    meta: {
      title: '项目跟踪详情'
    },
    props: true
  },
  {
    path: '/standardization',
    name: 'Standardization',
    component: () => import('../views/Standardization/index.vue'),
    meta: {
      title: '项目标准'
    }
  },
  {
    path: '/daily-report',
    name: 'DailyReportList',
    component: () => import('../views/DailyReportList/index.vue'),
    meta: {
      title: '日报填报',
      keepAlive: false, // 禁用缓存，确保每次都重新挂载
      noCache: true
    }
  },
  {
    path: '/daily-report-evaluation',
    name: 'DailyReportEvaluation',
    component: () => import('../views/DailyReportEvaluation/index.vue'),
    meta: {
      title: '日报评价'
    }
  },
  {
    path: '/debug/cost-test',
    name: 'CostTest',
    component: () => import('../views/Projects/Debug/CostTest.vue'),
    meta: {
      title: '成本数据调试'
    }
  },
  {
    path: '/debug/cost-api',
    name: 'CostAPITest',
    component: () => import('../views/Projects/Debug/CostAPITest.vue'),
    meta: {
      title: '成本API测试'
    }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  console.log('=== 路由守卫开始 ===')
  console.log('从:', from.path)
  console.log('到:', to.path)
  
  if (to.meta.title) {
    document.title = `${to.meta.title} - 项目成本跟踪系统`
  }

  const token = getToken()
  console.log('路由守卫检查 - Token存在:', !!token)

  if (to.path !== '/login') {
    if (!token) {
      console.log('❌ 未找到token，重定向到登录页面')
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      console.log('✅ Token存在，允许访问:', to.path)
      next()
    }
  } else {
    if (token) {
      console.log('⚠️ 已登录用户访问登录页，重定向到首页')
      next({ path: '/' })
    } else {
      console.log('✅ 未登录用户访问登录页，允许')
      next()
    }
  }
})

// 添加路由变化监听
router.afterEach((to, from) => {
  console.log('=== 路由变化完成 ===')
  console.log('路由变化:', from.path, '->', to.path)
  console.log('组件:', to.matched.map(r => r.name).join(' -> '))
  console.log('匹配到的路由记录:', to.matched.map(r => ({ name: r.name, path: r.path })))
  
  // 强制禁用页面缓存，确保组件重新挂载
  if (to.name === 'DailyReportList') {
    console.log('💡 日报列表页面 - 强制重新加载')
    // 清除页面缓存
    if (window.history.replaceState) {
      window.history.replaceState(null, '', to.fullPath)
    }
  }
  
  // 特殊处理：确保预览页面组件重新挂载
  if (to.name === 'DailyReportAttachmentPreview') {
    console.log('🔄 附件预览页面 - 强制重新加载组件')
    // 强制刷新页面确保组件重新挂载
    if (window.history.replaceState) {
      window.history.replaceState(null, '', to.fullPath + '?reload=' + Date.now())
    }
  }
})

export default router
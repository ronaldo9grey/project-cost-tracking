// pages/index/index.js
import {
  getUserInfo,
  getTodayReport,
  getReportList,
  getPendingEvaluations,
  quickGenerateReport
} from '../../utils/api.js'

Page({
  data: {
    userInfo: {},
    greeting: '',
    currentDate: '',
    todayStatus: '未提交',
    pendingEvaluations: 0,
    thisMonthReports: 0,
    recentReports: [],
    aiSuggestion: ''
  },

  onLoad() {
    this.setGreeting()
    this.setCurrentDate()
    this.loadData()
  },

  onShow() {
    this.loadData()
  },

  onPullDownRefresh() {
    this.loadData().then(() => {
      wx.stopPullDownRefresh()
    })
  },

  // 设置问候语
  setGreeting() {
    const hour = new Date().getHours()
    let greeting = '早上好'
    if (hour >= 12 && hour < 14) {
      greeting = '中午好'
    } else if (hour >= 14 && hour < 18) {
      greeting = '下午好'
    } else if (hour >= 18) {
      greeting = '晚上好'
    }
    this.setData({ greeting })
  },

  // 设置当前日期
  setCurrentDate() {
    const now = new Date()
    const dateStr = `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
    this.setData({ currentDate: dateStr })
  },

  // 加载数据
  async loadData() {
    wx.showLoading({ title: '加载中' })
    
    try {
      // 并行加载数据
      await Promise.all([
        this.loadUserInfo(),
        this.loadTodayReport(),
        this.loadRecentReports(),
        this.loadPendingEvaluations()
      ])
    } catch (error) {
      console.error('加载数据失败:', error)
    } finally {
      wx.hideLoading()
    }
  },

  // 加载用户信息
  async loadUserInfo() {
    try {
      const res = await getUserInfo()
      if (res.code === 200) {
        this.setData({ userInfo: res.data })
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  },

  // 加载今日日报状态
  async loadTodayReport() {
    try {
      const res = await getTodayReport()
      if (res.code === 200 && res.data) {
        this.setData({ todayStatus: '已提交' })
      } else {
        this.setData({ todayStatus: '未提交' })
      }
    } catch (error) {
      console.error('获取今日日报失败:', error)
    }
  },

  // 加载最近日报
  async loadRecentReports() {
    try {
      const res = await getReportList({ page_size: 5 })
      if (res.code === 200 && res.data) {
        const reports = res.data.items.map(item => ({
          id: item.id,
          report_date: item.report_date,
          status: item.status || 'draft',
          statusText: this.getStatusText(item.status),
          preview: this.getReportPreview(item),
          task_count: item.work_items ? item.work_items.length : 0,
          evaluation: item.evaluation ? item.evaluation.rating : null
        }))
        
        this.setData({
          recentReports: reports,
          thisMonthReports: res.data.total
        })
      }
    } catch (error) {
      console.error('获取日报列表失败:', error)
    }
  },

  // 加载待评价数量
  async loadPendingEvaluations() {
    try {
      const res = await getPendingEvaluations()
      if (res.code === 200 && res.data) {
        this.setData({ pendingEvaluations: res.data.length || 0 })
      }
    } catch (error) {
      console.error('获取待评价列表失败:', error)
    }
  },

  // 获取状态文本
  getStatusText(status) {
    const statusMap = {
      'draft': '草稿',
      'submitted': '已提交',
      'evaluated': '已评价'
    }
    return statusMap[status] || '草稿'
  },

  // 获取日报预览
  getReportPreview(report) {
    if (report.work_goals) {
      return report.work_goals.substring(0, 50) + '...'
    }
    if (report.main_work_items) {
      return report.main_work_items.substring(0, 50) + '...'
    }
    return '暂无内容'
  },

  // 快速填报
  quickFillReport() {
    wx.navigateTo({
      url: '/pages/daily-report/daily-report?mode=quick'
    })
  },

  // AI生成日报
  async aiGenerateReport() {
    wx.showLoading({ title: 'AI生成中...' })
    
    try {
      const res = await quickGenerateReport()
      if (res.code === 200 && res.data) {
        // 保存到本地存储，供填报页面使用
        wx.setStorageSync('aiGeneratedReport', res.data)
        
        wx.navigateTo({
          url: '/pages/daily-report/daily-report?mode=ai'
        })
      }
    } catch (error) {
      wx.showToast({
        title: '生成失败',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 查看日报列表
  viewReports() {
    wx.switchTab({
      url: '/pages/daily-report/daily-report'
    })
  },

  // 查看评价
  viewEvaluations() {
    wx.navigateTo({
      url: '/pages/evaluation/evaluation'
    })
  },

  // 查看日报详情
  viewReportDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/daily-report/detail?id=${id}`
    })
  },

  // 查看全部日报
  viewAllReports() {
    wx.switchTab({
      url: '/pages/daily-report/daily-report'
    })
  },

  // 去填报日报
  goToReport() {
    wx.switchTab({
      url: '/pages/daily-report/daily-report'
    })
  }
})

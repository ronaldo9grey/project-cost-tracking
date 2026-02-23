// utils/api.js
const app = getApp()

// API基础配置
const BASE_URL = app.globalData.apiBaseUrl || 'https://your-api-domain.com/api/v1'

// 请求拦截器
const request = (options) => {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync('token')
    
    wx.request({
      url: `${BASE_URL}${options.url}`,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : ''
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // Token过期，重新登录
          wx.removeStorageSync('token')
          wx.navigateTo({
            url: '/pages/login/login'
          })
          reject(new Error('登录已过期'))
        } else {
          wx.showToast({
            title: res.data.message || '请求失败',
            icon: 'none'
          })
          reject(res.data)
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// 登录
const login = (code) => {
  return request({
    url: '/auth/wechat-login',
    method: 'POST',
    data: { code }
  })
}

// 检查登录状态
const checkLogin = () => {
  const token = wx.getStorageSync('token')
  return !!token
}

// 获取用户信息
const getUserInfo = () => {
  return request({
    url: '/auth/users/me',
    method: 'GET'
  })
}

// ==================== 日报相关API ====================

// 获取今日日报
const getTodayReport = () => {
  return request({
    url: '/daily-report/today',
    method: 'GET'
  })
}

// 获取日报列表
const getReportList = (params = {}) => {
  return request({
    url: '/daily-report',
    method: 'GET',
    data: params
  })
}

// 提交日报
const submitReport = (data) => {
  return request({
    url: '/daily-report',
    method: 'POST',
    data
  })
}

// 更新日报
const updateReport = (id, data) => {
  return request({
    url: `/daily-report/${id}`,
    method: 'PUT',
    data
  })
}

// AI生成日报
const generateAIReport = (data) => {
  return request({
    url: '/ai-daily/generate',
    method: 'POST',
    data
  })
}

// AI快速生成日报
const quickGenerateReport = () => {
  return request({
    url: '/ai-daily/quick-generate',
    method: 'POST'
  })
}

// ==================== 评价相关API ====================

// 获取待评价列表
const getPendingEvaluations = () => {
  return request({
    url: '/daily-report-evaluation/pending',
    method: 'GET'
  })
}

// 提交评价
const submitEvaluation = (data) => {
  return request({
    url: '/daily-report-evaluation',
    method: 'POST',
    data
  })
}

// 获取评价列表
const getEvaluationList = (params = {}) => {
  return request({
    url: '/daily-report-evaluation',
    method: 'GET',
    data: params
  })
}

// ==================== 统计相关API ====================

// 获取统计数据
const getStatistics = () => {
  return request({
    url: '/daily-report-analysis/statistics',
    method: 'GET'
  })
}

// 获取工作量趋势
const getWorkloadTrend = (days = 7) => {
  return request({
    url: '/ai-daily/workload-trend',
    method: 'POST',
    data: { days }
  })
}

// ==================== 通知相关API ====================

// 获取通知设置
const getNotificationSettings = () => {
  return request({
    url: '/notifications/settings',
    method: 'GET'
  })
}

// 更新通知设置
const updateNotificationSettings = (data) => {
  return request({
    url: '/notifications/settings',
    method: 'PUT',
    data
  })
}

// 绑定企业微信ID
const bindWechatId = (wechatUserId) => {
  return request({
    url: '/notifications/settings/wechat-user-id',
    method: 'POST',
    data: { wechat_user_id: wechatUserId }
  })
}

module.exports = {
  request,
  login,
  checkLogin,
  getUserInfo,
  getTodayReport,
  getReportList,
  submitReport,
  updateReport,
  generateAIReport,
  quickGenerateReport,
  getPendingEvaluations,
  submitEvaluation,
  getEvaluationList,
  getStatistics,
  getWorkloadTrend,
  getNotificationSettings,
  updateNotificationSettings,
  bindWechatId
}

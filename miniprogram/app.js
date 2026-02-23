// app.js
import { request, checkLogin, login } from './utils/api.js'

App({
  globalData: {
    userInfo: null,
    token: null,
    apiBaseUrl: 'http://123.207.74.78:8000/api/v1'
  },

  onLaunch() {
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    this.getSystemInfo()
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
      // 验证token有效性
      this.validateToken()
    } else {
      // 未登录，跳转到登录页
      wx.navigateTo({
        url: '/pages/login/login'
      })
    }
  },

  // 验证token
  async validateToken() {
    try {
      const res = await request({
        url: '/auth/users/me',
        method: 'GET'
      })
      
      if (res.code === 200) {
        this.globalData.userInfo = res.data
      } else {
        // token无效，清除并重新登录
        wx.removeStorageSync('token')
        wx.navigateTo({
          url: '/pages/login/login'
        })
      }
    } catch (error) {
      console.error('验证token失败:', error)
    }
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
      }
    })
  },

  // 全局错误处理
  onError(msg) {
    console.error('全局错误:', msg)
    wx.showToast({
      title: '系统繁忙，请稍后重试',
      icon: 'none'
    })
  },

  // 网络状态监听
  onNetworkStatusChange() {
    wx.onNetworkStatusChange((res) => {
      if (!res.isConnected) {
        wx.showToast({
          title: '网络已断开',
          icon: 'none',
          duration: 2000
        })
      }
    })
  }
})

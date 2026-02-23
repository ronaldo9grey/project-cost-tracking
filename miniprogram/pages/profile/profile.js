// pages/profile/profile.js
import { getUserInfo, bindWechatId } from '../../utils/api.js'

Page({
  data: {
    userInfo: {}
  },

  onShow() {
    this.loadUserInfo()
  },

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

  bindWechat() {
    wx.showModal({
      title: '绑定企业微信',
      content: '请输入您的企业微信ID',
      editable: true,
      success: async (res) => {
        if (res.confirm && res.content) {
          try {
            const result = await bindWechatId(res.content)
            if (result.code === 200) {
              wx.showToast({ title: '绑定成功', icon: 'success' })
            }
          } catch (error) {
            wx.showToast({ title: '绑定失败', icon: 'none' })
          }
        }
      }
    })
  },

  notificationSettings() {
    wx.navigateTo({ url: '/pages/settings/notification' })
  },

  about() {
    wx.showModal({
      title: '关于',
      content: '项目管理系统 v1.0.0\n企业级项目成本跟踪解决方案',
      showCancel: false
    })
  }
})

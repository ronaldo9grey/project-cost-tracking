// pages/statistics/statistics.js
import { getStatistics, getWorkloadTrend } from '../../utils/api.js'

Page({
  data: {
    stats: {},
    analysis: ''
  },

  onLoad() {
    this.loadData()
  },

  async loadData() {
    wx.showLoading({ title: '加载中' })
    try {
      const [statsRes, trendRes] = await Promise.all([
        getStatistics(),
        getWorkloadTrend(30)
      ])
      
      if (statsRes.code === 200) {
        this.setData({ stats: statsRes.data })
      }
      
      if (trendRes.code === 200) {
        this.setData({ analysis: trendRes.data.analysis })
      }
    } catch (error) {
      console.error('加载统计失败:', error)
    } finally {
      wx.hideLoading()
    }
  }
})

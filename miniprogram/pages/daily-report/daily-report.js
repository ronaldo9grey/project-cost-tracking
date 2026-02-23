// pages/daily-report/daily-report.js
import { submitReport, updateReport, getTodayReport, generateAIReport } from '../../utils/api.js'

Page({
  data: {
    selectedDate: '',
    reportData: {
      work_goals: '',
      key_progress: '',
      tomorrow_plan: '',
      self_evaluation: 'B'
    },
    workItems: [],
    statusOptions: ['未开始', '进行中', '已完成'],
    evaluationOptions: [
      { value: 'A', grade: 'A', label: '超目标达成' },
      { value: 'B', grade: 'B', label: '按目标达成' },
      { value: 'C', grade: 'C', label: '基本达标' },
      { value: 'D', grade: 'D', label: '需要改进' }
    ],
    isEdit: false,
    reportId: null,
    showAIModal: false,
    aiInput: ''
  },

  onLoad(options) {
    // 设置默认日期为今天
    const today = new Date().toISOString().split('T')[0]
    this.setData({ selectedDate: today })
    
    // 检查是否有AI生成的内容
    const aiReport = wx.getStorageSync('aiGeneratedReport')
    if (aiReport && options.mode === 'ai') {
      this.fillAIReport(aiReport)
      wx.removeStorageSync('aiGeneratedReport')
    }
    
    // 加载今日日报（如果存在）
    this.loadTodayReport()
  },

  // 加载今日日报
  async loadTodayReport() {
    try {
      const res = await getTodayReport()
      if (res.code === 200 && res.data) {
        const report = res.data
        this.setData({
          isEdit: true,
          reportId: report.id,
          reportData: {
            work_goals: report.work_goals || '',
            key_progress: report.key_progress || '',
            tomorrow_plan: report.tomorrow_plan || '',
            self_evaluation: report.self_evaluation || 'B'
          },
          workItems: report.work_items || []
        })
      }
    } catch (error) {
      console.error('加载日报失败:', error)
    }
  },

  // 填充AI生成的内容
  fillAIReport(aiReport) {
    if (aiReport.result) {
      const result = aiReport.result
      this.setData({
        'reportData.work_goals': result.work_goals || '',
        'reportData.key_progress': result.key_progress || '',
        'reportData.tomorrow_plan': result.tomorrow_plan || ''
      })
      
      wx.showToast({
        title: 'AI生成内容已填入',
        icon: 'success'
      })
    }
  },

  // 日期变更
  onDateChange(e) {
    this.setData({ selectedDate: e.detail.value })
  },

  // 输入框变更
  onInputChange(e) {
    const field = e.currentTarget.dataset.field
    const value = e.detail.value
    this.setData({
      [`reportData.${field}`]: value
    })
  },

  // 添加工作事项
  addWorkItem() {
    const workItems = this.data.workItems
    workItems.push({
      name: '',
      status: '进行中',
      statusIndex: 1,
      planned_hours: ''
    })
    this.setData({ workItems })
  },

  // 删除工作事项
  deleteWorkItem(e) {
    const index = e.currentTarget.dataset.index
    const workItems = this.data.workItems
    workItems.splice(index, 1)
    this.setData({ workItems })
  },

  // 工作事项变更
  onWorkItemChange(e) {
    const { index, field } = e.currentTarget.dataset
    const value = e.detail.value
    const workItems = this.data.workItems
    workItems[index][field] = value
    this.setData({ workItems })
  },

  // 状态变更
  onStatusChange(e) {
    const index = e.currentTarget.dataset.index
    const statusIndex = e.detail.value
    const workItems = this.data.workItems
    workItems[index].status = this.data.statusOptions[statusIndex]
    workItems[index].statusIndex = parseInt(statusIndex)
    this.setData({ workItems })
  },

  // 选择自我评价
  selectEvaluation(e) {
    const value = e.currentTarget.dataset.value
    this.setData({
      'reportData.self_evaluation': value
    })
  },

  // 保存草稿
  async saveReport() {
    await this.submitReportData('draft')
  },

  // 提交日报
  async submitReport() {
    // 表单验证
    if (!this.data.reportData.work_goals.trim()) {
      wx.showToast({ title: '请填写工作目标', icon: 'none' })
      return
    }
    if (!this.data.reportData.key_progress.trim()) {
      wx.showToast({ title: '请填写工作进展', icon: 'none' })
      return
    }
    if (this.data.workItems.length === 0) {
      wx.showToast({ title: '请添加至少一项工作事项', icon: 'none' })
      return
    }

    await this.submitReportData('submitted')
  },

  // 提交数据
  async submitReportData(status) {
    wx.showLoading({ title: '提交中...' })

    const data = {
      report_date: this.data.selectedDate,
      work_goals: this.data.reportData.work_goals,
      key_progress: this.data.reportData.key_progress,
      main_work_items: this.formatWorkItems(),
      tomorrow_plan: this.data.reportData.tomorrow_plan,
      self_evaluation: this.data.reportData.self_evaluation,
      work_items: this.data.workItems,
      status: status
    }

    try {
      let res
      if (this.data.isEdit && this.data.reportId) {
        res = await updateReport(this.data.reportId, data)
      } else {
        res = await submitReport(data)
      }

      if (res.code === 200) {
        wx.showToast({
          title: status === 'draft' ? '保存成功' : '提交成功',
          icon: 'success'
        })
        
        if (status === 'submitted') {
          setTimeout(() => {
            wx.switchTab({ url: '/pages/index/index' })
          }, 1500)
        }
      } else {
        wx.showToast({
          title: res.message || '提交失败',
          icon: 'none'
        })
      }
    } catch (error) {
      wx.showToast({
        title: '网络错误',
        icon: 'none'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 格式化工作事项
  formatWorkItems() {
    return this.data.workItems.map(item => 
      `${item.name}(${item.status}, ${item.planned_hours}小时)`
    ).join('; ')
  },

  // 显示AI弹窗
  showAIGenerate() {
    this.setData({ showAIModal: true })
  },

  // 关闭AI弹窗
  closeAIModal() {
    this.setData({ showAIModal: false })
  },

  // AI输入变更
  onAIInputChange(e) {
    this.setData({ aiInput: e.detail.value })
  },

  // AI生成
  async generateByAI() {
    if (!this.data.aiInput.trim()) {
      wx.showToast({ title: '请输入工作内容', icon: 'none' })
      return
    }

    wx.showLoading({ title: 'AI生成中...' })

    try {
      const res = await generateAIReport({
        projects: ['项目A'],
        tasks: [{ name: this.data.aiInput, status: '已完成' }]
      })

      if (res.code === 200 && res.data) {
        this.fillAIReport({ result: res.data })
        this.closeAIModal()
      }
    } catch (error) {
      wx.showToast({ title: '生成失败', icon: 'none' })
    } finally {
      wx.hideLoading()
    }
  }
})

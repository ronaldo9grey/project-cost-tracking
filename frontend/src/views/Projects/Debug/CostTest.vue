<template>
  <div style="padding: 20px;">
    <h2>成本数据调试页面</h2>
    <el-button @click="testCosts" type="primary">测试获取成本数据</el-button>
    
    <div v-if="loading" style="margin-top: 20px;">
      <el-loading>加载中...</el-loading>
    </div>
    
    <div v-if="error" style="margin-top: 20px; color: red;">
      <h3>错误信息：</h3>
      <pre>{{ error }}</pre>
    </div>
    
    <div v-if="data" style="margin-top: 20px;">
      <h3>API响应结构：</h3>
      <pre>{{ JSON.stringify(Object.keys(data), null, 2) }}</pre>
      
      <div v-if="data.material_costs">
        <h3>物料成本 (API): {{ data.material_costs.length }}条</h3>
        <p>第一条数据字段：</p>
        <pre>{{ JSON.stringify(Object.keys(data.material_costs[0] || {}), null, 2) }}</pre>
        <p>第一条数据：</p>
        <pre>{{ JSON.stringify(data.material_costs[0] || {}, null, 2) }}</pre>
      </div>
      
      <div v-if="data.labor_costs">
        <h3>人工成本 (API): {{ data.labor_costs.length }}条</h3>
        <p>第一条数据字段：</p>
        <pre>{{ JSON.stringify(Object.keys(data.labor_costs[0] || {}), null, 2) }}</pre>
        <p>第一条数据：</p>
        <pre>{{ JSON.stringify(data.labor_costs[0] || {}, null, 2) }}</pre>
      </div>
      
      <div v-if="data.outsourcing_costs">
        <h3>外包成本 (API): {{ data.outsourcing_costs.length }}条</h3>
        <p>第一条数据字段：</p>
        <pre>{{ JSON.stringify(Object.keys(data.outsourcing_costs[0] || {}), null, 2) }}</pre>
        <p>第一条数据：</p>
        <pre>{{ JSON.stringify(data.outsourcing_costs[0] || {}, null, 2) }}</pre>
      </div>
      
      <div v-if="data.indirect_costs">
        <h3>间接成本 (API): {{ data.indirect_costs.length }}条</h3>
        <p>第一条数据字段：</p>
        <pre>{{ JSON.stringify(Object.keys(data.indirect_costs[0] || {}), null, 2) }}</pre>
        <p>第一条数据：</p>
        <pre>{{ JSON.stringify(data.indirect_costs[0] || {}, null, 2) }}</pre>
      </div>
      
      <h3>处理后的数据统计：</h3>
      <p>物料成本: {{ processed.material.length }}条</p>
      <p>人工成本: {{ processed.labor.length }}条</p>
      <p>外包成本: {{ processed.outsourcing.length }}条</p>
      <p>间接成本: {{ processed.indirect.length }}条</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { getProjectCosts } from '@/api/project'

const loading = ref(false)
const error = ref('')
const data = ref(null)
const processed = ref({
  material: [],
  labor: [],
  outsourcing: [],
  indirect: []
})

const testCosts = async () => {
  loading.value = true
  error.value = ''
  data.value = null
  
  try {
    console.log('开始测试成本数据API调用...')
    const response = await getProjectCosts(81)
    
    console.log('API响应:', response)
    data.value = response
    
    // 模拟Step2的数据处理逻辑
    const apiData = response.data || response
    
    // 物料成本字段映射
    processed.value.material = (apiData.material_costs || []).map(item => ({
      name: item.name,
      specification: item.specification,
      unit: item.unit,
      budget_quantity: item.quantity || 0,
      budget_unit_price: item.unit_price || 0,
      budget_total: item.total_price || 0,
      actual_quantity: item.quantity || 0,
      actual_unit_price: item.unit_price || 0,
      actual_total: item.total_price || 0,
      remark: item.remark || ''
    }))
    
    // 外包成本字段映射
    processed.value.outsourcing = (apiData.outsourcing_costs || []).map(item => ({
      service_type: item.service_type,
      budget_amount: item.total_price || 0,
      budget_start_date: '',
      budget_end_date: '',
      actual_amount: item.total_price || 0,
      actual_start_date: '',
      actual_end_date: '',
      remark: item.remark || ''
    }))
    
    // 间接成本字段映射
    processed.value.indirect = (apiData.indirect_costs || []).map(item => ({
      cost_type: item.cost_type,
      description: item.description,
      budget_amount: item.amount || 0,
      actual_amount: item.amount || 0,
      remark: item.remark || ''
    }))
    
    // 人工成本字段映射
    processed.value.labor = (apiData.labor_costs || []).map(item => ({
      personnel_name: item.employee_id || '',
      role: '',
      budget_hourly_rate: item.hourly_rate || 0,
      budget_hours: item.budget_hours || 0,
      budget_total: item.budget_cost || 0,
      actual_hourly_rate: item.hourly_rate || 0,
      actual_hours: item.actual_hours || 0,
      actual_total: item.actual_cost || 0,
      remark: item.remark || ''
    }))
    
    console.log('处理后的数据:', processed.value)
    
  } catch (err) {
    console.error('API调用失败:', err)
    error.value = err.message || '未知错误'
  } finally {
    loading.value = false
  }
}
</script>
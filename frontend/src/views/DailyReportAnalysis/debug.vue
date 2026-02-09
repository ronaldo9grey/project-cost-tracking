<template>
  <div style="padding: 20px;">
    <h2>API调试页面</h2>
    
    <div style="margin: 20px 0;">
      <h3>当前参数:</h3>
      <p>日期范围: {{ dateRange }}</p>
      <p>选择项目: {{ selectedProject }}</p>
      <p>图表类型: {{ hoursChartType }}</p>
    </div>
    
    <div style="margin: 20px 0;">
      <el-button @click="testHoursTrend" type="primary">测试工时趋势API</el-button>
      <el-button @click="testOverview" type="success">测试概览API</el-button>
      <el-button @click="testProjects" type="warning">测试项目API</el-button>
    </div>
    
    <div v-if="testResult" style="margin: 20px 0; padding: 10px; background: #f5f5f5; border-radius: 5px;">
      <h3>测试结果:</h3>
      <pre>{{ JSON.stringify(testResult, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getHoursTrend, getAnalysisOverview, getAnalysisProjectList } from '../../api/dailyReport'

const dateRange = ref(['2025-12-21', '2026-01-20'])
const selectedProject = ref('')
const hoursChartType = ref('day')
const testResult = ref(null)

const testHoursTrend = async () => {
  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      group_by: hoursChartType.value
    }
    console.log('调用工时趋势API，参数:', params)
    
    const response = await getHoursTrend(params)
    testResult.value = {
      api: 'hours-trend',
      params,
      response
    }
  } catch (error) {
    console.error('工时趋势API错误:', error)
    testResult.value = {
      api: 'hours-trend',
      params: {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1],
        group_by: hoursChartType.value
      },
      error: error
    }
  }
}

const testOverview = async () => {
  try {
    const params = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1]
    }
    console.log('调用概览API，参数:', params)
    
    const response = await getAnalysisOverview(params)
    testResult.value = {
      api: 'overview',
      params,
      response
    }
  } catch (error) {
    console.error('概览API错误:', error)
    testResult.value = {
      api: 'overview',
      params: {
        start_date: dateRange.value[0],
        end_date: dateRange.value[1]
      },
      error: error
    }
  }
}

const testProjects = async () => {
  try {
    console.log('调用项目列表API')
    
    const response = await getAnalysisProjectList()
    testResult.value = {
      api: 'projects',
      response
    }
  } catch (error) {
    console.error('项目API错误:', error)
    testResult.value = {
      api: 'projects',
      error
    }
  }
}

onMounted(() => {
  console.log('调试页面加载完成')
})
</script>
<template>
  <div class="supplier-performance-container">
    <h1>履约分析</h1>
    
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">供应商数量</div>
            <div class="stat-value">{{ overview.supplier_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">评价记录数</div>
            <div class="stat-value">{{ overview.evaluation_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">综合评分</div>
            <div class="stat-value">{{ overview.average_scores?.overall?.toFixed(2) || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-title">平均交付及时率</div>
            <div class="stat-value">{{ overview.average_scores?.delivery_punctuality?.toFixed(2) || '0.00' }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>供应商评分分布</span>
            </div>
          </template>
          <div ref="pieChart" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>评分指标对比</span>
            </div>
          </template>
          <div ref="barChart" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover" style="height: 400px;">
          <template #header>
            <div class="card-header">
              <span>供应商排名</span>
            </div>
          </template>
          <el-table :data="rankingList" style="width: 100%" max-height="320">
            <el-table-column prop="rank" label="排名" width="60" align="center" />
            <el-table-column prop="supplier_name" label="供应商名称" min-width="120" />
            <el-table-column prop="total_score" label="综合评分" width="90" align="center">
              <template #default="scope">
                <el-tag :type="getScoreTag(scope.row.total_score)" size="small">
                  {{ scope.row.total_score?.toFixed(2) || '0.00' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="suggested_level" label="合作建议" width="100" />
            <el-table-column prop="created_at" label="排名时间" min-width="150" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" style="height: 400px;">
          <template #header>
            <div class="card-header">
              <span>AI分析结果</span>
              <el-button type="primary" size="small" :loading="generatingAI" :disabled="generatingAI" @click="generateAIAnalysis">
                {{ generatingAI ? '分析中...' : '重新生成分析' }}
              </el-button>
            </div>
          </template>
          <div v-if="generatingAI" class="analyzing-tip">
            <el-icon class="is-loading"><Loading /></el-icon>
            <span>正在分析供应商数据，请稍候...</span>
          </div>
          <div v-else-if="aiAnalysis" class="ai-analysis-content">
            <h4>{{ aiAnalysis.supplier_name || '供应商履约分析报告' }}</h4>
            <p class="analysis-date">分析日期：{{ aiAnalysis.analysis_date || '-' }}</p>
            <div class="analysis-result">{{ aiAnalysis.analysis_result || '暂无AI分析结果' }}</div>
          </div>
          <div v-else class="no-data">
            暂无AI分析结果
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>供应商评价记录</span>
          <div>
            <el-button type="success" size="small" @click="showSupplierDialog">管理供应商</el-button>
            <el-button type="primary" size="small" @click="showAddDialog" style="margin-left: 10px;">新增评价</el-button>
          </div>
        </div>
      </template>
      
      <el-row :gutter="10" style="margin-bottom: 15px;">
        <el-col :span="6">
          <el-select
            v-model="selectedSupplierId"
            placeholder="选择供应商筛选"
            style="width: 100%;"
            clearable
            @change="filterEvaluations"
          >
            <el-option
              v-for="s in suppliers"
              :key="s.supplier_id"
              :label="s.name"
              :value="s.supplier_id"
            />
          </el-select>
        </el-col>
      </el-row>
      
      <el-table :data="evaluations" v-loading="loadingEvaluations" max-height="500" stripe style="width: 100%" :fit="true">
        <el-table-column prop="supplier_name" label="供应商名称" min-width="120" />
        <el-table-column prop="evaluation_date" label="评价日期" min-width="160" />
        <el-table-column label="交付及时率" min-width="100" align="center">
          <template #default="scope">
            <el-tooltip :content="scope.row.delivery_punctuality_evidence || '无评价说明'" placement="top">
              <el-tag :type="getScoreTag(scope.row.delivery_punctuality_score)" size="small" style="cursor: pointer;">
                {{ scope.row.delivery_punctuality_score || '-' }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="质量一致性" min-width="100" align="center">
          <template #default="scope">
            <el-tooltip :content="scope.row.quality_consistency_evidence || '无评价说明'" placement="top">
              <el-tag :type="getScoreTag(scope.row.quality_consistency_score)" size="small" style="cursor: pointer;">
                {{ scope.row.quality_consistency_score || '-' }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="服务响应率" min-width="100" align="center">
          <template #default="scope">
            <el-tooltip :content="scope.row.service_response_evidence || '无评价说明'" placement="top">
              <el-tag :type="getScoreTag(scope.row.service_response_score)" size="small" style="cursor: pointer;">
                {{ scope.row.service_response_score || '-' }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="合作配合度" min-width="100" align="center">
          <template #default="scope">
            <el-tooltip :content="scope.row.cooperation_evidence || '无评价说明'" placement="top">
              <el-tag :type="getScoreTag(scope.row.cooperation_score)" size="small" style="cursor: pointer;">
                {{ scope.row.cooperation_score || '-' }}
              </el-tag>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="overall_score" label="综合评分" min-width="90" align="center">
          <template #default="scope">
            <el-tag :type="getOverallTag(scope.row.overall_score)" size="small">
              {{ scope.row.overall_score?.toFixed(1) || '-' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="evaluator" label="评价人" min-width="100" />
        <el-table-column label="操作" min-width="120" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="editEvaluation(scope.row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteEvaluation(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div style="margin-top: 15px; text-align: right;">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalEvaluations"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑评价' : '新增评价'" width="750px">
      <el-form :model="evaluationForm" label-width="100px">
        <el-form-item label="供应商">
          <span v-if="isEdit" style="font-weight: bold; font-size: 15px; color: #409EFF;">{{ evaluationForm.supplier_name || getSupplierName(evaluationForm.supplier_id) }}</span>
          <el-select v-else v-model="evaluationForm.supplier_id" placeholder="选择供应商" style="width: 100%;">
            <el-option v-for="s in suppliers" :key="s.supplier_id" :label="s.name" :value="s.supplier_id" />
          </el-select>
        </el-form-item>
        <el-form-item label="评价日期">
          <el-date-picker v-model="evaluationForm.evaluation_date" type="datetime" placeholder="选择评价日期时间" style="width: 100%;" value-format="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="评价人">
          <span style="color: #909399;">{{ evaluationForm.evaluator || '当前用户' }}</span>
        </el-form-item>
        
        <div class="evaluation-group">
          <div class="group-header"><el-icon><Timer /></el-icon><span>交付及时率</span></div>
          <div class="group-content">
            <el-form-item label="评价说明">
              <el-input v-model="evaluationForm.delivery_punctuality_evidence" type="textarea" :rows="2" placeholder="请输入交付及时率评价说明" />
            </el-form-item>
            <el-form-item label="评分">
              <el-rate v-model="evaluationForm.delivery_punctuality_score" :max="10" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
            </el-form-item>
          </div>
        </div>
        
        <div class="evaluation-group">
          <div class="group-header"><el-icon><Medal /></el-icon><span>质量一致性</span></div>
          <div class="group-content">
            <el-form-item label="评价说明">
              <el-input v-model="evaluationForm.quality_consistency_evidence" type="textarea" :rows="2" placeholder="请输入质量一致性评价说明" />
            </el-form-item>
            <el-form-item label="评分">
              <el-rate v-model="evaluationForm.quality_consistency_score" :max="10" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
            </el-form-item>
          </div>
        </div>
        
        <div class="evaluation-group">
          <div class="group-header"><el-icon><Service /></el-icon><span>服务响应率</span></div>
          <div class="group-content">
            <el-form-item label="评价说明">
              <el-input v-model="evaluationForm.service_response_evidence" type="textarea" :rows="2" placeholder="请输入服务响应率评价说明" />
            </el-form-item>
            <el-form-item label="评分">
              <el-rate v-model="evaluationForm.service_response_score" :max="10" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
            </el-form-item>
          </div>
        </div>
        
        <div class="evaluation-group">
          <div class="group-header"><el-icon><UserFilled /></el-icon><span>合作配合度</span></div>
          <div class="group-content">
            <el-form-item label="评价说明">
              <el-input v-model="evaluationForm.cooperation_evidence" type="textarea" :rows="2" placeholder="请输入合作配合度评价说明" />
            </el-form-item>
            <el-form-item label="评分">
              <el-rate v-model="evaluationForm.cooperation_score" :max="10" :colors="['#99A9BF', '#F7BA2A', '#FF9900']" />
            </el-form-item>
          </div>
        </div>
        
        <el-form-item label="备注" style="margin-top: 10px;">
          <el-input v-model="evaluationForm.remarks" type="textarea" :rows="2" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEvaluation" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="supplierDialogVisible" title="供应商管理" width="800px">
      <div style="margin-bottom: 15px;">
        <el-button type="primary" size="small" @click="showSupplierFormDialog">新增供应商</el-button>
      </div>
      <el-table :data="suppliers" style="width: 100%" max-height="400" stripe>
        <el-table-column prop="name" label="供应商名称" min-width="150" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="contact_phone" label="联系电话" width="130" />
        <el-table-column prop="status" label="状态" width="80" align="center">
          <template #default="scope">
            <el-tag :type="scope.row.status === 1 ? 'success' : 'danger'" size="small">
              {{ scope.row.status === 1 ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remarks" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="editSupplier(scope.row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="deleteSupplier(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
    
    <el-dialog v-model="supplierFormDialogVisible" :title="isEditSupplier ? '编辑供应商' : '新增供应商'" width="500px">
      <el-form :model="supplierForm" label-width="100px">
        <el-form-item label="供应商名称" required>
          <el-input v-model="supplierForm.name" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="supplierForm.contact_person" placeholder="请输入联系人姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="supplierForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="联系邮箱">
          <el-input v-model="supplierForm.contact_email" placeholder="请输入联系邮箱" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="supplierForm.status" :active-value="1" :inactive-value="0" active-text="启用" inactive-text="禁用" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="supplierForm.remarks" type="textarea" :rows="3" placeholder="请输入备注信息" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="supplierFormDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSupplier" :loading="savingSupplier">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Timer, Medal, Service, UserFilled, Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { 
  getSuppliers, getSupplierAnalysisOverview, getSupplierAnalysisChartData,
  getSupplierRankingDetail, getSupplierAIAnalysis, getSupplierEvaluations,
  createSupplierEvaluation, updateSupplierEvaluation, deleteSupplierEvaluation,
  createSupplier, updateSupplier, deleteSupplier as deleteSupplierApi,
  generateSupplierAIAnalysis,
  type Supplier, type SupplierEvaluation, type SupplierEvaluationCreate,
  type SupplierEvaluationUpdate, type AnalysisOverview, type ChartData,
  type SupplierRanking, type SupplierAIAnalysis
} from '../../api/supplierAnalysis'

const suppliers = ref<Supplier[]>([])
const selectedSupplierId = ref<number | null>(null)
const overview = ref<AnalysisOverview>({ supplier_count: 0, evaluation_count: 0, ranking_count: 0, average_scores: { delivery_punctuality: 0, quality_consistency: 0, service_response: 0, cooperation: 0, overall: 0 } })
const rankingList = ref<SupplierRanking[]>([])
const aiAnalysis = ref<SupplierAIAnalysis | null>(null)
const allEvaluations = ref<SupplierEvaluation[]>([])
const evaluations = ref<SupplierEvaluation[]>([])
const loadingEvaluations = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalEvaluations = ref(0)
const saving = ref(false)
const generatingAI = ref(false)
const pieChart = ref<HTMLElement | null>(null)
const barChart = ref<HTMLElement | null>(null)
let pieChartInstance: echarts.ECharts | null = null
let barChartInstance: echarts.ECharts | null = null

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref<number | null>(null)
const savingSupplier = ref(false)
const supplierDialogVisible = ref(false)
const supplierFormDialogVisible = ref(false)
const isEditSupplier = ref(false)
const editingSupplierId = ref<number | null>(null)

interface EvaluationFormData extends SupplierEvaluationCreate { supplier_name?: string; delivery_punctuality_evidence?: string; quality_consistency_evidence?: string; service_response_evidence?: string; cooperation_evidence?: string }
const evaluationForm = ref<EvaluationFormData>({ supplier_id: 0, delivery_punctuality_score: 5, delivery_punctuality_evidence: '', quality_consistency_score: 5, quality_consistency_evidence: '', service_response_score: 5, service_response_evidence: '', cooperation_score: 5, cooperation_evidence: '', evaluator: localStorage.getItem('username') || '当前用户', remarks: '', evaluation_date: '' })

const supplierForm = ref({ name: '', contact_person: '', contact_phone: '', contact_email: '', status: 1, remarks: '' })

const getScoreTag = (score: number): string => { if (!score) return 'info'; if (score >= 8) return 'success'; if (score >= 6) return 'warning'; return 'danger' }
const getOverallTag = (score: number): string => { if (!score) return 'info'; if (score >= 8) return 'success'; if (score >= 6) return 'warning'; return 'danger' }
const getSupplierName = (supplierId: number): string => { const supplier = suppliers.value.find(s => s.supplier_id === supplierId); return supplier?.name || '' }

const loadSuppliers = async () => {
  try {
    const response = await getSuppliers({ page: 1, size: 100 })
    if (response.items && response.items.length > 0) {
      suppliers.value = response.items.map(item => ({ ...item, supplier_id: item.supplier_id, name: item.name }))
    }
  } catch (error) { console.error('加载供应商列表失败:', error) }
}

const loadOverview = async () => {
  try {
    const data = await getSupplierAnalysisOverview()
    overview.value = data
  } catch (error) { console.error('加载分析概览失败:', error) }
}

const loadChartData = async () => {
  try {
    const data = await getSupplierAnalysisChartData()
    const chartData = data as ChartData
    await nextTick()
    initPieChart(chartData.pie_chart)
    initBarChart(chartData.bar_chart)
  } catch (error) { console.error('加载图表数据失败:', error) }
}

const loadRanking = async () => {
  try {
    const data = await getSupplierRankingDetail()
    rankingList.value = (data as SupplierRanking[]).slice(0, 10)
  } catch (error) { console.error('加载排名数据失败:', error) }
}

const loadAIAnalysis = async () => {
  try {
    const response = await getSupplierAIAnalysis()
    console.log('=== loadAIAnalysis ===')
    console.log('response:', response)
    console.log('response.analysis_result:', response?.analysis_result)
    
    if (!response) {
      aiAnalysis.value = null
      return
    }
    
    if (response.analysis_result && typeof response.analysis_result === 'string') {
      console.log('发现有效AI分析数据')
      aiAnalysis.value = {
        supplier_id: response.supplier_id || 0,
        supplier_name: response.supplier_name || '',
        analysis_date: response.analysis_date || new Date().toISOString(),
        analysis_result: response.analysis_result,
        generated_at: response.generated_at || new Date().toISOString(),
        generated_by: response.generated_by || 'AI系统'
      }
      console.log('AI分析已设置:', aiAnalysis.value)
    } else {
      console.log('AI分析数据无效')
      aiAnalysis.value = null
    }
  } catch (error) {
    console.error('加载AI分析结果失败:', error)
    aiAnalysis.value = null
  }
}

const generateAIAnalysis = async () => {
  try {
    await ElMessageBox.confirm('AI分析将基于现有评价数据生成新的分析报告，确定继续吗？', '确认生成', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'info' })
  } catch { return }
  
  generatingAI.value = true
  aiAnalysis.value = null
  
  try {
    const result = await generateSupplierAIAnalysis()
    console.log('AI生成结果:', result)
    
    if (result && (result.analysis_result || result.code === 200)) {
      ElMessage.success('AI分析完成！')
      
      const now = new Date().toISOString()
      aiAnalysis.value = {
        supplier_id: result.supplier_id || 0,
        supplier_name: result.supplier_name || '',
        analysis_date: now,
        analysis_result: result.analysis_result || result.message || 'AI分析已完成',
        generated_at: now,
        generated_by: 'AI系统'
      }
      console.log('AI分析已显示:', aiAnalysis.value)
    } else {
      ElMessage.error(result?.message || 'AI分析失败')
    }
  } catch (error: any) {
    console.error('AI生成异常:', error)
    ElMessage.error(error.response?.data?.message || 'AI分析失败')
  } finally {
    generatingAI.value = false
  }
}

const loadAllEvaluations = async () => {
  try {
    allEvaluations.value = []
    evaluations.value = []
    totalEvaluations.value = 0
    for (const supplier of suppliers.value) {
      try {
        const response = await getSupplierEvaluations(supplier.supplier_id, { skip: 0, limit: 100 })
        if (response.items && response.items.length > 0) {
          allEvaluations.value.push(...response.items)
        }
      } catch { continue }
    }
    allEvaluations.value.sort((a, b) => (b.evaluation_id || 0) - (a.evaluation_id || 0))
    filterEvaluations()
  } catch (error) { console.error('加载评价记录失败:', error); ElMessage.error('加载评价记录失败') }
}

const filterEvaluations = () => {
  let filtered = allEvaluations.value
  if (selectedSupplierId.value) {
    filtered = filtered.filter(e => e.supplier_id === selectedSupplierId.value)
  }
  totalEvaluations.value = filtered.length
  const start = (currentPage.value - 1) * pageSize.value
  evaluations.value = filtered.slice(start, start + pageSize.value)
}

const initPieChart = (pieData: Array<{ value: number; name: string }>) => {
  if (pieChartInstance) pieChartInstance.dispose()
  if (!pieChart.value || pieData.length === 0) return
  pieChartInstance = echarts.init(pieChart.value)
  pieChartInstance.setOption({
    tooltip: { trigger: 'item', formatter: (params: any) => `${params.name}: ${params.value}分 (${params.percent}%)` },
    legend: { orient: 'vertical', left: 'left' },
    series: [{ name: '综合评分', type: 'pie', radius: '50%', data: pieData, emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0, 0, 0, 0.5)' } }, label: { formatter: '{b}: {d}%' } }]
  })
}

const initBarChart = (barData: { categories: string[]; delivery: number[]; quality: number[]; service: number[]; cooperation: number[] }) => {
  if (barChartInstance) barChartInstance.dispose()
  if (!barChart.value || barData.categories.length === 0) return
  barChartInstance = echarts.init(barChart.value)
  barChartInstance.setOption({
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: ['交付及时率', '质量一致性', '服务响应率', '合作配合度'] },
    xAxis: { type: 'category', data: barData.categories, axisLabel: { interval: 0, rotate: 30 } },
    yAxis: { type: 'value', name: '评分', min: 0, max: 10 },
    series: [
      { name: '交付及时率', type: 'bar', data: barData.delivery, itemStyle: { color: '#409EFF' } },
      { name: '质量一致性', type: 'bar', data: barData.quality, itemStyle: { color: '#67C23A' } },
      { name: '服务响应率', type: 'bar', data: barData.service, itemStyle: { color: '#E6A23C' } },
      { name: '合作配合度', type: 'bar', data: barData.cooperation, itemStyle: { color: '#909399' } }
    ]
  })
}

const initCharts = () => { if (pieChart.value) pieChartInstance = echarts.init(pieChart.value); if (barChart.value) barChartInstance = echarts.init(barChart.value) }

const showAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  const now = new Date()
  evaluationForm.value = { supplier_id: selectedSupplierId.value || (suppliers.value[0]?.supplier_id || 0), delivery_punctuality_score: 5, delivery_punctuality_evidence: '', quality_consistency_score: 5, quality_consistency_evidence: '', service_response_score: 5, service_response_evidence: '', cooperation_score: 5, cooperation_evidence: '', evaluator: localStorage.getItem('username') || '当前用户', remarks: '', evaluation_date: now.toISOString().replace('T', ' ').substring(0, 19) }
  dialogVisible.value = true
}

const editEvaluation = (row: SupplierEvaluation) => {
  isEdit.value = true
  editingId.value = row.evaluation_id
  evaluationForm.value = { supplier_id: row.supplier_id, delivery_punctuality_score: row.delivery_punctuality_score || 5, delivery_punctuality_evidence: row.delivery_punctuality_evidence || '', quality_consistency_score: row.quality_consistency_score || 5, quality_consistency_evidence: row.quality_consistency_evidence || '', service_response_score: row.service_response_score || 5, service_response_evidence: row.service_response_evidence || '', cooperation_score: row.cooperation_score || 5, cooperation_evidence: row.cooperation_evidence || '', evaluator: row.evaluator || '', remarks: row.remarks || '', evaluation_date: row.evaluation_date || '' }
  dialogVisible.value = true
}

const saveEvaluation = async () => {
  if (!evaluationForm.value.supplier_id) { ElMessage.warning('请选择供应商'); return }
  saving.value = true
  try {
    if (isEdit.value && editingId.value) {
      await updateSupplierEvaluation(editingId.value, evaluationForm.value as SupplierEvaluationUpdate)
      ElMessage.success('更新成功')
    } else {
      await createSupplierEvaluation(evaluationForm.value.supplier_id, evaluationForm.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await Promise.all([loadAllEvaluations(), loadOverview(), loadChartData()])
  } catch (error) { console.error('保存评价失败:', error); ElMessage.error('保存失败') } finally { saving.value = false }
}

const deleteEvaluation = async (row: SupplierEvaluation) => {
  try {
    await ElMessageBox.confirm(`确定要删除这条评价吗？`, '确认删除', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    await deleteSupplierEvaluation(row.evaluation_id)
    ElMessage.success('删除成功')
    await Promise.all([loadAllEvaluations(), loadOverview(), loadChartData()])
  } catch (error: any) { if (error !== 'cancel') { console.error('删除评价失败:', error); ElMessage.error('删除失败') } }
}

const showSupplierDialog = () => { supplierDialogVisible.value = true }
const showSupplierFormDialog = () => { isEditSupplier.value = false; editingSupplierId.value = null; supplierForm.value = { name: '', contact_person: '', contact_phone: '', contact_email: '', status: 1, remarks: '' }; supplierFormDialogVisible.value = true }
const editSupplier = (supplier: Supplier) => { isEditSupplier.value = true; editingSupplierId.value = supplier.supplier_id; supplierForm.value = { name: supplier.name || '', contact_person: supplier.contact_person || '', contact_phone: supplier.contact_phone || '', contact_email: supplier.contact_email || '', status: supplier.status || 1, remarks: supplier.remarks || '' }; supplierFormDialogVisible.value = true }

const saveSupplier = async () => {
  if (!supplierForm.value.name) { ElMessage.warning('请输入供应商名称'); return }
  savingSupplier.value = true
  try {
    if (isEditSupplier.value && editingSupplierId.value) {
      await updateSupplier(editingSupplierId.value, supplierForm.value)
      ElMessage.success('更新成功')
    } else {
      await createSupplier(supplierForm.value)
      ElMessage.success('创建成功')
    }
    supplierFormDialogVisible.value = false
    supplierDialogVisible.value = false
    await loadSuppliers()
  } catch (error) { console.error('保存供应商失败:', error); ElMessage.error('保存失败') } finally { savingSupplier.value = false }
}

const deleteSupplier = async (supplier: Supplier) => {
  try {
    await ElMessageBox.confirm(`确定要删除供应商"${supplier.name}"吗？`, '确认删除', { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' })
    await deleteSupplierApi(supplier.supplier_id)
    ElMessage.success('删除成功')
    await loadSuppliers()
    await loadOverview()
  } catch (error: any) {
    if (error === 'cancel') return
    const msg = error.response?.data?.message || error.response?.data?.detail || '删除失败'
    ElMessage.warning(msg)
  }
}

const handleSizeChange = (size: number) => { pageSize.value = size; filterEvaluations() }
const handleCurrentChange = (page: number) => { currentPage.value = page; filterEvaluations() }
const handleResize = () => { pieChartInstance?.resize(); barChartInstance?.resize() }

onMounted(async () => {
  await loadSuppliers()
  await Promise.all([loadOverview(), loadChartData(), loadRanking(), loadAIAnalysis(), loadAllEvaluations()])
  initCharts()
  window.addEventListener('resize', handleResize)
})
</script>

<style scoped>
.supplier-performance-container { padding: 20px; background-color: #f5f7fa; min-height: 100%; }
h1 { font-size: 24px; margin-bottom: 20px; color: #303133; }
.stat-card { height: 120px; display: flex; align-items: center; justify-content: center; }
.stat-content { text-align: center; width: 100%; }
.stat-title { font-size: 14px; color: #606266; margin-bottom: 10px; }
.stat-value { font-size: 24px; font-weight: bold; color: #1890ff; }
.chart-card { height: 420px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.chart-container { width: 100%; height: 360px; }
.ai-analysis-content { padding: 10px; max-height: 350px; overflow-y: auto; }
.ai-analysis-content h4 { margin: 0 0 10px 0; color: #303133; }
.analysis-date { font-size: 12px; color: #909399; margin-bottom: 15px; }
.analysis-result { font-size: 14px; color: #606266; line-height: 1.6; white-space: pre-wrap; }
.no-data { display: flex; align-items: center; justify-content: center; height: 300px; color: #909399; font-size: 14px; }
.analyzing-tip { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #409EFF; font-size: 16px; }
.analyzing-tip .el-icon { font-size: 48px; margin-bottom: 16px; }
.analyzing-tip span { margin-top: 8px; }
.evaluation-group { background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%); border-radius: 12px; margin-bottom: 16px; overflow: hidden; border: 1px solid #e0e4e8; }
.group-header { background: linear-gradient(90deg, #409EFF 0%, #66b1ff 100%); color: white; padding: 12px 20px; display: flex; align-items: center; gap: 10px; font-size: 15px; font-weight: 600; box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3); }
.group-header .el-icon { font-size: 20px; }
.group-content { padding: 16px 20px; }
.group-content .el-form-item { margin-bottom: 12px; }
.group-content .el-form-item .el-textarea, .group-content .el-form-item .el-textarea textarea { width: 100%; }
.group-content .el-form-item:last-child { margin-bottom: 0; }
</style>

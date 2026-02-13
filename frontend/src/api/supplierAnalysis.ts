import request from './axios'

export interface Supplier {
  id: number
  supplier_id: number
  name: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  status: number
  created_at?: string
  updated_at?: string
  remarks?: string
}

export interface SupplierEvaluation {
  id: number
  evaluation_id: number
  supplier_id: number
  supplier_name?: string
  delivery_punctuality_score: number
  delivery_punctuality_evidence?: string
  quality_consistency_score: number
  quality_consistency_evidence?: string
  service_response_score: number
  service_response_evidence?: string
  cooperation_score: number
  cooperation_evidence?: string
  overall_score?: number
  evaluation_date?: string
  remarks?: string
  created_by_id?: number
  created_at?: string
  updated_at?: string
}

export interface SupplierEvaluationCreate {
  supplier_id: number
  delivery_punctuality_score: number
  delivery_punctuality_evidence?: string
  quality_consistency_score: number
  quality_consistency_evidence?: string
  service_response_score: number
  service_response_evidence?: string
  cooperation_score: number
  cooperation_evidence?: string
  evaluation_date?: string
  remarks?: string
}

export interface SupplierEvaluationUpdate {
  delivery_punctuality_score?: number
  delivery_punctuality_evidence?: string
  quality_consistency_score?: number
  quality_consistency_evidence?: string
  service_response_score?: number
  service_response_evidence?: string
  cooperation_score?: number
  cooperation_evidence?: string
  evaluation_date?: string
  remarks?: string
}

export interface SupplierRanking {
  id: number
  supplier_id: number
  supplier_name: string
  rank: number
  overall_score: number
  delivery_punctuality_score: number
  quality_consistency_score: number
  service_response_score: number
  cooperation_score: number
  evaluation_count: number
  created_at?: string
}

export interface AnalysisOverview {
  supplier_count: number
  evaluation_count: number
  ranking_count: number
  average_scores: {
    delivery_punctuality: number
    quality_consistency: number
    service_response: number
    cooperation: number
    overall: number
  }
}

export interface ChartData {
  supplier_ranking: SupplierRanking[]
  score_distribution: {
    category: string
    count: number
    percentage: number
  }[]
  trend_data: {
    period: string
    average_score: number
    evaluation_count: number
  }[]
}

export interface TrendData {
  period: string
  average_score: number
  evaluation_count: number
}

export interface ComparisonData {
  suppliers: {
    id: number
    name: string
    scores: {
      delivery_punctuality: number
      quality_consistency: number
      service_response: number
      cooperation: number
      overall: number
    }
  }[]
}

export interface SupplierAIAnalysis {
  analysis_id: number
  analysis_date: string
  summary: string
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
  risk_assessment: string
  performance_trends: string
  competitive_analysis: string
  created_at?: string
}

// 工具函数：构建查询字符串
const buildQueryString = (params: Record<string, any>) => {
  const queryParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  }
  return queryParams.toString() ? '?' + queryParams.toString() : ''
}

// 供应商管理API
export const getSuppliers = (params?: { 
  skip?: number
  size?: number
  page?: number
  size?: number
  status?: number
  name?: string 
}) => {
  const url = '/api/v1/suppliers/' + buildQueryString(params || {})
  return request.get<{ items: Supplier[]; total: number; page: number; size: number }>(url)
}

export const getSupplier = (id: number) => {
  return request.get<Supplier>(`/api/v1/suppliers/${id}`)
}

export const createSupplier = (data: Partial<Supplier>) => {
  return request.post<Supplier>('/api/v1/suppliers/', data)
}

export const updateSupplier = (id: number, data: Partial<Supplier>) => {
  return request.put<Supplier>(`/api/v1/suppliers/${id}`, data)
}

export const deleteSupplier = (id: number) => {
  return request.delete(`/api/v1/suppliers/${id}`)
}

// 供应商评价API
export const getSupplierEvaluations = (
  supplierId: number,
  params?: { 
    skip?: number
    limit?: number
  }
) => {
  const url = `/api/v1/suppliers/${supplierId}/evaluations` + buildQueryString(params || {})
  return request.get<{ items: SupplierEvaluation[]; total: number }>(url)
}

export const createSupplierEvaluation = (
  supplierId: number,
  data: SupplierEvaluationCreate
) => {
  return request.post(`/api/v1/suppliers/${supplierId}/evaluations`, data)
}

export const updateSupplierEvaluation = (
  evaluationId: number,
  data: SupplierEvaluationUpdate
) => {
  return request.put(`/api/v1/suppliers/evaluations/${evaluationId}`, data)
}

export const deleteSupplierEvaluation = (evaluationId: number) => {
  return request.delete(`/api/v1/suppliers/evaluations/${evaluationId}`)
}

// 供应商分析API
export const getSupplierRanking = (limit: number = 10) => {
  return request.get<SupplierRanking[]>(
    `/api/v1/suppliers/performance/ranking?limit=${limit}`
  )
}

export const getSupplierAnalysisOverview = () => {
  return request.get<AnalysisOverview>('/api/v1/suppliers/analysis/overview')
}

export const getSupplierAnalysisTrend = (period: string = 'month') => {
  return request.get<{ period: string; trends: TrendData[] }>(
    `/api/v1/suppliers/analysis/trend?period=${period}`
  )
}

export const getSupplierAnalysisChartData = () => {
  return request.get<ChartData>('/api/v1/suppliers/analysis/chart-data')
}

export const getSupplierAnalysisComparison = (supplierIds: number[]) => {
  return request.get<ComparisonData>(
    `/api/v1/suppliers/analysis/comparison?supplier_ids=${supplierIds.join(',')}`
  )
}

export const getSupplierAIAnalysis = (supplierId?: number) => {
  return request.get(`/api/v1/suppliers/analysis/ai-result`)
}

export const generateSupplierAIAnalysis = () => {
  return request.post(`/api/v1/suppliers/analysis/ai-generate`)
}

export const getSupplierRankingDetail = () => {
  return request.get<SupplierRanking[]>('/api/v1/suppliers/analysis/ranking-detail')
}
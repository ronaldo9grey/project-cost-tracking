import request from './unifiedApi'

export interface CostOverview {
  project_id: number
  project_name: string
  total_budget: number
  total_actual: number
  remaining_budget: number
  budget_execution_rate: number
  material_budget: number
  material_actual: number
  outsourcing_budget: number
  outsourcing_actual: number
  indirect_budget: number
  indirect_actual: number
  labor_budget: number
  labor_actual: number
}

export interface CostCategorySummary {
  material: {
    budget: number
    actual: number
    count: number
  }
  labor: {
    budget: number
    actual: number
    count: number
  }
  outsourcing: {
    budget: number
    actual: number
    count: number
  }
  indirect: {
    budget: number
    actual: number
    count: number
  }
}

export interface CostDetail {
  id: number
  cost_type: string
  name?: string
  description?: string
  amount: number
  date?: string
  create_time?: string
}

export interface CostDetailsResponse {
  items: CostDetail[]
  total: number
  skip: number
  limit: number
}

export interface ChartData {
  pie_chart: Array<{ value: number; name: string }>
  bar_chart: {
    categories: string[]
    budget: number[]
    actual: number[]
  }
}

export interface ExecutionAnalysis {
  project_id: number
  project_name: string
  total_budget: number
  total_actual: number
  total_variance: number
  total_execution_rate: number
  categories: Array<{
    category: string
    field: string
    budget: number
    actual: number
    variance: number
    execution_rate: number
    status: string
  }>
}

export interface CostTrend {
  project_id: number
  project_name: string
  period: string
  trends: Array<{
    date: string
    material: number
    labor: number
    outsourcing: number
    indirect: number
    total: number
  }>
  summary: {
    total_material: number
    total_labor: number
    total_outsourcing: number
    total_indirect: number
    grand_total: number
  }
}

export interface ProjectComparison {
  projects: Array<{
    project_id: number
    project_name: string
    total_budget: number
    total_actual: number
    material_actual: number
    labor_actual: number
    outsourcing_actual: number
    indirect_actual: number
    budget_execution_rate: number
  }>
  comparison: {
    by_budget: any[]
    by_actual: any[]
    by_execution_rate: any[]
  }
}

function buildQueryString(params: Record<string, any>): string {
  const queryParams = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      queryParams.append(key, String(value))
    }
  }
  return queryParams.toString() ? '?' + queryParams.toString() : ''
}

export const getCostOverview = (projectId?: number) => {
  const params = projectId ? { project_id: projectId } : {}
  const queryString = buildQueryString(params)
  const url = '/api/v1/cost/analysis/overview' + queryString
  return request.get<CostOverview | CostOverview[]>(url)
}

export const getCostByCategory = (projectId: number) => {
  const url = '/api/v1/cost/analysis/category' + buildQueryString({ project_id: projectId })
  return request.get<{
    category_summary: CostCategorySummary
    details: CostDetail[]
  }>(url)
}

export const getCostDetails = (
  projectId: number,
  costType?: string,
  skip: number = 0,
  limit: number = 50
) => {
  const url = '/api/v1/cost/analysis/details' + buildQueryString({
    project_id: projectId,
    cost_type: costType,
    skip,
    limit
  })
  return request.get<CostDetailsResponse>(url)
}

export const getChartData = (projectId: number) => {
  const url = '/api/v1/cost/analysis/chart-data' + buildQueryString({ project_id: projectId })
  return request.get<ChartData>(url)
}

export const getBudgetExecutionAnalysis = (projectId: number) => {
  const url = '/api/v1/cost/analysis/execution-rate' + buildQueryString({ project_id: projectId })
  return request.get<ExecutionAnalysis>(url)
}

export const getCostTrend = (projectId: number, period: string = 'month') => {
  const url = '/api/v1/cost/analysis/trend' + buildQueryString({ project_id: projectId, period })
  return request.get<CostTrend>(url)
}

export const getProjectComparison = (projectIds: number[]) => {
  const url = '/api/v1/cost/analysis/comparison' + buildQueryString({ project_ids: projectIds.join(',') })
  return request.get<ProjectComparison>(url)
}

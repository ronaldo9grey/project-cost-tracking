import request from './axios'

export const getProjectFullData = (projectId: number) => {
  return request.get<{
    project: any
    tasks: any[]
    material_costs: any[]
    labor_costs: any[]
    outsourcing_costs: any[]
    indirect_costs: any[]
  }>(`/api/v1/ai/project/${projectId}/full-data`)
}

export const chatWithAI = (projectContext: any, userQuestion: string) => {
  return request.post<string>('/api/v1/ai/chat', {
    project_context: projectContext,
    user_question: userQuestion
  })
}

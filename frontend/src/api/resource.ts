import request from './unifiedApi'

// 人员管理相关接口

export interface Personnel {
  id: number
  employee_id: string
  name: string
  department: string
  position: string
  phone: string | null
  email: string | null
  created_by_id: number | null
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface PersonnelCreate {
  employee_id: string
  name: string
  department: string
  position: string
  phone?: string
  email?: string
  created_by_id?: number
  password?: string
  role_id?: number
}

export interface PersonnelUpdate {
  employee_id?: string
  name?: string
  department?: string
  position?: string
  phone?: string
  email?: string
  password?: string
  role_id?: number
}

/**
 * 获取人员列表
 * @param params 查询参数
 */
export const getPersonnel = (params?: { skip?: number; limit?: number; name?: string; employee_id?: string; department?: string }) => {
  return request.get<Personnel[]>('/api/v1/resource/personnel', { params })
}

/**
 * 创建人员
 * @param personnel 人员信息
 */
export const createPersonnel = (personnel: PersonnelCreate) => {
  return request.post<Personnel>('/api/v1/resource/personnel/', personnel)
}

/**
 * 更新人员
 * @param personnelId 人员ID
 * @param personnel 人员信息
 */
export const updatePersonnel = (personnelId: number, personnel: PersonnelUpdate) => {
  return request.put<Personnel>(`/v1/resource/personnel/${personnelId}/`, personnel)
}

/**
 * 删除人员
 * @param personnelId 人员ID
 */
export const deletePersonnel = (personnelId: number) => {
  return request.delete(`/v1/resource/personnel/${personnelId}/`)
}

// 设备管理相关接口
export interface Equipment {
  id: number
  name: string
  model: string | null
  serial_number: string | null
  status: string
  purchase_date: string | null
  purchase_price: number | null
  location: string | null
  description: string | null
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface EquipmentCreate {
  name: string
  model?: string
  serial_number?: string
  status: string
  purchase_date?: string
  purchase_price?: number
  location?: string
  description?: string
}

export interface EquipmentUpdate {
  name?: string
  model?: string
  serial_number?: string
  status?: string
  purchase_date?: string
  purchase_price?: number
  location?: string
  description?: string
}

/**
 * 获取设备列表
 * @param params 查询参数
 */
export const getEquipment = (params?: { skip?: number; limit?: number; status?: string }) => {
  return request.get<Equipment[]>('/api/v1/resource/equipment/', { params })
}

/**
 * 创建设备
 * @param equipment 设备信息
 */
export const createEquipment = (equipment: EquipmentCreate) => {
  return request.post<Equipment>('/api/v1/resource/equipment/', equipment)
}

/**
 * 更新设备
 * @param equipmentId 设备ID
 * @param equipment 设备信息
 */
export const updateEquipment = (equipmentId: number, equipment: EquipmentUpdate) => {
  return request.put<Equipment>(`/v1/resource/equipment/${equipmentId}/`, equipment)
}

/**
 * 删除设备
 * @param equipmentId 设备ID
 */
export const deleteEquipment = (equipmentId: number) => {
  return request.delete(`/v1/resource/equipment/${equipmentId}/`)
}

// 物料管理相关接口
export interface Material {
  material_id: string
  material_name: string
  specification: string | null
  unit: string | null
  stock_quantity: number
  unit_price: number
  supplier: string | null
  create_time: string
  update_time: string
  is_deleted: boolean
}

export interface MaterialCreate {
  material_id: string
  material_name: string
  specification?: string
  unit?: string
  stock_quantity?: number
  unit_price?: number
  supplier?: string
}

export interface MaterialUpdate {
  material_id?: string
  material_name?: string
  specification?: string
  unit?: string
  stock_quantity?: number
  unit_price?: number
  supplier?: string
}

/**
 * 获取物料列表
 * @param params 查询参数
 */
export const getMaterials = (params?: { skip?: number; limit?: number; material_name?: string; supplier?: string }) => {
  return request.get<Material[]>('/api/v1/resource/materials/', { params })
}

/**
 * 创建物料
 * @param material 物料信息
 */
export const createMaterial = (material: MaterialCreate) => {
  return request.post<Material>('/api/v1/resource/materials/', material)
}

/**
 * 更新物料
 * @param materialId 物料ID
 * @param material 物料信息
 */
export const updateMaterial = (materialId: string, material: MaterialUpdate) => {
  return request.put<Material>(`/v1/resource/materials/${materialId}/`, material)
}

/**
 * 删除物料
 * @param materialId 物料ID
 */
export const deleteMaterial = (materialId: string) => {
  return request.delete(`/v1/resource/materials/${materialId}/`)
}

// 间接成本类型相关接口
export interface IndirectCostType {
  id: number
  type_name: string
  description: string | null
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface IndirectCostTypeCreate {
  type_name: string
  description?: string
}

export interface IndirectCostTypeUpdate {
  type_name?: string
  description?: string
}

/**
 * 获取间接成本类型列表
 * @param params 查询参数
 */
export const getIndirectCostTypes = (params?: { skip?: number; limit?: number; type_name?: string }) => {
  return request.get<IndirectCostType[]>('/api/v1/resource/indirect-cost-types/', { params })
}

/**
 * 创建间接成本类型
 * @param costType 成本类型信息
 */
export const createIndirectCostType = (costType: IndirectCostTypeCreate) => {
  return request.post<IndirectCostType>('/api/v1/resource/indirect-cost-types/', costType)
}

/**
 * 更新间接成本类型
 * @param typeId 成本类型ID
 * @param costType 成本类型信息
 */
export const updateIndirectCostType = (typeId: number, costType: IndirectCostTypeUpdate) => {
  return request.put<IndirectCostType>(`/v1/resource/indirect-cost-types/${typeId}/`, costType)
}

/**
 * 删除间接成本类型
 * @param typeId 成本类型ID
 */
export const deleteIndirectCostType = (typeId: number) => {
  return request.delete(`/v1/resource/indirect-cost-types/${typeId}/`)
}

// 外包服务类型相关接口
export interface OutsourcingServiceType {
  id: number
  type_name: string
  description: string | null
  created_at: string
  updated_at: string
  is_deleted: boolean
}

export interface OutsourcingServiceTypeCreate {
  type_name: string
  description?: string
}

export interface OutsourcingServiceTypeUpdate {
  type_name?: string
  description?: string
}

// 简化的员工分组相关接口（单表设计）

export interface EmployeeGroupRelation {
  id: number
  group_name: string
  group_description?: string
  relation_type: 'member' | 'supervisor'
  employee_id?: string
  employee_name?: string
  department?: string
  position?: string
  supervisor_position?: string
  is_primary: boolean
  created_at: string
  updated_at: string
  created_by?: string
  remarks?: string
}

export interface GroupInfo {
  group_name: string
  group_description?: string
  members: {
    employee_id: string
    employee_name: string
    department?: string
    position?: string
  }[]
  supervisors: {
    id: number
    employee_id: string
    employee_name: string
    supervisor_position?: string
    is_primary: boolean
  }[]
}

export interface CreateGroupMember {
  group_name: string
  group_description?: string
  employee_id: string
  employee_name: string
  department?: string
  position?: string
}

export interface CreateGroupSupervisor {
  group_name: string
  group_description?: string
  employee_id: string
  employee_name: string
  supervisor_position?: string
  is_primary?: boolean
}

/**
 * 获取所有分组信息
 */
export const getEmployeeGroupRelations = () => {
  return request.get<EmployeeGroupRelation[]>('/api/v1/resource/employee-group-relations')
}

/**
 * 创建空分组
 */
export const createEmptyGroup = (data: { group_name: string; group_description: string }) => {
  return request.post('/api/v1/resource/groups', data)
}

/**
 * 创建分组（添加第一个成员时自动创建分组）
 */
export const createGroupMember = (data: CreateGroupMember) => {
  return request.post<EmployeeGroupRelation>('/api/v1/resource/group-members', data)
}

/**
 * 创建分组上级
 */
export const createGroupSupervisor = (data: CreateGroupSupervisor) => {
  return request.post<EmployeeGroupRelation>('/api/v1/resource/group-supervisors', data)
}

/**
 * 删除分组关系记录
 */
export const deleteGroupRelation = (id: number) => {
  return request.delete(`/api/v1/resource/group-relations/${id}`)
}

/**
 * 批量删除分组关系记录
 */
export const batchDeleteGroupRelations = (ids: number[]) => {
  return request.delete('/api/v1/resource/group-relations/batch', { data: { ids } })
}

/**
 * 更新分组描述
 */
export const updateGroupDescription = (groupName: string, description: string) => {
  return request.put(`/api/v1/resource/groups/${encodeURIComponent(groupName)}/description`, { description })
}

/**
 * 更新员工分组关系（主要用于设置主上级）
 */
export const updateEmployeeGroupRelation = (id: number, data: { is_primary?: boolean; supervisor_position?: string }) => {
  return request.put(`/api/v1/resource/group-relations/${id}`, data)
}

/**
 * 删除整个分组（删除所有相关记录）
 */
export const deleteEntireGroup = (groupName: string) => {
  return request.delete(`/api/v1/resource/groups/${encodeURIComponent(groupName)}`)
}

/**
 * 获取外包服务类型列表
 * @param params 查询参数
 */
export const getOutsourcingServiceTypes = (params?: { skip?: number; limit?: number; type_name?: string }) => {
  return request.get<OutsourcingServiceType[]>('/api/v1/resource/outsourcing-service-types/', { params })
}

/**
 * 创建外包服务类型
 * @param serviceType 服务类型信息
 */
export const createOutsourcingServiceType = (serviceType: OutsourcingServiceTypeCreate) => {
  return request.post<OutsourcingServiceType>('/api/v1/resource/outsourcing-service-types/', serviceType)
}

/**
 * 更新外包服务类型
 * @param typeId 服务类型ID
 * @param serviceType 服务类型信息
 */
export const updateOutsourcingServiceType = (typeId: number, serviceType: OutsourcingServiceTypeUpdate) => {
  return request.put<OutsourcingServiceType>(`/v1/resource/outsourcing-service-types/${typeId}/`, serviceType)
}

/**
 * 删除外包服务类型
 * @param typeId 服务类型ID
 */
export const deleteOutsourcingServiceType = (typeId: number) => {
  return request.delete(`/v1/resource/outsourcing-service-types/${typeId}/`)
}
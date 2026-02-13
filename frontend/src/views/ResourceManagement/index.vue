<template>
  <div class="resource-management-container">
    <h1>资源管理</h1>
    
    <!-- 资源类型标签页 -->
    <el-tabs v-model="activeTab" type="border-card" style="margin-bottom: 20px;" @tab-change="handleTabChange">
      <el-tab-pane label="人员管理" name="personnel">
        <!-- 人员管理内容 -->
        <div class="personnel-management">
          <!-- 操作栏 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="12">
              <el-input
                v-model="personnelSearchQuery"
                placeholder="搜索人员姓名或部门"
                style="width: 300px;"
              >
                <template #append>
                  <el-button type="primary">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" @click="openAddPersonnelDialog">
                <el-icon><Plus /></el-icon>
                新增人员
              </el-button>
              <el-button @click="refreshPersonnelList">
                <el-icon><Refresh /></el-icon>
                刷新列表
              </el-button>
            </el-col>
          </el-row>
          
          <!-- 人员列表 -->
          <el-table :data="filteredPersonnel" style="width: 100%" v-loading="loading">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="人员ID" width="80" />
            <el-table-column prop="employee_id" label="员工编号" width="120" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="department" label="部门" />
            <el-table-column prop="position" label="职位" />
            <el-table-column prop="phone" label="联系电话" />
            <el-table-column prop="email" label="邮箱" />
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewPersonnelDetails(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button type="warning" size="small" @click="editPersonnel(scope.row)">
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deletePersonnel(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="物料/设备管理" name="materials">
        <!-- 物料/设备管理内容 -->
        <div class="materials-management">
          <!-- 操作栏 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="12">
              <el-input
                v-model="materialsSearchQuery"
                placeholder="搜索物料名称或供应商"
                style="width: 300px;"
              >
                <template #append>
                  <el-button type="primary">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" @click="openAddMaterialDialog">
                <el-icon><Plus /></el-icon>
                新增物料/设备
              </el-button>
              <el-button @click="refreshMaterialsList">
                <el-icon><Refresh /></el-icon>
                刷新列表
              </el-button>
            </el-col>
          </el-row>
          
          <!-- 物料列表 -->
          <el-table :data="filteredMaterials" style="width: 100%" v-loading="materialsLoading">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="material_id" label="物料ID" width="120" />
            <el-table-column prop="material_name" label="物料名称" />
            <el-table-column prop="specification" label="规格型号" />
            <el-table-column prop="unit" label="单位" />
            <el-table-column prop="stock_quantity" label="库存数量" />
            <el-table-column prop="unit_price" label="单价" />
            <el-table-column prop="supplier" label="供应商" />
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewMaterialDetails(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button type="warning" size="small" @click="editMaterial(scope.row)">
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteMaterialHandler(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="间接成本类型" name="indirectCostTypes">
        <!-- 间接成本类型管理内容 -->
        <div class="indirect-cost-types-management">
          <!-- 操作栏 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="12">
              <el-input
                v-model="indirectCostTypeSearchQuery"
                placeholder="搜索成本类型名称"
                style="width: 300px;"
              >
                <template #append>
                  <el-button type="primary">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" @click="openAddIndirectCostTypeDialog">
                <el-icon><Plus /></el-icon>
                新增成本类型
              </el-button>
              <el-button @click="refreshIndirectCostTypesList">
                <el-icon><Refresh /></el-icon>
                刷新列表
              </el-button>
            </el-col>
          </el-row>
          
          <!-- 间接成本类型列表 -->
          <el-table :data="filteredIndirectCostTypes" style="width: 100%" v-loading="indirectCostTypesLoading">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="类型ID" width="80" />
            <el-table-column prop="type_name" label="类型名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewIndirectCostTypeDetails(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button type="warning" size="small" @click="editIndirectCostType(scope.row)">
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteIndirectCostTypeHandler(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="外包服务类型" name="outsourcingServiceTypes">
        <!-- 外包服务类型管理内容 -->
        <div class="outsourcing-service-types-management">
          <!-- 操作栏 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="12">
              <el-input
                v-model="outsourcingServiceTypeSearchQuery"
                placeholder="搜索服务类型名称"
                style="width: 300px;"
              >
                <template #append>
                  <el-button type="primary">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" @click="openAddOutsourcingServiceTypeDialog">
                <el-icon><Plus /></el-icon>
                新增服务类型
              </el-button>
              <el-button @click="refreshOutsourcingServiceTypesList">
                <el-icon><Refresh /></el-icon>
                刷新列表
              </el-button>
            </el-col>
          </el-row>
          
          <!-- 外包服务类型列表 -->
          <el-table :data="filteredOutsourcingServiceTypes" style="width: 100%" v-loading="outsourcingServiceTypesLoading">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="类型ID" width="80" />
            <el-table-column prop="type_name" label="类型名称" />
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="240" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="viewOutsourcingServiceTypeDetails(scope.row)">
                  <el-icon><View /></el-icon>
                  详情
                </el-button>
                <el-button type="warning" size="small" @click="editOutsourcingServiceType(scope.row)">
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteOutsourcingServiceTypeHandler(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="员工分组管理" name="hierarchy">
        <!-- 员工分组管理内容 -->
        <div class="hierarchy-management">
          <!-- 操作栏 -->
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="12">
              <el-input
                v-model="hierarchySearchQuery"
                placeholder="搜索分组名称"
                style="width: 300px;"
              >
                <template #append>
                  <el-button type="primary">搜索</el-button>
                </template>
              </el-input>
            </el-col>
            <el-col :span="12" style="text-align: right;">
              <el-button type="primary" @click="openAddGroupDialog">
                <el-icon><Plus /></el-icon>
                新建分组
              </el-button>
              <el-button @click="refreshHierarchyList">
                <el-icon><Refresh /></el-icon>
                刷新列表
              </el-button>
            </el-col>
          </el-row>
          
          <!-- 员工分组列表 -->
          <el-table :data="filteredHierarchyList" style="width: 100%" v-loading="hierarchyLoading">
            <el-table-column type="selection" width="55" />
            <el-table-column prop="group_name" label="分组名称" width="150" />
            <el-table-column prop="group_description" label="分组描述" min-width="200" show-overflow-tooltip />
            <el-table-column label="成员数量" width="100">
              <template #default="scope">
                <el-tag type="info">{{ scope.row.members?.length || 0 }}人</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="上级领导" min-width="250">
              <template #default="scope">
                <div v-if="scope.row.supervisors && scope.row.supervisors.length > 0">
                  <el-tag
                    v-for="(supervisor, index) in scope.row.supervisors"
                    :key="supervisor.id || supervisor.relation_id"
                    :type="supervisor.is_primary ? 'primary' : 'warning'"
                    style="margin-right: 6px; margin-bottom: 4px;"
                  >
                    {{ supervisor.employee_name || supervisor.name }}
                    <span v-if="supervisor.supervisor_position" style="margin-left: 4px;">({{ supervisor.supervisor_position }})</span>
                    <el-tag v-if="supervisor.is_primary" type="danger" size="mini" style="margin-left: 4px;">主</el-tag>
                  </el-tag>
                </div>
                <div v-else class="text-muted">暂无上级</div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="300" fixed="right">
              <template #default="scope">
                <el-button type="primary" size="small" @click="manageGroupMembers(scope.row)">
                  <el-icon><User /></el-icon>
                  成员
                </el-button>
                <el-button type="warning" size="small" @click="manageGroupSupervisors(scope.row)">
                  <el-icon><Avatar /></el-icon>
                  上级
                </el-button>
                <el-button type="success" size="small" @click="editGroup(scope.row)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteGroup(scope.row)">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 新增/编辑对话框 -->
    <!-- 人员对话框 -->
    <el-dialog
      v-model="personnelDialogVisible"
      :title="personnelDialogTitle"
      width="600px"
      @close="resetPersonnelForm"
    >
      <el-form ref="personnelForm" :model="personnelFormData" label-width="120px">
        <el-form-item label="姓名" prop="name" required>
          <el-input v-model="personnelFormData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="部门" required>
          <el-input v-model="personnelFormData.department" placeholder="请输入部门" />
        </el-form-item>
        <el-form-item label="职位" required>
          <el-input v-model="personnelFormData.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="联系电话" required>
          <el-input v-model="personnelFormData.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="personnelFormData.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="状态" required>
          <el-select v-model="personnelFormData.status" placeholder="请选择状态">
            <el-option label="在职" value="在职" />
            <el-option label="请假" value="请假" />
            <el-option label="离职" value="离职" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="personnelDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="savePersonnel">保存</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 物料对话框 -->
    <el-dialog
      v-model="materialDialogVisible"
      :title="materialDialogTitle"
      width="600px"
      @close="resetMaterialForm"
    >
      <el-form ref="materialForm" :model="materialFormData" label-width="120px">
        <el-form-item label="物料ID" prop="material_id" required>
          <el-input v-model="materialFormData.material_id" placeholder="请输入物料ID" />
        </el-form-item>
        <el-form-item label="物料名称" required>
          <el-input v-model="materialFormData.material_name" placeholder="请输入物料名称" />
        </el-form-item>
        <el-form-item label="规格型号">
          <el-input v-model="materialFormData.specification" placeholder="请输入规格型号" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="materialFormData.unit" placeholder="请输入单位" />
        </el-form-item>
        <el-form-item label="库存数量">
          <el-input v-model="materialFormData.stock_quantity" placeholder="请输入库存数量" type="number" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input v-model="materialFormData.unit_price" placeholder="请输入单价" type="number" />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="materialFormData.supplier" placeholder="请输入供应商" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="materialDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveMaterialHandler">保存</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 间接成本类型对话框 -->
    <el-dialog
      v-model="indirectCostTypeDialogVisible"
      :title="indirectCostTypeDialogTitle"
      width="600px"
      @close="resetIndirectCostTypeForm"
    >
      <el-form ref="indirectCostTypeForm" :model="indirectCostTypeFormData" label-width="120px">
        <el-form-item label="类型名称" required>
          <el-input v-model="indirectCostTypeFormData.type_name" placeholder="请输入成本类型名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="indirectCostTypeFormData.description" placeholder="请输入成本类型描述" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="indirectCostTypeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveIndirectCostTypeHandler">保存</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 外包服务类型对话框 -->
    <el-dialog
      v-model="outsourcingServiceTypeDialogVisible"
      :title="outsourcingServiceTypeDialogTitle"
      width="600px"
      @close="resetOutsourcingServiceTypeForm"
    >
      <el-form ref="outsourcingServiceTypeForm" :model="outsourcingServiceTypeFormData" label-width="120px">
        <el-form-item label="类型名称" required>
          <el-input v-model="outsourcingServiceTypeFormData.type_name" placeholder="请输入服务类型名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="outsourcingServiceTypeFormData.description" placeholder="请输入服务类型描述" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="outsourcingServiceTypeDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveOutsourcingServiceTypeHandler">保存</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 员工分组管理对话框 -->
    
    <!-- 新建分组对话框 -->
    <el-dialog
      v-model="groupDialogVisible"
      :title="groupDialogTitle"
      width="700px"
      @close="resetGroupForm"
    >
      <el-form ref="groupForm" :model="groupFormData" label-width="120px">
        <el-form-item label="分组名称" prop="group_name" required>
          <el-input v-model="groupFormData.group_name" placeholder="请输入分组名称（如：部门-小组）" />
        </el-form-item>
        <el-form-item label="分组描述" prop="group_description">
          <el-input 
            v-model="groupFormData.group_description" 
            type="textarea" 
            :rows="3"
            placeholder="请输入分组描述" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="groupDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveGroup">保存</el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 管理分组成员对话框 -->
    <el-dialog
      v-model="memberDialogVisible"
      title="管理分组成员"
      width="800px"
      :before-close="handleMemberDialogClose"
    >
      <div class="member-management">
        <!-- 添加成员 -->
        <div class="add-member-section">
          <h4>添加成员</h4>
          <el-form :model="addMemberForm" label-width="80px" inline>
            <el-form-item label="员工">
              <el-select 
                v-model="addMemberForm.employee_id" 
                filterable 
                placeholder="搜索员工姓名或编号"
                style="width: 250px;"
                :filter-method="filterMemberOptions"
              >
                <el-option
                  v-for="person in filteredMemberOptions"
                  :key="person.employee_id"
                  :label="`${person.name} (${person.employee_id})`"
                  :value="person.employee_id"
                  :disabled="isEmployeeInGroup(person.employee_id, currentGroupForMember)"
                />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="addGroupMember"
                :disabled="!addMemberForm.employee_id"
              >
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
              <el-button @click="memberDialogVisible = false" style="margin-left: 10px;">
                <el-icon><Close /></el-icon>
                关闭
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 成员列表 -->
        <div class="member-list-section">
          <h4>分组成员</h4>
          <el-table 
            :data="currentGroupForMember?.members || []" 
            style="width: 100%; margin-top: 10px;"
            size="small"
          >
            <el-table-column prop="employee_id" label="员工编号" width="120" />
            <el-table-column prop="employee_name" label="姓名" />
            <el-table-column prop="department" label="部门" />
            <el-table-column prop="position" label="职位" />
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="scope">
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeGroupMember(scope.$index, scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
    
    <!-- 管理分组上级对话框 -->
    <el-dialog
      v-model="supervisorDialogVisible"
      title="管理分组上级"
      width="800px"
      :before-close="handleSupervisorDialogClose"
    >
      <div class="supervisor-management">
        <!-- 添加上级 -->
        <div class="add-supervisor-section">
          <h4>添加上级</h4>
          <el-form :model="addSupervisorForm" label-width="80px" inline>
            <el-form-item label="上级">
              <el-select 
                v-model="addSupervisorForm.employee_id" 
                filterable 
                placeholder="选择上级"
                style="width: 200px;"
                @change="handleSupervisorChange"
              >
                <el-option
                  v-for="person in personnel"
                  :key="person.employee_id"
                  :label="`${person.name} (${person.employee_id})`"
                  :value="person.employee_id"
                  :disabled="isEmployeeInGroup(person.employee_id, currentGroupForSupervisor, 'supervisor')"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="职位">
              <el-input 
                v-model="addSupervisorForm.supervisor_position" 
                placeholder="上级职位"
                style="width: 200px;"
              />
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                @click="addGroupSupervisor"
                :disabled="!addSupervisorForm.employee_id"
              >
                <el-icon><Plus /></el-icon>
                添加
              </el-button>
              <el-button @click="supervisorDialogVisible = false" style="margin-left: 10px;">
                <el-icon><Close /></el-icon>
                关闭
              </el-button>
            </el-form-item>
          </el-form>
        </div>
        
        <!-- 上级列表 -->
        <div class="supervisor-list-section">
          <h4>分组上级</h4>
          <el-table 
            :data="currentGroupForSupervisor?.supervisors || []" 
            style="width: 100%; margin-top: 10px;"
            size="small"
          >
            <el-table-column prop="employee_id" label="员工编号" width="120" />
            <el-table-column prop="employee_name" label="姓名" />
            <el-table-column prop="supervisor_position" label="职位" />
            <el-table-column label="直接上级" width="100">
              <template #default="scope">
                <el-tag 
                  :type="scope.row.is_primary ? 'primary' : 'warning'" 
                  size="small"
                >
                  {{ scope.row.is_primary ? '是' : '否' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button 
                  type="warning" 
                  size="small" 
                  @click="togglePrimarySupervisor(scope.$index, scope.row)"
                  v-if="!scope.row.is_primary"
                >
                  <el-icon><Star /></el-icon>
                  设为直接
                </el-button>
                <el-button 
                  type="danger" 
                  size="small" 
                  @click="removeGroupSupervisor(scope.$index, scope.row)"
                >
                  <el-icon><Delete /></el-icon>
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { 
  Plus, 
  Refresh, 
  View, 
  EditPen, 
  Delete,
  User,
  Avatar,
  Star
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
// 导入资源管理API
import { 
  getPersonnel, 
  Personnel,
  getMaterials, 
  createMaterial, 
  updateMaterial, 
  deleteMaterial, 
  Material, 
  MaterialCreate, 
  MaterialUpdate,
  getIndirectCostTypes, 
  createIndirectCostType, 
  updateIndirectCostType, 
  deleteIndirectCostType, 
  IndirectCostType, 
  IndirectCostTypeCreate, 
  IndirectCostTypeUpdate,
  getOutsourcingServiceTypes, 
  createOutsourcingServiceType, 
  updateOutsourcingServiceType, 
  deleteOutsourcingServiceType, 
  OutsourcingServiceType, 
  OutsourcingServiceTypeCreate, 
  OutsourcingServiceTypeUpdate,
  getEmployeeGroupRelations,
  createGroupMember,
  createGroupSupervisor,
  createEmptyGroup,
  deleteGroupRelation,
  batchDeleteGroupRelations,
  updateGroupDescription,
  updateEmployeeGroupRelation,
  deleteEntireGroup,
  EmployeeGroupRelation,
  GroupInfo
} from '../../api/resource'

// 活跃的标签页
const activeTab = ref('personnel')

// 人员管理数据
const personnel = ref<Personnel[]>([])
const personnelSearchQuery = ref('')
const filteredPersonnel = computed(() => {
  if (!personnelSearchQuery.value) {
    return personnel.value
  }
  return personnel.value.filter(p => 
    p.name.toLowerCase().includes(personnelSearchQuery.value.toLowerCase()) ||
    p.department?.toLowerCase().includes(personnelSearchQuery.value.toLowerCase())
  )
})

// 下拉框过滤员工选项
const filteredMemberOptions = ref<Personnel[]>([])

// 过滤员工选项方法
const filterMemberOptions = (query: string) => {
  if (!query) {
    filteredMemberOptions.value = personnel.value
    return
  }
  filteredMemberOptions.value = personnel.value.filter(person => 
    person.name.toLowerCase().includes(query.toLowerCase()) ||
    person.employee_id.toLowerCase().includes(query.toLowerCase()) ||
    person.department?.toLowerCase().includes(query.toLowerCase())
  )
}

// 初始化过滤选项
onMounted(() => {
  filteredMemberOptions.value = personnel.value
})

// 物料管理数据
const materials = ref<Material[]>([])
const materialsSearchQuery = ref('')
const filteredMaterials = computed(() => {
  if (!materialsSearchQuery.value) {
    return materials.value
  }
  return materials.value.filter(m => 
    m.material_name.toLowerCase().includes(materialsSearchQuery.value.toLowerCase()) ||
    m.supplier?.toLowerCase().includes(materialsSearchQuery.value.toLowerCase())
  )
})

// 间接成本类型数据
const indirectCostTypes = ref<IndirectCostType[]>([])
const indirectCostTypeSearchQuery = ref('')
const filteredIndirectCostTypes = computed(() => {
  if (!indirectCostTypeSearchQuery.value) {
    return indirectCostTypes.value
  }
  return indirectCostTypes.value.filter(ict => 
    ict.type_name.toLowerCase().includes(indirectCostTypeSearchQuery.value.toLowerCase())
  )
})

// 外包服务类型数据
const outsourcingServiceTypes = ref<OutsourcingServiceType[]>([])
const outsourcingServiceTypeSearchQuery = ref('')
const filteredOutsourcingServiceTypes = computed(() => {
  if (!outsourcingServiceTypeSearchQuery.value) {
    return outsourcingServiceTypes.value
  }
  return outsourcingServiceTypes.value.filter(ost => 
    ost.type_name.toLowerCase().includes(outsourcingServiceTypeSearchQuery.value.toLowerCase())
  )
})

// 员工分组数据
const hierarchyList = ref<GroupInfo[]>([])
const hierarchySearchQuery = ref('')
const filteredHierarchyList = computed(() => {
  if (!hierarchySearchQuery.value) {
    return hierarchyList.value
  }
  return hierarchyList.value.filter(item => 
    item.group_name.toLowerCase().includes(hierarchySearchQuery.value.toLowerCase()) ||
    item.group_description?.toLowerCase().includes(hierarchySearchQuery.value.toLowerCase())
  )
})

// 加载状态
const loading = ref(false)
const materialsLoading = ref(false)
const indirectCostTypesLoading = ref(false)
const outsourcingServiceTypesLoading = ref(false)
const hierarchyLoading = ref(false)

// 加载人员数据
const loadPersonnel = async () => {
  loading.value = true
  try {
    console.log('开始加载人员数据...')
    // 由于axios拦截器已经处理了响应，直接返回数据
    const response = await getPersonnel()
    console.log('API返回数据:', response)
    
    // 检查响应格式，如果是对象且包含value属性，则使用value作为实际数据
    let personnelData: Personnel[] = []
    console.log('原始响应对象:', response)
    console.log('响应类型:', typeof response)
    console.log('是否为数组:', Array.isArray(response))
    console.log('是否有value属性:', response && 'value' in response)
    
    if (response && typeof response === 'object' && 'value' in response) {
      // 后端返回的是包含value和Count的对象，value才是实际数据
      console.log('使用value属性:', response.value)
      personnelData = response.value
    } else if (Array.isArray(response)) {
      // 直接返回数组的情况
      console.log('直接使用数组:', response)
      personnelData = response
    } else {
      console.log('其他情况，尝试使用data属性:', response?.data)
      if (response?.data && Array.isArray(response.data)) {
        personnelData = response.data
      }
    }
    
    personnel.value = personnelData
    // 更新下拉框过滤选项
    filteredMemberOptions.value = personnelData
    ElMessage.success('人员数据加载成功')
    console.log('人员数据:', personnel.value)
    console.log('数据长度:', personnel.value.length)
    console.log('筛选后数据:', filteredPersonnel.value)
  } catch (error) {
    console.error('加载人员数据失败:', error)
    ElMessage.error('加载人员数据失败')
  } finally {
    loading.value = false
  }
}

// 加载物料数据
const loadMaterials = async () => {
  materialsLoading.value = true
  try {
    console.log('开始加载物料数据...')
    // 由于axios拦截器已经处理了响应，直接返回数据
    const response = await getMaterials()
    console.log('API返回数据:', response)
    
    // 检查响应格式，如果是对象且包含value属性，则使用value作为实际数据
    let materialsData: Material[] = []
    if (response && typeof response === 'object' && 'value' in response) {
      // 后端返回的是包含value和Count的对象，value才是实际数据
      materialsData = response.value
    } else if (Array.isArray(response)) {
      // 直接返回数组的情况
      materialsData = response
    }
    
    materials.value = materialsData
    ElMessage.success('物料数据加载成功')
    console.log('物料数据:', materials.value)
  } catch (error) {
    console.error('加载物料数据失败:', error)
    ElMessage.error('加载物料数据失败')
  } finally {
    materialsLoading.value = false
  }
}

// 加载间接成本类型数据
const loadIndirectCostTypes = async () => {
  indirectCostTypesLoading.value = true
  try {
    console.log('开始加载间接成本类型数据...')
    // 由于axios拦截器已经处理了响应，直接返回数据
    const response = await getIndirectCostTypes()
    console.log('API返回数据:', response)
    
    // 检查响应格式，如果是对象且包含value属性，则使用value作为实际数据
    let costTypesData: IndirectCostType[] = []
    if (response && typeof response === 'object' && 'value' in response) {
      // 后端返回的是包含value和Count的对象，value才是实际数据
      costTypesData = response.value
    } else if (Array.isArray(response)) {
      // 直接返回数组的情况
      costTypesData = response
    }
    
    indirectCostTypes.value = costTypesData
    ElMessage.success('间接成本类型数据加载成功')
    console.log('间接成本类型数据:', indirectCostTypes.value)
  } catch (error) {
    console.error('加载间接成本类型数据失败:', error)
    ElMessage.error('加载间接成本类型数据失败')
  } finally {
    indirectCostTypesLoading.value = false
  }
}

// 加载外包服务类型数据
const loadOutsourcingServiceTypes = async () => {
  outsourcingServiceTypesLoading.value = true
  try {
    console.log('开始加载外包服务类型数据...')
    // 由于axios拦截器已经处理了响应，直接返回数据
    const response = await getOutsourcingServiceTypes()
    console.log('API返回数据:', response)
    
    // 检查响应格式，如果是对象且包含value属性，则使用value作为实际数据
    let serviceTypesData: OutsourcingServiceType[] = []
    if (response && typeof response === 'object' && 'value' in response) {
      // 后端返回的是包含value和Count的对象，value才是实际数据
      serviceTypesData = response.value
    } else if (Array.isArray(response)) {
      // 直接返回数组的情况
      serviceTypesData = response
    }
    
    outsourcingServiceTypes.value = serviceTypesData
    ElMessage.success('外包服务类型数据加载成功')
    console.log('外包服务类型数据:', outsourcingServiceTypes.value)
  } catch (error) {
    console.error('加载外包服务类型数据失败:', error)
    ElMessage.error('加载外包服务类型数据失败')
  } finally {
    outsourcingServiceTypesLoading.value = false
  }
}

// 初始化加载数据
onMounted(() => {
  loadPersonnel()
})

// 加载员工分组数据（简化为单表设计）
const loadHierarchyList = async () => {
  hierarchyLoading.value = true
  try {
    console.log('开始加载员工分组数据...')
    const response = await getEmployeeGroupRelations()
    console.log('API返回数据:', response)
    
    // 检查响应格式 - 新的API返回格式是 {code, message, data}
    let relationsData: EmployeeGroupRelation[] = []
    if (response && response.data && Array.isArray(response.data)) {
      relationsData = response.data
    } else if (response && typeof response === 'object' && 'value' in response) {
      relationsData = response.value
    } else if (Array.isArray(response)) {
      relationsData = response
    }
    
    console.log('处理后的关系数据:', relationsData)
    
    // 按分组整理数据
    const groupsMap = new Map<string, GroupInfo>()
    
    relationsData.forEach(relation => {
      const groupName = relation.group_name
      
      if (!groupsMap.has(groupName)) {
        groupsMap.set(groupName, {
          group_name: groupName,
          group_description: relation.group_description,
          members: [],
          supervisors: []
        })
      }
      
      const group = groupsMap.get(groupName)!
      
      if (relation.relation_type === 'member' && relation.employee_id) {
        group.members.push({
          employee_id: relation.employee_id,
          employee_name: relation.employee_name || '',
          department: relation.department,
          position: relation.position
        })
      } else if (relation.relation_type === 'supervisor' && relation.employee_id) {
        group.supervisors.push({
          id: relation.id,
          employee_id: relation.employee_id,
          employee_name: relation.employee_name || '',
          supervisor_position: relation.supervisor_position,
          is_primary: relation.is_primary
        })
      }
    })
    
    hierarchyList.value = Array.from(groupsMap.values())
    ElMessage.success('员工分组数据加载成功')
    console.log('整理后的分组数据:', hierarchyList.value)
  } catch (error) {
    console.error('加载员工分组数据失败:', error)
    ElMessage.error('加载员工分组数据失败')
  } finally {
    hierarchyLoading.value = false
  }
}

// 切换标签页时加载对应数据
const handleTabChange = (tab: string) => {
  if (tab === 'materials') {
    loadMaterials()
  } else if (tab === 'indirectCostTypes') {
    loadIndirectCostTypes()
  } else if (tab === 'outsourcingServiceTypes') {
    loadOutsourcingServiceTypes()
  } else if (tab === 'hierarchy') {
    loadHierarchyList()
  }
}

// 监听标签页变化
activeTab.value = 'personnel'

// 人员对话框数据
const personnelDialogVisible = ref(false)
const personnelDialogTitle = ref('新增人员')
const personnelForm = ref()
const personnelFormData = ref({
  id: null,
  name: '',
  department: '',
  position: '',
  phone: '',
  email: '',
  status: '在职'
})

// 物料对话框数据
const materialDialogVisible = ref(false)
const materialDialogTitle = ref('新增物料/设备')
const materialForm = ref()
const materialFormData = ref({
  material_id: '',
  material_name: '',
  specification: '',
  unit: '',
  stock_quantity: 0,
  unit_price: 0,
  supplier: ''
})

// 间接成本类型对话框数据
const indirectCostTypeDialogVisible = ref(false)
const indirectCostTypeDialogTitle = ref('新增间接成本类型')
const indirectCostTypeForm = ref()
const indirectCostTypeFormData = ref({
  type_name: '',
  description: ''
})

// 外包服务类型对话框数据
const outsourcingServiceTypeDialogVisible = ref(false)
const outsourcingServiceTypeDialogTitle = ref('新增外包服务类型')
const outsourcingServiceTypeForm = ref()
const outsourcingServiceTypeFormData = ref({
  type_name: '',
  description: ''
})

// 员工分组管理对话框数据
const groupDialogVisible = ref(false)
const groupDialogTitle = ref('新建分组')
const groupForm = ref()
const groupFormData = ref({
  group_name: '',
  group_description: ''
})

const memberDialogVisible = ref(false)
const supervisorDialogVisible = ref(false)
const currentGroupForMember = ref<GroupInfo | null>(null)
const currentGroupForSupervisor = ref<GroupInfo | null>(null)

const addMemberForm = ref({
  employee_id: '',
  employee_name: '',
  department: '',
  position: ''
})

const addSupervisorForm = ref({
  employee_id: '',
  employee_name: '',
  supervisor_position: '',
  is_primary: false
})

// 人员管理方法
const openAddPersonnelDialog = () => {
  personnelDialogTitle.value = '新增人员'
  resetPersonnelForm()
  personnelDialogVisible.value = true
}
const editPersonnel = (row: any) => {
  personnelDialogTitle.value = '编辑人员'
  personnelFormData.value = { ...row }
  personnelDialogVisible.value = true
}
const viewPersonnelDetails = (row: any) => {
  console.log('查看人员详情:', row)
}
const deletePersonnel = (row: any) => {
  console.log('删除人员:', row)
}
const savePersonnel = () => {
  console.log('保存人员:', personnelFormData.value)
  personnelDialogVisible.value = false
}
const resetPersonnelForm = () => {
  if (personnelForm.value) {
    personnelForm.value.resetFields()
  }
  personnelFormData.value = {
    id: null,
    name: '',
    department: '',
    position: '',
    phone: '',
    email: '',
    status: '在职'
  }
}
const refreshPersonnelList = () => {
  loadPersonnel()
}

// 物料管理方法
const openAddMaterialDialog = () => {
  materialDialogTitle.value = '新增物料/设备'
  resetMaterialForm()
  materialDialogVisible.value = true
}
const editMaterial = (row: Material) => {
  materialDialogTitle.value = '编辑物料/设备'
  materialFormData.value = { ...row }
  materialDialogVisible.value = true
}
const viewMaterialDetails = (row: Material) => {
  console.log('查看物料详情:', row)
}
const deleteMaterialHandler = async (row: Material) => {
  try {
    await deleteMaterial(row.material_id)
    ElMessage.success('物料删除成功')
    loadMaterials()
  } catch (error) {
    console.error('删除物料失败:', error)
    ElMessage.error('删除物料失败')
  }
}
const saveMaterialHandler = async () => {
  try {
    const materialData = materialFormData.value
    if (materialData.material_id) {
      // 检查是否是现有物料（更新操作）
      const existingMaterial = materials.value.find(m => m.material_id === materialData.material_id)
      if (existingMaterial) {
        // 执行更新操作
        await updateMaterial(materialData.material_id, materialData as MaterialUpdate)
        ElMessage.success('物料更新成功')
      } else {
        // 执行创建操作
        await createMaterial(materialData as MaterialCreate)
        ElMessage.success('物料创建成功')
      }
    } else {
      // 执行创建操作
      await createMaterial(materialData as MaterialCreate)
      ElMessage.success('物料创建成功')
    }
    materialDialogVisible.value = false
    loadMaterials()
  } catch (error) {
    console.error('保存物料失败:', error)
    ElMessage.error('保存物料失败')
  }
}
const resetMaterialForm = () => {
  if (materialForm.value) {
    materialForm.value.resetFields()
  }
  materialFormData.value = {
    material_id: '',
    material_name: '',
    specification: '',
    unit: '',
    stock_quantity: 0,
    unit_price: 0,
    supplier: ''
  }
}
const refreshMaterialsList = () => {
  loadMaterials()
}

// 员工分组管理方法（简化为单表设计）

// 新建分组
const openAddGroupDialog = () => {
  groupDialogTitle.value = '新建分组'
  resetGroupForm()
  groupDialogVisible.value = true
}

// 管理分组成员
const manageGroupMembers = (row: GroupInfo) => {
  currentGroupForMember.value = { ...row }
  resetMemberDialog()
  memberDialogVisible.value = true
}

// 管理分组上级
const manageGroupSupervisors = (row: GroupInfo) => {
  currentGroupForSupervisor.value = { ...row }
  resetSupervisorDialog()
  supervisorDialogVisible.value = true
}

const editGroup = (row: GroupInfo) => {
  groupDialogTitle.value = '编辑分组'
  groupFormData.value = {
    group_name: row.group_name,
    group_description: row.group_description || ''
  }
  groupDialogVisible.value = true
}

const deleteGroup = async (row: GroupInfo) => {
  try {
    await ElMessageBox.confirm(`确认删除分组 "${row.group_name}" 吗？删除后所有成员关系和上级关系将被清除。`, '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteEntireGroup(row.group_name)
    ElMessage.success('分组删除成功')
    loadHierarchyList()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除分组失败:', error)
      ElMessage.error('删除分组失败')
    }
  }
}

const refreshHierarchyList = () => {
  loadHierarchyList()
}

// 分组表单方法
const resetGroupForm = () => {
  if (groupForm.value) {
    groupForm.value.resetFields()
  }
  groupFormData.value = {
    group_name: '',
    group_description: ''
  }
}

const saveGroup = async () => {
  try {
    // 验证必填字段
    if (!groupFormData.value.group_name) {
      ElMessage.error('请输入分组名称')
      return
    }
    
    // 如果是编辑分组，更新描述
    if (groupDialogTitle.value === '编辑分组') {
      await updateGroupDescription(groupFormData.value.group_name, groupFormData.value.group_description)
      ElMessage.success('分组描述更新成功')
    } else {
      // 新建分组：通过创建一个空的分组记录来实现
      // 创建一个空的分组（没有成员和上级，只有分组信息）
      await createEmptyGroup({
        group_name: groupFormData.value.group_name,
        group_description: groupFormData.value.group_description || ''
      })
      ElMessage.success('分组创建成功')
    }
    
    groupDialogVisible.value = false
    loadHierarchyList()
  } catch (error) {
    console.error('保存分组失败:', error)
    ElMessage.error('保存分组失败')
  }
}

// 间接成本类型方法
const openAddIndirectCostTypeDialog = () => {
  indirectCostTypeDialogTitle.value = '新增间接成本类型'
  resetIndirectCostTypeForm()
  indirectCostTypeDialogVisible.value = true
}
const editIndirectCostType = (row: IndirectCostType) => {
  indirectCostTypeDialogTitle.value = '编辑间接成本类型'
  indirectCostTypeFormData.value = { ...row }
  indirectCostTypeDialogVisible.value = true
}
const viewIndirectCostTypeDetails = (row: IndirectCostType) => {
  console.log('查看间接成本类型详情:', row)
}
const deleteIndirectCostTypeHandler = async (row: IndirectCostType) => {
  try {
    await deleteIndirectCostType(row.id)
    ElMessage.success('间接成本类型删除成功')
    loadIndirectCostTypes()
  } catch (error) {
    console.error('删除间接成本类型失败:', error)
    ElMessage.error('删除间接成本类型失败')
  }
}
const saveIndirectCostTypeHandler = async () => {
  try {
    const costTypeData = indirectCostTypeFormData.value
    if (costTypeData.id) {
      // 检查是否是现有成本类型（更新操作）
      const existingType = indirectCostTypes.value.find(ict => ict.id === costTypeData.id)
      if (existingType) {
        // 执行更新操作
        await updateIndirectCostType(costTypeData.id, costTypeData as IndirectCostTypeUpdate)
        ElMessage.success('间接成本类型更新成功')
      } else {
        // 执行创建操作
        await createIndirectCostType(costTypeData as IndirectCostTypeCreate)
        ElMessage.success('间接成本类型创建成功')
      }
    } else {
      // 执行创建操作
      await createIndirectCostType(costTypeData as IndirectCostTypeCreate)
      ElMessage.success('间接成本类型创建成功')
    }
    indirectCostTypeDialogVisible.value = false
    loadIndirectCostTypes()
  } catch (error) {
    console.error('保存间接成本类型失败:', error)
    ElMessage.error('保存间接成本类型失败')
  }
}
const resetIndirectCostTypeForm = () => {
  if (indirectCostTypeForm.value) {
    indirectCostTypeForm.value.resetFields()
  }
  indirectCostTypeFormData.value = {
    type_name: '',
    description: ''
  }
}
const refreshIndirectCostTypesList = () => {
  loadIndirectCostTypes()
}

// 外包服务类型方法
const openAddOutsourcingServiceTypeDialog = () => {
  outsourcingServiceTypeDialogTitle.value = '新增外包服务类型'
  resetOutsourcingServiceTypeForm()
  outsourcingServiceTypeDialogVisible.value = true
}
const editOutsourcingServiceType = (row: OutsourcingServiceType) => {
  outsourcingServiceTypeDialogTitle.value = '编辑外包服务类型'
  outsourcingServiceTypeFormData.value = { ...row }
  outsourcingServiceTypeDialogVisible.value = true
}
const viewOutsourcingServiceTypeDetails = (row: OutsourcingServiceType) => {
  console.log('查看外包服务类型详情:', row)
}
const deleteOutsourcingServiceTypeHandler = async (row: OutsourcingServiceType) => {
  try {
    await deleteOutsourcingServiceType(row.id)
    ElMessage.success('外包服务类型删除成功')
    loadOutsourcingServiceTypes()
  } catch (error) {
    console.error('删除外包服务类型失败:', error)
    ElMessage.error('删除外包服务类型失败')
  }
}
const saveOutsourcingServiceTypeHandler = async () => {
  try {
    const serviceTypeData = outsourcingServiceTypeFormData.value
    if (serviceTypeData.id) {
      // 检查是否是现有服务类型（更新操作）
      const existingType = outsourcingServiceTypes.value.find(ost => ost.id === serviceTypeData.id)
      if (existingType) {
        // 执行更新操作
        await updateOutsourcingServiceType(serviceTypeData.id, serviceTypeData as OutsourcingServiceTypeUpdate)
        ElMessage.success('外包服务类型更新成功')
      } else {
        // 执行创建操作
        await createOutsourcingServiceType(serviceTypeData as OutsourcingServiceTypeCreate)
        ElMessage.success('外包服务类型创建成功')
      }
    } else {
      // 执行创建操作
      await createOutsourcingServiceType(serviceTypeData as OutsourcingServiceTypeCreate)
      ElMessage.success('外包服务类型创建成功')
    }
    outsourcingServiceTypeDialogVisible.value = false
    loadOutsourcingServiceTypes()
  } catch (error) {
    console.error('保存外包服务类型失败:', error)
    ElMessage.error('保存外包服务类型失败')
  }
}
const resetOutsourcingServiceTypeForm = () => {
  if (outsourcingServiceTypeForm.value) {
    outsourcingServiceTypeForm.value.resetFields()
  }
  outsourcingServiceTypeFormData.value = {
    type_name: '',
    description: ''
  }
}
const refreshOutsourcingServiceTypesList = () => {
  loadOutsourcingServiceTypes()
}

// 分组成员和上级管理方法

// 检查员工是否已在分组中
const isEmployeeInGroup = (employeeId: string, group: GroupInfo | null, type: 'member' | 'supervisor' = 'member') => {
  if (!group) return false
  
  if (type === 'member') {
    return group.members.some(member => member.employee_id === employeeId)
  } else {
    return group.supervisors.some(supervisor => supervisor.employee_id === employeeId)
  }
}

// 重置成员对话框
const resetMemberDialog = () => {
  addMemberForm.value = {
    employee_id: '',
    employee_name: '',
    department: '',
    position: ''
  }
}

// 处理成员对话框关闭
const handleMemberDialogClose = (done: () => void) => {
  resetMemberDialog()
  done()
}

// 重置上级对话框
const resetSupervisorDialog = () => {
  addSupervisorForm.value = {
    employee_id: '',
    employee_name: '',
    supervisor_position: '',
    is_primary: false
  }
}

// 处理上级对话框关闭
const handleSupervisorDialogClose = (done: () => void) => {
  resetSupervisorDialog()
  done()
}

// 处理选择上级时自动带出职位
const handleSupervisorChange = (employeeId: string) => {
  const selectedPerson = personnel.value.find(p => p.employee_id === employeeId)
  if (selectedPerson) {
    addSupervisorForm.value.employee_name = selectedPerson.name
    addSupervisorForm.value.department = selectedPerson.department || ''
    addSupervisorForm.value.position = selectedPerson.position || ''
    // 如果职位框为空，自动填充为选中人员的职位
    if (!addSupervisorForm.value.supervisor_position && selectedPerson.position) {
      addSupervisorForm.value.supervisor_position = selectedPerson.position
    }
  }
}

// 添加分组成员
const addGroupMember = async () => {
  try {
    if (!currentGroupForMember.value || !addMemberForm.value.employee_id) {
      ElMessage.error('请选择员工')
      return
    }
    
    const selectedPerson = personnel.value.find(p => p.employee_id === addMemberForm.value.employee_id)
    if (!selectedPerson) {
      ElMessage.error('员工信息不存在')
      return
    }
    
    await createGroupMember({
      group_name: currentGroupForMember.value.group_name,
      group_description: currentGroupForMember.value.group_description,
      relation_type: 'member',  // 添加必需的字段
      employee_id: selectedPerson.employee_id,
      employee_name: selectedPerson.name,
      department: selectedPerson.department,
      position: selectedPerson.position
    })
    
    ElMessage.success('添加成员成功')
    resetMemberDialog()
    loadHierarchyList()
    // 更新当前对话框的分组数据
    setTimeout(() => {
      const updatedGroup = hierarchyList.value.find(g => g.group_name === currentGroupForMember.value?.group_name)
      if (updatedGroup) {
        currentGroupForMember.value = { ...updatedGroup }
      }
    }, 500)
  } catch (error: any) {
    console.error('添加成员失败:', error)
    ElMessage.error(error.response?.data?.detail || '添加成员失败')
  }
}

// 移除分组成员
const removeGroupMember = async (index: number, member: any) => {
  try {
    await ElMessageBox.confirm(`确认移除成员 "${member.employee_name}" 吗？`, '确认移除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    // 这里需要后端API支持通过group_name和employee_id删除成员关系
    // 暂时用前端模拟删除，实际项目中需要完善后端API
    ElMessage.info('成员移除功能需要后端API支持，当前仅更新前端数据')
    
    // 更新当前对话框数据
    if (currentGroupForMember.value) {
      currentGroupForMember.value.members.splice(index, 1)
    }
    
    ElMessage.success('成员移除成功（前端模拟）')
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('移除成员失败:', error)
      ElMessage.error('移除成员失败')
    }
  }
}

// 添加分组上级
const addGroupSupervisor = async () => {
  try {
    if (!currentGroupForSupervisor.value || !addSupervisorForm.value.employee_id) {
      ElMessage.error('请选择上级')
      return
    }
    
    const selectedPerson = personnel.value.find(p => p.employee_id === addSupervisorForm.value.employee_id)
    if (!selectedPerson) {
      ElMessage.error('上级信息不存在')
      return
    }
    
    // 如果是第一个上级，自动设为主
    const isFirstSupervisor = !currentGroupForSupervisor.value.supervisors || 
                            currentGroupForSupervisor.value.supervisors.length === 0
    
    await createGroupSupervisor({
      group_name: currentGroupForSupervisor.value.group_name,
      group_description: currentGroupForSupervisor.value.group_description,
      relation_type: 'supervisor',  // 添加必需的字段
      employee_id: selectedPerson.employee_id,
      employee_name: selectedPerson.name,
      department: selectedPerson.department,
      position: selectedPerson.position,
      supervisor_position: addSupervisorForm.value.supervisor_position,
      is_primary: isFirstSupervisor
    })
    
    ElMessage.success('添加上级成功')
    resetSupervisorDialog()
    loadHierarchyList()
    // 更新当前对话框的分组数据
    setTimeout(() => {
      const updatedGroup = hierarchyList.value.find(g => g.group_name === currentGroupForSupervisor.value?.group_name)
      if (updatedGroup) {
        currentGroupForSupervisor.value = { ...updatedGroup }
      }
    }, 500)
  } catch (error: any) {
    console.error('添加上级失败:', error)
    ElMessage.error(error.response?.data?.detail || '添加上级失败')
  }
}

// 移除分组上级
const removeGroupSupervisor = async (index: number, supervisor: any) => {
  try {
    await ElMessageBox.confirm(`确认移除上级 "${supervisor.employee_name}" 吗？`, '确认移除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteGroupRelation(supervisor.id)
    ElMessage.success('移除上级成功')
    loadHierarchyList()
    
    // 更新当前对话框数据
    if (currentGroupForSupervisor.value) {
      currentGroupForSupervisor.value.supervisors.splice(index, 1)
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('移除上级失败:', error)
      ElMessage.error('移除上级失败')
    }
  }
}

// 切换主上级
const togglePrimarySupervisor = async (index: number, supervisor: any) => {
  try {
    await ElMessageBox.confirm(
      `确认要将 "${supervisor.employee_name}" 设为直接上级吗？`, 
      '确认设置直接上级', 
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 调用后端API更新主上级状态
    await updateEmployeeGroupRelation(supervisor.id, {
      is_primary: true
    })
    
    ElMessage.success('直接上级设置成功')
    loadHierarchyList()
    
    // 更新当前对话框数据
    setTimeout(() => {
      const updatedGroup = hierarchyList.value.find(g => g.group_name === currentGroupForSupervisor.value?.group_name)
      if (updatedGroup) {
        currentGroupForSupervisor.value = { ...updatedGroup }
      }
    }, 500)
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('设置直接上级失败:', error)
      ElMessage.error(error.response?.data?.detail || '设置直接上级失败')
    }
  }
}
</script>

<style scoped>
.resource-management-container {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100%;
}

h1 {
  font-size: 24px;
  margin-bottom: 20px;
  color: #303133;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 员工分组管理样式 */
.member-management,
.supervisor-management {
  padding: 10px 0;
}

.add-member-section,
.add-supervisor-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
}

.add-member-section h4,
.add-supervisor-section h4 {
  margin-bottom: 15px;
  color: #303133;
  font-weight: 600;
}

.member-list-section h4,
.supervisor-list-section h4 {
  margin: 20px 0 10px 0;
  color: #303133;
  font-weight: 600;
}

.text-muted {
  color: #909399;
  font-style: italic;
}

.member-management .el-form-item,
.supervisor-management .el-form-item {
  margin-bottom: 10px;
}

.member-management .el-select,
.supervisor-management .el-select {
  min-width: 200px;
}
</style>
<template>
  <el-dialog
    v-model="dialogVisible"
    title="快速添加任务"
    width="500px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
      size="default"
    >
      <el-form-item label="工作内容" prop="work_content">
        <el-input
          v-model="formData.work_content"
          type="textarea"
          :rows="3"
          placeholder="请详细描述工作内容..."
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="任务名称" prop="task_name">
        <el-input
          v-model="formData.task_name"
          placeholder="可选，关联现有任务或自定义任务名称"
        />
      </el-form-item>

      <el-form-item label="项目名称" prop="project_name">
        <el-input
          v-model="formData.project_name"
          placeholder="可选，所属项目"
        />
      </el-form-item>

      <el-form-item label="预计工时">
        <el-input-number
          v-model="formData.hours_spent"
          :min="0"
          :max="24"
          :step="0.5"
          :precision="1"
          placeholder="小时数"
          style="width: 100%;"
        />
      </el-form-item>

      <el-form-item label="完成进度">
        <div class="progress-input">
          <el-slider
            v-model="formData.progress_percentage"
            :min="0"
            :max="100"
            :step="5"
            show-stops
            show-input
            :show-input-controls="false"
            style="flex: 1; margin-right: 16px;"
          />
          <span class="progress-label">{{ formData.progress_percentage }}%</span>
        </div>
      </el-form-item>

      <el-form-item label="任务状态">
        <el-select v-model="formData.status" placeholder="选择状态" style="width: 100%;">
          <el-option label="进行中" value="进行中" />
          <el-option label="已完成" value="已完成" />
          <el-option label="暂停" value="暂停" />
          <el-option label="取消" value="取消" />
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="formData.is_key_work">
          标记为重点工作
        </el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button 
          type="primary" 
          @click="handleSubmit"
          :loading="submitting"
          :disabled="!formData.work_content?.trim()"
        >
          {{ submitting ? '添加中...' : '快速添加' }}
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

// Props
interface Props {
  visible: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  'update:visible': [value: boolean]
  'add-task': [taskData: any]
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const submitting = ref(false)
const dialogVisible = ref(props.visible)

const formData = ref({
  work_content: '',
  task_name: '',
  project_name: '',
  hours_spent: 1,
  progress_percentage: 0,
  status: '进行中',
  is_key_work: false
})

// 表单验证规则
const formRules: FormRules = {
  work_content: [
    { required: true, message: '请填写工作内容', trigger: 'blur' }
  ]
}

// 监听visible变化
watch(() => props.visible, (newVal) => {
  dialogVisible.value = newVal
})

// 监听dialogVisible变化
watch(dialogVisible, (newVal) => {
  emit('update:visible', newVal)
})

// 重置表单
const resetForm = () => {
  formData.value = {
    work_content: '',
    task_name: '',
    project_name: '',
    hours_spent: 1,
    progress_percentage: 0,
    status: '进行中',
    is_key_work: false
  }
  formRef.value?.clearValidate()
}

// 关闭对话框
const handleClose = () => {
  resetForm()
  dialogVisible.value = false
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    submitting.value = true
    
    // 构建提交数据
    const taskData = {
      work_content: formData.value.work_content.trim(),
      task_name: formData.value.task_name?.trim() || '',
      project_name: formData.value.project_name?.trim() || '',
      hours_spent: formData.value.hours_spent,
      progress_percentage: formData.value.progress_percentage,
      status: formData.value.status,
      is_key_work: formData.value.is_key_work
    }
    
    emit('add-task', taskData)
    
    // 显示成功消息
    ElMessage.success('任务添加成功')
    
    // 关闭对话框
    handleClose()
    
  } catch (error) {
    console.error('添加任务失败:', error)
    ElMessage.error('添加任务失败')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.progress-input {
  display: flex;
  align-items: center;
  width: 100%;
}

.progress-label {
  min-width: 40px;
  text-align: right;
  font-weight: 500;
  color: #409eff;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

:deep(.el-form-item) {
  margin-bottom: 18px;
}

:deep(.el-textarea__inner) {
  resize: vertical;
  min-height: 80px;
}

:deep(.el-slider__input) {
  width: 80px;
}
</style>
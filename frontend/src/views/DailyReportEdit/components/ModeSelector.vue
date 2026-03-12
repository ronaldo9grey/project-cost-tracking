<template>
  <el-dialog
    v-model="visible"
    title="选择日报填报模式"
    width="500px"
    :close-on-click-modal="false"
    :show-close="false"
    class="mode-selector-dialog"
  >
    <div class="mode-selector-content">
      <p class="selector-tip">请选择今日日报的填报方式：</p>
      
      <div class="mode-options">
        <!-- 自由填报模式 -->
        <div 
          class="mode-card"
          :class="{ active: selectedMode === 'free' }"
          @click="selectedMode = 'free'"
        >
          <div class="mode-icon">
            <el-icon><Edit /></el-icon>
          </div>
          <div class="mode-info">
            <h3>自由填报</h3>
            <p>适用于临时任务、项目工作或无明确目标时的填报</p>
            <ul>
              <li>手动填写工作目标</li>
              <li>自行组织工作事项</li>
              <li>灵活度高，适合多变的工作场景</li>
            </ul>
          </div>
          <div class="mode-check">
            <el-icon v-if="selectedMode === 'free'"><Check /></el-icon>
          </div>
        </div>

        <!-- 关联目标模式 -->
        <div 
          class="mode-card"
          :class="{ active: selectedMode === 'goal', disabled: !hasWeeklyGoal }"
          @click="hasWeeklyGoal && (selectedMode = 'goal')"
        >
          <div class="mode-icon goal-icon">
            <el-icon><Flag /></el-icon>
          </div>
          <div class="mode-info">
            <h3>关联目标 <el-tag v-if="!hasWeeklyGoal" type="warning" size="small">本周无目标</el-tag></h3>
            <p>基于月度/周目标快速填报，适合目标明确的日常工作</p>
            <ul>
              <li>自动带出本周目标</li>
              <li>只需填写完成情况</li>
              <li>快速完成，进度自动汇总</li>
            </ul>
            <!-- 无目标时显示跳转按钮 -->
            <div v-if="!hasWeeklyGoal" class="goal-action">
              <el-button 
                type="primary" 
                size="small" 
                @click.stop="handleCreateGoal"
              >
                <el-icon><Plus /></el-icon>
                去制定目标
              </el-button>
              <span class="goal-tip">制定目标后可使用此模式快速填报</span>
            </div>
          </div>
          <div class="mode-check">
            <el-icon v-if="selectedMode === 'goal'"><Check /></el-icon>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button type="primary" @click="handleConfirm" :disabled="!selectedMode">
          确认选择
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Edit, Flag, Check, Plus } from '@element-plus/icons-vue'

interface Props {
  modelValue: boolean
  hasWeeklyGoal: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'select', mode: 'free' | 'goal'): void
  (e: 'cancel'): void
  (e: 'create-goal'): void
}>()

const visible = ref(props.modelValue)
const selectedMode = ref<'free' | 'goal' | null>(null)

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    selectedMode.value = null
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleConfirm = () => {
  if (selectedMode.value) {
    emit('select', selectedMode.value)
    visible.value = false
  }
}

const handleCancel = () => {
  emit('cancel')
  visible.value = false
}

const handleCreateGoal = () => {
  emit('create-goal')
  visible.value = false
}
</script>

<style scoped lang="scss">
.mode-selector-content {
  padding: 10px 0;
}

.selector-tip {
  color: #606266;
  margin-bottom: 20px;
  font-size: 14px;
}

.mode-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.mode-card {
  display: flex;
  align-items: flex-start;
  padding: 20px;
  border: 2px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;

  &:hover:not(.disabled) {
    border-color: #409eff;
    background-color: #f5f7fa;
  }

  &.active {
    border-color: #409eff;
    background-color: #ecf5ff;
  }

  &.disabled {
    opacity: 0.6;
    cursor: not-allowed;
    background-color: #f5f7fa;
  }
}

.mode-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;

  .el-icon {
    font-size: 24px;
    color: #409eff;
  }

  &.goal-icon {
    background-color: #f0f9ff;
    
    .el-icon {
      color: #67c23a;
    }
  }
}

.mode-info {
  flex: 1;

  h3 {
    margin: 0 0 8px 0;
    font-size: 16px;
    color: #303133;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  p {
    margin: 0 0 10px 0;
    font-size: 13px;
    color: #606266;
  }

  ul {
    margin: 0;
    padding-left: 18px;
    font-size: 12px;
    color: #909399;

    li {
      margin-bottom: 4px;
    }
  }
}

.mode-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #409eff;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 10px;
  flex-shrink: 0;

  .el-icon {
    color: white;
    font-size: 14px;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.goal-action {
  margin-top: 12px;
  padding: 10px;
  background-color: #fff7e6;
  border: 1px dashed #ffd591;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 10px;

  .goal-tip {
    font-size: 12px;
    color: #fa8c16;
  }
}
</style>

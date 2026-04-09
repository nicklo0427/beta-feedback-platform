<script setup lang="ts">
import { computed } from 'vue'

import { fetchTaskFeedback } from '~/features/feedback/api'
import {
  formatFeedbackCategoryLabel,
  formatFeedbackSeverityLabel
} from '~/features/feedback/types'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import { fetchTaskDetail } from '~/features/tasks/api'
import { formatTaskStatusLabel } from '~/features/tasks/types'

const route = useRoute()
const taskId = computed(() => String(route.params.taskId))

const {
  data: task,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `task-detail-${taskId.value}`,
  () => fetchTaskDetail(taskId.value),
  {
    server: false,
    watch: [taskId],
    default: () => null
  }
)

const {
  data: feedbackResponse,
  pending: feedbackPending,
  error: feedbackError,
  refresh: refreshFeedback
} = useAsyncData(
  () => `task-feedback-${taskId.value}`,
  () => fetchTaskFeedback(taskId.value),
  {
    server: false,
    watch: [taskId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const feedbackItems = computed(() => feedbackResponse.value.items)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/tasks">
          任務
        </NuxtLink>
        <h1 class="resource-shell__title">任務詳情</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一任務的最小欄位、指派目標與狀態流上下文，為後續回饋流程預留清楚入口。
        </p>
        <div
          v-if="task"
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="task-edit-link"
            :to="`/tasks/${task.id}/edit`"
          >
            編輯任務
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="task-detail-loading"
      >
        <h2 class="resource-state__title">載入任務詳情中</h2>
        <p class="resource-state__description">
          正在從 API 載入任務詳情。
        </p>
      </section>

      <section
        v-else-if="error || !task"
        class="resource-state"
        data-testid="task-detail-error"
      >
        <h2 class="resource-state__title">無法載入任務詳情</h2>
        <p class="resource-state__description">
          {{ error?.message || '找不到指定的任務。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/tasks">
            返回任務列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="task-detail-panel"
      >
        <h2 class="resource-section__title">{{ task.title }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">狀態 {{ formatTaskStatusLabel(task.status) }}</span>
          <span class="resource-shell__meta-chip">活動 {{ task.campaign_id }}</span>
          <span class="resource-shell__meta-chip">
            {{
              task.device_profile_id
                ? `裝置設定檔 ${task.device_profile_id}`
                : '目前尚未指派裝置設定檔'
            }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">任務 ID</span>
            <span class="resource-key-value__value">{{ task.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">活動</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/campaigns/${task.campaign_id}`"
            >
              {{ task.campaign_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">裝置設定檔</span>
            <NuxtLink
              v-if="task.device_profile_id"
              class="resource-key-value__value"
              :to="`/device-profiles/${task.device_profile_id}`"
            >
              {{ task.device_profile_id }}
            </NuxtLink>
            <span v-else class="resource-key-value__value">
              尚未指派。
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">任務說明摘要</span>
            <span class="resource-key-value__value">
              {{ task.instruction_summary || '目前尚未提供任務說明摘要。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">提交時間</span>
            <span class="resource-key-value__value">
              {{ task.submitted_at || '尚未提交。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">更新時間</span>
            <span class="resource-key-value__value">{{ task.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">建立時間</span>
            <span class="resource-key-value__value">{{ task.created_at }}</span>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && task?.qualification_context"
        class="resource-section"
        data-testid="task-qualification-context"
      >
        <h2 class="resource-section__title">資格上下文</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            狀態 {{ formatQualificationStatusLabel(task.qualification_context.qualification_status) }}
          </span>
          <span
            v-if="task.qualification_context.qualification_drift"
            class="resource-shell__meta-chip"
            data-testid="task-qualification-drift-chip"
          >
            資格已漂移
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">指派裝置設定檔</span>
            <span class="resource-key-value__value">
              {{ task.qualification_context.device_profile_name }}（{{ task.qualification_context.device_profile_id }}）
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">命中資格規則</span>
            <span class="resource-key-value__value">
              {{ task.qualification_context.matched_rule_id || '目前沒有命中的資格規則。' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">資格摘要</span>
            <span class="resource-key-value__value">
              {{ task.qualification_context.reason_summary || '目前沒有額外的資格摘要。' }}
            </span>
          </div>
        </div>

        <div
          v-if="task.qualification_context.qualification_drift"
          class="resource-state"
          data-testid="task-qualification-drift-warning"
        >
          <h3 class="resource-state__title">目前指派已不再符合資格</h3>
          <p class="resource-state__description">
            這筆任務原本已完成指派，但目前依照最新的資格規則重新評估後，這個裝置設定檔已不再符合活動條件。
          </p>
        </div>
      </section>

      <section
        v-if="!pending && !error && task"
        class="resource-section"
        data-testid="task-feedback-section"
      >
        <div class="resource-state__actions">
          <h2 class="resource-section__title">回饋</h2>
          <NuxtLink
            class="resource-action"
            data-testid="task-feedback-create-link"
            :to="`/tasks/${task.id}/feedback/new`"
          >
            提交回饋
          </NuxtLink>
        </div>

        <div
          v-if="feedbackPending"
          class="resource-state"
          data-testid="task-feedback-loading"
        >
          <h3 class="resource-state__title">載入回饋中</h3>
          <p class="resource-state__description">
            正在載入這個任務底下的結構化回饋。
          </p>
        </div>

        <div
          v-else-if="feedbackError"
          class="resource-state"
          data-testid="task-feedback-error"
        >
          <h3 class="resource-state__title">無法載入回饋</h3>
          <p class="resource-state__description">
            {{ feedbackError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshFeedback()">
              重試
            </button>
          </div>
        </div>

        <div
          v-else-if="feedbackItems.length === 0"
          class="resource-state"
          data-testid="task-feedback-empty"
        >
          <h3 class="resource-state__title">目前還沒有回饋</h3>
          <p class="resource-state__description">
            目前這個任務尚未收到任何結構化回饋，後續可在後端建立後由此區塊直接承接。
          </p>
          <div class="resource-state__actions">
            <NuxtLink
              class="resource-action"
              data-testid="task-feedback-empty-create-link"
              :to="`/tasks/${task.id}/feedback/new`"
            >
              提交第一筆回饋
            </NuxtLink>
          </div>
        </div>

        <div
          v-else
          class="resource-section__body"
          data-testid="task-feedback-list"
        >
          <NuxtLink
            v-for="feedback in feedbackItems"
            :key="feedback.id"
            class="resource-card"
            :data-testid="`feedback-card-${feedback.id}`"
            :to="`/tasks/${task.id}/feedback/${feedback.id}`"
          >
            <span class="resource-shell__breadcrumb">回饋</span>
            <h3 class="resource-card__title">{{ feedback.summary }}</h3>
            <p class="resource-card__description">
              {{ formatFeedbackCategoryLabel(feedback.category) }} · {{ formatFeedbackSeverityLabel(feedback.severity) }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">提交於 {{ feedback.submitted_at }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <NuxtPage />
    </section>
  </main>
</template>

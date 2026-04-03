<script setup lang="ts">
import { computed } from 'vue'

import { fetchTaskFeedback } from '~/features/feedback/api'
import { fetchTaskDetail } from '~/features/tasks/api'

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
          Tasks
        </NuxtLink>
        <h1 class="resource-shell__title">Task Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 Task 的最小欄位、assignment target 與 status flow 上下文，為後續 feedback 流程預留清楚入口。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="task-detail-loading"
      >
        <h2 class="resource-state__title">Loading task detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 Task detail。
        </p>
      </section>

      <section
        v-else-if="error || !task"
        class="resource-state"
        data-testid="task-detail-error"
      >
        <h2 class="resource-state__title">Task detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested task could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/tasks">
            Back to tasks
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
          <span class="resource-shell__meta-chip">Status {{ task.status }}</span>
          <span class="resource-shell__meta-chip">Campaign {{ task.campaign_id }}</span>
          <span class="resource-shell__meta-chip">
            {{
              task.device_profile_id
                ? `Device Profile ${task.device_profile_id}`
                : 'No device profile assigned'
            }}
          </span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Task ID</span>
            <span class="resource-key-value__value">{{ task.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Campaign</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/campaigns/${task.campaign_id}`"
            >
              {{ task.campaign_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Profile</span>
            <NuxtLink
              v-if="task.device_profile_id"
              class="resource-key-value__value"
              :to="`/device-profiles/${task.device_profile_id}`"
            >
              {{ task.device_profile_id }}
            </NuxtLink>
            <span v-else class="resource-key-value__value">
              Not assigned yet.
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Instruction Summary</span>
            <span class="resource-key-value__value">
              {{ task.instruction_summary || 'No instruction summary provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Submitted At</span>
            <span class="resource-key-value__value">
              {{ task.submitted_at || 'Not submitted yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ task.updated_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Created At</span>
            <span class="resource-key-value__value">{{ task.created_at }}</span>
          </div>
        </div>
      </section>

      <section
        v-if="!pending && !error && task"
        class="resource-section"
        data-testid="task-feedback-section"
      >
        <h2 class="resource-section__title">Feedback</h2>

        <div
          v-if="feedbackPending"
          class="resource-state"
          data-testid="task-feedback-loading"
        >
          <h3 class="resource-state__title">Loading feedback</h3>
          <p class="resource-state__description">
            正在載入這個 Task 底下的結構化 feedback。
          </p>
        </div>

        <div
          v-else-if="feedbackError"
          class="resource-state"
          data-testid="task-feedback-error"
        >
          <h3 class="resource-state__title">Feedback unavailable</h3>
          <p class="resource-state__description">
            {{ feedbackError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshFeedback()">
              Retry
            </button>
          </div>
        </div>

        <div
          v-else-if="feedbackItems.length === 0"
          class="resource-state"
          data-testid="task-feedback-empty"
        >
          <h3 class="resource-state__title">No feedback yet</h3>
          <p class="resource-state__description">
            目前這個 Task 尚未收到任何結構化 feedback，後續可在 backend 建立後由此區塊直接承接。
          </p>
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
            <span class="resource-shell__breadcrumb">Feedback</span>
            <h3 class="resource-card__title">{{ feedback.summary }}</h3>
            <p class="resource-card__description">
              {{ feedback.category }} · {{ feedback.severity }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">Submitted {{ feedback.submitted_at }}</span>
            </div>
          </NuxtLink>
        </div>
      </section>

      <NuxtPage />
    </section>
  </main>
</template>

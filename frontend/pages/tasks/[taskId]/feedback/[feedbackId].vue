<script setup lang="ts">
import { computed } from 'vue'

import { fetchFeedbackDetail } from '~/features/feedback/api'

const route = useRoute()
const taskId = computed(() => String(route.params.taskId))
const feedbackId = computed(() => String(route.params.feedbackId))

const {
  data: feedback,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `feedback-detail-${feedbackId.value}`,
  () => fetchFeedbackDetail(feedbackId.value),
  {
    server: false,
    watch: [feedbackId],
    default: () => null
  }
)
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/tasks/${taskId}`">
          Task Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Feedback Detail Shell</h1>
        <p class="resource-shell__description">
          這個頁面先承接單一 feedback 的核心欄位，提供後續 triage 與回饋整理流程可依附的最小 detail shell。
        </p>
        <div
          v-if="feedback"
          class="resource-state__actions"
        >
          <NuxtLink
            class="resource-action"
            data-testid="feedback-edit-link"
            :to="`/tasks/${taskId}/feedback/${feedback.id}/edit`"
          >
            Edit feedback
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="feedback-detail-loading"
      >
        <h2 class="resource-state__title">Loading feedback detail</h2>
        <p class="resource-state__description">
          正在從 API 載入 feedback detail。
        </p>
      </section>

      <section
        v-else-if="error || !feedback"
        class="resource-state"
        data-testid="feedback-detail-error"
      >
        <h2 class="resource-state__title">Feedback detail unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested feedback could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" :to="`/tasks/${taskId}`">
            Back to task
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="feedback-detail-panel"
      >
        <h2 class="resource-section__title">{{ feedback.summary }}</h2>

        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">Severity {{ feedback.severity }}</span>
          <span class="resource-shell__meta-chip">Category {{ feedback.category }}</span>
          <span class="resource-shell__meta-chip">Task {{ feedback.task_id }}</span>
        </div>

        <div class="resource-key-value">
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Feedback ID</span>
            <span class="resource-key-value__value">{{ feedback.id }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Campaign ID</span>
            <NuxtLink
              class="resource-key-value__value"
              :to="`/campaigns/${feedback.campaign_id}`"
            >
              {{ feedback.campaign_id }}
            </NuxtLink>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Device Profile ID</span>
            <NuxtLink
              v-if="feedback.device_profile_id"
              class="resource-key-value__value"
              :to="`/device-profiles/${feedback.device_profile_id}`"
            >
              {{ feedback.device_profile_id }}
            </NuxtLink>
            <span v-else class="resource-key-value__value">
              Not derived yet.
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Rating</span>
            <span class="resource-key-value__value">
              {{ feedback.rating ?? 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Reproduction Steps</span>
            <span class="resource-key-value__value">
              {{ feedback.reproduction_steps || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Expected Result</span>
            <span class="resource-key-value__value">
              {{ feedback.expected_result || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Actual Result</span>
            <span class="resource-key-value__value">
              {{ feedback.actual_result || 'Not provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Note</span>
            <span class="resource-key-value__value">
              {{ feedback.note || 'No note provided yet.' }}
            </span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Submitted At</span>
            <span class="resource-key-value__value">{{ feedback.submitted_at }}</span>
          </div>
          <div class="resource-key-value__row">
            <span class="resource-key-value__label">Updated At</span>
            <span class="resource-key-value__value">{{ feedback.updated_at }}</span>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

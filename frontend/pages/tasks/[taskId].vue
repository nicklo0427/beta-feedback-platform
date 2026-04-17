<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import ActivityTimelinePanel from '~/features/activity-events/ActivityTimelinePanel.vue'
import { fetchTaskTimeline } from '~/features/activity-events/api'
import {
  getActorAwareMutationErrorMessage,
  getActorAwareReadErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { fetchTaskFeedback } from '~/features/feedback/api'
import {
  formatFeedbackCategoryLabel,
  formatFeedbackSeverityLabel
} from '~/features/feedback/types'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import { formatParticipationRequestStatusLabel } from '~/features/participation-requests/types'
import { fetchTaskDetail, updateTask } from '~/features/tasks/api'
import {
  TASK_RESOLUTION_OUTCOMES,
  formatTaskResolutionOutcomeLabel,
  formatTaskStatusLabel,
  type TaskResolutionOutcome
} from '~/features/tasks/types'

const route = useRoute()
const taskId = computed(() => String(route.params.taskId))
useCurrentActorPersistence()
const { locale, t } = useAppI18n()
const currentActorId = useCurrentActorId()

const {
  data: task,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `task-detail-${taskId.value}-${currentActorId.value ?? 'none'}`,
  () => fetchTaskDetail(taskId.value, currentActorId.value),
  {
    server: false,
    watch: [taskId, currentActorId],
    default: () => null
  }
)

const {
  data: feedbackResponse,
  pending: feedbackPending,
  error: feedbackError,
  refresh: refreshFeedback
} = useAsyncData(
  () => `task-feedback-${taskId.value}-${currentActorId.value ?? 'none'}`,
  () => fetchTaskFeedback(taskId.value, currentActorId.value),
  {
    server: false,
    watch: [taskId, currentActorId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const feedbackItems = computed(() => feedbackResponse.value.items)
const taskDetailErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(error.value, t('taskDetail.errorFallback'))
)
const {
  data: timelineResponse,
  pending: timelinePending,
  error: timelineError
} = useAsyncData(
  () => `task-timeline-${taskId.value}-${currentActorId.value ?? 'none'}`,
  () => fetchTaskTimeline(taskId.value, currentActorId.value),
  {
    server: false,
    watch: [taskId, currentActorId],
    default: () => ({
      items: [],
      total: 0
    })
  }
)
const timelineEvents = computed(() => timelineResponse.value.items)
const timelineErrorMessage = computed(() =>
  timelineError.value
    ? getActorAwareReadErrorMessage(timelineError.value, t('taskDetail.timelineTitle'))
    : null
)
const resolutionOutcome = ref<TaskResolutionOutcome>('confirmed_issue')
const resolutionNote = ref('')
const resolutionSubmitting = ref(false)
const resolutionError = ref<string | null>(null)

const canResolveTask = computed(
  () => !!task.value && !!currentActorId.value && ['submitted', 'closed'].includes(task.value.status)
)

watch(
  task,
  (nextTask) => {
    if (!nextTask) {
      return
    }

    resolutionOutcome.value = nextTask.resolution_context?.resolution_outcome ?? 'confirmed_issue'
    resolutionNote.value = nextTask.resolution_context?.resolution_note ?? ''
    resolutionError.value = null
  },
  {
    immediate: true
  }
)

async function handleResolutionSubmit(): Promise<void> {
  if (!task.value) {
    resolutionError.value = t('taskDetail.resolutionNoTask')
    return
  }

  if (!currentActorId.value) {
    resolutionError.value = t('taskDetail.resolutionNoActor')
    return
  }

  resolutionError.value = null
  resolutionSubmitting.value = true

  try {
    await updateTask(
      task.value.id,
      {
        status: 'closed',
        resolution_outcome: resolutionOutcome.value,
        resolution_note: resolutionNote.value.trim() || null
      },
      currentActorId.value
    )
    await refresh()
  } catch (submitFailure) {
    resolutionError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      t('taskDetail.resolutionFallback')
    )
  } finally {
    resolutionSubmitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/tasks">
          {{ t('taskDetail.breadcrumb') }}
        </NuxtLink>
        <h1 class="resource-shell__title">{{ t('taskDetail.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('taskDetail.description') }}
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
            {{ t('taskDetail.editTask') }}
          </NuxtLink>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="task-detail-loading"
      >
        <h2 class="resource-state__title">{{ t('taskDetail.loadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('taskDetail.loadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="error || !task"
        class="resource-state"
        data-testid="task-detail-error"
      >
        <h2 class="resource-state__title">{{ t('taskDetail.errorTitle') }}</h2>
        <p class="resource-state__description">
          {{ taskDetailErrorMessage }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            {{ t('common.retry') }}
          </button>
          <NuxtLink class="resource-action" to="/tasks">
            {{ t('taskDetail.backToTasks') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="detail-layout"
        data-testid="task-detail-layout"
      >
        <div class="detail-layout__main">
          <section
            class="resource-section"
            data-testid="task-detail-panel"
          >
            <span class="resource-section__eyebrow">{{ t('taskDetail.eyebrow') }}</span>
            <h2 class="resource-section__title">{{ task.title }}</h2>

            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">{{ t('taskDetail.statusLabel') }} {{ formatTaskStatusLabel(task.status, locale) }}</span>
              <span class="resource-shell__meta-chip">{{ t('taskDetail.campaignLabel') }} {{ task.campaign_id }}</span>
              <span class="resource-shell__meta-chip">
                {{
                  task.device_profile_id
                    ? `${t('taskDetail.deviceProfileLabel')} ${task.device_profile_id}`
                    : t('taskDetail.unassignedDeviceProfile')
                }}
              </span>
            </div>

            <div class="resource-key-value">
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.taskIdLabel') }}</span>
                <span class="resource-key-value__value">{{ task.id }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.campaignLabel') }}</span>
                <NuxtLink
                  class="resource-key-value__value"
                  :to="`/campaigns/${task.campaign_id}`"
                >
                  {{ task.campaign_id }}
                </NuxtLink>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.deviceProfileLabel') }}</span>
                <NuxtLink
                  v-if="task.device_profile_id"
                  class="resource-key-value__value"
                  :to="`/device-profiles/${task.device_profile_id}`"
                >
                  {{ task.device_profile_id }}
                </NuxtLink>
                <span v-else class="resource-key-value__value">{{ t('taskDetail.unassignedDeviceProfile') }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.instructionSummaryLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.instruction_summary || t('taskDetail.instructionSummaryEmpty') }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.submittedAtLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.submitted_at || t('taskDetail.notSubmitted') }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.updatedAtLabel') }}</span>
                <span class="resource-key-value__value">{{ task.updated_at }}</span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.createdAtLabel') }}</span>
                <span class="resource-key-value__value">{{ task.created_at }}</span>
              </div>
            </div>
          </section>

          <section
            class="resource-section"
            data-testid="task-resolution-section"
          >
            <div class="resource-state__actions">
              <div>
                <span class="resource-section__eyebrow">{{ t('taskDetail.resolutionEyebrow') }}</span>
                <h2 class="resource-section__title">{{ t('taskDetail.resolutionTitle') }}</h2>
              </div>
              <span
                v-if="task.resolution_context"
                class="resource-shell__meta-chip"
                data-testid="task-resolution-chip"
              >
                {{ t('taskDetail.resolutionLabel') }} {{ formatTaskResolutionOutcomeLabel(task.resolution_context.resolution_outcome, locale) }}
              </span>
            </div>

            <div
              v-if="task.resolution_context"
              class="resource-key-value"
              data-testid="task-resolution-context"
            >
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.resolutionContextLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ formatTaskResolutionOutcomeLabel(task.resolution_context.resolution_outcome, locale) }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.resolutionNoteLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.resolution_context.resolution_note || t('taskDetail.resolutionNoteEmpty') }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.resolvedByLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.resolution_context.resolved_by_account_display_name }}（{{ task.resolution_context.resolved_by_account_id }}）
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.resolvedAtLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.resolution_context.resolved_at }}
                </span>
              </div>
            </div>

            <div
              v-else
              class="resource-state"
              data-testid="task-resolution-empty"
            >
              <h3 class="resource-state__title">{{ t('taskDetail.resolutionEmptyTitle') }}</h3>
              <p class="resource-state__description">
                {{ t('taskDetail.resolutionEmptyDescription') }}
              </p>
            </div>

            <form
              v-if="canResolveTask"
              class="resource-form"
              data-testid="task-resolution-form"
              @submit.prevent="handleResolutionSubmit"
            >
              <div
                v-if="resolutionError"
                class="resource-form__error"
                data-testid="task-resolution-error"
              >
                {{ resolutionError }}
              </div>

              <section class="resource-form__section">
                <div>
                  <h3 class="resource-form__section-title">{{ t('taskDetail.resolutionFormTitle') }}</h3>
                  <p class="resource-form__section-description">
                    {{ t('taskDetail.resolutionFormDescription') }}
                  </p>
                </div>

                <div class="resource-form__section-grid">
                  <label class="resource-field">
                    <span class="resource-field__label">{{ t('taskDetail.resolutionContextLabel') }}</span>
                    <select
                      v-model="resolutionOutcome"
                      class="resource-select"
                      data-testid="task-resolution-outcome-field"
                      :disabled="resolutionSubmitting"
                    >
                      <option
                        v-for="outcome in TASK_RESOLUTION_OUTCOMES"
                        :key="outcome"
                        :value="outcome"
                      >
                        {{ formatTaskResolutionOutcomeLabel(outcome, locale) }}
                      </option>
                    </select>
                  </label>
                </div>

                <label class="resource-field">
                  <span class="resource-field__label">{{ t('taskDetail.resolutionNoteLabel') }}</span>
                  <textarea
                    v-model="resolutionNote"
                    class="resource-textarea"
                    data-testid="task-resolution-note-input"
                    rows="4"
                    :disabled="resolutionSubmitting"
                  />
                </label>
              </section>

              <div class="resource-form__sticky-actions">
                <button
                  class="resource-action"
                  data-testid="task-resolution-submit"
                  type="submit"
                  :disabled="resolutionSubmitting"
                >
                  {{ resolutionSubmitting ? t('taskDetail.resolutionSaving') : t('taskDetail.resolutionSubmit') }}
                </button>
              </div>
            </form>
          </section>

          <section
            class="resource-section"
            data-testid="task-feedback-section"
          >
            <div class="resource-state__actions">
              <div>
                <span class="resource-section__eyebrow">{{ t('taskDetail.feedbackEyebrow') }}</span>
                <h2 class="resource-section__title">{{ t('taskDetail.feedbackTitle') }}</h2>
              </div>
              <NuxtLink
                class="resource-action"
                data-testid="task-feedback-create-link"
                :to="`/tasks/${task.id}/feedback/new`"
              >
                {{ t('taskDetail.submitFeedback') }}
              </NuxtLink>
            </div>

            <div
              v-if="feedbackPending"
              class="resource-state"
              data-testid="task-feedback-loading"
            >
              <h3 class="resource-state__title">{{ t('taskDetail.feedbackLoadingTitle') }}</h3>
              <p class="resource-state__description">
                {{ t('taskDetail.feedbackLoadingDescription') }}
              </p>
            </div>

            <div
              v-else-if="feedbackError"
              class="resource-state"
              data-testid="task-feedback-error"
            >
              <h3 class="resource-state__title">{{ t('taskDetail.feedbackErrorTitle') }}</h3>
              <p class="resource-state__description">
                {{ getActorAwareReadErrorMessage(feedbackError, t('taskDetail.feedbackErrorFallback')) }}
              </p>
              <div class="resource-state__actions">
                <button class="resource-action" type="button" @click="refreshFeedback()">
                  {{ t('common.retry') }}
                </button>
              </div>
            </div>

            <div
              v-else-if="feedbackItems.length === 0"
              class="resource-state"
              data-testid="task-feedback-empty"
            >
              <h3 class="resource-state__title">{{ t('taskDetail.feedbackEmptyTitle') }}</h3>
              <p class="resource-state__description">
                {{ t('taskDetail.feedbackEmptyDescription') }}
              </p>
              <div class="resource-state__actions">
                <NuxtLink
                  class="resource-action"
                  data-testid="task-feedback-empty-create-link"
                  :to="`/tasks/${task.id}/feedback/new`"
                >
                  {{ t('taskDetail.submitFirstFeedback') }}
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
                <span class="resource-shell__breadcrumb">{{ t('taskDetail.feedbackBreadcrumb') }}</span>
                <h3 class="resource-card__title">{{ feedback.summary }}</h3>
                <p class="resource-card__description">
                  {{ formatFeedbackCategoryLabel(feedback.category, locale) }} · {{ formatFeedbackSeverityLabel(feedback.severity, locale) }}
                </p>
                <div class="resource-card__meta">
                  <span class="resource-card__chip">{{ t('taskDetail.submittedAtShortLabel') }} {{ feedback.submitted_at }}</span>
                </div>
              </NuxtLink>
            </div>
          </section>
        </div>

        <aside class="detail-layout__rail">
          <section
            v-if="task.qualification_context"
            class="resource-section"
            data-testid="task-qualification-context"
          >
            <span class="resource-section__eyebrow">{{ t('taskDetail.qualificationEyebrow') }}</span>
            <h2 class="resource-section__title">{{ t('taskDetail.qualificationTitle') }}</h2>

            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">
                {{ t('taskDetail.qualificationStatusLabel') }} {{ formatQualificationStatusLabel(task.qualification_context.qualification_status, locale) }}
              </span>
              <span
                v-if="task.qualification_context.qualification_drift"
                class="resource-shell__meta-chip"
                data-testid="task-qualification-drift-chip"
              >
                {{ t('taskDetail.qualificationDrift') }}
              </span>
            </div>

            <div class="resource-key-value">
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.assignedDeviceProfileLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.qualification_context.device_profile_name }}（{{ task.qualification_context.device_profile_id }}）
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.matchedRuleLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.qualification_context.matched_rule_id || t('taskDetail.matchedRuleEmpty') }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.qualificationSummaryLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.qualification_context.reason_summary || t('taskDetail.qualificationSummaryEmpty') }}
                </span>
              </div>
            </div>

            <div
              v-if="task.qualification_context.qualification_drift"
              class="resource-state"
              data-testid="task-qualification-drift-warning"
            >
              <h3 class="resource-state__title">{{ t('taskDetail.driftWarningTitle') }}</h3>
              <p class="resource-state__description">
                {{ t('taskDetail.driftWarningDescription') }}
              </p>
            </div>
          </section>

          <section
            v-if="task.participation_request_context"
            class="resource-section"
            data-testid="task-participation-request-context"
          >
            <span class="resource-section__eyebrow">{{ t('taskDetail.traceabilityEyebrow') }}</span>
            <h2 class="resource-section__title">{{ t('taskDetail.traceabilityTitle') }}</h2>

            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                data-testid="task-participation-request-review-link"
                :to="`/review/participation-requests/${task.participation_request_context.request_id}`"
              >
                {{ t('taskDetail.viewDeveloperReview') }}
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                data-testid="task-participation-request-my-link"
                to="/my/participation-requests"
              >
                {{ t('taskDetail.viewMyParticipationRequests') }}
              </NuxtLink>
            </div>

            <div class="resource-key-value">
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.requestIdLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.participation_request_context.request_id }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.testerLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.participation_request_context.tester_account_display_name }}（{{ task.participation_request_context.tester_account_id }}）
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.requestStatusLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ formatParticipationRequestStatusLabel(task.participation_request_context.request_status, locale) }}
                </span>
              </div>
              <div class="resource-key-value__row">
                <span class="resource-key-value__label">{{ t('taskDetail.assignmentCreatedAtLabel') }}</span>
                <span class="resource-key-value__value">
                  {{ task.participation_request_context.assignment_created_at || t('taskDetail.assignmentCreatedAtEmpty') }}
                </span>
              </div>
            </div>
          </section>

          <ActivityTimelinePanel
            :title="t('taskDetail.timelineTitle')"
            :description="t('taskDetail.timelineDescription')"
            :pending="timelinePending"
            :error-message="timelineErrorMessage"
            :events="timelineEvents"
            :empty-message="t('taskDetail.timelineEmpty')"
            test-id-prefix="task-timeline"
          />
        </aside>
      </section>

      <NuxtPage />
    </section>
  </main>
</template>

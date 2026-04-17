<script setup lang="ts">
import { computed, ref } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import { fetchTasks, startAssignedTask } from '~/features/tasks/api'
import {
  formatTaskResolutionOutcomeLabel,
  formatTaskStatusLabel,
  type TaskStatus
} from '~/features/tasks/types'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'

const TESTER_INBOX_STATUSES: TaskStatus[] = [
  'assigned',
  'in_progress',
  'submitted',
  'closed'
]

useCurrentActorPersistence()

const { locale, t } = useAppI18n()
const currentActorId = useCurrentActorId()
const activeStatus = ref<TaskStatus>('assigned')
const actionError = ref<string | null>(null)
const startingTaskId = ref<string | null>(null)

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-task-accounts', () => fetchAccounts(), {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
const currentActor = computed(
  () => accounts.value.find((account) => account.id === currentActorId.value) ?? null
)
const isTesterActor = computed(() => currentActor.value?.role === 'tester')

const {
  data: taskResponse,
  pending: tasksPending,
  error: tasksError,
  refresh: refreshTasks
} = useAsyncData(
  () =>
    `my-tasks-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}-${activeStatus.value}`,
  async () => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchTasks({
      mine: true,
      status: activeStatus.value,
      actorId: currentActorId.value
    })
  },
  {
    server: false,
    watch: [currentActorId, currentActor, activeStatus],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const tasks = computed(() => taskResponse.value.items)

async function handleStartTask(taskId: string): Promise<void> {
  actionError.value = null
  startingTaskId.value = taskId

  try {
    if (!currentActorId.value) {
      actionError.value = t('myTasks.startTaskNoActor')
      return
    }

    await startAssignedTask(taskId, currentActorId.value)
    await refreshTasks()
  } catch (submitFailure) {
    actionError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      t('myTasks.startTaskFallback')
    )
  } finally {
    startingTaskId.value = null
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header app-page-header">
        <NuxtLink class="resource-shell__breadcrumb" to="/dashboard">Dashboard</NuxtLink>
        <h1 class="resource-shell__title">{{ t('myTasks.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('myTasks.description') }}
        </p>
        <div class="resource-state__actions app-page-actions">
          <NuxtLink class="resource-action" to="/tasks">
            {{ t('myTasks.viewAllTasks') }}
          </NuxtLink>
        </div>
      </header>
      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-tasks-actor-error"
      >
        <h2 class="resource-state__title">{{ t('myTasks.actorErrorTitle') }}</h2>
        <p class="resource-state__description">
          {{ accountsError.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            {{ t('common.retry') }}
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="my-tasks-actor-loading"
      >
        <h2 class="resource-state__title">{{ t('myTasks.actorLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myTasks.actorLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-tasks-select-actor"
      >
        <h2 class="resource-state__title">{{ t('myTasks.selectActorTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myTasks.selectActorDescription') }}
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-tasks-actor-missing"
      >
        <h2 class="resource-state__title">{{ t('myTasks.actorMissingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('myTasks.actorMissingDescription') }}
        </p>
      </section>

      <section
        v-else-if="!isTesterActor"
        class="resource-state"
        data-testid="my-tasks-role-mismatch"
      >
        <h2 class="resource-state__title">{{ t('myTasks.roleMismatchTitle') }}</h2>
        <p class="resource-state__description">
          {{
            t('myTasks.roleMismatchDescription', {
              role: formatAccountRoleLabel(currentActor.role, locale)
            })
          }}
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-tasks-filters">
          <h2 class="resource-section__title">{{ t('myTasks.filtersTitle') }}</h2>
          <div class="resource-state__actions app-page-actions">
            <button
              v-for="status in TESTER_INBOX_STATUSES"
              :key="status"
              class="resource-action"
              :data-testid="`my-tasks-filter-${status}`"
              type="button"
              @click="activeStatus = status"
            >
              {{ formatTaskStatusLabel(status, locale) }}
            </button>
          </div>
          <div class="app-page-summary-grid">
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('myTasks.currentAccount') }}</span>
              <strong class="app-page-summary-card__value">{{ currentActor.display_name }}</strong>
              <span class="app-page-summary-card__description">這個 inbox 只聚焦你目前帳號可處理的 tester 任務。</span>
            </article>
            <article class="app-page-summary-card">
              <span class="app-page-summary-card__label">{{ t('myTasks.currentStatus') }}</span>
              <strong class="app-page-summary-card__value">{{ formatTaskStatusLabel(activeStatus, locale) }}</strong>
              <span class="app-page-summary-card__description">切換狀態後，列表會保留同一套任務卡片節奏與下一步操作。</span>
            </article>
          </div>
        </section>

        <section
          v-if="tasksPending"
          class="resource-state"
          data-testid="my-tasks-loading"
        >
          <h2 class="resource-state__title">{{ t('myTasks.loadingTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('myTasks.loadingDescription') }}
          </p>
        </section>

        <section
          v-else-if="tasksError"
          class="resource-state"
          data-testid="my-tasks-error"
        >
          <h2 class="resource-state__title">{{ t('myTasks.errorTitle') }}</h2>
          <p class="resource-state__description">
            {{ tasksError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshTasks()">
              {{ t('common.retry') }}
            </button>
          </div>
        </section>

        <section
          v-else-if="tasks.length === 0"
          class="resource-state"
          data-testid="my-tasks-empty"
        >
          <h2 class="resource-state__title">{{ t('myTasks.emptyTitle') }}</h2>
          <p class="resource-state__description">
            {{ t('myTasks.emptyDescription', { status: formatTaskStatusLabel(activeStatus, locale) }) }}
          </p>
        </section>

        <section
          v-else
          class="resource-section__body app-page-card-grid"
          data-testid="my-tasks-list"
        >
          <div
            v-if="actionError"
            class="resource-state"
            data-testid="my-tasks-action-error"
          >
            <h3 class="resource-state__title">{{ t('myTasks.actionErrorTitle') }}</h3>
            <p class="resource-state__description">
              {{ actionError }}
            </p>
          </div>

          <article
            v-for="task in tasks"
            :key="task.id"
            class="resource-card"
            :data-testid="`my-task-card-${task.id}`"
          >
            <span class="resource-shell__breadcrumb">{{ t('myTasks.breadcrumb') }}</span>
            <h2 class="resource-card__title">{{ task.title }}</h2>
            <p class="resource-card__description">
              {{
                task.device_profile_id
                  ? t('myTasks.assignmentDescription', { deviceProfileId: task.device_profile_id })
                  : t('myTasks.assignmentEmptyDescription')
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">{{ t('myTasks.currentStatus') }} {{ formatTaskStatusLabel(task.status, locale) }}</span>
              <span class="resource-card__chip">{{ t('myTasks.campaignLabel') }} {{ task.campaign_id }}</span>
              <span class="resource-card__chip">{{ t('myTasks.updatedAtLabel') }} {{ task.updated_at }}</span>
              <span
                v-if="task.qualification_context"
                class="resource-card__chip"
              >
                {{ t('myTasks.qualificationLabel') }} {{ formatQualificationStatusLabel(task.qualification_context.qualification_status, locale) }}
              </span>
              <span
                v-if="task.qualification_context?.qualification_drift"
                class="resource-card__chip"
                :data-testid="`my-task-drift-chip-${task.id}`"
              >
                {{ t('myTasks.qualificationDrift') }}
              </span>
              <span
                v-if="task.resolution_context"
                class="resource-card__chip"
                :data-testid="`my-task-resolution-chip-${task.id}`"
              >
                {{ t('myTasks.resolutionLabel') }} {{ formatTaskResolutionOutcomeLabel(task.resolution_context.resolution_outcome, locale) }}
              </span>
            </div>
            <p
              v-if="task.qualification_context"
              class="resource-card__description"
              :data-testid="`my-task-qualification-summary-${task.id}`"
            >
              {{ task.qualification_context.reason_summary || t('myTasks.qualificationSummaryEmpty') }}
            </p>
            <p
              v-if="task.qualification_context?.qualification_drift"
              class="resource-state__description"
              :data-testid="`my-task-drift-warning-${task.id}`"
            >
              {{ t('myTasks.driftWarning') }}
            </p>
            <p
              v-if="task.resolution_context"
              class="resource-card__description"
              :data-testid="`my-task-resolution-summary-${task.id}`"
            >
              {{
                t('myTasks.resolutionSummary', {
                  resolvedAt: task.resolution_context.resolved_at,
                  outcome: formatTaskResolutionOutcomeLabel(task.resolution_context.resolution_outcome, locale)
                })
              }}
            </p>
            <p
              v-if="task.resolution_context?.resolution_note"
              class="resource-state__description"
              :data-testid="`my-task-resolution-note-${task.id}`"
            >
              {{ task.resolution_context.resolution_note }}
            </p>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`my-task-detail-link-${task.id}`"
                :to="`/tasks/${task.id}`"
              >
                {{ t('myTasks.openTaskDetail') }}
              </NuxtLink>
              <button
                v-if="task.status === 'assigned'"
                class="resource-action"
                :data-testid="`my-task-start-${task.id}`"
                type="button"
                :disabled="startingTaskId === task.id"
                @click="handleStartTask(task.id)"
              >
                {{ startingTaskId === task.id ? t('myTasks.starting') : t('myTasks.startTask') }}
              </button>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>

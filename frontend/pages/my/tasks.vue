<script setup lang="ts">
import { computed, ref } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { ApiClientError } from '~/services/api/client'
import { fetchTasks, startAssignedTask } from '~/features/tasks/api'
import { formatTaskStatusLabel, type TaskStatus } from '~/features/tasks/types'
import { formatQualificationStatusLabel } from '~/features/eligibility/types'

const TESTER_INBOX_STATUSES: TaskStatus[] = [
  'assigned',
  'in_progress',
  'submitted',
  'closed'
]

useCurrentActorPersistence()

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
      actionError.value = '開始任務前，請先選擇目前操作帳號。'
      return
    }

    await startAssignedTask(taskId, currentActorId.value)
    await refreshTasks()
  } catch (submitFailure) {
    actionError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法開始這個任務。'
    )
  } finally {
    startingTaskId.value = null
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">我的任務</h1>
        <p class="resource-shell__description">
          這個頁面提供測試者端的最小任務收件匣，讓你可以查看屬於自己裝置設定檔的任務，並對已指派任務做最小狀態推進。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/tasks">
            查看所有任務
          </NuxtLink>
        </div>
      </header>

      <CurrentActorSelector
        title="測試者情境"
        description="選擇目前正在操作的測試者帳號，收件匣會依照它擁有的裝置設定檔推導我的任務。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-tasks-actor-error"
      >
        <h2 class="resource-state__title">無法取得操作情境</h2>
        <p class="resource-state__description">
          {{ accountsError.message }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshAccounts()">
            重試
          </button>
        </div>
      </section>

      <section
        v-else-if="accountsPending"
        class="resource-state"
        data-testid="my-tasks-actor-loading"
      >
        <h2 class="resource-state__title">載入測試者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的測試者情境。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-tasks-select-actor"
      >
        <h2 class="resource-state__title">請選擇測試者帳號</h2>
        <p class="resource-state__description">
          先選擇一個目前操作帳號，系統才知道要推導哪一位測試者的任務收件匣。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-tasks-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的測試者帳號。
        </p>
      </section>

      <section
        v-else-if="!isTesterActor"
        class="resource-state"
        data-testid="my-tasks-role-mismatch"
      >
        <h2 class="resource-state__title">測試者收件匣需要測試者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到測試者帳號，再查看已指派任務收件匣。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-tasks-filters">
          <h2 class="resource-section__title">收件匣狀態篩選</h2>
          <div class="resource-state__actions">
            <button
              v-for="status in TESTER_INBOX_STATUSES"
              :key="status"
              class="resource-action"
              :data-testid="`my-tasks-filter-${status}`"
              type="button"
              @click="activeStatus = status"
            >
              {{ formatTaskStatusLabel(status) }}
            </button>
          </div>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              目前帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              狀態 {{ formatTaskStatusLabel(activeStatus) }}
            </span>
          </div>
        </section>

        <section
          v-if="tasksPending"
          class="resource-state"
          data-testid="my-tasks-loading"
        >
          <h2 class="resource-state__title">載入我的任務中</h2>
          <p class="resource-state__description">
            正在根據目前操作帳號與其擁有的裝置設定檔推導測試者收件匣。
          </p>
        </section>

        <section
          v-else-if="tasksError"
          class="resource-state"
          data-testid="my-tasks-error"
        >
        <h2 class="resource-state__title">無法載入我的任務</h2>
          <p class="resource-state__description">
            {{ tasksError.message }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshTasks()">
              重試
            </button>
          </div>
        </section>

        <section
          v-else-if="tasks.length === 0"
          class="resource-state"
          data-testid="my-tasks-empty"
        >
          <h2 class="resource-state__title">這個收件匣狀態下沒有任務</h2>
          <p class="resource-state__description">
            目前這位測試者在 {{ formatTaskStatusLabel(activeStatus) }} 狀態下沒有任何任務。
          </p>
        </section>

        <section
          v-else
          class="resource-section__body"
          data-testid="my-tasks-list"
        >
          <div
            v-if="actionError"
            class="resource-state"
            data-testid="my-tasks-action-error"
          >
            <h3 class="resource-state__title">任務操作失敗</h3>
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
            <span class="resource-shell__breadcrumb">我的任務</span>
            <h2 class="resource-card__title">{{ task.title }}</h2>
            <p class="resource-card__description">
              {{
                task.device_profile_id
                  ? `已指派給裝置設定檔 ${task.device_profile_id}`
                  : '目前尚未指派裝置設定檔。'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">狀態 {{ formatTaskStatusLabel(task.status) }}</span>
              <span class="resource-card__chip">活動 {{ task.campaign_id }}</span>
              <span class="resource-card__chip">更新於 {{ task.updated_at }}</span>
              <span
                v-if="task.qualification_context"
                class="resource-card__chip"
              >
                資格 {{ formatQualificationStatusLabel(task.qualification_context.qualification_status) }}
              </span>
              <span
                v-if="task.qualification_context?.qualification_drift"
                class="resource-card__chip"
                :data-testid="`my-task-drift-chip-${task.id}`"
              >
                資格已漂移
              </span>
            </div>
            <p
              v-if="task.qualification_context"
              class="resource-card__description"
              :data-testid="`my-task-qualification-summary-${task.id}`"
            >
              {{ task.qualification_context.reason_summary || '目前沒有額外的資格摘要。' }}
            </p>
            <p
              v-if="task.qualification_context?.qualification_drift"
              class="resource-state__description"
              :data-testid="`my-task-drift-warning-${task.id}`"
            >
              這筆任務目前依照最新資格規則重新評估後，已不再符合活動條件。
            </p>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`my-task-detail-link-${task.id}`"
                :to="`/tasks/${task.id}`"
              >
                開啟任務詳情
              </NuxtLink>
              <button
                v-if="task.status === 'assigned'"
                class="resource-action"
                :data-testid="`my-task-start-${task.id}`"
                type="button"
                :disabled="startingTaskId === task.id"
                @click="handleStartTask(task.id)"
              >
                {{ startingTaskId === task.id ? '開始中...' : '開始任務' }}
              </button>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>

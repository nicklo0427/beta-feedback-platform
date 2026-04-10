<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  getActorAwareReadErrorMessage,
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import {
  fetchMyParticipationRequests,
  withdrawParticipationRequest
} from '~/features/participation-requests/api'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const actionError = ref<string | null>(null)
const withdrawingRequestId = ref<string | null>(null)

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('my-participation-requests-accounts', () => fetchAccounts(), {
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
  data: requestResponse,
  pending: requestsPending,
  error: requestsError,
  refresh: refreshRequests
} = useAsyncData(
  () =>
    `my-participation-requests-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchMyParticipationRequests(currentActorId.value)
  },
  {
    server: false,
    watch: [currentActorId, currentActor],
    default: () => ({
      items: [],
      total: 0
    })
  }
)

const participationRequests = computed(() => requestResponse.value.items)
const requestsErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(
    requestsError.value,
    '目前無法載入我的參與意圖。'
  )
)

async function handleWithdrawRequest(requestId: string): Promise<void> {
  actionError.value = null
  withdrawingRequestId.value = requestId

  try {
    if (!currentActorId.value) {
      actionError.value = '撤回參與意圖前，請先選擇目前操作帳號。'
      return
    }

    await withdrawParticipationRequest(requestId, currentActorId.value)
    await refreshRequests()
  } catch (withdrawFailure) {
    actionError.value = getActorAwareMutationErrorMessage(
      withdrawFailure,
      '目前無法撤回這筆參與意圖。'
    )
  } finally {
    withdrawingRequestId.value = null
  }
}

watch([currentActorId, currentActor], () => {
  actionError.value = null
  withdrawingRequestId.value = null
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">我的參與意圖</h1>
        <p class="resource-shell__description">
          這個頁面提供測試者端最小的 participation request 工作區，讓你查看自己送出的活動參與意圖，並在待處理時主動撤回。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/my/eligible-campaigns">
            查看符合資格的活動
          </NuxtLink>
          <NuxtLink class="resource-action" to="/my/tasks">
            查看我的任務
          </NuxtLink>
        </div>
      </header>

      <CurrentActorSelector
        title="測試者參與意圖工作區"
        description="選擇目前正在操作的測試者帳號，系統會依據這位測試者列出自己送出的活動參與意圖。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="my-participation-requests-actor-error"
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
        data-testid="my-participation-requests-actor-loading"
      >
        <h2 class="resource-state__title">載入測試者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的參與意圖工作區。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="my-participation-requests-select-actor"
      >
        <h2 class="resource-state__title">請選擇測試者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要列出哪一位測試者送出的參與意圖。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="my-participation-requests-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的測試者帳號。
        </p>
      </section>

      <section
        v-else-if="!isTesterActor"
        class="resource-state"
        data-testid="my-participation-requests-role-mismatch"
      >
        <h2 class="resource-state__title">參與意圖工作區需要測試者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到測試者帳號，再查看我的參與意圖。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="my-participation-requests-summary">
          <h2 class="resource-section__title">我的參與意圖總覽</h2>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              目前帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              參與意圖 {{ requestResponse.total }}
            </span>
          </div>
        </section>

        <section
          v-if="requestsPending"
          class="resource-state"
          data-testid="my-participation-requests-loading"
        >
          <h2 class="resource-state__title">載入我的參與意圖中</h2>
          <p class="resource-state__description">
            正在根據目前操作帳號整理這位測試者送出的 participation requests。
          </p>
        </section>

        <section
          v-else-if="requestsError"
          class="resource-state"
          data-testid="my-participation-requests-error"
        >
          <h2 class="resource-state__title">無法載入我的參與意圖</h2>
          <p class="resource-state__description">
            {{ requestsErrorMessage }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshRequests()">
              重試
            </button>
          </div>
        </section>

        <section
          v-else-if="participationRequests.length === 0"
          class="resource-state"
          data-testid="my-participation-requests-empty"
        >
          <h2 class="resource-state__title">目前還沒有送出任何參與意圖</h2>
          <p class="resource-state__description">
            目前這位測試者還沒有對任何活動送出 participation request。你可以先到符合資格的活動清單，挑一個活動送出參與意圖。
          </p>
          <div class="resource-state__actions">
            <NuxtLink class="resource-action" to="/my/eligible-campaigns">
              查看符合資格的活動
            </NuxtLink>
          </div>
        </section>

        <section
          v-else
          class="resource-section__body"
          data-testid="my-participation-requests-list"
        >
          <div
            v-if="actionError"
            class="resource-state"
            data-testid="my-participation-requests-action-error"
          >
            <h2 class="resource-state__title">無法更新參與意圖</h2>
            <p class="resource-state__description">
              {{ actionError }}
            </p>
          </div>

          <article
            v-for="request in participationRequests"
            :key="request.id"
            class="resource-card"
            :data-testid="`participation-request-card-${request.id}`"
          >
            <span class="resource-shell__breadcrumb">參與意圖</span>
            <h2 class="resource-card__title">{{ request.campaign_name }}</h2>
            <p class="resource-card__description">
              {{
                request.note
                  ? request.note
                  : '目前沒有補充說明。'
              }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                狀態 {{ formatParticipationRequestStatusLabel(request.status) }}
              </span>
              <span class="resource-card__chip">
                裝置 {{ request.device_profile_name }}
              </span>
              <span class="resource-card__chip">
                任務橋接 {{ formatParticipationAssignmentStatusLabel(request.assignment_status) }}
              </span>
            </div>
            <div class="resource-card__meta">
              <span class="resource-card__chip">建立時間 {{ request.created_at }}</span>
              <span class="resource-card__chip">更新時間 {{ request.updated_at }}</span>
            </div>
            <div
              v-if="request.decided_at || request.decision_note"
              class="resource-card__meta"
            >
              <span
                v-if="request.decided_at"
                class="resource-card__chip"
              >
                處理時間 {{ request.decided_at }}
              </span>
              <span
                v-if="request.decision_note"
                class="resource-card__chip"
              >
                處理備註 {{ request.decision_note }}
              </span>
            </div>
            <div
              v-if="request.linked_task_id || request.status === 'accepted'"
              class="resource-card__meta"
            >
              <span
                v-if="request.assignment_created_at"
                class="resource-card__chip"
              >
                建立任務時間 {{ request.assignment_created_at }}
              </span>
              <span
                v-else-if="request.status === 'accepted'"
                class="resource-card__chip"
              >
                已接受，等待建立任務
              </span>
            </div>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`participation-request-campaign-link-${request.id}`"
                :to="`/campaigns/${request.campaign_id}`"
              >
                查看活動
              </NuxtLink>
              <NuxtLink
                v-if="request.linked_task_id"
                class="resource-action"
                :data-testid="`participation-request-task-link-${request.id}`"
                :to="`/tasks/${request.linked_task_id}`"
              >
                查看對應任務
              </NuxtLink>
              <button
                v-if="request.status === 'pending'"
                class="resource-action"
                type="button"
                :data-testid="`participation-request-withdraw-${request.id}`"
                :disabled="withdrawingRequestId === request.id"
                @click="handleWithdrawRequest(request.id)"
              >
                {{ withdrawingRequestId === request.id ? '撤回中...' : '撤回參與意圖' }}
              </button>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>

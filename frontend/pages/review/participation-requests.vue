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
  decideParticipationRequest,
  fetchReviewParticipationRequests
} from '~/features/participation-requests/api'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const actionError = ref<string | null>(null)
const decidingRequestId = ref<string | null>(null)
const decisionNoteDrafts = ref<Record<string, string>>({})

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('review-participation-requests-accounts', () => fetchAccounts(), {
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
const isDeveloperActor = computed(() => currentActor.value?.role === 'developer')

const {
  data: queueResponse,
  pending: queuePending,
  error: queueError,
  refresh: refreshQueue
} = useAsyncData(
  () =>
    `review-participation-requests-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async () => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        items: [],
        total: 0
      }
    }

    return fetchReviewParticipationRequests(currentActorId.value)
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

const participationRequests = computed(() => queueResponse.value.items)
const pendingRequestsCount = computed(
  () => participationRequests.value.filter((request) => request.status === 'pending').length
)
const acceptedRequestsCount = computed(
  () =>
    participationRequests.value.filter(
      (request) => request.status === 'accepted' && request.assignment_status === 'not_assigned'
    ).length
)
const involvedCampaignCount = computed(
  () => new Set(participationRequests.value.map((request) => request.campaign_id)).size
)
const queueErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(
    queueError.value,
    '目前無法載入參與意圖審查佇列。'
  )
)

async function handleDecision(
  requestId: string,
  status: 'accepted' | 'declined'
): Promise<void> {
  actionError.value = null
  decidingRequestId.value = requestId

  try {
    if (!currentActorId.value) {
      actionError.value = '送出審查決策前，請先選擇目前操作帳號。'
      return
    }

    await decideParticipationRequest(
      requestId,
      {
        status,
        decision_note: decisionNoteDrafts.value[requestId]?.trim() || null
      },
      currentActorId.value
    )
    await refreshQueue()
  } catch (decisionFailure) {
    actionError.value = getActorAwareMutationErrorMessage(
      decisionFailure,
      '目前無法更新這筆參與意圖的審查決策。'
    )
  } finally {
    decidingRequestId.value = null
  }
}

watch(participationRequests, (items) => {
  const nextDrafts: Record<string, string> = {}

  for (const request of items) {
    nextDrafts[request.id] =
      decisionNoteDrafts.value[request.id] ?? request.decision_note ?? ''
  }

  decisionNoteDrafts.value = nextDrafts
})

watch([currentActorId, currentActor], () => {
  actionError.value = null
  decidingRequestId.value = null
})
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">參與意圖審查佇列</h1>
        <p class="resource-shell__description">
          這個頁面提供開發者端最小的 participation request 審查佇列，讓你可以查看自己擁有活動底下待處理的參與意圖，並直接接受或婉拒。
        </p>
      </header>

      <CurrentActorSelector
        title="開發者情境"
        description="選擇目前正在操作的開發者帳號，系統會依據它擁有的活動推導待處理的 participation requests。"
      />

      <section
        v-if="accountsError"
        class="resource-state"
        data-testid="participation-review-actor-error"
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
        data-testid="participation-review-actor-loading"
      >
        <h2 class="resource-state__title">載入開發者情境中</h2>
        <p class="resource-state__description">
          正在確認目前操作帳號與可用的參與意圖審查佇列。
        </p>
      </section>

      <section
        v-else-if="!currentActorId"
        class="resource-state"
        data-testid="participation-review-select-actor"
      >
        <h2 class="resource-state__title">請選擇開發者帳號</h2>
        <p class="resource-state__description">
          先選擇目前操作帳號，系統才知道要列出哪一位開發者擁有活動底下的 participation requests。
        </p>
      </section>

      <section
        v-else-if="!currentActor"
        class="resource-state"
        data-testid="participation-review-actor-missing"
      >
        <h2 class="resource-state__title">找不到已選擇的帳號</h2>
        <p class="resource-state__description">
          目前找不到你選擇的帳號，請重新選擇一筆可用的開發者帳號。
        </p>
      </section>

      <section
        v-else-if="!isDeveloperActor"
        class="resource-state"
        data-testid="participation-review-role-mismatch"
      >
        <h2 class="resource-state__title">參與意圖審查需要開發者帳號</h2>
        <p class="resource-state__description">
          目前選到的是{{ formatAccountRoleLabel(currentActor.role) }}帳號。請切換到開發者帳號，再查看 participation request 審查佇列。
        </p>
      </section>

      <template v-else>
        <section class="resource-section" data-testid="participation-review-summary">
          <h2 class="resource-section__title">待處理參與意圖總覽</h2>
          <div class="resource-shell__meta">
            <span class="resource-shell__meta-chip">
              目前帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              需處理 / 建立任務 {{ queueResponse.total }}
            </span>
            <span class="resource-shell__meta-chip">
              待處理 {{ pendingRequestsCount }}
            </span>
            <span class="resource-shell__meta-chip">
              已接受待建任務 {{ acceptedRequestsCount }}
            </span>
            <span class="resource-shell__meta-chip">
              涉及活動 {{ involvedCampaignCount }}
            </span>
          </div>
        </section>

        <section
          v-if="queuePending"
          class="resource-state"
          data-testid="participation-review-loading"
        >
          <h2 class="resource-state__title">載入參與意圖審查佇列中</h2>
          <p class="resource-state__description">
            正在根據目前操作帳號與其擁有的活動整理待處理 participation requests。
          </p>
        </section>

        <section
          v-else-if="queueError"
          class="resource-state"
          data-testid="participation-review-error"
        >
          <h2 class="resource-state__title">無法載入參與意圖審查佇列</h2>
          <p class="resource-state__description">
            {{ queueErrorMessage }}
          </p>
          <div class="resource-state__actions">
            <button class="resource-action" type="button" @click="refreshQueue()">
              重試
            </button>
          </div>
        </section>

        <section
          v-else-if="participationRequests.length === 0"
          class="resource-state"
          data-testid="participation-review-empty"
        >
          <h2 class="resource-state__title">目前沒有待處理或待建立任務的參與意圖</h2>
          <p class="resource-state__description">
            目前這位開發者擁有的活動底下沒有任何待處理 participation requests，也沒有已接受但尚未建立任務的 request。
          </p>
        </section>

        <section
          v-else
          class="resource-section__body"
          data-testid="participation-review-list"
        >
          <div
            v-if="actionError"
            class="resource-state"
            data-testid="participation-review-action-error"
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
            :data-testid="`review-participation-request-card-${request.id}`"
          >
            <span class="resource-shell__breadcrumb">參與意圖審查</span>
            <h2 class="resource-card__title">{{ request.campaign_name }}</h2>
            <p class="resource-card__description">
              測試者 {{ request.tester_account_id }} · 裝置 {{ request.device_profile_name }}
            </p>
            <div class="resource-card__meta">
              <span class="resource-card__chip">
                狀態 {{ formatParticipationRequestStatusLabel(request.status) }}
              </span>
              <span class="resource-card__chip">
                任務橋接 {{ formatParticipationAssignmentStatusLabel(request.assignment_status) }}
              </span>
              <span class="resource-card__chip">建立時間 {{ request.created_at }}</span>
              <span
                v-if="request.assignment_created_at"
                class="resource-card__chip"
              >
                已建立任務 {{ request.assignment_created_at }}
              </span>
            </div>
            <p
              v-if="request.note"
              class="resource-card__description"
            >
              測試者備註：{{ request.note }}
            </p>
            <p
              v-if="request.decision_note"
              class="resource-card__description"
            >
              處理備註：{{ request.decision_note }}
            </p>
            <label
              v-if="request.status === 'pending'"
              class="resource-field"
              :for="`participation-review-note-${request.id}`"
            >
              <span class="resource-field__label">處理備註</span>
              <textarea
                :id="`participation-review-note-${request.id}`"
                v-model="decisionNoteDrafts[request.id]"
                class="resource-textarea"
                rows="3"
                :data-testid="`review-participation-decision-note-${request.id}`"
                placeholder="選填，說明接受或婉拒的原因。"
              />
            </label>
            <div class="resource-state__actions">
              <NuxtLink
                class="resource-action"
                :data-testid="`review-participation-detail-link-${request.id}`"
                :to="`/review/participation-requests/${request.id}`"
              >
                查看參與意圖詳情
              </NuxtLink>
              <NuxtLink
                class="resource-action"
                :data-testid="`review-participation-campaign-link-${request.id}`"
                :to="`/campaigns/${request.campaign_id}`"
              >
                查看活動
              </NuxtLink>
              <template v-if="request.status === 'pending'">
                <button
                  class="resource-action"
                  type="button"
                  :disabled="decidingRequestId === request.id"
                  :data-testid="`review-participation-accept-${request.id}`"
                  @click="handleDecision(request.id, 'accepted')"
                >
                  {{ decidingRequestId === request.id ? '處理中...' : '接受參與意圖' }}
                </button>
                <button
                  class="resource-action"
                  type="button"
                  :disabled="decidingRequestId === request.id"
                  :data-testid="`review-participation-decline-${request.id}`"
                  @click="handleDecision(request.id, 'declined')"
                >
                  {{ decidingRequestId === request.id ? '處理中...' : '婉拒參與意圖' }}
                </button>
              </template>
              <NuxtLink
                v-else-if="request.status === 'accepted' && !request.linked_task_id"
                class="resource-action"
                :data-testid="`review-participation-create-task-${request.id}`"
                :to="`/review/participation-requests/${request.id}/tasks/new`"
              >
                從 request 建立任務
              </NuxtLink>
              <NuxtLink
                v-else-if="request.linked_task_id"
                class="resource-action"
                :data-testid="`review-participation-linked-task-${request.id}`"
                :to="`/tasks/${request.linked_task_id}`"
              >
                查看對應任務
              </NuxtLink>
            </div>
          </article>
        </section>
      </template>
    </section>
  </main>
</template>

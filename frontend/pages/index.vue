<script setup lang="ts">
import { computed } from 'vue'

import { fetchAccounts } from '~/features/accounts/api'
import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { fetchCampaigns } from '~/features/campaigns/api'
import { fetchDeviceProfiles } from '~/features/device-profiles/api'
import { fetchFeedbackQueue } from '~/features/feedback/api'
import { fetchProjects } from '~/features/projects/api'
import { fetchTasks } from '~/features/tasks/api'

interface DeveloperOverview {
  projectCount: number
  campaignCount: number
  reviewQueueCount: number
}

interface TesterOverview {
  deviceProfileCount: number
  assignedTaskCount: number
  inProgressTaskCount: number
}

useCurrentActorPersistence()

const currentActorId = useCurrentActorId()

const {
  data: accountResponse,
  pending: accountsPending,
  error: accountsError,
  refresh: refreshAccounts
} = useAsyncData('current-actor-accounts', () => fetchAccounts(), {
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
const isTesterActor = computed(() => currentActor.value?.role === 'tester')

const {
  data: developerOverview,
  pending: developerOverviewPending,
  error: developerOverviewError,
  refresh: refreshDeveloperOverview
} = useAsyncData(
  () =>
    `home-developer-overview-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async (): Promise<DeveloperOverview> => {
    if (!currentActorId.value || !isDeveloperActor.value) {
      return {
        projectCount: 0,
        campaignCount: 0,
        reviewQueueCount: 0
      }
    }

    const [projectsResponse, campaignsResponse, reviewQueueResponse] = await Promise.all([
      fetchProjects({
        mine: true,
        actorId: currentActorId.value
      }),
      fetchCampaigns({
        mine: true,
        actorId: currentActorId.value
      }),
      fetchFeedbackQueue({
        mine: true,
        actorId: currentActorId.value,
        reviewStatus: 'submitted'
      })
    ])

    return {
      projectCount: projectsResponse.total,
      campaignCount: campaignsResponse.total,
      reviewQueueCount: reviewQueueResponse.total
    }
  },
  {
    server: false,
    watch: [currentActorId, currentActor],
    default: () => ({
      projectCount: 0,
      campaignCount: 0,
      reviewQueueCount: 0
    })
  }
)

const {
  data: testerOverview,
  pending: testerOverviewPending,
  error: testerOverviewError,
  refresh: refreshTesterOverview
} = useAsyncData(
  () =>
    `home-tester-overview-${currentActorId.value ?? 'none'}-${currentActor.value?.role ?? 'unknown'}`,
  async (): Promise<TesterOverview> => {
    if (!currentActorId.value || !isTesterActor.value) {
      return {
        deviceProfileCount: 0,
        assignedTaskCount: 0,
        inProgressTaskCount: 0
      }
    }

    const [deviceProfilesResponse, assignedTasksResponse, inProgressTasksResponse] =
      await Promise.all([
        fetchDeviceProfiles({
          mine: true,
          actorId: currentActorId.value
        }),
        fetchTasks({
          mine: true,
          actorId: currentActorId.value,
          status: 'assigned'
        }),
        fetchTasks({
          mine: true,
          actorId: currentActorId.value,
          status: 'in_progress'
        })
      ])

    return {
      deviceProfileCount: deviceProfilesResponse.total,
      assignedTaskCount: assignedTasksResponse.total,
      inProgressTaskCount: inProgressTasksResponse.total
    }
  },
  {
    server: false,
    watch: [currentActorId, currentActor],
    default: () => ({
      deviceProfileCount: 0,
      assignedTaskCount: 0,
      inProgressTaskCount: 0
    })
  }
)
</script>

<template>
  <main class="app-shell">
    <section class="app-panel">
      <p class="app-eyebrow">跨平台 Beta 測試營運</p>
      <h1 class="app-title">beta-feedback-platform</h1>
      <p class="app-description">
        這是一個跨平台 Beta 測試媒合與回饋管理平台，讓開發者能在同一個系統內完成
        測試招募、資格條件設定、任務派發、結構化回饋整理，以及第一版信譽摘要。
      </p>

      <div class="home-hero-actions">
        <NuxtLink
          class="resource-action"
          data-testid="home-start-projects-link"
          to="/projects"
        >
          從專案開始
        </NuxtLink>
        <NuxtLink
          class="resource-action"
          data-testid="home-start-campaigns-link"
          to="/campaigns"
        >
          查看活動
        </NuxtLink>
        <NuxtLink
          class="resource-action"
          data-testid="home-review-feedback-link"
          to="/review/feedback"
        >
          查看回饋審查佇列
        </NuxtLink>
      </div>

      <CurrentActorSelector
        title="依角色切換的操作情境"
        description="切換目前正在操作的帳號後，首頁入口與摘要會依開發者或測試者角色自動調整。"
      />

      <section
        class="resource-section"
        data-testid="home-role-aware-section"
      >
        <h2 class="resource-section__title">依角色顯示的總覽</h2>

        <section
          v-if="accountsError"
          class="resource-state"
          data-testid="home-role-actor-error"
        >
          <h3 class="resource-state__title">操作情境暫時無法使用</h3>
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
          data-testid="home-role-actor-loading"
        >
          <h3 class="resource-state__title">正在載入角色情境</h3>
          <p class="resource-state__description">
            正在確認目前操作帳號與可用的角色入口。
          </p>
        </section>

        <section
          v-else-if="!currentActorId"
          class="resource-state"
          data-testid="home-role-select-actor"
        >
          <h3 class="resource-state__title">請先選擇目前操作帳號</h3>
          <p class="resource-state__description">
            先選擇一筆帳號，首頁才會切換成開發者或測試者的工作入口。
          </p>
        </section>

        <section
          v-else-if="!currentActor"
          class="resource-state"
          data-testid="home-role-actor-missing"
        >
          <h3 class="resource-state__title">所選帳號目前無法使用</h3>
          <p class="resource-state__description">
            目前找不到這筆帳號，請重新選擇可用的操作帳號。
          </p>
        </section>

        <template v-else-if="isDeveloperActor">
          <div class="resource-shell__meta" data-testid="home-role-meta">
            <span class="resource-shell__meta-chip">
              目前操作帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              角色 {{ formatAccountRoleLabel(currentActor.role) }}
            </span>
          </div>

          <div class="home-role-actions" data-testid="home-role-developer-actions">
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-projects"
              to="/my/projects"
            >
              查看我的專案
            </NuxtLink>
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-review-feedback"
              to="/review/feedback"
            >
              查看審查佇列
            </NuxtLink>
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-campaigns"
              to="/my/campaigns"
            >
              查看我的活動
            </NuxtLink>
          </div>

          <section
            v-if="developerOverviewPending"
            class="resource-state"
            data-testid="home-role-developer-loading"
          >
            <h3 class="resource-state__title">正在載入開發者總覽</h3>
            <p class="resource-state__description">
              正在整理這位開發者擁有的專案與待審查回饋。
            </p>
          </section>

          <section
            v-else-if="developerOverviewError"
            class="resource-state"
            data-testid="home-role-developer-error"
          >
            <h3 class="resource-state__title">開發者總覽暫時無法使用</h3>
            <p class="resource-state__description">
              {{ developerOverviewError.message }}
            </p>
            <div class="resource-state__actions">
              <button class="resource-action" type="button" @click="refreshDeveloperOverview()">
                重試
              </button>
            </div>
          </section>

          <div
            v-else
            class="home-role-grid"
            data-testid="home-role-developer"
          >
            <article class="home-role-card" data-testid="home-role-card-projects">
              <span class="home-role-card__eyebrow">開發者</span>
              <h3 class="home-role-card__title">我的專案</h3>
              <strong class="home-role-card__metric">
                {{ developerOverview.projectCount }}
              </strong>
              <p class="home-role-card__description">
                以目前操作帳號為擁有者推導出的專案數量。
              </p>
            </article>

            <article class="home-role-card" data-testid="home-role-card-campaigns">
              <span class="home-role-card__eyebrow">開發者</span>
              <h3 class="home-role-card__title">我的活動</h3>
              <strong class="home-role-card__metric">
                {{ developerOverview.campaignCount }}
              </strong>
              <p class="home-role-card__description">
                由目前操作帳號擁有的專案推導出的活動數量。
              </p>
            </article>

            <article class="home-role-card" data-testid="home-role-card-review-queue">
              <span class="home-role-card__eyebrow">開發者</span>
              <h3 class="home-role-card__title">待審查回饋</h3>
              <strong class="home-role-card__metric">
                {{ developerOverview.reviewQueueCount }}
              </strong>
              <p class="home-role-card__description">
                目前屬於這位開發者，且仍在已提交狀態下等待審查的回饋數量。
              </p>
            </article>
          </div>
        </template>

        <template v-else-if="isTesterActor">
          <div class="resource-shell__meta" data-testid="home-role-meta">
            <span class="resource-shell__meta-chip">
              目前操作帳號 {{ currentActor.display_name }}
            </span>
            <span class="resource-shell__meta-chip">
              角色 {{ formatAccountRoleLabel(currentActor.role) }}
            </span>
          </div>

          <div class="home-role-actions" data-testid="home-role-tester-actions">
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-eligible-campaigns"
              to="/my/eligible-campaigns"
            >
              查看符合資格的活動
            </NuxtLink>
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-my-tasks"
              to="/my/tasks"
            >
              查看我的任務
            </NuxtLink>
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-device-profiles"
              to="/device-profiles"
            >
              查看我的裝置設定檔
            </NuxtLink>
            <NuxtLink
              class="resource-action"
              data-testid="home-role-action-accounts"
              to="/accounts"
            >
              查看帳號
            </NuxtLink>
          </div>

          <section
            v-if="testerOverviewPending"
            class="resource-state"
            data-testid="home-role-tester-loading"
          >
            <h3 class="resource-state__title">正在載入測試者總覽</h3>
            <p class="resource-state__description">
              正在整理這位測試者擁有的裝置設定檔與任務收件匣。
            </p>
          </section>

          <section
            v-else-if="testerOverviewError"
            class="resource-state"
            data-testid="home-role-tester-error"
          >
            <h3 class="resource-state__title">測試者總覽暫時無法使用</h3>
            <p class="resource-state__description">
              {{ testerOverviewError.message }}
            </p>
            <div class="resource-state__actions">
              <button class="resource-action" type="button" @click="refreshTesterOverview()">
                重試
              </button>
            </div>
          </section>

          <div
            v-else
            class="home-role-grid"
            data-testid="home-role-tester"
          >
            <article class="home-role-card" data-testid="home-role-card-device-profiles">
              <span class="home-role-card__eyebrow">測試者</span>
              <h3 class="home-role-card__title">我的裝置設定檔</h3>
              <strong class="home-role-card__metric">
                {{ testerOverview.deviceProfileCount }}
              </strong>
              <p class="home-role-card__description">
                以目前操作帳號為擁有者推導出的裝置設定檔數量。
              </p>
            </article>

            <article class="home-role-card" data-testid="home-role-card-assigned-tasks">
              <span class="home-role-card__eyebrow">測試者</span>
              <h3 class="home-role-card__title">已指派任務</h3>
              <strong class="home-role-card__metric">
                {{ testerOverview.assignedTaskCount }}
              </strong>
              <p class="home-role-card__description">
                目前仍待開始處理的測試者收件匣任務數量。
              </p>
            </article>

            <article class="home-role-card" data-testid="home-role-card-in-progress-tasks">
              <span class="home-role-card__eyebrow">測試者</span>
              <h3 class="home-role-card__title">進行中任務</h3>
              <strong class="home-role-card__metric">
                {{ testerOverview.inProgressTaskCount }}
              </strong>
              <p class="home-role-card__description">
                目前已開始執行、但尚未提交回饋的任務數量。
              </p>
            </article>
          </div>
        </template>
      </section>

      <section
        class="resource-section"
        data-testid="home-overview-section"
      >
        <h2 class="resource-section__title">產品總覽</h2>
        <div class="home-grid">
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">這個平台做什麼</h3>
            <p class="home-summary-card__description">
              幫助開發者找到合適的測試者、管理不同平台的測試活動，並把任務與回饋
              留在同一條可追蹤流程內。
            </p>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">這個平台不是什麼</h3>
            <ul class="home-list" data-testid="home-non-goals">
              <li>不是互刷平台</li>
              <li>不是評論交換平台</li>
              <li>不是灌量工具</li>
            </ul>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">第一階段支援平台</h3>
            <div class="resource-shell__meta">
              <span class="resource-shell__meta-chip">網頁 / 行動網頁 / PWA</span>
              <span class="resource-shell__meta-chip">iOS</span>
              <span class="resource-shell__meta-chip">Android</span>
            </div>
          </div>
        </div>
      </section>

      <section
        class="resource-section"
        data-testid="home-primary-nav"
      >
        <h2 class="resource-section__title">核心模組</h2>
        <nav class="shell-link-grid" aria-label="主要模組導覽">
          <NuxtLink class="shell-link-card" data-testid="home-projects-link" to="/projects">
            <span class="shell-link-label">專案</span>
            <strong class="shell-link-title">產品與測試範圍</strong>
            <span class="shell-link-description">
              從產品主體開始整理測試目標，作為後續 campaign 與 task 的入口。
            </span>
          </NuxtLink>

          <NuxtLink class="shell-link-card" data-testid="home-campaigns-link" to="/campaigns">
            <span class="shell-link-label">活動</span>
            <strong class="shell-link-title">活動、安全與規則</strong>
            <span class="shell-link-description">
              管理測試批次、來源標示、安全風險與 eligibility 條件。
            </span>
          </NuxtLink>

          <NuxtLink
            class="shell-link-card"
            data-testid="home-accounts-link"
            to="/accounts"
          >
            <span class="shell-link-label">帳號</span>
            <strong class="shell-link-title">開發者與測試者基礎</strong>
            <span class="shell-link-description">
              建立最小帳號基線，作為擁有權、目前操作帳號與依角色協作流程的基礎。
            </span>
          </NuxtLink>

          <NuxtLink
            class="shell-link-card"
            data-testid="home-device-profiles-link"
            to="/device-profiles"
          >
            <span class="shell-link-label">裝置設定檔</span>
            <strong class="shell-link-title">測試者裝置情境</strong>
            <span class="shell-link-description">
              維護測試裝置與平台資訊，作為資格規則、任務與信譽的基礎。
            </span>
          </NuxtLink>

          <NuxtLink class="shell-link-card" data-testid="home-tasks-link" to="/tasks">
            <span class="shell-link-label">任務</span>
            <strong class="shell-link-title">指派與狀態流</strong>
            <span class="shell-link-description">
              追蹤任務指派、狀態流轉，以及回饋提交所在的主要操作入口。
            </span>
          </NuxtLink>
        </nav>
      </section>

      <section
        class="resource-section"
        data-testid="home-core-flow"
      >
        <h2 class="resource-section__title">核心流程</h2>
        <ol class="home-flow">
          <li class="home-flow__item">
            <strong>專案</strong>
            <span>定義產品或測試主體。</span>
          </li>
          <li class="home-flow__item">
            <strong>活動</strong>
            <span>設定測試批次、平台條件、安全來源與資格規則。</span>
          </li>
          <li class="home-flow__item">
            <strong>裝置設定檔</strong>
            <span>建立測試者的裝置情境，對齊資格規則與指派基礎。</span>
          </li>
          <li class="home-flow__item">
            <strong>任務</strong>
            <span>派發任務並追蹤狀態流。</span>
          </li>
          <li class="home-flow__item">
            <strong>回饋</strong>
            <span>在任務情境下提交結構化回饋，並累積第一版信譽訊號。</span>
          </li>
        </ol>
      </section>

      <section class="resource-section">
        <h2 class="resource-section__title">安全與信任原則</h2>
        <div class="home-grid">
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">安全優先</h3>
            <ul class="home-list">
              <li>優先採用各平台官方測試 / 分發機制</li>
              <li>不鼓勵來源不明安裝檔</li>
              <li>不鼓勵關閉裝置安全防護</li>
            </ul>
          </div>
          <div class="home-summary-card">
            <h3 class="home-summary-card__title">信任來自實際合作</h3>
            <p class="home-summary-card__description">
              第一版信譽只做推導式摘要，不做公開排行；重點是讓開發者與測試者都能看到最基本的合作訊號。
            </p>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped lang="scss">
.home-hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.home-grid {
  display: grid;
  gap: 1rem;
}

.home-summary-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  &__title {
    margin: 0;
    font-size: 1.05rem;
  }

  &__description {
    margin: 0;
    color: #cbd5e1;
    line-height: 1.7;
  }
}

.home-role-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.home-role-grid {
  display: grid;
  gap: 1rem;
}

.home-role-card {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1.25rem;
  border: 1px solid rgba(148, 163, 184, 0.16);
  border-radius: 1rem;
  background: rgba(15, 23, 42, 0.78);

  &__eyebrow {
    color: #93c5fd;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
  }

  &__title {
    margin: 0;
    font-size: 1.05rem;
  }

  &__metric {
    font-size: clamp(1.75rem, 4vw, 2.5rem);
    line-height: 1;
  }

  &__description {
    margin: 0;
    color: #cbd5e1;
    line-height: 1.7;
  }
}

.home-list {
  margin: 0;
  padding-left: 1.1rem;
  color: #cbd5e1;
  line-height: 1.8;
}

.home-flow {
  display: grid;
  gap: 0.85rem;
  margin: 0;
  padding-left: 1.25rem;
}

.home-flow__item {
  color: #cbd5e1;
  line-height: 1.7;

  strong {
    color: #e2e8f0;
    margin-right: 0.4rem;
  }
}

@media (min-width: 768px) {
  .home-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .home-role-grid {
    grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
  }
}
</style>

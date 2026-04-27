<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  getActorAwareReadErrorMessage,
  useAuthSession,
  useAuthSessionPending,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  formatAccountRoleLabel,
  formatAccountRolesLabel,
  normalizeAccountRoles,
  type AccountRole
} from '~/features/accounts/types'
import { useActiveWorkspaceRolePersistence } from '~/features/accounts/workspace-role'
import { fetchCampaigns } from '~/features/campaigns/api'
import { formatCampaignStatusLabel } from '~/features/campaigns/types'
import { fetchFeedbackQueue } from '~/features/feedback/api'
import { formatFeedbackReviewStatusLabel } from '~/features/feedback/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'
import { formatPlatformLabel } from '~/features/platform-display'
import {
  fetchMyParticipationRequests,
  fetchReviewParticipationRequests
} from '~/features/participation-requests/api'
import {
  formatParticipationAssignmentStatusLabel,
  formatParticipationRequestStatusLabel
} from '~/features/participation-requests/types'
import { fetchProjects } from '~/features/projects/api'
import { fetchTasks } from '~/features/tasks/api'
import {
  formatTaskResolutionOutcomeLabel,
  formatTaskStatusLabel
} from '~/features/tasks/types'

definePageMeta({
  layout: 'app'
})

useCurrentActorPersistence()

type DeveloperDashboardData = {
  kind: 'developer'
  projects: Awaited<ReturnType<typeof fetchProjects>>
  campaigns: Awaited<ReturnType<typeof fetchCampaigns>>
  feedbackQueue: Awaited<ReturnType<typeof fetchFeedbackQueue>>
  participationQueue: Awaited<ReturnType<typeof fetchReviewParticipationRequests>>
}

type TesterDashboardData = {
  kind: 'tester'
  assignedTasks: Awaited<ReturnType<typeof fetchTasks>>
  inProgressTasks: Awaited<ReturnType<typeof fetchTasks>>
  eligibleCampaigns: Awaited<ReturnType<typeof fetchCampaigns>>
  participationRequests: Awaited<ReturnType<typeof fetchMyParticipationRequests>>
}

type DashboardData = DeveloperDashboardData | TesterDashboardData | null

const router = useRouter()
const { locale, t } = useAppI18n()
const authSession = useAuthSession()
const authSessionPending = useAuthSessionPending()
const redirectingToLogin = ref(false)

const sessionAccount = computed(() => authSession.value?.account ?? null)
const activeWorkspaceRole = useActiveWorkspaceRolePersistence(sessionAccount)
const dashboardWorkspaceRole = computed<AccountRole | null>(() => {
  const availableRoles = normalizeAccountRoles(sessionAccount.value ?? {})

  if (availableRoles.length === 0) {
    return null
  }

  if (activeWorkspaceRole.value && availableRoles.includes(activeWorkspaceRole.value)) {
    return activeWorkspaceRole.value
  }

  return availableRoles[0]
})

watch(
  [authSession, authSessionPending],
  ([session, pending]) => {
    if (session || pending || redirectingToLogin.value || !import.meta.client) {
      return
    }

    redirectingToLogin.value = true
    void router.replace('/login')
  },
  {
    immediate: true
  }
)

const {
  data: dashboardResponse,
  pending: dashboardPending,
  error: dashboardError,
  refresh: refreshDashboard
} = useAsyncData(
  () =>
    `dashboard-${sessionAccount.value?.id ?? 'none'}-${dashboardWorkspaceRole.value ?? 'none'}`,
  async (): Promise<DashboardData> => {
    if (!sessionAccount.value || !dashboardWorkspaceRole.value) {
      return null
    }

    const actorIdValue = sessionAccount.value.id

    if (dashboardWorkspaceRole.value === 'developer') {
      const [projects, campaigns, feedbackQueue, participationQueue] =
        await Promise.all([
          fetchProjects({
            mine: true,
            actorId: actorIdValue
          }),
          fetchCampaigns({
            mine: true,
            actorId: actorIdValue
          }),
          fetchFeedbackQueue({
            mine: true,
            actorId: actorIdValue,
            reviewStatus: 'submitted'
          }),
          fetchReviewParticipationRequests(actorIdValue)
        ])

      return {
        kind: 'developer',
        projects,
        campaigns,
        feedbackQueue,
        participationQueue
      }
    }

    const [assignedTasks, inProgressTasks, eligibleCampaigns, participationRequests] =
      await Promise.all([
        fetchTasks({
          mine: true,
          status: 'assigned',
          actorId: actorIdValue
        }),
        fetchTasks({
          mine: true,
          status: 'in_progress',
          actorId: actorIdValue
        }),
        fetchCampaigns({
          qualifiedForMe: true,
          actorId: actorIdValue
        }),
        fetchMyParticipationRequests(actorIdValue)
      ])

    return {
      kind: 'tester',
      assignedTasks,
      inProgressTasks,
      eligibleCampaigns,
      participationRequests
    }
  },
  {
    server: false,
    watch: [sessionAccount, dashboardWorkspaceRole],
    default: () => null
  }
)

const dashboardErrorMessage = computed(() =>
  getActorAwareReadErrorMessage(
    dashboardError.value,
    t('dashboard.errorFallback')
  )
)

const developerData = computed(() =>
  dashboardResponse.value?.kind === 'developer' ? dashboardResponse.value : null
)
const testerData = computed(() =>
  dashboardResponse.value?.kind === 'tester' ? dashboardResponse.value : null
)

const developerRecentProjects = computed(
  () => developerData.value?.projects.items.slice(0, 3) ?? []
)
const developerRecentCampaigns = computed(
  () => developerData.value?.campaigns.items.slice(0, 3) ?? []
)
const developerRecentFeedback = computed(
  () => developerData.value?.feedbackQueue.items.slice(0, 3) ?? []
)
const developerRecentParticipationRequests = computed(
  () => developerData.value?.participationQueue.items.slice(0, 3) ?? []
)

const testerAssignedTasks = computed(
  () => testerData.value?.assignedTasks.items.slice(0, 3) ?? []
)
const testerInProgressTasks = computed(
  () => testerData.value?.inProgressTasks.items.slice(0, 3) ?? []
)
const testerEligibleCampaigns = computed(
  () => testerData.value?.eligibleCampaigns.items.slice(0, 3) ?? []
)
const testerRecentParticipationRequests = computed(
  () => testerData.value?.participationRequests.items.slice(0, 3) ?? []
)
</script>

<template>
  <main class="app-shell" :data-locale="locale">
    <section
      v-if="authSessionPending"
      class="resource-shell"
      data-testid="dashboard-loading"
    >
      <section class="resource-state">
        <h1 class="resource-state__title">{{ t('dashboard.loadingTitle') }}</h1>
        <p class="resource-state__description">
          {{ t('dashboard.loadingDescription') }}
        </p>
      </section>
    </section>

    <section
      v-else-if="redirectingToLogin"
      class="resource-shell"
      data-testid="dashboard-redirecting"
    >
      <section class="resource-state">
        <h1 class="resource-state__title">{{ t('dashboard.redirectTitle') }}</h1>
        <p class="resource-state__description">
          {{ t('dashboard.redirectDescription') }}
        </p>
      </section>
    </section>

    <section
      v-else-if="sessionAccount"
      class="resource-shell"
      data-testid="dashboard-shell"
    >
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">
          {{ t('shell.nav.home') }}
        </NuxtLink>
        <h1 class="resource-shell__title">{{ t('dashboard.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('dashboard.description') }}
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{ t('dashboard.sessionLabel') }} {{ sessionAccount.display_name }}
          </span>
          <span class="resource-shell__meta-chip">
            {{ t('dashboard.roleLabel') }}
            {{ formatAccountRolesLabel(sessionAccount, locale) }}
          </span>
          <span
            v-if="dashboardWorkspaceRole"
            class="resource-shell__meta-chip"
            data-testid="dashboard-active-workspace-role"
          >
            {{ t('dashboard.activeViewLabel') }}
            {{ formatAccountRoleLabel(dashboardWorkspaceRole, locale) }}
          </span>
        </div>
      </header>

      <section
        v-if="dashboardPending"
        class="resource-state"
        data-testid="dashboard-data-loading"
      >
        <h2 class="resource-state__title">{{ t('dashboard.dataLoadingTitle') }}</h2>
        <p class="resource-state__description">
          {{ t('dashboard.dataLoadingDescription') }}
        </p>
      </section>

      <section
        v-else-if="dashboardError"
        class="resource-state"
        data-testid="dashboard-error"
      >
        <h2 class="resource-state__title">{{ t('dashboard.errorTitle') }}</h2>
        <p class="resource-state__description">
          {{ dashboardErrorMessage }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refreshDashboard()">
            {{ t('common.retry') }}
          </button>
        </div>
      </section>

      <template v-else-if="developerData">
        <section
          class="resource-section dashboard-section-stack"
          data-testid="dashboard-developer-handoff"
        >
          <div>
            <span class="resource-section__eyebrow">{{ t('dashboard.developer.eyebrow') }}</span>
            <h2 class="resource-section__title">{{ t('dashboard.developer.title') }}</h2>
            <p class="resource-section__description">
              {{ t('dashboard.developer.description') }}
            </p>
          </div>

          <section data-testid="dashboard-developer-summary">
            <h3 class="resource-section__title">{{ t('dashboard.summaryTitle') }}</h3>
            <p class="resource-section__description">
              {{ t('dashboard.summaryDescription') }}
            </p>
            <div class="dashboard-summary-grid">
              <article class="summary-stat-card" data-testid="dashboard-developer-projects-card">
                <span class="summary-stat-card__label">{{ t('dashboard.developer.summary.projectsLabel') }}</span>
                <strong class="summary-stat-card__value">{{ developerData.projects.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.developer.summary.projectsDescription') }}
                </p>
              </article>
              <article class="summary-stat-card" data-testid="dashboard-developer-campaigns-card">
                <span class="summary-stat-card__label">{{ t('dashboard.developer.summary.campaignsLabel') }}</span>
                <strong class="summary-stat-card__value">{{ developerData.campaigns.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.developer.summary.campaignsDescription') }}
                </p>
              </article>
              <article class="summary-stat-card" data-testid="dashboard-developer-participation-card">
                <span class="summary-stat-card__label">{{ t('dashboard.developer.summary.participationLabel') }}</span>
                <strong class="summary-stat-card__value">{{ developerData.participationQueue.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.developer.summary.participationDescription') }}
                </p>
              </article>
              <article class="summary-stat-card" data-testid="dashboard-developer-feedback-card">
                <span class="summary-stat-card__label">{{ t('dashboard.developer.summary.feedbackLabel') }}</span>
                <strong class="summary-stat-card__value">{{ developerData.feedbackQueue.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.developer.summary.feedbackDescription') }}
                </p>
              </article>
            </div>
          </section>

          <section data-testid="dashboard-developer-actions">
            <h3 class="resource-section__title">{{ t('dashboard.nextActionsTitle') }}</h3>
            <p class="resource-section__description">
              {{ t('dashboard.nextActionsDescription') }}
            </p>
            <div class="dashboard-action-grid">
              <NuxtLink class="shell-link-card" to="/my/projects">
                <span class="shell-link-label">{{ t('dashboard.developer.quickActions.projectsLabel') }}</span>
                <strong class="shell-link-title">{{ t('dashboard.developer.primary') }}</strong>
                <span class="shell-link-description">
                  {{ t('dashboard.developer.quickActions.projectsDescription') }}
                </span>
              </NuxtLink>
              <NuxtLink class="shell-link-card" to="/my/campaigns">
                <span class="shell-link-label">{{ t('dashboard.developer.quickActions.campaignsLabel') }}</span>
                <strong class="shell-link-title">{{ t('dashboard.developer.secondary') }}</strong>
                <span class="shell-link-description">
                  {{ t('dashboard.developer.quickActions.campaignsDescription') }}
                </span>
              </NuxtLink>
              <NuxtLink class="shell-link-card" to="/review/feedback">
                <span class="shell-link-label">{{ t('dashboard.developer.quickActions.feedbackLabel') }}</span>
                <strong class="shell-link-title">{{ t('dashboard.developer.tertiary') }}</strong>
                <span class="shell-link-description">
                  {{ t('dashboard.developer.quickActions.feedbackDescription') }}
                </span>
              </NuxtLink>
            </div>
          </section>

          <section data-testid="dashboard-developer-queues">
            <h3 class="resource-section__title">{{ t('dashboard.queuesTitle') }}</h3>
            <p class="resource-section__description">
              {{ t('dashboard.queuesDescription') }}
            </p>
            <div class="dashboard-queue-grid">
              <article class="resource-card" data-testid="dashboard-developer-queue-participation">
                <span class="shell-link-label">{{ t('dashboard.developer.queue.participationLabel') }}</span>
                <h4 class="resource-card__title">{{ t('dashboard.developer.queue.participationTitle') }}</h4>
                <p class="resource-card__description">
                  {{ t('dashboard.developer.queue.participationDescription') }}
                </p>
                <div
                  v-if="developerRecentParticipationRequests.length === 0"
                  class="resource-state"
                >
                  <p class="resource-state__description">
                    {{ t('dashboard.developer.queue.participationEmpty') }}
                  </p>
                </div>
                <div v-else class="dashboard-card-list">
                  <article
                    v-for="request in developerRecentParticipationRequests"
                    :key="request.id"
                    class="dashboard-card-list__item"
                  >
                    <strong>{{ request.campaign_name }}</strong>
                    <span>{{ request.device_profile_name }}</span>
                    <div class="dashboard-card-list__meta">
                      <span class="resource-card__chip">
                        {{ formatParticipationRequestStatusLabel(request.status, locale) }}
                      </span>
                      <span class="resource-card__chip">
                        {{ formatParticipationAssignmentStatusLabel(request.assignment_status, locale) }}
                      </span>
                    </div>
                  </article>
                </div>
                <div class="resource-state__actions">
                  <NuxtLink class="resource-action" to="/review/participation-requests">
                    {{ t('dashboard.developer.queue.openParticipation') }}
                  </NuxtLink>
                </div>
              </article>

              <article class="resource-card" data-testid="dashboard-developer-queue-feedback">
                <span class="shell-link-label">{{ t('dashboard.developer.queue.feedbackLabel') }}</span>
                <h4 class="resource-card__title">{{ t('dashboard.developer.queue.feedbackTitle') }}</h4>
                <p class="resource-card__description">
                  {{ t('dashboard.developer.queue.feedbackDescription') }}
                </p>
                <div
                  v-if="developerRecentFeedback.length === 0"
                  class="resource-state"
                >
                  <p class="resource-state__description">
                    {{ t('dashboard.developer.queue.feedbackEmpty') }}
                  </p>
                </div>
                <div v-else class="dashboard-card-list">
                  <article
                    v-for="feedback in developerRecentFeedback"
                    :key="feedback.id"
                    class="dashboard-card-list__item"
                  >
                    <strong>{{ feedback.summary }}</strong>
                    <span>{{ t('dashboard.developer.queue.feedbackTaskHint', { taskId: feedback.task_id }) }}</span>
                    <div class="dashboard-card-list__meta">
                      <span class="resource-card__chip">
                        {{ formatFeedbackReviewStatusLabel(feedback.review_status, locale) }}
                      </span>
                    </div>
                  </article>
                </div>
                <div class="resource-state__actions">
                  <NuxtLink class="resource-action" to="/review/feedback">
                    {{ t('dashboard.developer.queue.openFeedback') }}
                  </NuxtLink>
                </div>
              </article>

              <article class="resource-card" data-testid="dashboard-developer-queue-campaigns">
                <span class="shell-link-label">{{ t('dashboard.developer.queue.campaignsLabel') }}</span>
                <h4 class="resource-card__title">{{ t('dashboard.developer.queue.campaignsTitle') }}</h4>
                <p class="resource-card__description">
                  {{ t('dashboard.developer.queue.campaignsDescription') }}
                </p>
                <div
                  v-if="developerRecentCampaigns.length === 0"
                  class="resource-state"
                >
                  <p class="resource-state__description">
                    {{ t('dashboard.developer.queue.campaignsEmpty') }}
                  </p>
                </div>
                <div v-else class="dashboard-card-list">
                  <article
                    v-for="campaign in developerRecentCampaigns"
                    :key="campaign.id"
                    class="dashboard-card-list__item"
                  >
                    <strong>{{ campaign.name }}</strong>
                    <div class="dashboard-card-list__meta">
                      <span class="resource-card__chip">
                        {{ formatCampaignStatusLabel(campaign.status, locale) }}
                      </span>
                      <span class="resource-card__chip">
                        {{ t('dashboard.updatedAtLabel') }} {{ campaign.updated_at }}
                      </span>
                    </div>
                  </article>
                </div>
                <div class="resource-state__actions">
                  <NuxtLink class="resource-action" to="/my/campaigns">
                    {{ t('dashboard.developer.queue.openCampaigns') }}
                  </NuxtLink>
                </div>
              </article>
            </div>
          </section>
        </section>
      </template>

      <template v-else-if="testerData">
        <section
          class="resource-section dashboard-section-stack"
          data-testid="dashboard-tester-handoff"
        >
          <div>
            <span class="resource-section__eyebrow">{{ t('dashboard.tester.eyebrow') }}</span>
            <h2 class="resource-section__title">{{ t('dashboard.tester.title') }}</h2>
            <p class="resource-section__description">
              {{ t('dashboard.tester.description') }}
            </p>
          </div>

          <section data-testid="dashboard-tester-summary">
            <h3 class="resource-section__title">{{ t('dashboard.summaryTitle') }}</h3>
            <p class="resource-section__description">
              {{ t('dashboard.summaryDescription') }}
            </p>
            <div class="dashboard-summary-grid">
              <article class="summary-stat-card" data-testid="dashboard-tester-assigned-card">
                <span class="summary-stat-card__label">{{ t('dashboard.tester.summary.assignedLabel') }}</span>
                <strong class="summary-stat-card__value">{{ testerData.assignedTasks.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.tester.summary.assignedDescription') }}
                </p>
              </article>
              <article class="summary-stat-card" data-testid="dashboard-tester-in-progress-card">
                <span class="summary-stat-card__label">{{ t('dashboard.tester.summary.inProgressLabel') }}</span>
                <strong class="summary-stat-card__value">{{ testerData.inProgressTasks.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.tester.summary.inProgressDescription') }}
                </p>
              </article>
              <article class="summary-stat-card" data-testid="dashboard-tester-eligible-card">
                <span class="summary-stat-card__label">{{ t('dashboard.tester.summary.eligibleLabel') }}</span>
                <strong class="summary-stat-card__value">{{ testerData.eligibleCampaigns.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.tester.summary.eligibleDescription') }}
                </p>
              </article>
              <article class="summary-stat-card" data-testid="dashboard-tester-participation-card">
                <span class="summary-stat-card__label">{{ t('dashboard.tester.summary.participationLabel') }}</span>
                <strong class="summary-stat-card__value">{{ testerData.participationRequests.total }}</strong>
                <p class="home-summary-card__description">
                  {{ t('dashboard.tester.summary.participationDescription') }}
                </p>
              </article>
            </div>
          </section>

          <section data-testid="dashboard-tester-actions">
            <h3 class="resource-section__title">{{ t('dashboard.nextActionsTitle') }}</h3>
            <p class="resource-section__description">
              {{ t('dashboard.nextActionsDescription') }}
            </p>
            <div class="dashboard-action-grid">
              <NuxtLink class="shell-link-card" to="/my/tasks">
                <span class="shell-link-label">{{ t('dashboard.tester.quickActions.tasksLabel') }}</span>
                <strong class="shell-link-title">{{ t('dashboard.tester.primary') }}</strong>
                <span class="shell-link-description">
                  {{ t('dashboard.tester.quickActions.tasksDescription') }}
                </span>
              </NuxtLink>
              <NuxtLink class="shell-link-card" to="/my/eligible-campaigns">
                <span class="shell-link-label">{{ t('dashboard.tester.quickActions.eligibleLabel') }}</span>
                <strong class="shell-link-title">{{ t('dashboard.tester.secondary') }}</strong>
                <span class="shell-link-description">
                  {{ t('dashboard.tester.quickActions.eligibleDescription') }}
                </span>
              </NuxtLink>
              <NuxtLink class="shell-link-card" to="/my/participation-requests">
                <span class="shell-link-label">{{ t('dashboard.tester.quickActions.participationLabel') }}</span>
                <strong class="shell-link-title">{{ t('dashboard.tester.tertiary') }}</strong>
                <span class="shell-link-description">
                  {{ t('dashboard.tester.quickActions.participationDescription') }}
                </span>
              </NuxtLink>
            </div>
          </section>

          <section data-testid="dashboard-tester-queues">
            <h3 class="resource-section__title">{{ t('dashboard.queuesTitle') }}</h3>
            <p class="resource-section__description">
              {{ t('dashboard.queuesDescription') }}
            </p>
            <div class="dashboard-queue-grid">
              <article class="resource-card" data-testid="dashboard-tester-queue-tasks">
                <span class="shell-link-label">{{ t('dashboard.tester.queue.tasksLabel') }}</span>
                <h4 class="resource-card__title">{{ t('dashboard.tester.queue.tasksTitle') }}</h4>
                <p class="resource-card__description">
                  {{ t('dashboard.tester.queue.tasksDescription') }}
                </p>
                <div
                  v-if="testerAssignedTasks.length === 0 && testerInProgressTasks.length === 0"
                  class="resource-state"
                >
                  <p class="resource-state__description">
                    {{ t('dashboard.tester.queue.tasksEmpty') }}
                  </p>
                </div>
                <div v-else class="dashboard-card-list">
                  <article
                    v-for="task in [...testerAssignedTasks, ...testerInProgressTasks]"
                    :key="task.id"
                    class="dashboard-card-list__item"
                  >
                    <strong>{{ task.title }}</strong>
                    <span>{{ t('dashboard.tester.queue.taskCampaignHint', { campaignId: task.campaign_id }) }}</span>
                    <div class="dashboard-card-list__meta">
                      <span class="resource-card__chip">
                        {{ formatTaskStatusLabel(task.status, locale) }}
                      </span>
                      <span
                        v-if="task.resolution_context"
                        class="resource-card__chip"
                      >
                        {{ formatTaskResolutionOutcomeLabel(task.resolution_context.resolution_outcome, locale) }}
                      </span>
                    </div>
                  </article>
                </div>
                <div class="resource-state__actions">
                  <NuxtLink class="resource-action" to="/my/tasks">
                    {{ t('dashboard.tester.queue.openTasks') }}
                  </NuxtLink>
                </div>
              </article>

              <article class="resource-card" data-testid="dashboard-tester-queue-eligible">
                <span class="shell-link-label">{{ t('dashboard.tester.queue.eligibleLabel') }}</span>
                <h4 class="resource-card__title">{{ t('dashboard.tester.queue.eligibleTitle') }}</h4>
                <p class="resource-card__description">
                  {{ t('dashboard.tester.queue.eligibleDescription') }}
                </p>
                <div
                  v-if="testerEligibleCampaigns.length === 0"
                  class="resource-state"
                >
                  <p class="resource-state__description">
                    {{ t('dashboard.tester.queue.eligibleEmpty') }}
                  </p>
                </div>
                <div v-else class="dashboard-card-list">
                  <article
                    v-for="campaign in testerEligibleCampaigns"
                    :key="campaign.id"
                    class="dashboard-card-list__item"
                  >
                    <strong>{{ campaign.name }}</strong>
                    <span>{{ campaign.qualification_summary || t('dashboard.tester.queue.eligibleFallback') }}</span>
                    <div class="dashboard-card-list__meta">
                      <span
                        v-for="platform in campaign.target_platforms"
                        :key="platform"
                        class="resource-card__chip"
                      >
                        {{ formatPlatformLabel(platform, locale) }}
                      </span>
                    </div>
                  </article>
                </div>
                <div class="resource-state__actions">
                  <NuxtLink class="resource-action" to="/my/eligible-campaigns">
                    {{ t('dashboard.tester.queue.openEligible') }}
                  </NuxtLink>
                </div>
              </article>

              <article class="resource-card" data-testid="dashboard-tester-queue-participation">
                <span class="shell-link-label">{{ t('dashboard.tester.queue.participationLabel') }}</span>
                <h4 class="resource-card__title">{{ t('dashboard.tester.queue.participationTitle') }}</h4>
                <p class="resource-card__description">
                  {{ t('dashboard.tester.queue.participationDescription') }}
                </p>
                <div
                  v-if="testerRecentParticipationRequests.length === 0"
                  class="resource-state"
                >
                  <p class="resource-state__description">
                    {{ t('dashboard.tester.queue.participationEmpty') }}
                  </p>
                </div>
                <div v-else class="dashboard-card-list">
                  <article
                    v-for="request in testerRecentParticipationRequests"
                    :key="request.id"
                    class="dashboard-card-list__item"
                  >
                    <strong>{{ request.campaign_name }}</strong>
                    <span>{{ request.device_profile_name }}</span>
                    <div class="dashboard-card-list__meta">
                      <span class="resource-card__chip">
                        {{ formatParticipationRequestStatusLabel(request.status, locale) }}
                      </span>
                      <span class="resource-card__chip">
                        {{ formatParticipationAssignmentStatusLabel(request.assignment_status, locale) }}
                      </span>
                    </div>
                  </article>
                </div>
                <div class="resource-state__actions">
                  <NuxtLink class="resource-action" to="/my/participation-requests">
                    {{ t('dashboard.tester.queue.openParticipation') }}
                  </NuxtLink>
                </div>
              </article>
            </div>
          </section>
        </section>
      </template>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  useAuthSession,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  formatAccountRoleLabel,
  formatAccountRolesLabel,
  type AccountRole
} from '~/features/accounts/types'
import {
  useActiveWorkspaceRolePersistence,
  useWorkspaceRoleOptions
} from '~/features/accounts/workspace-role'
import {
  type AppLocale,
  setAppLocale,
  useAppI18n,
  useAppLocaleOptions,
  useAppLocalePersistence
} from '~/features/i18n/use-app-i18n'
import { useThemeMode, useThemePersistence } from '~/features/ui/theme'

useCurrentActorPersistence()
useThemePersistence()
useAppLocalePersistence()

const route = useRoute()
const themeMode = useThemeMode()
const { locale, t } = useAppI18n()
const localeOptions = useAppLocaleOptions()
const mobileNavigationOpen = ref(false)
const selectedLocale = ref(locale.value)
const authSession = useAuthSession()
const sessionAccount = computed(() => authSession.value?.account ?? null)
const workspaceRoleOptions = useWorkspaceRoleOptions(sessionAccount)
const activeWorkspaceRole = useActiveWorkspaceRolePersistence(sessionAccount)
const showWorkspaceRoleSwitch = computed(() => workspaceRoleOptions.value.length > 1)
const activeWorkspaceRoleLabel = computed(() =>
  activeWorkspaceRole.value
    ? formatAccountRoleLabel(activeWorkspaceRole.value, locale.value)
    : t('shell.workspace.statusPending')
)

type NavigationItem = {
  label: string
  description: string
  to: string
  icon: string
  testId: string
}

type NavigationGroup = {
  title: string
  items: NavigationItem[]
}

const navigationGroups = computed<NavigationGroup[]>(() => {
  locale.value

  return [
    {
      title: t('shell.nav.overview'),
      items: [
        {
          label: t('shell.nav.dashboard'),
          description: t('shell.page.overviewDescription'),
          to: '/dashboard',
          icon: '總覽',
          testId: 'nav-dashboard'
        }
      ]
    },
    {
      title: t('shell.nav.myWorkspace'),
      items: [
        {
          label: t('shell.nav.myProjects'),
          description: t('shell.page.workspaceDescription'),
          to: '/my/projects',
          icon: '專案',
          testId: 'nav-my-projects'
        },
        {
          label: t('shell.nav.myCampaigns'),
          description: t('shell.page.workspaceDescription'),
          to: '/my/campaigns',
          icon: '活動',
          testId: 'nav-my-campaigns'
        },
        {
          label: t('shell.nav.eligibleCampaigns'),
          description: t('shell.page.workspaceDescription'),
          to: '/my/eligible-campaigns',
          icon: '資格',
          testId: 'nav-my-eligible-campaigns'
        },
        {
          label: t('shell.nav.myParticipationRequests'),
          description: t('shell.page.workspaceDescription'),
          to: '/my/participation-requests',
          icon: '參與',
          testId: 'nav-my-participation-requests'
        },
        {
          label: t('shell.nav.myTasks'),
          description: t('shell.page.workspaceDescription'),
          to: '/my/tasks',
          icon: '任務',
          testId: 'nav-my-tasks'
        }
      ]
    },
    {
      title: t('shell.nav.operations'),
      items: [
        {
          label: t('shell.nav.reviewFeedback'),
          description: t('shell.page.operationsDescription'),
          to: '/review/feedback',
          icon: '回饋',
          testId: 'nav-review-feedback'
        },
        {
          label: t('shell.nav.reviewParticipationRequests'),
          description: t('shell.page.operationsDescription'),
          to: '/review/participation-requests',
          icon: '審查',
          testId: 'nav-review-participation-requests'
        }
      ]
    },
    {
      title: t('shell.nav.resources'),
      items: [
        {
          label: t('shell.nav.projects'),
          description: t('shell.page.resourcesDescription'),
          to: '/projects',
          icon: '專案',
          testId: 'nav-projects'
        },
        {
          label: t('shell.nav.campaigns'),
          description: t('shell.page.resourcesDescription'),
          to: '/campaigns',
          icon: '活動',
          testId: 'nav-campaigns'
        },
        {
          label: t('shell.nav.deviceProfiles'),
          description: t('shell.page.resourcesDescription'),
          to: '/device-profiles',
          icon: '裝置',
          testId: 'nav-device-profiles'
        },
        {
          label: t('shell.nav.tasks'),
          description: t('shell.page.resourcesDescription'),
          to: '/tasks',
          icon: '任務',
          testId: 'nav-tasks'
        },
        {
          label: t('shell.nav.accounts'),
          description: t('shell.page.resourcesDescription'),
          to: '/accounts',
          icon: '帳號',
          testId: 'nav-accounts'
        }
      ]
    }
  ]
})

const matchedNavigation = computed(() => {
  const matchedItem = navigationGroups.value
    .flatMap((group) => group.items.map((item) => ({ group, item })))
    .find(({ item }) => route.path === item.to || route.path.startsWith(`${item.to}/`))

  return matchedItem ?? null
})

const pageTitle = computed(() => {
  if (route.path === '/dashboard') {
    return t('dashboard.title')
  }

  return matchedNavigation.value?.item.label ?? 'beta-feedback-platform'
})

const pageEyebrow = computed(() => {
  if (route.path === '/dashboard') {
    return t('shell.nav.overview')
  }

  return matchedNavigation.value?.group.title ?? t('shell.page.productWorkspace')
})

const pageDescription = computed(() => {
  if (route.path === '/dashboard') {
    return t('shell.page.overviewDescription')
  }

  return matchedNavigation.value?.item.description ?? t('shell.page.productWorkspace')
})

watch(
  locale,
  (nextLocale) => {
    if (selectedLocale.value !== nextLocale) {
      selectedLocale.value = nextLocale
    }
  },
  {
    flush: 'sync'
  }
)

watch(
  () => route.fullPath,
  () => {
    mobileNavigationOpen.value = false
  }
)

function handleLocaleChange(nextLocale: AppLocale): void {
  selectedLocale.value = nextLocale

  if (nextLocale !== locale.value) {
    setAppLocale(nextLocale, locale)
  }
}

function toggleTheme(): void {
  themeMode.value = themeMode.value === 'light' ? 'dark' : 'light'
}

function toggleMobileNavigation(): void {
  mobileNavigationOpen.value = !mobileNavigationOpen.value
}

function setActiveWorkspaceRole(role: AccountRole): void {
  if (!workspaceRoleOptions.value.includes(role)) {
    return
  }

  activeWorkspaceRole.value = role
}

useHead(() => ({
  titleTemplate: (titleChunk) =>
    titleChunk ? `${titleChunk} | beta-feedback-platform` : 'beta-feedback-platform',
  htmlAttrs: {
    lang: locale.value,
    'data-theme': themeMode.value
  },
  link: [
    {
      rel: 'preconnect',
      href: 'https://fonts.googleapis.com'
    },
    {
      rel: 'preconnect',
      href: 'https://fonts.gstatic.com',
      crossorigin: ''
    },
    {
      rel: 'stylesheet',
      href:
        'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Sora:wght@500;600;700;800&display=swap'
    }
  ]
}))
</script>

<template>
  <div
    class="app-frame"
    :class="{ 'app-frame--navigation-open': mobileNavigationOpen }"
    data-testid="app-shell-root"
  >
    <div
      v-if="mobileNavigationOpen"
      class="app-drawer-backdrop"
      @click="mobileNavigationOpen = false"
    />

    <aside
      class="app-navigation"
      :class="{ 'app-navigation--open': mobileNavigationOpen }"
      data-testid="app-shell-navigation"
    >
      <div class="app-navigation__surface">
        <NuxtLink class="app-brand app-brand--nav" to="/dashboard">
          <span class="app-brand__icon" aria-hidden="true">
            <img
              class="app-brand__icon-image"
              :src="'/brand/header-brand-icon.webp'"
              alt=""
              data-testid="app-shell-brand-icon"
            >
          </span>
          <span class="app-brand__copy">
            <span class="app-brand__title">beta-feedback-platform</span>
          </span>
        </NuxtLink>

        <section class="app-navigation__context" data-testid="app-shell-context">
          <span class="app-navigation__context-eyebrow">{{ t('shell.workspace.title') }}</span>
          <strong class="app-navigation__context-title">
            {{ sessionAccount?.display_name || t('shell.workspace.noSession') }}
          </strong>
          <p class="app-navigation__context-description">
            {{ t('shell.workspace.description') }}
          </p>
          <div class="app-navigation__context-meta">
            <span class="resource-card__chip">
              {{ t('shell.workspace.roleLabel') }}
              {{
                sessionAccount
                  ? formatAccountRolesLabel(sessionAccount, locale)
                  : t('shell.workspace.statusPending')
              }}
            </span>
            <span class="resource-card__chip">
              {{ sessionAccount ? t('shell.workspace.statusReady') : t('shell.workspace.statusPending') }}
            </span>
          </div>
          <section
            v-if="sessionAccount"
            class="app-workspace-role"
            data-testid="active-workspace-role-panel"
          >
            <span class="app-workspace-role__label">
              {{ t('shell.workspace.activeRoleLabel') }}
            </span>
            <div
              v-if="showWorkspaceRoleSwitch"
              class="app-workspace-role__switch"
              role="group"
              :aria-label="t('shell.workspace.switchAria')"
              data-testid="active-workspace-role-switch"
            >
              <button
                v-for="role in workspaceRoleOptions"
                :key="role"
                class="app-workspace-role__option"
                :class="{
                  'app-workspace-role__option--active': activeWorkspaceRole === role
                }"
                type="button"
                :aria-pressed="activeWorkspaceRole === role"
                :data-testid="`active-workspace-role-option-${role}`"
                @click="setActiveWorkspaceRole(role)"
              >
                {{ formatAccountRoleLabel(role, locale) }}
              </button>
            </div>
            <span
              v-else
              class="resource-card__chip"
              data-testid="active-workspace-role-single"
            >
              {{ activeWorkspaceRoleLabel }}
            </span>
            <p class="app-workspace-role__hint">
              {{
                showWorkspaceRoleSwitch
                  ? t('shell.workspace.switchHint')
                  : t('shell.workspace.singleHint')
              }}
            </p>
          </section>
        </section>

        <nav class="app-navigation__groups" :aria-label="t('shell.actions.navigation')">
          <section
            v-for="group in navigationGroups"
            :key="group.title"
            class="app-navigation__group"
          >
            <h2 class="app-navigation__group-title">{{ group.title }}</h2>
            <NuxtLink
              v-for="item in group.items"
              :key="item.to"
              class="app-navigation__link"
              :class="{
                'app-navigation__link--active':
                  route.path === item.to || route.path.startsWith(`${item.to}/`)
              }"
              :to="item.to"
              :data-testid="item.testId"
            >
              <span class="app-navigation__icon">{{ item.icon }}</span>
              <span class="app-navigation__link-copy">
                <span class="app-navigation__link-label">{{ item.label }}</span>
                <span class="app-navigation__link-description">{{ item.description }}</span>
              </span>
            </NuxtLink>
          </section>
        </nav>
      </div>

      <div class="app-navigation__footer">
        <NuxtLink
          class="app-navigation__footer-link"
          to="/"
          data-testid="nav-public-home"
        >
          {{ t('shell.workspace.publicHome') }}
        </NuxtLink>
      </div>
    </aside>

    <div class="app-main-frame">
      <header class="app-topbar" data-testid="app-shell-topbar">
        <div class="app-topbar__intro">
          <button
            class="app-topbar__menu"
            type="button"
            data-testid="app-mobile-nav-toggle"
            @click="toggleMobileNavigation"
          >
            {{ t('shell.actions.navigation') }}
          </button>
          <div class="app-topbar__copy">
            <span class="app-topbar__eyebrow">{{ pageEyebrow }}</span>
            <div class="app-topbar__headline">
              <NuxtLink class="app-topbar__title" to="/dashboard">{{ pageTitle }}</NuxtLink>
              <span
                v-if="sessionAccount"
                class="resource-card__chip app-topbar__session-chip"
              >
                {{ formatAccountRolesLabel(sessionAccount, locale) }}
              </span>
              <span
                v-if="sessionAccount && activeWorkspaceRole"
                class="resource-card__chip app-topbar__session-chip"
                data-testid="active-workspace-role-chip"
              >
                {{ t('shell.workspace.activeRoleLabel') }} {{ activeWorkspaceRoleLabel }}
              </span>
            </div>
            <p class="app-topbar__description">{{ pageDescription }}</p>
          </div>
        </div>

        <div class="app-topbar__actions">
          <div class="app-topbar__controls">
            <label class="app-topbar__locale">
              <span class="app-topbar__locale-label">{{ t('shell.locale.label') }}</span>
              <select
                v-model="selectedLocale"
                class="resource-select"
                data-testid="locale-select"
                @change="handleLocaleChange(($event.target as HTMLSelectElement).value as AppLocale)"
              >
                <option
                  v-for="option in localeOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.label }}
                </option>
              </select>
            </label>
            <button
              class="resource-action resource-action--quiet"
              type="button"
              data-testid="theme-toggle"
              @click="toggleTheme"
            >
              {{ themeMode === 'light' ? t('shell.actions.switchToDark') : t('shell.actions.switchToLight') }}
            </button>
          </div>
          <div class="app-topbar__context">
            <CurrentActorSelector
              variant="compact"
              :title="t('shell.actor.title')"
              :description="t('shell.actor.description')"
            />
          </div>
        </div>
      </header>

      <main class="app-main-content">
        <div class="app-page-frame">
          <div
            class="app-content-slot"
            :key="locale"
            :data-theme-mode="themeMode"
            data-testid="app-content-slot"
          >
            <slot />
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

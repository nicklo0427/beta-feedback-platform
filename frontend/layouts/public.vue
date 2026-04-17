<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  useAuthSession,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  type AppLocale,
  setAppLocale,
  useAppI18n,
  useAppLocaleOptions,
  useAppLocalePersistence
} from '~/features/i18n/use-app-i18n'
import { useThemeMode, useThemePersistence } from '~/features/ui/theme'

useThemePersistence()
useAppLocalePersistence()
useCurrentActorPersistence()

const route = useRoute()
const themeMode = useThemeMode()
const { locale, t } = useAppI18n()
const localeOptions = useAppLocaleOptions()
const selectedLocale = ref(locale.value)
const authSession = useAuthSession()

const isLoginRoute = computed(() => route.path === '/login')
const isRegisterRoute = computed(() => route.path === '/register')
const isAuthenticated = computed(() => authSession.value !== null)

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

function handleLocaleChange(nextLocale: AppLocale): void {
  selectedLocale.value = nextLocale

  if (nextLocale !== locale.value) {
    setAppLocale(nextLocale, locale)
  }
}

function toggleTheme(): void {
  themeMode.value = themeMode.value === 'light' ? 'dark' : 'light'
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
  <div class="public-frame" data-testid="public-shell-root">
    <header class="public-topbar" data-testid="public-shell-header">
      <NuxtLink class="app-brand app-brand--public" to="/">
        <span class="app-brand__eyebrow">{{ t('shell.brand.eyebrow') }}</span>
        <span class="app-brand__title">beta-feedback-platform</span>
        <span class="app-brand__description">{{ t('shell.brand.description') }}</span>
      </NuxtLink>

      <div class="public-topbar__actions">
        <label class="public-topbar__locale">
          <span class="public-topbar__locale-label">{{ t('shell.locale.label') }}</span>
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
        <div
          v-if="isAuthenticated"
          class="public-topbar__cta"
          data-testid="public-shell-session-actions"
        >
          <span class="resource-shell__meta-chip" data-testid="public-shell-session-state">
            {{ t('common.signedIn') }}
          </span>
          <NuxtLink
            class="resource-action"
            data-testid="public-shell-dashboard-link"
            to="/dashboard"
          >
            {{ t('common.openDashboard') }}
          </NuxtLink>
        </div>
        <div v-else class="public-topbar__cta" data-testid="public-shell-auth-actions">
          <NuxtLink
            class="resource-action"
            :class="{ 'resource-action--quiet': isLoginRoute }"
            data-testid="public-shell-login-link"
            to="/login"
          >
            {{ t('common.login') }}
          </NuxtLink>
          <NuxtLink
            class="resource-action"
            :class="{ 'resource-action--quiet': isRegisterRoute }"
            data-testid="public-shell-register-link"
            to="/register"
          >
            {{ t('common.register') }}
          </NuxtLink>
        </div>
      </div>
    </header>

    <main class="app-main-content public-main-content">
      <div
        class="app-content-slot"
        :key="locale"
        :data-theme-mode="themeMode"
        data-testid="public-content-slot"
      >
        <slot />
      </div>
    </main>
  </div>
</template>

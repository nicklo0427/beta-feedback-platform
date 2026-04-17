<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { logoutCurrentSession } from '~/features/auth/api'
import { fetchAccounts } from '~/features/accounts/api'
import {
  clearAuthenticatedSession,
  getActorAwareMutationErrorMessage,
  useAuthRuntimeMode,
  useAuthSession,
  useAuthSessionPending,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { formatAccountRoleLabel } from '~/features/accounts/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    variant?: 'panel' | 'compact'
  }>(),
  {
    variant: 'panel'
  }
)

useCurrentActorPersistence()

const router = useRouter()
const { locale, t } = useAppI18n()
const currentActorId = useCurrentActorId()
const authRuntimeMode = useAuthRuntimeMode()
const authSession = useAuthSession()
const authSessionPending = useAuthSessionPending()
const logoutPending = ref(false)
const logoutError = ref<string | null>(null)
const sessionOnlyMode = computed(() => authRuntimeMode.value === 'session_only')
const compactVariant = computed(() => props.variant === 'compact')

const {
  data: accountResponse,
  pending,
  error,
  refresh
} = useAsyncData('current-actor-accounts', async () => {
  if (sessionOnlyMode.value) {
    return {
      items: [],
      total: 0
    }
  }

  return fetchAccounts()
}, {
  server: false,
  default: () => ({
    items: [],
    total: 0
  })
})

const accounts = computed(() => accountResponse.value.items)
const selectedActorId = computed({
  get: () => currentActorId.value ?? '',
  set: (value: string) => {
    currentActorId.value = value || null
  }
})
const selectedAccount = computed(
  () => accounts.value.find((account) => account.id === currentActorId.value) ?? null
)
const sessionAccount = computed(() => authSession.value?.account ?? null)
const isAuthenticated = computed(() => sessionAccount.value !== null)
const resolvedTitle = computed(() => props.title ?? t('actor.defaultTitle'))
const resolvedDescription = computed(() =>
  props.description ?? t('actor.defaultDescription')
)
const compactLabel = computed(() => {
  if (isAuthenticated.value && sessionAccount.value) {
    return `${sessionAccount.value.display_name} · ${formatAccountRoleLabel(sessionAccount.value.role, locale.value)}`
  }

  if (selectedAccount.value) {
    return `${selectedAccount.value.display_name} · ${formatAccountRoleLabel(selectedAccount.value.role, locale.value)}`
  }

  return sessionOnlyMode.value
    ? t('actor.compact.notSignedIn')
    : t('actor.compact.noActorSelected')
})

watch(
  accounts,
  (nextAccounts) => {
    if (!currentActorId.value || isAuthenticated.value) {
      return
    }

    const actorStillExists = nextAccounts.some(
      (account) => account.id === currentActorId.value
    )

    if (!actorStillExists) {
      currentActorId.value = null
    }
  },
  {
    immediate: true
  }
)

async function handleLogout(): Promise<void> {
  logoutPending.value = true
  logoutError.value = null

  try {
    await logoutCurrentSession()
    clearAuthenticatedSession()
    await router.push('/login')
  } catch (error) {
    logoutError.value = getActorAwareMutationErrorMessage(
      error,
      locale.value === 'en' ? 'Unable to sign out right now.' : '目前無法登出。'
    )
  } finally {
    logoutPending.value = false
  }
}
</script>

<template>
  <section
    v-if="compactVariant"
    class="actor-compact"
    data-testid="current-actor-compact"
  >
    <div class="actor-compact__summary">
      <span class="actor-compact__eyebrow">{{ t('actor.compact.eyebrow') }}</span>
      <span
        v-if="authSessionPending"
        class="actor-compact__value"
        data-testid="current-actor-compact-loading"
      >
        {{ t('actor.compact.loading') }}
      </span>
      <span
        v-else
        class="actor-compact__value"
        data-testid="current-actor-compact-label"
      >
        {{ compactLabel }}
      </span>
    </div>

    <div
      v-if="logoutError"
      class="resource-form__error"
      data-testid="current-session-logout-error"
    >
      {{ logoutError }}
    </div>

    <template v-if="isAuthenticated && sessionAccount">
      <div class="actor-compact__actions">
        <NuxtLink
          class="resource-action resource-action--quiet"
          data-testid="current-session-account-link"
          :to="`/accounts/${sessionAccount.id}`"
        >
          {{ t('actor.compact.myAccount') }}
        </NuxtLink>
        <button
          class="resource-action resource-action--quiet"
          data-testid="current-session-logout"
          type="button"
          :disabled="logoutPending"
          @click="handleLogout"
        >
          {{ logoutPending ? t('actor.compact.loggingOut') : t('actor.compact.logout') }}
        </button>
      </div>
    </template>

    <template v-else-if="sessionOnlyMode">
      <div class="actor-compact__actions">
        <NuxtLink
          class="resource-action resource-action--quiet"
          data-testid="current-actor-compact-login"
          to="/login"
        >
          {{ t('common.login') }}
        </NuxtLink>
        <NuxtLink
          class="resource-action resource-action--quiet"
          data-testid="current-actor-compact-register"
          to="/register"
        >
          {{ t('common.register') }}
        </NuxtLink>
      </div>
    </template>

    <template v-else-if="pending">
      <span class="actor-compact__hint">{{ t('actor.compact.loadingAccounts') }}</span>
    </template>

    <template v-else-if="error">
      <div class="actor-compact__actions">
        <span class="actor-compact__hint">{{ t('actor.compact.unavailable') }}</span>
        <button class="resource-action resource-action--quiet" type="button" @click="refresh()">
          {{ t('common.retry') }}
        </button>
      </div>
    </template>

    <template v-else-if="accounts.length === 0">
      <div class="actor-compact__actions">
        <NuxtLink class="resource-action resource-action--quiet" to="/register">
          {{ t('common.createAccount') }}
        </NuxtLink>
      </div>
    </template>

    <template v-else>
      <label class="actor-compact__select-wrap">
        <span class="actor-compact__hint">{{ t('actor.compact.fallbackActor') }}</span>
        <select
          v-model="selectedActorId"
          class="resource-select"
          data-testid="current-actor-select"
          :aria-label="t('actor.compact.selectAria')"
          name="current_actor_id"
        >
          <option value="">{{ t('actor.compact.placeholder') }}</option>
          <option
            v-for="account in accounts"
            :key="account.id"
            :value="account.id"
          >
            {{ account.display_name }} · {{ formatAccountRoleLabel(account.role, locale) }}
          </option>
        </select>
      </label>
    </template>
  </section>

  <section
    v-else
    class="resource-section"
    data-testid="current-actor-panel"
  >
    <h2 class="resource-section__title">{{ resolvedTitle }}</h2>
    <p class="resource-state__description">
      {{ resolvedDescription }}
    </p>

    <div
      v-if="authSessionPending"
      class="resource-state"
      data-testid="current-session-loading"
    >
      <h3 class="resource-state__title">{{ t('actor.panel.loadingTitle') }}</h3>
      <p class="resource-state__description">
        {{ t('actor.panel.loadingDescription') }}
      </p>
    </div>

    <div
      v-else-if="isAuthenticated && sessionAccount"
      class="resource-section__body"
      data-testid="current-session-ready"
    >
      <div class="resource-state__actions">
        <NuxtLink class="resource-action" data-testid="current-session-account-link" :to="`/accounts/${sessionAccount.id}`">
          {{ t('actor.panel.viewMyAccount') }}
        </NuxtLink>
        <button
          class="resource-action"
          data-testid="current-session-logout"
          type="button"
          :disabled="logoutPending"
          @click="handleLogout"
        >
          {{ logoutPending ? t('actor.compact.loggingOut') : t('actor.compact.logout') }}
        </button>
      </div>

      <div
        v-if="logoutError"
        class="resource-form__error"
        data-testid="current-session-logout-error"
      >
        {{ logoutError }}
      </div>

      <div class="resource-key-value" data-testid="current-session-summary">
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">{{ t('actor.panel.signedInAccount') }}</span>
          <span class="resource-key-value__value">
            {{ sessionAccount.display_name }}
          </span>
        </div>
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">{{ t('actor.panel.role') }}</span>
          <span class="resource-key-value__value">
            {{ formatAccountRoleLabel(sessionAccount.role, locale) }}
          </span>
        </div>
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">{{ t('actor.panel.email') }}</span>
          <span class="resource-key-value__value">
            {{ sessionAccount.email }}
          </span>
        </div>
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">{{ t('actor.panel.sessionStatus') }}</span>
          <span class="resource-key-value__value">{{ t('actor.panel.sessionReady') }}</span>
        </div>
      </div>
    </div>

    <div
      v-else-if="sessionOnlyMode"
      class="resource-state"
      data-testid="current-actor-session-only"
    >
      <h3 class="resource-state__title">{{ t('actor.panel.sessionOnlyTitle') }}</h3>
      <p class="resource-state__description">
        {{ t('actor.panel.sessionOnlyDescription') }}
      </p>
      <div class="resource-state__actions">
        <NuxtLink class="resource-action" to="/login">
          {{ t('actor.panel.goLogin') }}
        </NuxtLink>
        <NuxtLink class="resource-action" to="/register">
          {{ t('actor.panel.registerAccount') }}
        </NuxtLink>
      </div>
    </div>

    <div
      v-else-if="pending"
      class="resource-state"
      data-testid="current-actor-loading"
    >
      <h3 class="resource-state__title">{{ t('actor.panel.loadingTitleAccounts') }}</h3>
      <p class="resource-state__description">
        {{ t('actor.panel.loadingDescriptionAccounts') }}
      </p>
    </div>

    <div
      v-else-if="error"
      class="resource-state"
      data-testid="current-actor-error"
    >
      <h3 class="resource-state__title">{{ t('actor.panel.errorTitle') }}</h3>
      <p class="resource-state__description">
        {{ error.message }}
      </p>
      <div class="resource-state__actions">
        <button class="resource-action" type="button" @click="refresh()">
          {{ t('common.retry') }}
        </button>
      </div>
    </div>

    <div
      v-else-if="accounts.length === 0"
      class="resource-state"
      data-testid="current-actor-empty"
    >
      <h3 class="resource-state__title">{{ t('actor.panel.emptyTitle') }}</h3>
      <p class="resource-state__description">
        {{ t('actor.panel.emptyDescription') }}
      </p>
      <div class="resource-state__actions">
        <NuxtLink class="resource-action" to="/register">
          {{ t('actor.panel.registerAccount') }}
        </NuxtLink>
        <NuxtLink class="resource-action" to="/login">
          {{ t('actor.panel.goLogin') }}
        </NuxtLink>
      </div>
    </div>

    <div
      v-else
      class="resource-section__body"
      data-testid="current-actor-ready"
    >
      <div class="resource-state__actions">
        <NuxtLink class="resource-action" to="/register">
          {{ t('common.register') }}
        </NuxtLink>
        <NuxtLink class="resource-action" to="/login">
          {{ t('common.login') }}
        </NuxtLink>
      </div>

      <label class="resource-field">
        <span class="resource-field__label">{{ t('actor.panel.selectedAccountLabel') }}</span>
        <select
          v-model="selectedActorId"
          class="resource-select"
          data-testid="current-actor-select"
          name="current_actor_id"
        >
          <option value="">{{ t('actor.compact.placeholder') }}</option>
          <option
            v-for="account in accounts"
            :key="account.id"
            :value="account.id"
          >
            {{ account.display_name }} · {{ formatAccountRoleLabel(account.role, locale) }}
          </option>
        </select>
      </label>

      <div class="resource-key-value" data-testid="current-actor-summary">
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">{{ t('actor.panel.accountIdLabel') }}</span>
          <span class="resource-key-value__value">
            {{ selectedAccount?.id || t('actor.panel.noActorSelected') }}
          </span>
        </div>
        <div class="resource-key-value__row">
          <span class="resource-key-value__label">{{ t('actor.panel.role') }}</span>
          <span class="resource-key-value__value">
            {{
              selectedAccount
                ? formatAccountRoleLabel(selectedAccount.role, locale)
                : t('actor.panel.roleFallback')
            }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

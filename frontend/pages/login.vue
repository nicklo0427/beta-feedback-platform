<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { loginWithPassword } from '~/features/auth/api'
import type { LoginPayload } from '~/features/auth/types'
import {
  applyAuthenticatedSession,
  useAuthSession,
  useAuthSessionPending,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

definePageMeta({
  layout: 'public'
})

const router = useRouter()
useCurrentActorPersistence()
const { locale, t } = useAppI18n()

const authSession = useAuthSession()
const authSessionPending = useAuthSessionPending()
const email = ref('')
const password = ref('')
const submitting = ref(false)
const redirecting = ref(false)
const submitError = ref<string | null>(null)
const isAuthenticated = computed(() => authSession.value !== null)
const showingRedirectState = computed(
  () => authSessionPending.value || isAuthenticated.value || redirecting.value
)

watch(
  authSession,
  (session) => {
    if (!session || redirecting.value || !import.meta.client) {
      return
    }

    redirecting.value = true
    void router.replace('/dashboard')
  },
  {
    immediate: true
  }
)

async function handleSubmit(): Promise<void> {
  submitError.value = null

  const payload: LoginPayload = {
    email: email.value.trim().toLowerCase(),
    password: password.value.trim()
  }

  if (!payload.email || !payload.password) {
    submitError.value = t('auth.login.requiredError')
    return
  }

  submitting.value = true

  try {
    const session = await loginWithPassword(payload)
    redirecting.value = true
    applyAuthenticatedSession(session)
    await router.push('/dashboard')
  } catch (error) {
    submitError.value =
      error instanceof Error ? error.message : t('auth.login.unavailableError')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell" :data-locale="locale">
    <section class="auth-shell">
      <section class="auth-shell__brand">
        <span class="resource-section__eyebrow">{{ t('auth.login.brandEyebrow') }}</span>
        <h1 class="resource-shell__title">{{ t('auth.login.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('auth.login.description') }}
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action resource-action--quiet" to="/">
            {{ t('auth.shared.backHome') }}
          </NuxtLink>
        </div>
        <div class="auth-shell__stats">
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('auth.login.workflowLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('auth.login.workflowValue') }}</strong>
            <p class="home-summary-card__description">{{ t('auth.login.workflowDescription') }}</p>
          </article>
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('auth.login.dataModeLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('auth.login.dataModeValue') }}</strong>
            <p class="home-summary-card__description">{{ t('auth.login.dataModeDescription') }}</p>
          </article>
        </div>
      </section>

      <section
        v-if="showingRedirectState"
        class="auth-shell__panel"
        data-testid="login-redirecting"
      >
        <span class="resource-section__eyebrow">{{ t('auth.signedIn.eyebrow') }}</span>
        <h2 class="resource-section__title">{{ t('auth.signedIn.title') }}</h2>
        <p class="resource-section__description">
          {{ t('auth.signedIn.description') }}
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/dashboard">
            {{ t('auth.signedIn.action') }}
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="auth-shell__panel"
        data-testid="login-panel"
      >
        <span class="resource-section__eyebrow">{{ t('auth.login.panelEyebrow') }}</span>
        <h2 class="resource-section__title">{{ t('auth.login.panelTitle') }}</h2>
        <p class="resource-section__description">
          {{ t('auth.login.panelDescription') }}
        </p>

        <form class="resource-form" @submit.prevent="handleSubmit">
          <div
            v-if="submitError"
            class="resource-form__error"
            data-testid="login-error"
          >
            {{ submitError }}
          </div>

          <section class="resource-form__section">
            <div>
              <h3 class="resource-form__section-title">{{ t('auth.login.formSectionTitle') }}</h3>
              <p class="resource-form__section-description">
                {{ t('auth.login.formSectionDescription') }}
              </p>
            </div>
            <div class="resource-form__section-grid">
              <label class="resource-field">
                <span class="resource-field__label">{{ t('auth.fields.email') }}</span>
                <input
                  v-model="email"
                  class="resource-input"
                  data-testid="login-email-input"
                  type="email"
                  autocomplete="email"
                />
              </label>

              <label class="resource-field">
                <span class="resource-field__label">{{ t('auth.fields.password') }}</span>
                <input
                  v-model="password"
                  class="resource-input"
                  data-testid="login-password-input"
                  type="password"
                  autocomplete="current-password"
                />
              </label>
            </div>
          </section>

          <div class="resource-form__sticky-actions">
            <button
              class="resource-action"
              data-testid="login-submit"
              type="submit"
              :disabled="submitting"
            >
              {{ submitting ? t('auth.login.submitting') : t('auth.login.submit') }}
            </button>
            <NuxtLink class="resource-action" to="/register">
              {{ t('auth.login.goRegister') }}
            </NuxtLink>
          </div>
        </form>
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { registerWithPassword } from '~/features/auth/api'
import type { AuthRole, RegisterPayload } from '~/features/auth/types'
import {
  applyAuthenticatedSession,
  useAuthSession,
  useAuthSessionPending,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import {
  ACCOUNT_ROLE_OPTIONS,
  formatAccountRoleLabel,
  normalizeAccountRoles
} from '~/features/accounts/types'
import { useAppI18n } from '~/features/i18n/use-app-i18n'

definePageMeta({
  layout: 'public'
})

const router = useRouter()
const route = useRoute()
useCurrentActorPersistence()
const { locale, t } = useAppI18n()

const authSession = useAuthSession()
const authSessionPending = useAuthSessionPending()
const displayName = ref('')
const roles = ref<AuthRole[]>([...ACCOUNT_ROLE_OPTIONS])
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
  () => route.query.role,
  (queryRole) => {
    roles.value =
      queryRole === 'developer' || queryRole === 'tester'
        ? [queryRole]
        : [...ACCOUNT_ROLE_OPTIONS]
  },
  {
    immediate: true
  }
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

  const selectedRoles = normalizeAccountRoles({ roles: roles.value })

  const payload: RegisterPayload = {
    display_name: displayName.value.trim(),
    role: selectedRoles[0] ?? 'developer',
    roles: selectedRoles,
    email: email.value.trim().toLowerCase(),
    password: password.value.trim()
  }

  if (!payload.display_name || !payload.email || !payload.password) {
    submitError.value = t('auth.register.requiredError')
    return
  }

  if (payload.roles.length === 0) {
    submitError.value = t('auth.register.roleRequiredError')
    return
  }

  submitting.value = true

  try {
    const session = await registerWithPassword(payload)
    redirecting.value = true
    applyAuthenticatedSession(session)
    await router.push('/dashboard')
  } catch (error) {
    submitError.value =
      error instanceof Error ? error.message : t('auth.register.unavailableError')
  } finally {
    submitting.value = false
  }
}

function roleIsSelected(role: AuthRole): boolean {
  return roles.value.includes(role)
}

function toggleRole(role: AuthRole): void {
  if (submitting.value) {
    return
  }

  if (roleIsSelected(role)) {
    roles.value = roles.value.filter((selectedRole) => selectedRole !== role)
    return
  }

  roles.value = normalizeAccountRoles({
    roles: [...roles.value, role]
  })
}
</script>

<template>
  <main class="app-shell" :data-locale="locale">
    <section class="auth-shell">
      <section class="auth-shell__brand">
        <span class="resource-section__eyebrow">{{ t('auth.register.brandEyebrow') }}</span>
        <h1 class="resource-shell__title">{{ t('auth.register.title') }}</h1>
        <p class="resource-shell__description">
          {{ t('auth.register.description') }}
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action resource-action--quiet" to="/">
            {{ t('auth.shared.backHome') }}
          </NuxtLink>
        </div>
        <div class="auth-shell__stats">
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('auth.register.developerLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('auth.register.developerValue') }}</strong>
            <p class="home-summary-card__description">{{ t('auth.register.developerDescription') }}</p>
          </article>
          <article class="summary-stat-card">
            <span class="summary-stat-card__label">{{ t('auth.register.testerLabel') }}</span>
            <strong class="summary-stat-card__value">{{ t('auth.register.testerValue') }}</strong>
            <p class="home-summary-card__description">{{ t('auth.register.testerDescription') }}</p>
          </article>
        </div>
      </section>

      <section
        v-if="showingRedirectState"
        class="auth-shell__panel"
        data-testid="register-redirecting"
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
        data-testid="register-panel"
      >
        <span class="resource-section__eyebrow">{{ t('auth.register.panelEyebrow') }}</span>
        <h2 class="resource-section__title">{{ t('auth.register.panelTitle') }}</h2>
        <p class="resource-section__description">
          {{ t('auth.register.panelDescription') }}
        </p>

        <form class="resource-form" @submit.prevent="handleSubmit">
          <div
            v-if="submitError"
            class="resource-form__error"
            data-testid="register-error"
          >
            {{ submitError }}
          </div>

          <section class="resource-form__section">
            <div>
              <h3 class="resource-form__section-title">{{ t('auth.register.profileSectionTitle') }}</h3>
              <p class="resource-form__section-description">
                {{ t('auth.register.profileSectionDescription') }}
              </p>
            </div>
            <div class="resource-form__section-grid">
              <label class="resource-field">
                <span class="resource-field__label">{{ t('auth.fields.displayName') }}</span>
                <input
                  v-model="displayName"
                  class="resource-input"
                  data-testid="register-display-name-input"
                  type="text"
                  autocomplete="name"
                />
              </label>

              <fieldset class="resource-field">
                <legend class="resource-field__label">{{ t('auth.fields.role') }}</legend>
                <div
                  class="resource-choice-grid"
                  data-testid="register-role-options"
                >
                  <label
                    v-for="roleOption in ACCOUNT_ROLE_OPTIONS"
                    :key="roleOption"
                    class="resource-choice-card"
                  >
                    <input
                      :checked="roleIsSelected(roleOption)"
                      :disabled="submitting"
                      :data-testid="`register-role-checkbox-${roleOption}`"
                      :name="`roles_${roleOption}`"
                      type="checkbox"
                      @change="toggleRole(roleOption)"
                    >
                    <span class="resource-choice-card__content">
                      <span class="resource-choice-card__label">
                        {{ formatAccountRoleLabel(roleOption, locale) }}
                      </span>
                      <span class="resource-choice-card__hint">
                        {{
                          roleOption === 'developer'
                            ? t('auth.register.developerDescription')
                            : t('auth.register.testerDescription')
                        }}
                      </span>
                    </span>
                  </label>
                </div>
              </fieldset>
            </div>
          </section>

          <section class="resource-form__section">
            <div>
              <h3 class="resource-form__section-title">{{ t('auth.register.authSectionTitle') }}</h3>
              <p class="resource-form__section-description">
                {{ t('auth.register.authSectionDescription') }}
              </p>
            </div>
            <div class="resource-form__section-grid">
              <label class="resource-field">
                <span class="resource-field__label">{{ t('auth.fields.email') }}</span>
                <input
                  v-model="email"
                  class="resource-input"
                  data-testid="register-email-input"
                  type="email"
                  autocomplete="email"
                />
              </label>

              <label class="resource-field">
                <span class="resource-field__label">{{ t('auth.fields.password') }}</span>
                <input
                  v-model="password"
                  class="resource-input"
                  data-testid="register-password-input"
                  type="password"
                  autocomplete="new-password"
                />
              </label>
            </div>
          </section>

          <div class="resource-form__sticky-actions">
            <button
              class="resource-action"
              data-testid="register-submit"
              type="submit"
              :disabled="submitting"
            >
              {{ submitting ? t('auth.register.submitting') : t('auth.register.submit') }}
            </button>
            <NuxtLink class="resource-action" to="/login">
              {{ t('auth.register.goLogin') }}
            </NuxtLink>
          </div>
        </form>
      </section>
    </section>
  </main>
</template>

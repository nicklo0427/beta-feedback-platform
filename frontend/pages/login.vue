<script setup lang="ts">
import { computed, ref } from 'vue'

import { loginWithPassword } from '~/features/auth/api'
import type { LoginPayload } from '~/features/auth/types'
import {
  applyAuthenticatedSession,
  useAuthSession,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'

const router = useRouter()
useCurrentActorPersistence()

const authSession = useAuthSession()
const email = ref('')
const password = ref('')
const submitting = ref(false)
const submitError = ref<string | null>(null)
const isAuthenticated = computed(() => authSession.value !== null)

async function handleSubmit(): Promise<void> {
  submitError.value = null

  const payload: LoginPayload = {
    email: email.value.trim().toLowerCase(),
    password: password.value.trim()
  }

  if (!payload.email || !payload.password) {
    submitError.value = 'Email 和密碼都為必填。'
    return
  }

  submitting.value = true

  try {
    const session = await loginWithPassword(payload)
    applyAuthenticatedSession(session)
    await router.push('/')
  } catch (error) {
    submitError.value = error instanceof Error ? error.message : '目前無法登入。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/">首頁</NuxtLink>
        <h1 class="resource-shell__title">登入</h1>
        <p class="resource-shell__description">
          使用最小 session/auth baseline 登入，之後 role-aware workflow 會直接依你的 session 推導目前 actor。
        </p>
      </header>

      <section
        v-if="isAuthenticated"
        class="resource-state"
        data-testid="login-authenticated"
      >
        <h2 class="resource-state__title">目前已登入</h2>
        <p class="resource-state__description">
          你已經有可用的 session，可直接返回首頁繼續操作。
        </p>
        <div class="resource-state__actions">
          <NuxtLink class="resource-action" to="/">返回首頁</NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="login-panel"
      >
        <h2 class="resource-section__title">登入帳號</h2>

        <div
          v-if="submitError"
          class="resource-form__error"
          data-testid="login-error"
        >
          {{ submitError }}
        </div>

        <div class="resource-form__grid">
          <label class="resource-field">
            <span class="resource-field__label">Email</span>
            <input
              v-model="email"
              class="resource-input"
              data-testid="login-email-input"
              type="email"
              autocomplete="email"
            />
          </label>

          <label class="resource-field">
            <span class="resource-field__label">密碼</span>
            <input
              v-model="password"
              class="resource-input"
              data-testid="login-password-input"
              type="password"
              autocomplete="current-password"
            />
          </label>
        </div>

        <div class="resource-state__actions">
          <button
            class="resource-action"
            data-testid="login-submit"
            type="button"
            :disabled="submitting"
            @click="handleSubmit"
          >
            {{ submitting ? '登入中...' : '登入' }}
          </button>
          <NuxtLink class="resource-action" to="/register">
            前往註冊
          </NuxtLink>
        </div>
      </section>
    </section>
  </main>
</template>

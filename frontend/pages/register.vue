<script setup lang="ts">
import { computed, ref } from 'vue'

import { registerWithPassword } from '~/features/auth/api'
import type { AuthRole, RegisterPayload } from '~/features/auth/types'
import {
  applyAuthenticatedSession,
  useAuthSession,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'

const router = useRouter()
useCurrentActorPersistence()

const authSession = useAuthSession()
const displayName = ref('')
const role = ref<AuthRole>('developer')
const email = ref('')
const password = ref('')
const submitting = ref(false)
const submitError = ref<string | null>(null)
const isAuthenticated = computed(() => authSession.value !== null)

async function handleSubmit(): Promise<void> {
  submitError.value = null

  const payload: RegisterPayload = {
    display_name: displayName.value.trim(),
    role: role.value,
    email: email.value.trim().toLowerCase(),
    password: password.value.trim()
  }

  if (!payload.display_name || !payload.email || !payload.password) {
    submitError.value = '顯示名稱、Email 和密碼都為必填。'
    return
  }

  submitting.value = true

  try {
    const session = await registerWithPassword(payload)
    applyAuthenticatedSession(session)
    await router.push('/')
  } catch (error) {
    submitError.value = error instanceof Error ? error.message : '目前無法註冊。'
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
        <h1 class="resource-shell__title">註冊</h1>
        <p class="resource-shell__description">
          建立 public beta 可用的最小登入帳號。註冊完成後會直接建立 session 並登入。
        </p>
      </header>

      <section
        v-if="isAuthenticated"
        class="resource-state"
        data-testid="register-authenticated"
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
        data-testid="register-panel"
      >
        <h2 class="resource-section__title">建立帳號</h2>

        <div
          v-if="submitError"
          class="resource-form__error"
          data-testid="register-error"
        >
          {{ submitError }}
        </div>

        <div class="resource-form__grid">
          <label class="resource-field">
            <span class="resource-field__label">顯示名稱</span>
            <input
              v-model="displayName"
              class="resource-input"
              data-testid="register-display-name-input"
              type="text"
              autocomplete="name"
            />
          </label>

          <label class="resource-field">
            <span class="resource-field__label">角色</span>
            <select
              v-model="role"
              class="resource-select"
              data-testid="register-role-select"
            >
              <option value="developer">開發者</option>
              <option value="tester">測試者</option>
            </select>
          </label>

          <label class="resource-field">
            <span class="resource-field__label">Email</span>
            <input
              v-model="email"
              class="resource-input"
              data-testid="register-email-input"
              type="email"
              autocomplete="email"
            />
          </label>

          <label class="resource-field">
            <span class="resource-field__label">密碼</span>
            <input
              v-model="password"
              class="resource-input"
              data-testid="register-password-input"
              type="password"
              autocomplete="new-password"
            />
          </label>
        </div>

        <div class="resource-state__actions">
          <button
            class="resource-action"
            data-testid="register-submit"
            type="button"
            :disabled="submitting"
            @click="handleSubmit"
          >
            {{ submitting ? '註冊中...' : '註冊並登入' }}
          </button>
          <NuxtLink class="resource-action" to="/login">
            已有帳號，前往登入
          </NuxtLink>
        </div>
      </section>
    </section>
  </main>
</template>

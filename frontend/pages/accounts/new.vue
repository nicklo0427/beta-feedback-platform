<script setup lang="ts">
import { ref } from 'vue'

import AccountForm from '~/features/accounts/AccountForm.vue'
import { createAccount } from '~/features/accounts/api'
import {
  buildAccountCreatePayload,
  createEmptyAccountFormValues
} from '~/features/accounts/form'
import type { AccountFormValues } from '~/features/accounts/types'
import { ApiClientError } from '~/services/api/client'

const router = useRouter()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyAccountFormValues()

async function handleSubmit(values: AccountFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    const createdAccount = await createAccount(buildAccountCreatePayload(values))
    await router.push(`/accounts/${createdAccount.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : '目前無法儲存帳號。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/accounts">
          帳號列表
        </NuxtLink>
        <h1 class="resource-shell__title">建立帳號</h1>
        <p class="resource-shell__description">
          建立最小的開發者 / 測試者帳號，作為後續擁有權與目前操作帳號流程的基礎。
        </p>
      </header>

      <section class="resource-section" data-testid="account-create-panel">
        <h2 class="resource-section__title">新增帳號</h2>
        <AccountForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立帳號"
          cancel-to="/accounts"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

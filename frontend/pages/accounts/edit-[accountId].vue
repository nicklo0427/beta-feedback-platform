<script setup lang="ts">
definePageMeta({
  path: '/accounts/:accountId/edit'
})

import { computed, ref, watch } from 'vue'

import AccountForm from '~/features/accounts/AccountForm.vue'
import { fetchAccountDetail, updateAccount } from '~/features/accounts/api'
import {
  buildAccountUpdatePayload,
  createEmptyAccountFormValues,
  toAccountFormValues
} from '~/features/accounts/form'
import type { AccountFormValues } from '~/features/accounts/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const accountId = computed(() => String(route.params.accountId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyAccountFormValues())

const {
  data: account,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `account-edit-${accountId.value}`,
  () => fetchAccountDetail(accountId.value),
  {
    server: false,
    watch: [accountId],
    default: () => null
  }
)

watch(
  account,
  (nextAccount) => {
    if (!nextAccount) {
      return
    }

    initialValues.value = toAccountFormValues(nextAccount)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: AccountFormValues): Promise<void> {
  if (!account.value) {
    submitError.value = '帳號詳情暫時無法使用。'
    return
  }

  const payload = buildAccountUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedAccount = await updateAccount(accountId.value, payload)
    await router.push(`/accounts/${updatedAccount.id}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : '目前無法更新帳號。'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/accounts/${accountId}`">
          帳號詳情
        </NuxtLink>
        <h1 class="resource-shell__title">編輯帳號</h1>
        <p class="resource-shell__description">
          更新既有帳號的最小欄位，為後續擁有權與依角色協作流程維持乾淨的角色基礎。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="account-edit-loading"
      >
        <h2 class="resource-state__title">正在載入帳號編輯表單</h2>
        <p class="resource-state__description">
          正在從 API 載入既有帳號。
        </p>
      </section>

      <section
        v-else-if="error || !account"
        class="resource-state"
        data-testid="account-edit-error"
      >
        <h2 class="resource-state__title">帳號編輯暫時無法使用</h2>
        <p class="resource-state__description">
          {{ error?.message || '無法載入指定的帳號。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/accounts">
            返回帳號列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="account-edit-panel"
      >
        <h2 class="resource-section__title">編輯 {{ account.display_name }}</h2>
        <AccountForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新帳號"
          :cancel-to="`/accounts/${accountId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
definePageMeta({
  path: '/projects/:projectId/campaigns/new'
})

import { computed, ref } from 'vue'

import {
  getActorAwareMutationErrorMessage,
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import CampaignForm from '~/features/campaigns/CampaignForm.vue'
import { createCampaign } from '~/features/campaigns/api'
import {
  buildCampaignCreatePayload,
  createEmptyCampaignFormValues
} from '~/features/campaigns/form'
import type { CampaignFormValues } from '~/features/campaigns/types'
import { fetchProjectDetail } from '~/features/projects/api'

const route = useRoute()
const router = useRouter()
useCurrentActorPersistence()

const projectId = computed(() => String(route.params.projectId))
const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyCampaignFormValues()

const {
  data: project,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `campaign-create-project-${projectId.value}`,
  () => fetchProjectDetail(projectId.value),
  {
    server: false,
    watch: [projectId],
    default: () => null
  }
)

async function handleSubmit(values: CampaignFormValues): Promise<void> {
  if (!currentActorId.value) {
    submitError.value = '建立活動前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const createdCampaign = await createCampaign(
      buildCampaignCreatePayload(projectId.value, values),
      currentActorId.value
    )
    await router.push(`/campaigns/${createdCampaign.id}`)
  } catch (submitFailure) {
    submitError.value = getActorAwareMutationErrorMessage(
      submitFailure,
      '目前無法儲存活動。'
    )
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" :to="`/projects/${projectId}`">
          專案詳情
        </NuxtLink>
        <h1 class="resource-shell__title">建立活動</h1>
        <p class="resource-shell__description">
          在目前的專案底下建立最小活動，作為後續安全設定、資格條件、任務與回饋流程的操作核心。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{
              project
                ? `專案 ${project.name}`
                : `專案 ${projectId}`
            }}
          </span>
          <span
            v-if="currentActorId"
            class="resource-shell__meta-chip"
          >
            actor {{ currentActorId }}
          </span>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-create-loading"
      >
        <h2 class="resource-state__title">正在載入活動建立表單</h2>
        <p class="resource-state__description">
          正在載入專案情境。
        </p>
      </section>

      <section
        v-else-if="error || !project"
        class="resource-state"
        data-testid="campaign-create-error"
      >
        <h2 class="resource-state__title">活動建立暫時無法使用</h2>
        <p class="resource-state__description">
          {{ error?.message || '無法載入活動建立表單。' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            重試
          </button>
          <NuxtLink class="resource-action" to="/projects">
            返回專案列表
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-create-panel"
      >
        <h2 class="resource-section__title">新增活動</h2>
        <CampaignForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立活動"
          :cancel-to="`/projects/${projectId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

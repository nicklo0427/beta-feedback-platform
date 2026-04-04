<script setup lang="ts">
definePageMeta({
  path: '/projects/:projectId/campaigns/new'
})

import { computed, ref } from 'vue'

import CampaignForm from '~/features/campaigns/CampaignForm.vue'
import { createCampaign } from '~/features/campaigns/api'
import {
  buildCampaignCreatePayload,
  createEmptyCampaignFormValues
} from '~/features/campaigns/form'
import type { CampaignFormValues } from '~/features/campaigns/types'
import { fetchProjectDetail } from '~/features/projects/api'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => String(route.params.projectId))
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
  submitError.value = null
  submitting.value = true

  try {
    const createdCampaign = await createCampaign(
      buildCampaignCreatePayload(projectId.value, values)
    )
    await router.push(`/campaigns/${createdCampaign.id}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : 'Unable to save the campaign right now.'
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
          Project Detail
        </NuxtLink>
        <h1 class="resource-shell__title">Create Campaign</h1>
        <p class="resource-shell__description">
          在目前的 Project 底下建立最小 Campaign，作為後續 safety、eligibility、task 與 feedback 流程的操作核心。
        </p>
        <div class="resource-shell__meta">
          <span class="resource-shell__meta-chip">
            {{
              project
                ? `Project ${project.name}`
                : `Project ${projectId}`
            }}
          </span>
        </div>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="campaign-create-loading"
      >
        <h2 class="resource-state__title">Loading campaign create form</h2>
        <p class="resource-state__description">
          正在載入 project context。
        </p>
      </section>

      <section
        v-else-if="error || !project"
        class="resource-state"
        data-testid="campaign-create-error"
      >
        <h2 class="resource-state__title">Campaign create unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The campaign create form could not be loaded.' }}
        </p>
        <div class="resource-state__actions">
          <button class="resource-action" type="button" @click="refresh()">
            Retry
          </button>
          <NuxtLink class="resource-action" to="/projects">
            Back to projects
          </NuxtLink>
        </div>
      </section>

      <section
        v-else
        class="resource-section"
        data-testid="campaign-create-panel"
      >
        <h2 class="resource-section__title">New Campaign</h2>
        <CampaignForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Create campaign"
          :cancel-to="`/projects/${projectId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

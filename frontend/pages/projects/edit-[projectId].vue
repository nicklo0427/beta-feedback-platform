<script setup lang="ts">
definePageMeta({
  path: '/projects/:projectId/edit'
})

import { computed, ref, watch } from 'vue'

import { fetchProjectDetail, updateProject } from '~/features/projects/api'
import ProjectForm from '~/features/projects/ProjectForm.vue'
import {
  buildProjectUpdatePayload,
  createEmptyProjectFormValues,
  toProjectFormValues
} from '~/features/projects/form'
import type { ProjectFormValues } from '~/features/projects/types'
import { ApiClientError } from '~/services/api/client'

const route = useRoute()
const router = useRouter()
const projectId = computed(() => String(route.params.projectId))
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = ref(createEmptyProjectFormValues())

const {
  data: project,
  pending,
  error,
  refresh
} = useAsyncData(
  () => `project-edit-${projectId.value}`,
  () => fetchProjectDetail(projectId.value),
  {
    server: false,
    watch: [projectId],
    default: () => null
  }
)

watch(
  project,
  (nextProject) => {
    if (!nextProject) {
      return
    }

    initialValues.value = toProjectFormValues(nextProject)
    submitError.value = null
  },
  {
    immediate: true
  }
)

async function handleSubmit(values: ProjectFormValues): Promise<void> {
  if (!project.value) {
    submitError.value = '專案詳情暫時無法使用。'
    return
  }

  const payload = buildProjectUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = '目前沒有可儲存的變更。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const updatedProject = await updateProject(projectId.value, payload)
    await router.push(`/projects/${updatedProject.id}`)
  } catch (submitFailure) {
    submitError.value =
      submitFailure instanceof ApiClientError
        ? submitFailure.message
        : '目前無法更新專案。'
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
        <h1 class="resource-shell__title">編輯專案</h1>
        <p class="resource-shell__description">
          更新既有專案的最小欄位，讓上游產品與測試範圍資訊維持一致。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="project-edit-loading"
      >
        <h2 class="resource-state__title">正在載入專案編輯表單</h2>
        <p class="resource-state__description">
          正在從 API 載入既有專案。
        </p>
      </section>

      <section
        v-else-if="error || !project"
        class="resource-state"
        data-testid="project-edit-error"
      >
        <h2 class="resource-state__title">專案編輯暫時無法使用</h2>
        <p class="resource-state__description">
          {{ error?.message || '無法載入指定的專案。' }}
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
        data-testid="project-edit-panel"
      >
        <h2 class="resource-section__title">編輯 {{ project.name }}</h2>
        <ProjectForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="更新專案"
          :cancel-to="`/projects/${projectId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

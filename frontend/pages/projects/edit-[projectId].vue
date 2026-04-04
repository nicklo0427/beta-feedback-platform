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
    submitError.value = 'Project detail is unavailable.'
    return
  }

  const payload = buildProjectUpdatePayload(values, initialValues.value)

  if (!payload) {
    submitError.value = 'No changes to save yet.'
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
        : 'Unable to update the project right now.'
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
        <h1 class="resource-shell__title">Edit Project</h1>
        <p class="resource-shell__description">
          更新既有 Project 的最小欄位，讓上游產品與測試範圍資訊維持一致。
        </p>
      </header>

      <section
        v-if="pending"
        class="resource-state"
        data-testid="project-edit-loading"
      >
        <h2 class="resource-state__title">Loading project edit form</h2>
        <p class="resource-state__description">
          正在從 API 載入既有 Project。
        </p>
      </section>

      <section
        v-else-if="error || !project"
        class="resource-state"
        data-testid="project-edit-error"
      >
        <h2 class="resource-state__title">Project edit unavailable</h2>
        <p class="resource-state__description">
          {{ error?.message || 'The requested project could not be loaded.' }}
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
        data-testid="project-edit-panel"
      >
        <h2 class="resource-section__title">Edit {{ project.name }}</h2>
        <ProjectForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Update project"
          :cancel-to="`/projects/${projectId}`"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import { createProject } from '~/features/projects/api'
import ProjectForm from '~/features/projects/ProjectForm.vue'
import {
  buildProjectCreatePayload,
  createEmptyProjectFormValues
} from '~/features/projects/form'
import type { ProjectFormValues } from '~/features/projects/types'
import { ApiClientError } from '~/services/api/client'

const router = useRouter()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyProjectFormValues()

async function handleSubmit(values: ProjectFormValues): Promise<void> {
  submitError.value = null
  submitting.value = true

  try {
    const createdProject = await createProject(buildProjectCreatePayload(values))
    await router.push(`/projects/${createdProject.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : 'Unable to save the project right now.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="resource-shell">
      <header class="resource-shell__header">
        <NuxtLink class="resource-shell__breadcrumb" to="/projects">
          Projects
        </NuxtLink>
        <h1 class="resource-shell__title">Create Project</h1>
        <p class="resource-shell__description">
          建立一筆最小的 Project，作為後續 campaign、task 與 feedback 流程的上游入口。
        </p>
      </header>

      <section class="resource-section" data-testid="project-create-panel">
        <h2 class="resource-section__title">New Project</h2>
        <ProjectForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="Create project"
          cancel-to="/projects"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>

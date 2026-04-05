<script setup lang="ts">
import { ref } from 'vue'

import CurrentActorSelector from '~/features/accounts/CurrentActorSelector.vue'
import {
  useCurrentActorId,
  useCurrentActorPersistence
} from '~/features/accounts/current-actor'
import { createProject } from '~/features/projects/api'
import ProjectForm from '~/features/projects/ProjectForm.vue'
import {
  buildProjectCreatePayload,
  createEmptyProjectFormValues
} from '~/features/projects/form'
import type { ProjectFormValues } from '~/features/projects/types'
import { ApiClientError } from '~/services/api/client'

const router = useRouter()
useCurrentActorPersistence()

const currentActorId = useCurrentActorId()
const submitError = ref<string | null>(null)
const submitting = ref(false)
const initialValues = createEmptyProjectFormValues()

async function handleSubmit(values: ProjectFormValues): Promise<void> {
  if (!currentActorId.value) {
    submitError.value = '建立專案前，請先選擇目前操作帳號。'
    return
  }

  submitError.value = null
  submitting.value = true

  try {
    const createdProject = await createProject(
      buildProjectCreatePayload(values),
      currentActorId.value
    )
    await router.push(`/projects/${createdProject.id}`)
  } catch (error) {
    submitError.value =
      error instanceof ApiClientError
        ? error.message
        : '目前無法儲存專案。'
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
          專案列表
        </NuxtLink>
        <h1 class="resource-shell__title">建立專案</h1>
        <p class="resource-shell__description">
          建立一筆最小的專案，作為後續活動、任務與回饋流程的上游入口。
        </p>
      </header>

      <CurrentActorSelector
        title="專案擁有者"
        description="選擇目前正在操作的開發者帳號，建立後會自動寫入專案的擁有者欄位。"
      />

      <section class="resource-section" data-testid="project-create-panel">
        <h2 class="resource-section__title">新增專案</h2>
        <ProjectForm
          :initial-values="initialValues"
          :pending="submitting"
          :error-message="submitError"
          submit-label="建立專案"
          cancel-to="/projects"
          @submit="handleSubmit"
        />
      </section>
    </section>
  </main>
</template>
